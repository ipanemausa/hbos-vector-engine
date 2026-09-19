import os
import sys
import json
import time
import math
import hashlib
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

print("==========================================================================")
print(">>> [FASE 2] CREAR COLECCIÓN hbos_metricas (operation_id=178) <<<")
print("==========================================================================")

collection_name = "hbos_metricas"

# 1. Crear colección si no existe
for attempt in range(1, 4):
    try:
        collections = [c.name for c in client.get_collections().collections]
        if collection_name not in collections:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            print(f"[OK] Colección '{collection_name}' creada en Qdrant con dim 384 (Cosine).")
        else:
            print(f"[*] Colección '{collection_name}' ya existía en Qdrant.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 creando colección: {e}")
        time.sleep(2)

# 2. Insertar métrica canónica inicial de referencia (ID 1)
metrica_base = {
    "operation_id": 178,
    "tarea": "generar_voces_ep04",
    "modelo_usado": "cosyvoice2",
    "tokens_input": 800,
    "tokens_output": 700,
    "tokens_sin_compresion": 12000,
    "tokens_ahorrados": 10500,
    "porcentaje_ahorro": 87.5,
    "costo_efectivo": "$0.00",
    "latencia_seg": 28,
    "arbitraje": "free",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
}

vec = generate_embedding(f"Metrica {metrica_base['tarea']} {metrica_base['modelo_usado']} ahorro {metrica_base['porcentaje_ahorro']}% costo {metrica_base['costo_efectivo']}")

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name=collection_name,
            points=[models.PointStruct(id=1, vector=vec, payload=metrica_base)]
        )
        print(f"[OK] Punto ID 1 de métrica insertado en '{collection_name}'.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 insertando métrica: {e}")
        time.sleep(2)

# 3. Registrar en registro_ecosistema (op 178)
payload_op178 = {
    "operation_id": 178,
    "fase": "FASE 2 — CREAR COLECCIÓN hbos_metricas",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "coleccion": collection_name,
    "metrica_canonica": metrica_base,
    "estado": "COMPLETADO"
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=178,
                vector=generate_embedding("Coleccion hbos_metricas tokens input output ahorro arbitraje op 178"),
                payload=payload_op178
            )]
        )
        print("[OK] operation_id = 178 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 registrando op 178: {e}")
        time.sleep(2)

# 4. Actualizar hbos_estado
for attempt in range(1, 4):
    try:
        p = client.retrieve("hbos_estado", ids=[1])[0].payload
        p["operation_ids"] = "45 a 178"
        p["hecho_hoy"].append("Colección hbos_metricas creada con esquema de ahorro R768 (op 178)")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado op 178"), payload=p)]
        )
        print("[OK] hbos_estado actualizado a op 178.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 actualizando hbos_estado: {e}")
        time.sleep(2)
