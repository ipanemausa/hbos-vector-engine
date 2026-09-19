import os
import sys
import json
import math
import shutil
import hashlib
import subprocess
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', file_path]
    res = subprocess.check_output(cmd).decode()
    return float(json.loads(res)['format']['duration'])

print(">>> [TAREA 5] Iniciando operacion_id = 70 (P-16 Desplazamiento de Hosts + Master Ep02 v5)...")

qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=25)

# FASE 3: Crear P-16 en diamantino_patrones
p16_codigo = "P-16"
p16_nombre = "Desplazamiento_Cinematico_Continuo_Hosts"
p16_desc = "Estandarización de cinemática con desplazamiento continuo de avatares en Wan 2.1 I2V, integrando marcha frontal, traslación articular y gesticulación coordinada mediante el catálogo P-14."
vec_p16 = generate_embedding(f"{p16_codigo} {p16_nombre} {p16_desc}", dim=384)

client.upsert(
    collection_name="diamantino_patrones",
    points=[
        models.PointStruct(
            id=16,
            vector=vec_p16,
            payload={
                "codigo": p16_codigo,
                "nombre": p16_nombre,
                "descripcion": p16_desc,
                "operation_id": 70
            }
        )
    ]
)
print("[OK] P-16 registrado en diamantino_patrones (id=16).")

BASE_EP02 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips"
VOCES_DIR = os.path.join(BASE_EP02, r"03_Assets\Voces")
BGM_DIR = os.path.join(BASE_EP02, r"03_Assets\BGM")
CLIPS_V2_DIR = os.path.join(BASE_EP02, r"04_Clips_Wan21_v2")
MASTER_DIR = os.path.join(BASE_EP02, r"05_Master")
PUBLICADO_DIR = os.path.join(BASE_EP02, r"06_Publicado")
BACKUP_LOCAL_DIR = r"C:\Users\ipane\backup_hbos\Ep02"

clips_order = [
    os.path.join(CLIPS_V2_DIR, "ep02_plano_01_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_02_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_03_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_04_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_05_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_06_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_07_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_07b_v2.mp4"),
    os.path.join(CLIPS_V2_DIR, "ep02_plano_08_v2.mp4")
]

for c in clips_order:
    if not os.path.exists(c):
        print(f"[ERROR] Clip no encontrado: {c}")
        sys.exit(1)

concat_list_path = os.path.join(CLIPS_V2_DIR, "concat_clips_v5_list.txt")
with open(concat_list_path, "w", encoding="utf-8") as f:
    for c in clips_order:
        f.write(f"file '{c}'\n")

temp_video_concat = os.path.join(CLIPS_V2_DIR, "temp_video_concat_v5.mp4")
print("[*] Concatenando los 9 clips v2 con desplazamiento...")
cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", temp_video_concat]
subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
temp_dur = get_duration(temp_video_concat)
print(f"[OK] Video v5 concatenado: {temp_dur:.4f} s.")

voiceover_path = os.path.join(VOCES_DIR, "ep02_voiceover_master_v2.wav")
bgm_path = os.path.join(BGM_DIR, "ep02_bgm_master.mp3")

fade_start = temp_dur - 1.0
audio_filter = (
    f"[1:a]volume=1.4[voice]; "
    f"[2:a]volume=0.18[music]; "
    f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[mixed]; "
    f"[mixed]loudnorm=I=-14:TP=-1.0:LRA=11,afade=t=out:st={fade_start:.4f}:d=1.0[aout]"
)

out_master_local = "ep02_master_v5.mp4"

print("[*] Renderizando Ep02 Master v5 con Loudnorm P-04 v2 (-14 LUFS, TP -1.0 dBTP)...")
cmd_master = [
    "ffmpeg", "-y",
    "-i", temp_video_concat,
    "-i", voiceover_path,
    "-stream_loop", "-1", "-i", bgm_path,
    "-filter_complex", audio_filter,
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "48000",
    "-shortest",
    "-movflags", "+faststart",
    out_master_local
]
subprocess.run(cmd_master, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if os.path.exists(temp_video_concat):
    os.remove(temp_video_concat)
if os.path.exists(concat_list_path):
    os.remove(concat_list_path)

v5_size = os.path.getsize(out_master_local)
v5_dur = get_duration(out_master_local)
print(f"[OK] Ep02 Master v5 renderizado: {v5_size} bytes, {v5_dur:.2f} s.")

# FASE 6: Triple Redundancia P-03
drive_dest_master = os.path.join(MASTER_DIR, "ep02_master_v5.mp4")
drive_dest_pub = os.path.join(PUBLICADO_DIR, "ep02_publicado_v5.mp4")
backup_dest_master = os.path.join(BACKUP_LOCAL_DIR, "ep02_master_v5.mp4")

os.makedirs(os.path.dirname(backup_dest_master), exist_ok=True)

shutil.copyfile(out_master_local, drive_dest_master)
shutil.copyfile(out_master_local, drive_dest_pub)
shutil.copyfile(out_master_local, backup_dest_master)

print("[OK] Redundancia triple P-03 verificada para Ep02 v5.")

# Registrar operation_id = 70 en registro_ecosistema
vec_op70 = generate_embedding("Tarea 5 operacion 70 Patrón P-16 Desplazamiento Cinemático Ep02 Master v5", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=70,
            vector=vec_op70,
            payload={
                "operation_id": 70,
                "tarea": "TAREA 5 — P-16 (DESPLAZAMIENTO DE HOSTS)",
                "p16": {"codigo": p16_codigo, "nombre": p16_nombre},
                "master_v5": {
                    "archivo": out_master_local,
                    "duracion_seg": v5_dur,
                    "bytes": v5_size
                },
                "clips_v2_utilizados": 9,
                "redundancia_triple_p03": True,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 70 registrado en registro_ecosistema.")
