import os
import sys
import shutil
import hashlib
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

local_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_HBOS_MEMORY.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_HBOS_MEMORY.md"
backup_file = r"C:\Users\ipane\backup_hbos\_MAESTRO\_HBOS_MEMORY.md"

os.makedirs(os.path.dirname(drive_file), exist_ok=True)
os.makedirs(os.path.dirname(backup_file), exist_ok=True)

shutil.copy2(local_file, drive_file)
shutil.copy2(local_file, backup_file)

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest(), os.path.getsize(path)

h_local, s_local = get_hash(local_file)
h_drive, s_drive = get_hash(drive_file)
h_backup, s_backup = get_hash(backup_file)

print(f"Local:  {s_local} bytes | SHA256: {h_local}")
print(f"Drive:  {s_drive} bytes | SHA256: {h_drive}")
print(f"Backup: {s_backup} bytes | SHA256: {h_backup}")

assert h_local == h_drive == h_backup, "Error: Discrepancia de bytes en triple redundancia"
print("[OK] Verificación de bytes idénticos 100% exitosa.")

def generate_embedding(text, dim=384):
    import math
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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op162 = {
    "operation_id": 162,
    "tarea": "TAREA 1 — DOCUMENTAR HBOS MEMORY (MEMORIA PERSISTENTE)",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "archivo": "_HBOS_MEMORY.md",
    "rutas": {"local": local_file, "drive": drive_file, "backup": backup_file},
    "tamano_bytes": s_local,
    "sha256": h_local,
    "resumen": "Documentación de arquitectura, integración, ejemplos e impacto de HBOS MEMORY",
    "redundancia_triple_verificada": True,
    "estado": "COMPLETADO"
}

vec_162 = generate_embedding("Tarea 1 operacion 162 Documentar HBOS MEMORY Memoria Persistente Unificada Qdrant hbos_estado Antigravity", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=162,
            vector=vec_162,
            payload=payload_op162
        )
    ]
)
print("[OK] operation_id = 162 registrado exitosamente en registro_ecosistema.")
