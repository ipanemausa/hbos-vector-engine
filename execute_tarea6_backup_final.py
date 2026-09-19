import os
import sys
import shutil
import math
import hashlib
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
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

src_ep04 = "Ep04"
dst_backup = r"C:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep04_2026-09-19"
os.makedirs(dst_backup, exist_ok=True)

copied = 0
total_bytes = 0

for root, dirs, files in os.walk(src_ep04):
    rel = os.path.relpath(root, src_ep04)
    target_dir = os.path.join(dst_backup, rel) if rel != "." else dst_backup
    os.makedirs(target_dir, exist_ok=True)
    for f in files:
        s_p = os.path.join(root, f)
        d_p = os.path.join(target_dir, f)
        shutil.copyfile(s_p, d_p)
        copied += 1
        total_bytes += os.path.getsize(s_p)

# Copiar también scripts clave de producción y maestros
extra_files = [
    "produce_ep04_final.py",
    os.path.join("_MAESTRO", "_ESTADO_PRODUCCION_EP04.md"),
    os.path.join("_MAESTRO", "_PLAN_RENOVACION_OCTUBRE.md")
]
for ef in extra_files:
    if os.path.exists(ef):
        shutil.copyfile(ef, os.path.join(dst_backup, os.path.basename(ef)))
        copied += 1
        total_bytes += os.path.getsize(ef)

# Verificar integridad
verified = True
for root, dirs, files in os.walk(src_ep04):
    rel = os.path.relpath(root, src_ep04)
    target_dir = os.path.join(dst_backup, rel) if rel != "." else dst_backup
    for f in files:
        s_p = os.path.join(root, f)
        d_p = os.path.join(target_dir, f)
        if not os.path.exists(d_p) or os.path.getsize(s_p) != os.path.getsize(d_p):
            verified = False

print(f"[OK] Backup local completado: {copied} archivos ({total_bytes} bytes). Integridad: {verified}")

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)
vec_op81 = generate_embedding("Tarea 6 operacion 81 Push Git Commit fb8fa6c Backup Local Triple Redundancia Ep04", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=81,
            vector=vec_op81,
            payload={
                "operation_id": 81,
                "tarea": "TAREA 6 — PUSH A GIT + BACKUP",
                "commit_hash": "fb8fa6c",
                "branch": "main",
                "archivos_commit": 7,
                "backup_local": dst_backup,
                "archivos_backup": copied,
                "bytes_backup": total_bytes,
                "verificacion_bytes_identicos": verified,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 81 registrado en registro_ecosistema.")
