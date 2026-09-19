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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

col_name = "diamantino_agentes"
collections_res = client.get_collections()
existing_names = [c.name for c in collections_res.collections]

print(f"[*] Colecciones existentes en Qdrant: {existing_names}")

if col_name not in existing_names:
    print(f"[*] Creando colección '{col_name}' con dimensión 384 y métrica Cosine...")
    client.create_collection(
        collection_name=col_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    print(f"[OK] Colección '{col_name}' creada exitosamente.")
else:
    print(f"[OK] La colección '{col_name}' ya existe en Qdrant Cloud.")

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

# Actualizar el punto 1 canónico (ALEJAVI) con el payload canónico estándar
schema_payload_alejavis = {
    "agente": "ALEJAVI",
    "tipo": "interno",
    "categoria": "Orquestador Supremo",
    "funcion": "Orquestación integral del Ecosistema HBOS-Diamantino, gobierno de directivas DAG/RAG/R768 y producción soberana",
    "estado": "activo",
    "fecha_creacion": "2026-09-19",
    "operation_id": "147",
    "dependencias": ["qdrant", "antigravity", "drive", "local_ffmpeg"],
    "rutas": {
        "workspace": r"c:\Users\ipane\hbos-deploy\hbos-vector-engine",
        "maestro": r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
    },
    "documentacion": "_MAESTRO/_MANIFIESTO_HBOS_DIAMANTINO.md"
}

vec_1 = generate_embedding("ALEJAVI Orquestador Supremo interno HBOS Diamantino Vector Engine DAG RAG R768", dim=384)

client.upsert(
    collection_name=col_name,
    points=[
        models.PointStruct(
            id=1,
            vector=vec_1,
            payload=schema_payload_alejavis
        )
    ]
)
print(f"[OK] Punto ID=1 estandarizado en '{col_name}'.")

# Registrar en registro_ecosistema (operation_id = 147)
payload_op147 = {
    "operation_id": 147,
    "tarea": "FASE 1 — CREAR / VERIFICAR COLECCIÓN diamantino_agentes",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "coleccion": col_name,
    "dimension": 384,
    "metrica": "Cosine",
    "esquema_payload": {
        "agente": "nombre",
        "tipo": "interno/externo/mcp/proveedor",
        "categoria": "función",
        "funcion": "descripción",
        "estado": "activo/inactivo/pendiente",
        "fecha_creacion": "YYYY-MM-DD",
        "operation_id": "XXX",
        "dependencias": [],
        "rutas": {},
        "documentacion": "ruta"
    },
    "estado": "COMPLETADO"
}

vec_147 = generate_embedding("Fase 1 operacion 147 Crear Coleccion Qdrant diamantino_agentes Esquema Canonico Agentes MCPs Proveedores", dim=384)

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

col_info = client.get_collection(col_name)
print(f"[OK] Colección '{col_name}': {col_info.points_count} puntos activos.")
