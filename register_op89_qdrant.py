import os
import sys
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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op89 = {
    "operation_id": 89,
    "tarea": "TAREA 1 — VERIFICAR RENOVACIÓN DE CRÉDITOS",
    "timestamp": "2026-09-19T13:53:00Z",
    "fase1_elevenlabs": {
        "status_code": 401,
        "character_cost_limit": 10000,
        "credits_remaining": 9,
        "cuota_disponible": "NO",
        "error_tipo": "quota_exceeded",
        "detalle": "This request exceeds your quota of 10000. You have 9 credits remaining."
    },
    "fase2_dashscope": {
        "status_code": 403,
        "codigo_error": "AllocationQuota.FreeTierOnly",
        "cuota_disponible": "NO",
        "detalle": "The free quota has been exhausted. To continue accessing the model on a paid basis, please complete your payment information."
    },
    "fase3_gemini": {
        "status_code": 200,
        "cuota_disponible": "SÍ",
        "total_modelos": 50,
        "estado": "ACTIVO"
    },
    "fase4_conclusion": {
        "se_puede_producir_ep04": "NO",
        "motivo_bloqueo": "Falta de cuota en Wan 2.1 (DashScope HTTP 403) y ElevenLabs (HTTP 401 - 9 créditos restantes)",
        "estado": "COMPLETADO"
    }
}

vec_89 = generate_embedding("Tarea 1 operacion 89 Verificacion Renovacion de Creditos ElevenLabs DashScope Gemini Ep04", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=89,
            vector=vec_89,
            payload=payload_op89
        )
    ]
)
print("[OK] operation_id = 89 registrado exitosamente en registro_ecosistema de Qdrant.")
