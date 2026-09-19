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
print(">>> [FASE 1] CREAR DIRECTORIO HBOS EN QDRANT (operation_id=172) <<<")
print("==========================================================================")

collection_name = "hbos_directorio"

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

# 2. Definir los 7 componentes del directorio HBOS
componentes = [
    {
        "id": 1,
        "componente": "FreeLLMAPI",
        "tipo": "app",
        "ubicacion_local": "G:\\My Drive\\HBOS-Diamantino\\_SANDBOX\\FreeLLMAPI\\app\\FreeLLMAPI.exe",
        "ubicacion_nube": "http://localhost:3001",
        "como_acceder": "MCP hbos-freellmapi / REST http://localhost:3001",
        "estado": "activo",
        "descripcion": "Servidor local portable de inferencia multimodelo, compresión de contexto y proxy de APIs.",
        "operation_id": 172
    },
    {
        "id": 2,
        "componente": "Google_Drive_HBOS",
        "tipo": "almacenamiento_cloud_stream",
        "ubicacion_local": "G:\\My Drive\\HBOS-Diamantino",
        "ubicacion_nube": "Google Drive Cloud",
        "como_acceder": "Ruta de sistema local montada G:\\My Drive\\HBOS-Diamantino\\ / MCP gdrive",
        "estado": "activo",
        "descripcion": "Almacenamiento persistente de assets maestros, renderizados de video, backups y sandboxes.",
        "operation_id": 172
    },
    {
        "id": 3,
        "componente": "Qdrant_Vector_Database",
        "tipo": "base_de_datos_vectorial",
        "ubicacion_local": "c:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine\\hbos_estado.py",
        "ubicacion_nube": "https://d03a1188-3ca9-48fb-b856-fbf377f0a8fc.us-east4-0.gcp.cloud.qdrant.io",
        "como_acceder": "qdrant_client Python SDK (API Key en .env.local)",
        "estado": "activo",
        "descripcion": "Memoria canónica del ecosistema, patrones P-01..P-54, lecciones L-01..L-40, catálogo de agentes y estado diario.",
        "operation_id": 172
    },
    {
        "id": 4,
        "componente": "HBOS_SANDBOX",
        "tipo": "entorno_aislado_pruebas",
        "ubicacion_local": "G:\\My Drive\\HBOS-Diamantino\\_SANDBOX",
        "ubicacion_nube": "N/A",
        "como_acceder": "Aislamiento de procesos externos (FreeLLMAPI, Playwright .venv, tests de audio)",
        "estado": "activo",
        "descripcion": "Directorio aislado para ejecución de ejecutables externos y venvs sin contaminar el workspace principal.",
        "operation_id": 172
    },
    {
        "id": 5,
        "componente": "Episodios_Diamantino",
        "tipo": "produccion_audiovisual",
        "ubicacion_local": "c:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine\\diamantino\\",
        "ubicacion_nube": "G:\\My Drive\\HBOS-Diamantino\\diamantino",
        "como_acceder": "Pipelines Python ffmpeg, Wan 2.1, CosyVoice2/ElevenLabs",
        "estado": "activo",
        "descripcion": "Ep02 (Masters consolidados v3/v4/v5 responsive), Ep03 (Masters v1/v2), Ep04 (Preproducción y clips Wan 2.1 00 y 01).",
        "operation_id": 172
    },
    {
        "id": 6,
        "componente": "Diamantino_Patrones",
        "tipo": "gobernanza_tecnica_arquitectura",
        "ubicacion_local": "c:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine\\_MAESTRO\\",
        "ubicacion_nube": "Qdrant: colección diamantino_patrones",
        "como_acceder": "Qdrant query / scripts de consulta hbos_estado.py",
        "estado": "activo",
        "descripcion": "Rango canónico P-01 a P-54. Estándares arquitectónicos, ducking P-05, master LUFS P-04, R768 P-54.",
        "operation_id": 172
    },
    {
        "id": 7,
        "componente": "Diamantino_Lecciones",
        "tipo": "lecciones_aprendidas_heuristica",
        "ubicacion_local": "c:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine\\_MAESTRO\\",
        "ubicacion_nube": "Qdrant: colección diamantino_lecciones",
        "como_acceder": "Qdrant query / scripts de consulta hbos_estado.py",
        "estado": "activo",
        "descripcion": "Rango canónico L-01 a L-40. Prevención de 120 hrs/mes perdidas, cuotas de APIs, R768 contra alucinaciones.",
        "operation_id": 172
    }
]

# 3. Vectorizar e insertar puntos
points = []
for c in componentes:
    texto_vec = f"{c['componente']} {c['tipo']} {c['ubicacion_local']} {c['ubicacion_nube']} {c['como_acceder']} {c['descripcion']}"
    vec = generate_embedding(texto_vec)
    point_payload = {k: v for k, v in c.items() if k != 'id'}
    points.append(models.PointStruct(id=c["id"], vector=vec, payload=point_payload))

for attempt in range(1, 4):
    try:
        client.upsert(collection_name=collection_name, points=points)
        print(f"[OK] {len(points)} componentes indexados y vectorizados en '{collection_name}'.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 indexando componentes: {e}")
        time.sleep(2)

# 4. Registrar operation_id = 172 en registro_ecosistema
payload_op172 = {
    "operation_id": 172,
    "fase": "FASE 1 — CREAR DIRECTORIO EN QDRANT",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "coleccion": collection_name,
    "componentes_indexados": [c["componente"] for c in componentes],
    "total_componentes": len(componentes),
    "estado": "COMPLETADO"
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=172,
                vector=generate_embedding("Tarea directorio Qdrant hbos_directorio componentes FreeLLMAPI Drive Sandbox"),
                payload=payload_op172
            )]
        )
        print("[OK] operation_id = 172 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 registrando op 172: {e}")
        time.sleep(2)

# 5. Actualizar hbos_estado
for attempt in range(1, 4):
    try:
        p = client.retrieve("hbos_estado", ids=[1])[0].payload
        p["operation_ids"] = "45 a 172"
        p["hecho_hoy"].append("Creación de colección hbos_directorio con 7 componentes (op 172)")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado op 172"), payload=p)]
        )
        print("[OK] hbos_estado actualizado a op 172.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 actualizando hbos_estado: {e}")
        time.sleep(2)
