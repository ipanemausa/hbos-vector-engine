import os
import sys
import math
import shutil
import hashlib
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

print(">>> [TAREA 9] Ejecutando Backup Local a C:\\Users\\ipane\\backup_hbos\\...")

backup_root = r"C:\Users\ipane\backup_hbos"
os.makedirs(backup_root, exist_ok=True)

# Copiar directorios clave: _MAESTRO, Ep04, guion_v3
items_to_backup = [
    ("_MAESTRO", os.path.join(backup_root, "_MAESTRO")),
    ("Ep04", os.path.join(backup_root, "Ep04")),
    ("guion_v3.md", os.path.join(backup_root, "guion_v3.md")),
    ("formatos", os.path.join(backup_root, "formatos_v4_v2"))
]

audit_backup = []

for src, dst in items_to_backup:
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        audit_backup.append({"item": src, "tipo": "dir", "destino": dst, "existe": os.path.exists(dst)})
    elif os.path.isfile(src):
        shutil.copyfile(src, dst)
        eq = os.path.getsize(src) == os.path.getsize(dst)
        audit_backup.append({"item": src, "tipo": "file", "bytes_orig": os.path.getsize(src), "bytes_dst": os.path.getsize(dst), "identicos": eq})

print("[OK] Backup local completado:")
for a in audit_backup:
    print("  ->", a)

# Registrar operation_id = 74 en Qdrant
vec_op74 = generate_embedding("Tarea 9 operacion 74 Push a Git y Backup Local Inmutable", dim=384)
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=74,
            vector=vec_op74,
            payload={
                "operation_id": 74,
                "tarea": "TAREA 9 — PUSH A GIT + BACKUP",
                "commit_hash": "bac5499",
                "branch": "main",
                "backup_dir": backup_root,
                "items_respaldados": audit_backup,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 74 registrado en registro_ecosistema.")
