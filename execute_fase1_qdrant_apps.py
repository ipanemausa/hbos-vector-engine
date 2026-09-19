import os
import sys
import math
import hashlib
import json
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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

col_name = "diamantino_apps"
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
    print(f"[*] La colección '{col_name}' ya existe.")

# Punto 1: Esquema Base del Navegador de Apps
schema_payload = {
    "app": "hbos-app-navigator",
    "version": "1.0",
    "ruta": "/schema",
    "accion": "Esquema canónico de mapeo y navegación autónoma de aplicaciones para el ecosistema HBOS",
    "opciones": {
        "engine": "playwright",
        "headless": True,
        "timeout_ms": 15000
    },
    "prerequisitos": ["playwright", "qdrant_client"],
    "selector": "body",
    "operation_id": 114
}

vec_schema = generate_embedding("diamantino_apps schema hbos-app-navigator ruta accion opciones prerequisitos selector", dim=384)

client.upsert(
    collection_name=col_name,
    points=[
        models.PointStruct(
            id=1,
            vector=vec_schema,
            payload=schema_payload
        )
    ]
)
print(f"[OK] Punto schema ID=1 insertado en '{col_name}'.")

# Registrar en registro_ecosistema (operation_id = 114)
payload_op114 = {
    "operation_id": 114,
    "tarea": "FASE 1 — CREAR COLECCIÓN QDRANT (diamantino_apps)",
    "coleccion_creada": col_name,
    "dimension": 384,
    "metrica": "Cosine",
    "esquema_payload": {
        "app": "nombre",
        "version": "1.0",
        "ruta": "/path",
        "accion": "descripción",
        "opciones": {},
        "prerequisitos": [],
        "selector": "#element"
    },
    "estado": "COMPLETADO"
}

vec_op114 = generate_embedding("Tarea operacion 114 Crear Coleccion Qdrant diamantino_apps Agente Navegador de Apps Mapeo y Ejecucion Playwright", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=114,
            vector=vec_op114,
            payload=payload_op114
        )
    ]
)
print("[OK] operation_id = 114 registrado exitosamente en registro_ecosistema.")

# Verificación de puntos
col_info = client.get_collection(col_name)
print(f"[OK] Colección '{col_name}': {col_info.points_count} puntos activos.")
