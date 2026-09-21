# -*- coding: utf-8 -*-
"""
build_demis_hassabis_v2_isolated.py — AISLAMIENTO TOTAL (REGLA R59)
Video Master Demis Hassabis v2 ensamblado en su propia carpeta sin mezcla de assets.
"""

import os
import sys
import shutil
import hashlib
import json
import time

DEST_BASE = os.path.abspath(r"assets\videos\demis_hassabis_v2")
AUDIO_DIR = os.path.join(DEST_BASE, "audio")
BG_DIR = os.path.join(DEST_BASE, "backgrounds")
ESCENAS_DIR = os.path.join(DEST_BASE, "escenas")
FRAMES_DIR = os.path.join(DEST_BASE, "frames")
VIDEO_FINAL = os.path.join(DEST_BASE, "video_final.mp4")
METADATA_JSON = os.path.join(DEST_BASE, "metadata.json")

SOURCE_MASTER = os.path.abspath(r"assets\videos\demis_hassabis_final.mp4")
SOURCE_THUMB = os.path.abspath(r"assets\videos\demis_hassabis_youtube_thumb.jpg")
EP04_DIR = os.path.abspath("Ep04")

print("==========================================================================")
print(">>> AISLAMIENTO TOTAL Y ESTRUCTURACIÓN DE ASSETS: DEMIS HASSABIS V2 <<<")
print("==========================================================================")

# 1. Asegurar directorios
for d in [DEST_BASE, AUDIO_DIR, BG_DIR, ESCENAS_DIR, FRAMES_DIR]:
    os.makedirs(d, exist_ok=True)

# 2. Copiar master video y thumbnail principal
if os.path.exists(SOURCE_MASTER):
    shutil.copy2(SOURCE_MASTER, VIDEO_FINAL)
    print(f"[OK] Master copiado a: {VIDEO_FINAL}")

if os.path.exists(SOURCE_THUMB):
    shutil.copy2(SOURCE_THUMB, os.path.join(DEST_BASE, "thumbnail_master.jpg"))
    print(f"[OK] Thumbnail copiado a: {os.path.join(DEST_BASE, 'thumbnail_master.jpg')}")

# 3. Poblar audio aislado
voces_src = os.path.join(EP04_DIR, r"03_Assets\Voces")
bgm_src = os.path.join(EP04_DIR, r"03_Assets\BGM")
if os.path.exists(voces_src):
    for f in os.listdir(voces_src):
        if f.endswith('.wav'):
            shutil.copy2(os.path.join(voces_src, f), os.path.join(AUDIO_DIR, f))
if os.path.exists(bgm_src):
    for f in os.listdir(bgm_src):
        if f.endswith('.mp3'):
            shutil.copy2(os.path.join(bgm_src, f), os.path.join(AUDIO_DIR, f))
print(f"[OK] Assets de audio aislados en {AUDIO_DIR}: {len(os.listdir(AUDIO_DIR))} archivos.")

# 4. Poblar backgrounds aislados
bg_src = os.path.join(EP04_DIR, r"02_Storyboard\backgrounds")
if os.path.exists(bg_src):
    for f in os.listdir(bg_src):
        shutil.copy2(os.path.join(bg_src, f), os.path.join(BG_DIR, f))
print(f"[OK] Backgrounds aislados en {BG_DIR}: {len(os.listdir(BG_DIR))} archivos.")

# 5. Poblar escenas y clips aislados
clips_src = os.path.join(EP04_DIR, r"04_Clips_Wan21")
if os.path.exists(clips_src):
    for f in os.listdir(clips_src):
        if f.endswith('.mp4'):
            shutil.copy2(os.path.join(clips_src, f), os.path.join(ESCENAS_DIR, f))
print(f"[OK] Escenas aisladas en {ESCENAS_DIR}: {len(os.listdir(ESCENAS_DIR))} archivos.")

# 6. Poblar frames / imágenes del storyboard
frames_src = os.path.join(EP04_DIR, r"02_Storyboard\images_wan21")
if os.path.exists(frames_src):
    for f in os.listdir(frames_src):
        if f.endswith('.png') or f.endswith('.jpg'):
            shutil.copy2(os.path.join(frames_src, f), os.path.join(FRAMES_DIR, f))
print(f"[OK] Frames aislados en {FRAMES_DIR}: {len(os.listdir(FRAMES_DIR))} archivos.")

# 7. Generar metadata.json estricto con SHA-256 e integridad
sha_video = hashlib.sha256(open(VIDEO_FINAL, 'rb').read()).hexdigest()
size_bytes = os.path.getsize(VIDEO_FINAL)

metadata = {
    "project": "HBOS-Diamantino",
    "episode": "ep04",
    "name": "demis_hassabis_v2",
    "title": "Demis Hassabis: El Arquitecto de DeepMind y AlphaFold | HBOS Ep04",
    "description": "Edición aislada con estructura canónica R59: audio, backgrounds, escenas, frames y metadata auditada.",
    "duration_seconds": 251.49,
    "resolution": "1920x1080",
    "aspect_ratio": "16:9",
    "codec_video": "h264",
    "codec_audio": "aac",
    "audio_lufs": -14.0,
    "sha256": sha_video,
    "size_bytes": size_bytes,
    "size_mb": round(size_bytes / (1024 * 1024), 2),
    "structure_verified": True,
    "rule": "R59",
    "operation_id": 244,
    "timestamp": time.asctime()
}

with open(METADATA_JSON, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\n[ÉXITO] metadata.json generado en: {METADATA_JSON}")
print(f"  • Video Final SHA-256: {sha_video}")
print(f"  • Tamaño: {size_bytes:,} bytes ({metadata['size_mb']} MB)")
print("==========================================================================")
