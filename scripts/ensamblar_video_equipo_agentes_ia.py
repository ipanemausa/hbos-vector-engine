# -*- coding: utf-8 -*-
r"""
Ensamblador Canónico de Video para "Equipo de Agentes de IA"
Arquitectura HBOS (Pre-composite Turbo):
- 10 Bloques 16:9 (1920x1080 @ 30fps)
- Fondos futuristas bg_01.jpg a bg_10.jpg
- Avatares 3D transparentes en esquina inferior derecha (scale=-1:780, format=rgba, overlay=W-w-40:H-h)
- Pre-composición instantánea por bloque con PIL + Codificación H.264 stillimage
- Audio masterizado (-14 LUFS, 48kHz, sin afftdn)
- Conexión e indexación en Qdrant (canon_video_hbos_r768)
- Auto-launch canónico (RULE_AUTO_LAUNCH_01)
"""

import os
import sys
import json
import uuid
import hashlib
import shutil
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PROD_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25")
FONDOS_DIR = PROD_DIR / "fondos_16x9"
AVATAR_DIR = Path(r"G:\My Drive\Avatar Guillermo - transparencias")
VOZ_DIR = PROD_DIR / "02_voz_guiahoy"
AUDIO_MASTER = VOZ_DIR / "equipo_agentes_ia_guiahoy.wav"
TIMINGS_FILE = PROD_DIR / "block_timings.json"

FINAL_MP4 = PROD_DIR / "2026-11-25_Equipo_Agentes_IA_10min.mp4"
VAULT_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL")
VAULT_MP4 = VAULT_DIR / "2026-11-25_Equipo_Agentes_IA_10min.mp4"
MANIFEST_FILE = PROD_DIR / "2026-11-25_Equipo_Agentes_IA_10min_manifest.json"
SRT_FILE = PROD_DIR / "2026-11-25_Equipo_Agentes_IA_10min.srt"

TEMP_DIR = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\temp_render")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

QDRANT_LOCAL_URL = "http://127.0.0.1:6333"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def render_blocks():
    assert AUDIO_MASTER.exists(), f"ERROR: {AUDIO_MASTER} no existe"
    assert TIMINGS_FILE.exists(), f"ERROR: {TIMINGS_FILE} no existe"
    
    with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
        timings_data = json.load(f)
        
    blocks = timings_data["blocks"]
    total = len(blocks)
    print(f"[*] Pre-componiendo y ensamblando {total} bloques 16:9...")
    
    rendered_clips = []
    for idx, b in enumerate(blocks):
        b_id = b["block_id"]
        bg_path = FONDOS_DIR / b["fondo"]
        av_path = AVATAR_DIR / b["avatar"]
        
        pause = 0.8 if idx < total - 1 else 0.0
        clip_dur = round(b["duration"] + pause, 3)
        
        # 1. Pre-composición PIL (escala avatar a altura 780, anclado a W-w-40, H-h)
        composite_jpg = TEMP_DIR / f"composite_block_{b_id:02d}.jpg"
        bg_img = Image.open(bg_path).convert("RGBA").resize((1920, 1080))
        av_img = Image.open(av_path).convert("RGBA")
        
        orig_w, orig_h = av_img.size
        new_h = 780
        new_w = int(orig_w * (new_h / orig_h))
        av_scaled = av_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        x_pos = 1920 - new_w - 40
        y_pos = 1080 - new_h
        bg_img.paste(av_scaled, (x_pos, y_pos), av_scaled)
        bg_img.convert("RGB").save(str(composite_jpg), quality=95)
        
        # 2. Codificación turbo H.264 stillimage
        out_clip = TEMP_DIR / f"clip_block_{b_id:02d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", "30", "-t", str(clip_dur),
            "-i", str(composite_jpg),
            "-c:v", "libx264", "-tune", "stillimage", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            str(out_clip)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Bloque {b_id:02d}: {b['modulo'][:30]}... ({clip_dur:.2f}s) OK")
        rendered_clips.append(str(out_clip))
        
    # Concatenar todos los clips de video
    concat_txt = TEMP_DIR / "video_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in rendered_clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")
            
    temp_silent_video = TEMP_DIR / "video_silent_full.mp4"
    print("[*] Concatenando flujo de video maestro...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "copy",
        str(temp_silent_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Mux con audio maestro
    print("[*] Muxing final con audio maestro...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(temp_silent_video),
        "-i", str(AUDIO_MASTER),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest",
        str(FINAL_MP4)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Copiar a Media Vault
    print(f"[*] Replicando a bóveda: {VAULT_MP4}")
    shutil.copy2(str(FINAL_MP4), str(VAULT_MP4))
    
    # Copiar a artifacts
    artifact_mp4 = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83\2026-11-25_Equipo_Agentes_IA_10min.mp4")
    shutil.copy2(str(FINAL_MP4), str(artifact_mp4))
    
    # Calcular hash
    h_final = sha256_file(FINAL_MP4)
    size_mb = round(FINAL_MP4.stat().st_size / (1024 * 1024), 2)
    
    pcmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(FINAL_MP4)]
    res = subprocess.run(pcmd, capture_output=True, text=True, check=True)
    dur_final = float(json.loads(res.stdout)["format"]["duration"])
    
    manifest_data = {
        "project": "Equipo de Agentes de IA",
        "date": "2026-11-25",
        "title": "Equipo de Agentes de IA - 10 Bloques de Productividad Autonoma",
        "speaker": "Guillermo Alonso Hoyos (Guiahoy)",
        "resolution": "1920x1080",
        "fps": 30,
        "video_codec": "h264",
        "audio_codec": "aac_48khz",
        "loudness_target": "-14.0 LUFS EBU R128",
        "duration_seconds": dur_final,
        "duration_minutes": round(dur_final / 60, 2),
        "size_mb": size_mb,
        "sha256": h_final,
        "path_drive": str(FINAL_MP4),
        "path_vault": str(VAULT_MP4),
        "srt_path": str(SRT_FILE),
        "timings_path": str(TIMINGS_FILE),
        "layers": {
            "guion": "guion_equipo_agentes_ia.md (10 bloques)",
            "audio": "02_voz_guiahoy/equipo_agentes_ia_guiahoy.wav",
            "fondos": "fondos_16x9/bg_01.jpg a bg_10.jpg",
            "avatar": "Avatar Guillermo - transparencias (RGBA -1:780 overlay)",
            "subtitulos": "2026-11-25_Equipo_Agentes_IA_10min.srt"
        }
    }
    
    MANIFEST_FILE.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[+] MANIFIESTO SHA-256 GUARDADO: {MANIFEST_FILE}")
    print(f"    SHA-256: {h_final}")
    print(f"    Duración: {dur_final:.2f}s ({dur_final/60:.2f} min) | Tamaño: {size_mb} MB")
    
    index_qdrant(manifest_data)
    auto_launch()

def deterministic_vector(text: str, dim: int = 768) -> list:
    vec = []
    counter = 0
    while len(vec) < dim:
        h = hashlib.sha256(f"{text}:{counter}".encode("utf-8")).digest()
        for i in range(0, len(h), 4):
            if len(vec) >= dim:
                break
            val = int.from_bytes(h[i:i+4], "little", signed=True) / 2147483648.0
            vec.append(round(val, 6))
        counter += 1
    norm = sum(x * x for x in vec) ** 0.5 or 1.0
    return [round(x / norm, 6) for x in vec]

def index_qdrant(manifest: dict):
    print("[*] Indexando metadatos en Qdrant...")
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"hbos_equipo_agentes_ia_20261125_{manifest['sha256']}"))
    vec_768 = deterministic_vector(f"guiahoy equipo agentes ia 2026-11-25 {manifest['sha256']}", 768)
    
    payload = {
        "project": manifest["project"],
        "date": manifest["date"],
        "title": manifest["title"],
        "speaker": manifest["speaker"],
        "duration_sec": manifest["duration_seconds"],
        "sha256": manifest["sha256"],
        "drive_path": manifest["path_drive"],
        "vault_path": manifest["path_vault"],
        "srt_path": manifest["srt_path"],
        "status": "PRODUCED_CANONICAL_HBOS",
        "architecture": "HBOS_PRODUCTION_DAG_01"
    }
    
    body = json.dumps({"points": [{"id": point_id, "vector": vec_768, "payload": payload}]}).encode("utf-8")
    req = urllib.request.Request(
        f"{QDRANT_LOCAL_URL}/collections/canon_video_hbos_r768/points?wait=true",
        data=body, headers={"Content-Type": "application/json"}, method="PUT"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status in (200, 201):
                print(f"[+] Indexado exitoso en Qdrant canon_video_hbos_r768 (ID: {point_id})")
    except Exception as e:
        print(f"[!] Qdrant aviso: {e}")

def auto_launch():
    print("[*] Disparando RULE_AUTO_LAUNCH_01...")
    try:
        os.startfile(str(FINAL_MP4))
        print(f"[+] Reproductor de sistema abierto para {FINAL_MP4.name}")
    except Exception as e:
        print(f"[!] Aviso al disparar os.startfile: {e}")

if __name__ == "__main__":
    render_blocks()
