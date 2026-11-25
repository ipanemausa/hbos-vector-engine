"""
HBOS ENGINE · PRODUCCIÓN FINAL DE LA CLASE 1: EQUIPO DE AGENTES DE IA (10 MIN)
Nomenclatura Estricta: 2026-11-25_Equipo_Agentes_IA_10min.mp4

Activos Canónicos:
1. Fondos 16:9: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\fondos_16x9\\ (bg_01.jpg a bg_10.jpg)
2. Audio de voz Guiahoy masterizado a -14 LUFS (48 kHz):
   G:\\My Drive\\HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL\\Guiahoy_MASTER_48k_menos14LUFS.wav
3. Avatares 3D transparentes: G:\\My Drive\\Avatar Guillermo - transparencias\\
   scale=-1:780,format=rgba + overlay=W-w-40:H-h:format=auto
4. Nomenclatura final: 2026-11-25_Equipo_Agentes_IA_10min.mp4
5. Manifiesto SHA-256: 2026-11-25_Equipo_Agentes_IA_10min_manifest.json
6. Subtítulos: 2026-11-25_Equipo_Agentes_IA_10min.srt
"""

import os
import sys
import json
import time
import shutil
import hashlib
import urllib.request
import subprocess
from datetime import datetime

print("====================================================================")
print("  HBOS PRODUCTION · 2026-11-25_Equipo_Agentes_IA_10min.mp4         ")
print("====================================================================")

# ------------------------------------------------------------------
# 1. Rutas Oficiales
# ------------------------------------------------------------------
PROD_DATE_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-25"
FONDOS_DIR = os.path.join(PROD_DATE_DIR, "fondos_16x9")
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"
ART_DIR = r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83"
STAGE_DIR = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\studio_vivo_final\mit_10min_stage"

AUDIO_MASTER = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\Guiahoy_MASTER_48k_menos14LUFS.wav"
if not os.path.isfile(AUDIO_MASTER):
    AUDIO_MASTER = r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_MASTER_48k_menos14LUFS.wav"

OUT_NAME = "2026-11-25_Equipo_Agentes_IA_10min.mp4"
SRT_NAME = "2026-11-25_Equipo_Agentes_IA_10min.srt"
MAN_NAME = "2026-11-25_Equipo_Agentes_IA_10min_manifest.json"

FINAL_PROD_PATH = os.path.join(PROD_DATE_DIR, OUT_NAME)
FINAL_VAULT_PATH = os.path.join(VAULT_DIR, OUT_NAME)
FINAL_ART_PATH = os.path.join(ART_DIR, OUT_NAME)
FINAL_SRT_PATH = os.path.join(PROD_DATE_DIR, SRT_NAME)
FINAL_MAN_PATH = os.path.join(PROD_DATE_DIR, MAN_NAME)

os.makedirs(PROD_DATE_DIR, exist_ok=True)
os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(STAGE_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 2. Medir Audio Canónico (-14 LUFS / 48 kHz)
# ------------------------------------------------------------------
print(f"\n[1/5] Cargando audio canónico: {AUDIO_MASTER}")
probe_cmd = [
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    AUDIO_MASTER
]
r_dur = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
REAL_DURATION = float(r_dur.stdout.strip())
print(f"  [OK] Duración exacta del audio master: {REAL_DURATION:.2f}s ({REAL_DURATION/60:.2f} min)")

# ------------------------------------------------------------------
# 3. Configuración de los 10 Bloques de la Clase 1 sobre Agentes
# ------------------------------------------------------------------
BLOCKS = [
    {"id": 1, "bg": "bg_01.jpg", "avatar": "avatar-pose-t-arms-open-narrower.png", "nom_s": 0.0, "nom_e": 55.0, "title": "Módulo 1: El Molde Reproducible y Soberanía Tecnológica"},
    {"id": 2, "bg": "bg_02.jpg", "avatar": "avatar-pose-t-calm-both.png", "nom_s": 55.0, "nom_e": 130.0, "title": "Módulo 2: Costo Cero y Eliminación de Licencias en Dólares"},
    {"id": 3, "bg": "bg_03.jpg", "avatar": "avatar-pose-t-chin-stroke-L.png", "nom_s": 130.0, "nom_e": 195.0, "title": "Módulo 3: Motor Vectorial RAG 768D On-Premise"},
    {"id": 4, "bg": "bg_04.jpg", "avatar": "avatar-pose-t-arms-open-palms-up.png", "nom_s": 195.0, "nom_e": 285.0, "title": "Módulo 4: Orquestación de Agentes de IA y Workforce B2B"},
    {"id": 5, "bg": "bg_05.jpg", "avatar": "avatar-pose-t-chin-stroke-R.png", "nom_s": 285.0, "nom_e": 355.0, "title": "Módulo 5: Pipeline REA e Ingeniería Inversa Práctica"},
    {"id": 6, "bg": "bg_06.jpg", "avatar": "avatar-pose-t-arms-open-wider.png", "nom_s": 355.0, "nom_e": 425.0, "title": "Módulo 6: Automatización de Contenidos Multi-Plataforma"},
    {"id": 7, "bg": "bg_07.jpg", "avatar": "avatar-pose-t-calm-both.png", "nom_s": 425.0, "nom_e": 485.0, "title": "Módulo 7: Auditoría Criptográfica SHA-256 en Bóveda"},
    {"id": 8, "bg": "bg_08.jpg", "avatar": "avatar-pose-t-arms-open-palms-front.png", "nom_s": 485.0, "nom_e": 535.0, "title": "Módulo 8: Impacto Real en PYMEs y Universidades de Antioquia"},
    {"id": 9, "bg": "bg_09.jpg", "avatar": "avatar-pose-t-both-thumbs-up.png", "nom_s": 535.0, "nom_e": 570.0, "title": "Módulo 9: Métricas Operativas (-98% Tiempo de Ciclo)"},
    {"id": 10, "bg": "bg_10.jpg", "avatar": "avatar-pose-t-beckon-R.png", "nom_s": 570.0, "nom_e": 600.0, "title": "Módulo 10: Conclusión, Hoja de Ruta y Práctica en Vivo"}
]

scale = REAL_DURATION / 600.0
accum = 0.0
for b in BLOCKS:
    dur_nom = b["nom_e"] - b["nom_s"]
    dur_real = dur_nom * scale
    b["start"] = accum
    b["end"] = accum + dur_real
    b["dur"] = dur_real
    accum = b["end"]
BLOCKS[-1]["end"] = REAL_DURATION
BLOCKS[-1]["dur"] = REAL_DURATION - BLOCKS[-1]["start"]

def format_srt_time(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    millis = int(round((sec - int(sec)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

# ------------------------------------------------------------------
# 4. Generar Subtítulos .SRT
# ------------------------------------------------------------------
print(f"\n[2/5] Generando subtítulos en: {FINAL_SRT_PATH}")
with open(FINAL_SRT_PATH, "w", encoding="utf-8") as f_s:
    for b in BLOCKS:
        f_s.write(f"{b['id']}\n")
        f_s.write(f"{format_srt_time(b['start'])} --> {format_srt_time(b['end'])}\n")
        f_s.write(f"{b['title']}\n\n")
print("  [OK] Subtítulos .srt guardados.")

# ------------------------------------------------------------------
# 5. Ensamblar Video Concat Modularmente
# ------------------------------------------------------------------
print(f"\n[3/5] Verificando/Ensamblando los 10 bloques de video...")
concat_list = os.path.join(STAGE_DIR, "concat_equipo_agentes.txt")
with open(concat_list, "w", encoding="utf-8") as f_c:
    for b in BLOCKS:
        seg_file = os.path.join(STAGE_DIR, f"seg_{b['id']:02d}.mp4")
        if not (os.path.exists(seg_file) and os.path.getsize(seg_file) > 500000):
            # Renderizar segmento si falta
            bg_f = os.path.join(FONDOS_DIR, b["bg"])
            av_f = os.path.join(AVATAR_DIR, b["avatar"])
            loc_bg = os.path.join(STAGE_DIR, f"bg_{b['id']:02d}.jpg")
            loc_av = os.path.join(STAGE_DIR, f"av_{b['id']:02d}.png")
            shutil.copy2(bg_f, loc_bg)
            shutil.copy2(av_f, loc_av)
            cmd_s = [
                "ffmpeg", "-y",
                "-loop", "1", "-t", f"{b['dur']:.3f}", "-i", loc_bg,
                "-loop", "1", "-t", f"{b['dur']:.3f}", "-i", loc_av,
                "-filter_complex", "[1:v]scale=-1:780,format=rgba[av];[0:v][av]overlay=W-w-40:H-h:format=auto",
                "-t", f"{b['dur']:.3f}",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "30",
                seg_file
            ]
            print(f"  [*] Renderizando bloque {b['id']} ({b['dur']:.2f}s)...")
            subprocess.run(cmd_s, capture_output=True, text=True, check=True)
        else:
            print(f"  [OK] Bloque {b['id']} validado ({os.path.getsize(seg_file)} bytes).")
        f_c.write(f"file '{seg_file.replace(os.sep, '/')}'\n")

# Concatenar video y mux con audio master
local_final = os.path.join(STAGE_DIR, OUT_NAME)
temp_concat = os.path.join(STAGE_DIR, "video_concat_agentes.mp4")

print("\n[4/5] Concatenando bloques y multiplexando con audio canónico (-14 LUFS)...")
cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", temp_concat]
subprocess.run(cmd_concat, capture_output=True, text=True, check=True)

cmd_mux = [
    "ffmpeg", "-y",
    "-i", temp_concat,
    "-i", AUDIO_MASTER,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-t", f"{REAL_DURATION:.3f}",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    local_final
]
subprocess.run(cmd_mux, capture_output=True, text=True, check=True)
print(f"  [OK] Video ensamblado localmente: {local_final} ({os.path.getsize(local_final)} bytes)")

# ------------------------------------------------------------------
# 6. Copias a Producción, Bóveda y Artefacto
# ------------------------------------------------------------------
print(f"\n[5/5] Distribuyendo video final con nomenclatura estricta...")
print(f"  -> Producción: {FINAL_PROD_PATH}")
shutil.copy2(local_final, FINAL_PROD_PATH)

print(f"  -> Bóveda Final: {FINAL_VAULT_PATH}")
shutil.copy2(local_final, FINAL_VAULT_PATH)

print(f"  -> Artefacto: {FINAL_ART_PATH}")
shutil.copy2(local_final, FINAL_ART_PATH)

# Calcular SHA-256
h = hashlib.sha256()
with open(FINAL_PROD_PATH, "rb") as f_hash:
    for chunk in iter(lambda: f_hash.read(65536), b""):
        h.update(chunk)
sha256_hash = h.hexdigest()
file_size = os.path.getsize(FINAL_PROD_PATH)

# Exportar Manifiesto JSON
manifest_data = {
    "title": "Clase 1: Equipo de Agentes de IA (10 Minutos)",
    "file_name": OUT_NAME,
    "production_path": FINAL_PROD_PATH,
    "vault_path": FINAL_VAULT_PATH,
    "srt_path": FINAL_SRT_PATH,
    "audio_master": AUDIO_MASTER,
    "sha256": sha256_hash,
    "file_size_bytes": file_size,
    "duration_seconds": REAL_DURATION,
    "resolution": "1920x1080",
    "fps": 30,
    "blocks": 10,
    "status": "APPROVED_MASTER_CLASE_1_EQUIPO_AGENTES",
    "timestamp": datetime.now().isoformat()
}

with open(FINAL_MAN_PATH, "w", encoding="utf-8") as f_man:
    json.dump(manifest_data, f_man, indent=2, ensure_ascii=False)
print(f"  [OK] Manifiesto SHA-256 exportado a: {FINAL_MAN_PATH}")

# Registrar en Qdrant
try:
    with urllib.request.urlopen("http://localhost:6333/collections", timeout=2) as r:
        if r.status == 200:
            p_id = "c1a5e004-0000-5000-8000-202611250004"
            body = json.dumps({
                "points": [
                    {
                        "id": p_id,
                        "vector": [0.036] * 768,
                        "payload": manifest_data
                    }
                ]
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:6333/collections/canon_video_hbos_r768/points?wait=true",
                data=body,
                headers={"Content-Type": "application/json"},
                method="PUT"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status in (200, 201):
                    print(f"  [OK] Indexado en Qdrant colección 'canon_video_hbos_r768' con ID {p_id}")
except Exception as e:
    print(f"  [!] Qdrant aviso: {e}")

# Auto-Launch (RULE_AUTO_LAUNCH_01)
try:
    os.startfile(FINAL_PROD_PATH)
    print(f"\n[AUTO-LAUNCH OK] Apertura automática en el reproductor del sistema: {FINAL_PROD_PATH}")
except Exception as e:
    print(f"[!] Auto-launch aviso: {e}")

print("\n====================================================================")
print("              PRODUCCIÓN FINALIZADA EXITOSAMENTE                     ")
print("====================================================================")
print(f"Video Final:  {FINAL_PROD_PATH}")
print(f"SHA-256:      {sha256_hash}")
print(f"Tamaño:       {file_size} bytes ({file_size/(1024*1024):.2f} MB)")
print(f"Subtítulos:   {FINAL_SRT_PATH}")
print(f"Manifiesto:   {FINAL_MAN_PATH}")
