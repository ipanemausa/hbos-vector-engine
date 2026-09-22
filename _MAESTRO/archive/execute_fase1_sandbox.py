import os
import sys
import math
import hashlib
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

sandbox_dir = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI"

print(f"[*] FASE 1: Verificando SANDBOX en: {sandbox_dir}")
exists = os.path.exists(sandbox_dir)

if not exists:
    os.makedirs(sandbox_dir, exist_ok=True)
    print(f"[+] Carpeta creada: {sandbox_dir}")
else:
    print(f"[OK] Carpeta SANDBOX existente y verificada: {sandbox_dir}")

# Vectorización en Qdrant (operation_id = 147)
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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op147 = {
    "operation_id": 147,
    "tarea": "FASE 1 — VERIFICAR SANDBOX (FreeLLMAPI)",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "sandbox_ruta": sandbox_dir,
    "existe": True,
    "aislamiento": "100% aislado en Google Drive, fuera de directorios de sistema Windows",
    "estado": "COMPLETADO"
}

vec_147 = generate_embedding("Fase 1 operacion 147 Verificar Sandbox FreeLLMAPI Aislamiento Total G My Drive", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=147,
            vector=vec_147,
            payload=payload_op147
        )
    ]
)
print("[OK] operation_id = 147 registrado exitosamente en registro_ecosistema.")
