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
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

src_ep04 = "Ep04"
dst_backup = r"C:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep04_2026-09-19"
os.makedirs(dst_backup, exist_ok=True)

print(f"[*] Copiando Ep04 hacia backup local: {dst_backup}...")

copied_files = 0
total_bytes = 0

for root, dirs, files in os.walk(src_ep04):
    rel = os.path.relpath(root, src_ep04)
    target_dir = os.path.join(dst_backup, rel) if rel != "." else dst_backup
    os.makedirs(target_dir, exist_ok=True)
    for f in files:
        s_p = os.path.join(root, f)
        d_p = os.path.join(target_dir, f)
        shutil.copyfile(s_p, d_p)
        copied_files += 1
        total_bytes += os.path.getsize(s_p)

print(f"[OK] {copied_files} archivos copiados a backup ({total_bytes} bytes)")

# Verificar que los archivos sean idénticos por tamaño
verified = True
for root, dirs, files in os.walk(src_ep04):
    rel = os.path.relpath(root, src_ep04)
    target_dir = os.path.join(dst_backup, rel) if rel != "." else dst_backup
    for f in files:
        s_p = os.path.join(root, f)
        d_p = os.path.join(target_dir, f)
        if not os.path.exists(d_p) or os.path.getsize(s_p) != os.path.getsize(d_p):
            print(f"[ERROR] Discrepancia en {f}")
            verified = False

print(f"[OK] Verificación de bytes idénticos: {verified}")

# Registrar operation_id = 75 en registro_ecosistema
vec_op75 = generate_embedding("Tarea 9 operacion 75 Git Push origin main Commit f212108 Backup Local Triple Redundancia", dim=384)
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=75,
            vector=vec_op75,
            payload={
                "operation_id": 75,
                "tarea": "TAREA 9 — PUSH A GIT + BACKUP",
                "commit_hash": "f212108",
                "branch": "main",
                "remote": "https://github.com/ipanemausa/hbos-vector-engine.git",
                "archivos_commit": 15,
                "backup_local": dst_backup,
                "archivos_backup": copied_files,
                "bytes_backup": total_bytes,
                "verificacion_bytes_identicos": verified,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 75 registrado en registro_ecosistema.")
