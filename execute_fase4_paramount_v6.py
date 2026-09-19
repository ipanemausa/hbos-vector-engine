import os
import sys
import shutil
import hashlib
import time
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    import math
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

src_file = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_PROMPT_PARAMOUNT_v6.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_PROMPT_PARAMOUNT_v6.md"
backup_file = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\backup_hbos\_PROMPT_PARAMOUNT_v6.md"

# 1. Triple redundancia
os.makedirs(os.path.dirname(drive_file), exist_ok=True)
os.makedirs(os.path.dirname(backup_file), exist_ok=True)

shutil.copy2(src_file, drive_file)
shutil.copy2(src_file, backup_file)

with open(src_file, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
size = os.path.getsize(src_file)

print(f"[OK] _PROMPT_PARAMOUNT_v6.md sincronizado con triple redundancia. Tamaño: {size} bytes | SHA256: {sha[:16]}...")

# 2. Vectorizar en registro_ecosistema (op 175)
payload_op175 = {
    "operation_id": 175,
    "fase": "FASE 4 — ACTUALIZAR PROMPT PARAMOUNT v6",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "archivo": "_MAESTRO/_PROMPT_PARAMOUNT_v6.md",
    "sha256": sha,
    "bytes": size,
    "elementos_clave": [
        "Protocolo de búsqueda en cascada de 5 pasos",
        "Conector MCP hbos-freellmapi en puerto 3001",
        "Directorio Qdrant hbos_directorio (7 componentes)",
        "Memoria HBOS MEMORY P-53, P-54, L-39, L-40"
    ],
    "estado": "COMPLETADO"
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=175,
                vector=generate_embedding("Prompt Paramount v6 Directiva Total busqueda cascada MCP hbos freellmapi directorio Qdrant op 175"),
                payload=payload_op175
            )]
        )
        print("[OK] operation_id = 175 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento op 175: {e}")
        time.sleep(2)

# 3. Actualizar hbos_estado
for attempt in range(1, 4):
    try:
        p = client.retrieve("hbos_estado", ids=[1])[0].payload
        p["operation_ids"] = "45 a 175"
        p["hecho_hoy"].append("Prompt Paramount v6.0 consolidado y sincronizado (op 175)")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado op 175"), payload=p)]
        )
        print("[OK] hbos_estado actualizado a op 175.")
        break
    except Exception as e:
        print(f"[!] Reintento hbos_estado: {e}")
        time.sleep(2)
