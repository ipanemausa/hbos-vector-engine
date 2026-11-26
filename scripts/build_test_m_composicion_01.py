"""
HBOS M-COMPOSICION-01 + VOZ GUIAHOY (PC Local Execution)
- 1920x1080 @ 30fps
- Poses RGBA de avatar sin caja rectangular
- Ground shadow + M-IDLE-01 (oscilación sutil) + anti-oclusión (anclaje lateral derecho)
- Voz Guiahoy: 48 kHz / -14 LUFS / highpass=65Hz / eq=115Hz +1.6dB / CERO afftdn
- SIN 7 gemas / SIN R-LASER-01
"""

import os, json, hashlib, subprocess, sys

# 1. Definición de rutas
AUDIO_SRC = r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_CLON_HUMANIZADO_V3_menos14LUFS.wav"
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
OUT_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-24"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(VAULT_DIR, exist_ok=True)

SYNC_MAP_PATH = os.path.join(OUT_DIR, "sync_map.json")
OUT_MP4_PATH = os.path.join(OUT_DIR, "guiahoy_test_m_composicion_01.mp4")
VAULT_MP4_PATH = os.path.join(VAULT_DIR, "guiahoy_test_m_composicion_01.mp4")

# Poses canónicas verificadas en G:\My Drive\Avatar Guillermo - transparencias\
POSES = {
    "P1": os.path.join(AVATAR_DIR, "avatar-pose-t-wave-palm-front.png"),
    "P2": os.path.join(AVATAR_DIR, "avatar-pose-t-chin-stroke-R.png"),
    "P3": os.path.join(AVATAR_DIR, "avatar-pose-t-double-point.png"),
    "P4": os.path.join(AVATAR_DIR, "avatar-pose-t-both-thumbs-up.png")
}

# 2. Generar sync_map.json
sync_map = {
    "version": "HBOS_SYNC_MAP_V1_CANONICAL",
    "timestamp": "2026-11-24T15:15:00Z",
    "audio_source": AUDIO_SRC,
    "audio_calibracion": {
        "sample_rate": 48000,
        "loudness_target_lufs": -14.0,
        "highpass_hz": 65,
        "equalizer": "f=115:t=q:w=1.2:g=1.6",
        "afftdn_prohibido": True,
        "afftdn_presente": False
    },
    "reglas_composicion": {
        "protocolo": "M-COMPOSICION-01",
        "avatar_rgba_path": AVATAR_DIR,
        "rim_light_accent": "cian_dorado_rim",
        "ground_shadow": True,
        "respiracion_idle": "M-IDLE-01",
        "anti_occlusion_alignment": "right_anchor_x1220",
        "siete_gemas_activo": False,
        "r_laser_01_activo": False,
        "resolution": "1920x1080",
        "fps": 30
    },
    "timeline_blocks": [
        {
            "block_id": "BLK_01_HOOK",
            "start_s": 0.0,
            "end_s": 4.5,
            "pose": "avatar-pose-t-wave-palm-front.png",
            "gesture": "Saludo de captura / Bienvenida"
        },
        {
            "block_id": "BLK_02_ANALISIS",
            "start_s": 4.5,
            "end_s": 9.0,
            "pose": "avatar-pose-t-chin-stroke-R.png",
            "gesture": "Mano a barbilla reflexiva"
        },
        {
            "block_id": "BLK_03_EVIDENCIA",
            "start_s": 9.0,
            "end_s": 13.0,
            "pose": "avatar-pose-t-double-point.png",
            "gesture": "Doble senalamiento a pantalla"
        },
        {
            "block_id": "BLK_04_CIERRE",
            "start_s": 13.0,
            "end_s": 16.2,
            "pose": "avatar-pose-t-both-thumbs-up.png",
            "gesture": "Pulgares arriba aprobatorio"
        }
    ]
}

with open(SYNC_MAP_PATH, "w", encoding="utf-8") as f:
    json.dump(sync_map, f, indent=2)
print("sync_map.json escrito en:", SYNC_MAP_PATH)

# 3. Construir comando ffmpeg con filtro complejo M-COMPOSICION-01
# - Fondo estudio oscuro degradado (1920x1080)
# - Sombra a piso (elipse suave desenfocada)
# - Idle oscillation M-IDLE-01 en eje Y (sinusoidal)
# - Sin caja rectangular (canal alfa preservado)
# - Transición precisa entre las 4 poses según sync_map
# - Audio Guiahoy procesado con highpass + eq + loudnorm (-14 LUFS, 48k)

filter_complex = (
    # [0:v] Fondo base 1920x1080 degradado
    "color=c=#070c18:s=1920x1080:r=30:d=16.2[bg];"
    # Sombra de piso suave bajo el avatar
    "color=c=black@0.55:s=340x70:r=30:d=16.2,format=rgba,boxblur=12:enable='between(t,0,16.2)'[shadow];"
    "[bg][shadow]overlay=1260:985[bg_shadow];"
    # Escalar poses avatar a altura 920px
    "[1:v]scale=-1:920,format=rgba[p1];"
    "[2:v]scale=-1:920,format=rgba[p2];"
    "[3:v]scale=-1:920,format=rgba[p3];"
    "[4:v]scale=-1:920,format=rgba[p4];"
    # M-IDLE-01 en Y: 150 + 5*sin(2*PI*t/3.2)
    # Overlay secuencial sin cajas rectangulares
    "[bg_shadow][p1]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,0,4.5)'[v1];"
    "[v1][p2]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,4.5,9.0)'[v2];"
    "[v2][p3]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,9.0,13.0)'[v3];"
    "[v3][p4]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,13.0,16.2)'[vfinal];"
    # Cadena de audio estricta VOZ_GUIAHOY (sin afftdn)
    "[0:a]highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.0:LRA=11,aformat=sample_rates=48000:channel_layouts=mono[afinal]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", AUDIO_SRC,
    "-loop", "1", "-i", POSES["P1"],
    "-loop", "1", "-i", POSES["P2"],
    "-loop", "1", "-i", POSES["P3"],
    "-loop", "1", "-i", POSES["P4"],
    "-filter_complex", filter_complex,
    "-map", "[vfinal]",
    "-map", "[afinal]",
    "-t", "16.2",
    "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    OUT_MP4_PATH
]

print("Ejecutando renderizado M-COMPOSICION-01...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Error ffmpeg:")
    print(res.stderr[-1000:])
    sys.exit(1)

# 4. Copiar a Media Vault Final y calcular SHA256
import shutil
shutil.copy2(OUT_MP4_PATH, VAULT_MP4_PATH)

h = hashlib.sha256()
with open(OUT_MP4_PATH, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        h.update(chunk)
sha256_hash = h.hexdigest()
file_size = os.path.getsize(OUT_MP4_PATH)

print("\n=== RENDER COMPLETADO CON EXITO ===")
print("Ruta Produccion:", OUT_MP4_PATH)
print("Ruta Vault Final:", VAULT_MP4_PATH)
print("Tamano:", file_size, "bytes")
print("SHA256:", sha256_hash)

# Copiar al directorio de artefactos para previsualización directa
art_dir = r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83"
art_mp4 = os.path.join(art_dir, "guiahoy_test_m_composicion_01.mp4")
shutil.copy2(OUT_MP4_PATH, art_mp4)
print("Copiado a artefacto:", art_mp4)
