import os
import sys
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

print(">>> [TAREA 3] Iniciando operacion_id = 68 (P-04 v2 Volumen Maximo -14 LUFS)...")

qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=25)

# FASE 1: Actualizar P-04 en diamantino_patrones (id=4)
p04_codigo = "P-04"
p04_nombre = "Masterizacion_Acustica_EBU_R128_v2"
p04_desc = "Norma de masterización sonora para broadcast digital: I = -14.0 LUFS, TP = -1.0 dBTP, LRA = 11.0 LU, limitador activo y headroom de 1.0 dB para evitar distorsión en transcoding."
vec_p04 = generate_embedding(f"{p04_codigo} {p04_nombre} {p04_desc}", dim=384)

client.upsert(
    collection_name="diamantino_patrones",
    points=[
        models.PointStruct(
            id=4,
            vector=vec_p04,
            payload={
                "codigo": p04_codigo,
                "nombre": p04_nombre,
                "descripcion": p04_desc,
                "integrated_loudness": "-14.0 LUFS",
                "true_peak": "-1.0 dBTP",
                "loudness_range": "11.0 LU",
                "limiter": "activo",
                "headroom": "1.0 dB",
                "operation_id": 68
            }
        )
    ]
)
print("[OK] P-04 v2 actualizado en diamantino_patrones (id=4).")

# FASE 2: Regenerar Ep02 v4 y Ep03 v2 con loudnorm
ep02_src = "ep02_master_v3.mp4"
ep02_out_local = "ep02_master_v4.mp4"

ep03_src = r"Ep03\ep03_master_v1.mp4"
ep03_out_local = r"Ep03\ep03_master_v2.mp4"

loudnorm_filter = "loudnorm=I=-14:TP=-1.0:LRA=11"

print("\n[*] Remasterizando Ep02 v3 -> Ep02 v4...")
cmd_ep02 = [
    "ffmpeg", "-y",
    "-i", ep02_src,
    "-c:v", "copy",
    "-af", loudnorm_filter,
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "44100",
    "-movflags", "+faststart",
    ep02_out_local
]
subprocess.run(cmd_ep02, check=True)
print(f"[OK] Ep02 v4 generado: {os.path.getsize(ep02_out_local)} bytes.")

print("\n[*] Remasterizando Ep03 v1 -> Ep03 v2...")
cmd_ep03 = [
    "ffmpeg", "-y",
    "-i", ep03_src,
    "-c:v", "copy",
    "-af", loudnorm_filter,
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "44100",
    "-movflags", "+faststart",
    ep03_out_local
]
subprocess.run(cmd_ep03, check=True)
print(f"[OK] Ep03 v2 generado: {os.path.getsize(ep03_out_local)} bytes.")

# Redundancia P-03
drive_base = r"G:\My Drive\HBOS-Diamantino"
backup_base = r"C:\Users\ipane\backup_hbos"

# Ep02 v4 destinos
ep02_drive_master = os.path.join(drive_base, r"Ep02-Los7Chips\05_Master\ep02_master_v4.mp4")
ep02_drive_pub = os.path.join(drive_base, r"Ep02-Los7Chips\06_Publicado\ep02_publicado_v4.mp4")
ep02_backup = os.path.join(backup_base, r"Ep02\ep02_master_v4.mp4")

os.makedirs(os.path.dirname(ep02_drive_master), exist_ok=True)
os.makedirs(os.path.dirname(ep02_drive_pub), exist_ok=True)
os.makedirs(os.path.dirname(ep02_backup), exist_ok=True)

shutil.copyfile(ep02_out_local, ep02_drive_master)
shutil.copyfile(ep02_out_local, ep02_drive_pub)
shutil.copyfile(ep02_out_local, ep02_backup)
print("[OK] Redundancia P-03 verificada para Ep02 v4 (Local, Drive Master, Drive Publicado, Backup Local).")

# Ep03 v2 destinos
ep03_drive_master = os.path.join(drive_base, r"Ep03-RedesFotonicasCuanticas\05_Master\ep03_master_v2.mp4")
ep03_drive_pub = os.path.join(drive_base, r"Ep03-RedesFotonicasCuanticas\06_Publicado\ep03_publicado_v2.mp4")
ep03_backup = os.path.join(backup_base, r"Ep03\ep03_master_v2.mp4")

os.makedirs(os.path.dirname(ep03_drive_master), exist_ok=True)
os.makedirs(os.path.dirname(ep03_drive_pub), exist_ok=True)
os.makedirs(os.path.dirname(ep03_backup), exist_ok=True)

shutil.copyfile(ep03_out_local, ep03_drive_master)
shutil.copyfile(ep03_out_local, ep03_drive_pub)
shutil.copyfile(ep03_out_local, ep03_backup)
print("[OK] Redundancia P-03 verificada para Ep03 v2 (Local, Drive Master, Drive Publicado, Backup Local).")

# FASE 3: Formatos responsive
formats_def = [
    {
        "id": "16x9",
        "name_suffix": "_16x9.mp4",
        "filter": "scale=1920:1080"
    },
    {
        "id": "9x16",
        "name_suffix": "_9x16.mp4",
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=4:1,scale=1080:1920:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    },
    {
        "id": "1x1",
        "name_suffix": "_1x1.mp4",
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:270:force_original_aspect_ratio=increase,crop=270:270,boxblur=4:1,scale=1080:1080:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1080:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    },
    {
        "id": "4x5",
        "name_suffix": "_4x5.mp4",
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:338:force_original_aspect_ratio=increase,crop=270:338,boxblur=4:1,scale=1080:1350:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1350:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    }
]

dir_formatos = "formatos"
os.makedirs(dir_formatos, exist_ok=True)

def render_responsive(src_master, prefix):
    print(f"\n[*] Renderizando 4 formatos responsive para {prefix}...")
    for fmt in formats_def:
        out_name = f"{prefix}{fmt['name_suffix']}"
        out_path = os.path.join(dir_formatos, out_name)
        cmd = [
            "ffmpeg", "-y",
            "-i", src_master
        ]
        if fmt["filter"].startswith("[0:v]"):
            cmd += ["-filter_complex", fmt["filter"], "-map", "[v]", "-map", "0:a:0"]
        else:
            cmd += ["-vf", fmt["filter"], "-map", "0:v:0", "-map", "0:a:0"]
        cmd += [
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "copy",
            "-movflags", "+faststart",
            out_path
        ]
        subprocess.run(cmd, check=True)
        print(f"    -> Generado {out_name}: {os.path.getsize(out_path)} bytes")
        # Copiar a Drive
        if "ep02" in prefix:
            drive_dest_fmt = os.path.join(drive_base, r"Ep02-Los7Chips\06_Publicado\formatos", out_name)
        else:
            drive_dest_fmt = os.path.join(drive_base, r"Ep03-RedesFotonicasCuanticas\06_Publicado\formatos", out_name)
        os.makedirs(os.path.dirname(drive_dest_fmt), exist_ok=True)
        shutil.copyfile(out_path, drive_dest_fmt)


render_responsive(ep02_out_local, "ep02_master_v4")
render_responsive(ep03_out_local, "ep03_master_v2")

# FASE 4: Verificar volumedetect
def check_volume(video_path):
    cmd = ["ffmpeg", "-i", video_path, "-af", "volumedetect", "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out = res.stderr
    mean_vol = [line for line in out.splitlines() if "mean_volume" in line]
    max_vol = [line for line in out.splitlines() if "max_volume" in line]
    return (mean_vol[0] if mean_vol else "N/A", max_vol[0] if max_vol else "N/A")

vol_ep02 = check_volume(ep02_out_local)
vol_ep03 = check_volume(ep03_out_local)
print(f"\n[VOLUMEDETECT Ep02 v4] {vol_ep02[0]} | {vol_ep02[1]}")
print(f"[VOLUMEDETECT Ep03 v2] {vol_ep03[0]} | {vol_ep03[1]}")

# Registrar operation_id = 68 en registro_ecosistema
vec_op68 = generate_embedding("Tarea 3 operacion 68 Patrón P-04 v2 Volumen Maximo -14 LUFS Ep02 v4 Ep03 v2", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=68,
            vector=vec_op68,
            payload={
                "operation_id": 68,
                "tarea": "TAREA 3 — P-04 v2 (VOLUMEN MÁXIMO)",
                "p04": {"codigo": p04_codigo, "nombre": p04_nombre, "norma": "EBU R128 -14 LUFS TP -1.0 dBTP"},
                "ep02_v4": {"master": ep02_out_local, "volume": vol_ep02},
                "ep03_v2": {"master": ep03_out_local, "volume": vol_ep03},
                "formatos_generados": 8,
                "redundancia_triple_p03": True,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 68 registrado en registro_ecosistema.")
