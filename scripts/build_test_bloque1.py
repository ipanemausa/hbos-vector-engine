# -*- coding: utf-8 -*-
r"""
HBOS SINGLE SHORT TEST CLIP GENERATOR: test_bloque1.mp4
======================================================
Genera un clip de prueba aislado de 8 segundos en:
G:\My Drive\Guiahoy_Produccion\2026-11-25\_test_clean_clip\test_bloque1.mp4
Insumos:
- Fondo: bg_01.jpg (1920x1080) con zoompan continuo lento
- Avatar: AVM_01_HOOK_OPENING.mp4 (8.0s) de 06_Avatar_Clip_Library
- Audio: Voz clonada de Guiahoy (primeros 8s de Guiahoy_CLONE_REF_90s_48k.wav a 48kHz / -14 LUFS / 109.2Hz)
"""

import os, sys, subprocess, shutil, hashlib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

PROD_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25")
TEST_DIR = PROD_DIR / "_test_clean_clip"
TEST_DIR.mkdir(parents=True, exist_ok=True)

BG_PATH = PROD_DIR / "fondos_16x9" / "bg_01.jpg"
AVATAR_PATH = Path(r"G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library\AVM_01_HOOK_OPENING.mp4")
AUDIO_REF = Path(r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_CLONE_REF_90s_48k.wav")

OUT_MP4 = TEST_DIR / "test_bloque1.mp4"
TEMP_DIR = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\temp_cinematic")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
TEMP_AUDIO = TEMP_DIR / "audio_8s_test.wav"

DUR = 8.0
FRAMES = int(DUR * 30)

print(f"[*] 1. Extrayendo audio de voz clonada Guiahoy ({DUR}s, -14 LUFS)...")
subprocess.run([
    "ffmpeg", "-y",
    "-t", str(DUR),
    "-i", str(AUDIO_REF),
    "-af", "highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.5:LRA=11",
    "-ar", "48000", "-ac", "1",
    str(TEMP_AUDIO)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"[+] Audio listo: {TEMP_AUDIO} ({TEMP_AUDIO.stat().st_size} bytes)")

print(f"[*] 2. Componiendo clip de prueba ({DUR}s): bg_01.jpg + AVM_01 + voz...")
filter_complex = (
    f"[0:v]zoompan=z='min(zoom+0.0004,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={FRAMES}:s=1920x1080:fps=30[bg];"
    f"[1:v]scale=640:360,format=yuv420p[av];"
    f"[bg][av]overlay=W-w-30:H-h-20:shortest=1[v]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", str(BG_PATH),
    "-i", str(AVATAR_PATH),
    "-i", str(TEMP_AUDIO),
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "2:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-t", str(DUR),
    str(OUT_MP4)
]
subprocess.run(cmd, check=True)

# Copiar a directorio de artefactos para visor HTML
ARTIFACT_DIR = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83")
artifact_clip = ARTIFACT_DIR / "test_bloque1.mp4"
shutil.copy2(str(OUT_MP4), str(artifact_clip))

h = hashlib.sha256()
with open(OUT_MP4, "rb") as f:
    for chunk in iter(lambda: f.read(1024*1024), b""):
        h.update(chunk)
sha = h.hexdigest()
size_kb = OUT_MP4.stat().st_size / 1024

print(f"\n[+] CLIP DE PRUEBA GENERADO EXITOSAMENTE:")
print(f"    Ruta: {OUT_MP4}")
print(f"    Ruta Artefacto: {artifact_clip}")
print(f"    Duración: {DUR}s | Tamaño: {size_kb:.1f} KB")
print(f"    SHA-256: {sha}")
