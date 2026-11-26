# -*- coding: utf-8 -*-
import os, sys, hashlib, subprocess, json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

PROD_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25")
VAULT_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL")
ARTIFACT_DIR = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83")

print("=== 1. VERIFICACIÓN DE ARCHIVOS MP4 ===")
for p in [
    PROD_DIR / "2026-11-25_Equipo_Agentes_IA_10min.mp4",
    VAULT_DIR / "2026-11-25_Equipo_Agentes_IA_10min.mp4",
    ARTIFACT_DIR / "2026-11-25_Equipo_Agentes_IA_10min.mp4"
]:
    if p.exists():
        size = p.stat().st_size
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                h.update(chunk)
        print(f"Ruta: {p}")
        print(f"  Tamaño: {size} bytes ({size/(1024*1024):.2f} MB)")
        print(f"  SHA-256: {h.hexdigest()}")
        print(f"  Mtime: {p.stat().st_mtime}")
    else:
        print(f"Ruta: {p} (NO EXISTE)")

print("\n=== 2. INSPECCIÓN DE AUDIO (equipo_agentes_ia_guiahoy.wav) ===")
wav_p = PROD_DIR / "02_voz_guiahoy" / "equipo_agentes_ia_guiahoy.wav"
if wav_p.exists():
    print(f"Audio path: {wav_p} ({wav_p.stat().st_size} bytes)")
    # Check if there is another audio or what is the text spoken
    pcmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(wav_p)]
    res = subprocess.run(pcmd, capture_output=True, text=True)
    info = json.loads(res.stdout)
    print("  Duration:", info["format"].get("duration"))
    print("  Bitrate:", info["format"].get("bit_rate"))
    print("  Tags:", info["format"].get("tags", {}))

print("\n=== 3. INSPECCIÓN DE FONDOS (fondos_16x9) ===")
fondos_dir = PROD_DIR / "fondos_16x9"
for f in sorted(fondos_dir.glob("bg_*.jpg")):
    print(f"  {f.name}: {f.stat().st_size} bytes, mtime={f.stat().st_mtime}")

print("\n=== 4. INSPECCIÓN DEL REPRODUCTOR HTML ===")
rep_html = ARTIFACT_DIR / "reproductor_equipo_agentes_ia_10min.html"
if rep_html.exists():
    content = rep_html.read_text(encoding="utf-8")
    for line in content.splitlines():
        if "source src" in line or "meta-val" in line or "sha256" in line.lower() or "video" in line.lower():
            print("  [HTML]", line.strip())

print("\n=== 5. INSPECCIÓN DE CLIPS DE AVATAR (06_Avatar_Clip_Library) ===")
av_lib = Path(r"G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library")
for c in sorted(av_lib.glob("AVM_*.mp4"))[:3]:
    print(f"  {c.name}: {c.stat().st_size} bytes")
