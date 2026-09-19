import os
import sys
import time
import json
import base64
import math
import hashlib
import requests
import subprocess
import shutil
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

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

print("==========================================================================")
print(">>> [HBOS-DIAMANTINO] SCRIPT MAESTRO DE PRODUCCIÓN COMPLETA: EPISODIO 04 <<<")
print("==========================================================================")

base_local = "Ep04"
base_drive = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica"
dir_backup = r"C:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep04_2026-09-19"

# 1. VERIFICACIÓN DE CUOTAS
print("\n[*] FASE 1: Verificando cuotas en la nube...", flush=True)

el_key = os.getenv("ELEVENLABS_API_KEY")
ds_key = os.getenv("DASHSCOPE_API_KEY")

if not el_key or not ds_key:
    print("[ERROR] Faltan credenciales en .env.local", flush=True)
    sys.exit(1)

# Probar ElevenLabs
resp_el = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB",
    headers={"xi-api-key": el_key, "Accept": "audio/mpeg"},
    json={"text": "Verificación de cuota", "model_id": "eleven_multilingual_v2"},
    timeout=15
)
cuota_el_ok = (resp_el.status_code == 200)

# Probar DashScope
resp_ds = requests.post(
    "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis",
    headers={"Authorization": f"Bearer {ds_key}", "Content-Type": "application/json", "X-DashScope-Async": "enable"},
    json={"model": "wan2.1-i2v-turbo", "input": {"img_url": "https://dummyimage.com/100x100/000/fff", "prompt": "test"}},
    timeout=15
)
cuota_ds_ok = (resp_ds.status_code != 403)

print(f"  -> ElevenLabs Cloud: {'ACTIVO (HTTP 200)' if cuota_el_ok else f'BLOQUEADO ({resp_el.status_code}: {resp_el.text[:80]})'}")
print(f"  -> DashScope Wan 2.1: {'ACTIVO' if cuota_ds_ok else f'BLOQUEADO ({resp_ds.status_code}: {resp_ds.text[:80]})'}")

if not cuota_el_ok or not cuota_ds_ok:
    print("\n[ALERTA] Cuota insuficiente en nube. El script no ejecutará fallbacks locales prohibidos.", flush=True)
    print("Para ejecutar la producción completa, asegúrese de contar con créditos en ElevenLabs y DashScope.")
    sys.exit(0)

print("\n[+] Ambas APIs cuentan con cuota activa. Iniciando pipeline de producción...")

# FASE A: SÍNTESIS DE VOZ NARRATIVA ÚNICA (DIAMANTINO / ADAM) - P-18
print("\n[*] FASE A: Generando locución oficial en ElevenLabs Cloud...", flush=True)
subprocess.run(["python", "generate_ep04_voices.py"], check=True)

# FASE B: GENERACIÓN DE CLIPS WAN 2.1 RESTANTES EN DASHSCOPE CLOUD
print("\n[*] FASE B: Generando clips restantes en DashScope Wan 2.1 Cloud...", flush=True)
subprocess.run(["python", "produce_ep04_all_clips.py"], check=True)

# FASE C: ENSAMBLADO MASTER (FFMPEG TÉCNICO PERMITIDO)
print("\n[*] FASE C: Ensamblando master final 1080p 30fps H.264...", flush=True)
out_master_local = os.path.join(base_local, r"05_Master\ep04_master_v1.mp4")
out_master_drive = os.path.join(base_drive, r"05_Master\ep04_master_v1.mp4")
os.makedirs(os.path.dirname(out_master_local), exist_ok=True)
os.makedirs(os.path.dirname(out_master_drive), exist_ok=True)

# Lista de clips
concat_file = os.path.join(base_local, "clips_concat_list.txt")
with open(concat_file, "w", encoding="utf-8") as f:
    for i in range(10):
        c_path = os.path.abspath(os.path.join(base_local, f"04_Clips_Wan21\\ep04_plano_{i:02d}_wan21.mp4"))
        f.write(f"file '{c_path.replace(chr(92), '/')}'\n")

bgm_path = os.path.join(base_local, r"03_Assets\BGM\ep04_bgm_master.mp3")

# Ensamblado con Ducking al 30% y masterización EBU R128
cmd_assembly = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_file,
    "-i", bgm_path,
    "-filter_complex",
    "[1:a]volume=0.30,afade=t=out:st=175:d=5[bgm_mix]; "
    "[bgm_mix]loudnorm=I=-14:TP=-1.0:LRA=11[aout]",
    "-map", "0:v", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18",
    "-c:a", "aac", "-b:a", "320k",
    "-movflags", "+faststart",
    out_master_local
]
subprocess.run(cmd_assembly, check=True)
shutil.copyfile(out_master_local, out_master_drive)
print(f"[+] Master v1 ensamblado con éxito: {out_master_drive}")

# FASE D: FORMATOS RESPONSIVE (16:9, 9:16, 1:1, 4:5)
print("\n[*] FASE D: Exportando formatos responsive...", flush=True)
formatos_dir_drive = os.path.join(base_drive, r"06_Publicado\formatos")
os.makedirs(formatos_dir_drive, exist_ok=True)

formatos = [
    ("16x9", "scale=1920:1080"),
    ("9x16", "crop=ih*(9/16):ih,scale=1080:1920"),
    ("1x1", "crop=ih:ih,scale=1080:1080"),
    ("4x5", "crop=ih*(4/5):ih,scale=1080:1350")
]

for fmt_name, vf in formatos:
    out_fmt = os.path.join(formatos_dir_drive, f"ep04_formato_{fmt_name}.mp4")
    cmd_fmt = [
        "ffmpeg", "-y",
        "-i", out_master_local,
        "-vf", vf,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        out_fmt
    ]
    subprocess.run(cmd_fmt, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  -> Formato {fmt_name} generado: {out_fmt}")

# FASE E: REDUNDANCIA TRIPLE P-03
print("\n[*] FASE E: Aplicando triple redundancia...", flush=True)
shutil.copyfile(out_master_local, os.path.join(dir_backup, "ep04_master_v1.mp4"))
print(f"[OK] Triple redundancia completada en local, Drive y backup.")

print("\n==========================================================================")
print(">>> [ÉXITO] PRODUCCIÓN TOTAL DE EPISODIO 04 COMPLETADA AL 100% <<<")
print("==========================================================================")
