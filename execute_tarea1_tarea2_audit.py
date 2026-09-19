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

# 1. Registrar operation_id = 76 (Auditoría de APIs y Alternativas)
audit_payload = {
    "operation_id": 76,
    "tarea": "TAREA 1 — AUDITORÍA DE ALTERNATIVAS GRATUITAS DISPONIBLES",
    "apis_evaluadas": {
        "elevenlabs": {
            "estado": "CUOTA_AGOTADA",
            "saldo_restante": "21 caracteres (~21 créditos) de 10,000 mensuales",
            "requerido_ep04": "~1,800 caracteres para locución v2",
            "estatus_http": "401 quota_exceeded para bloques estándar"
        },
        "dashscope_wan21": {
            "estado": "CUOTA_FREETIER_AGOTADA",
            "error_codigo": "AllocationQuota.FreeTierOnly",
            "estatus_http": "403 Forbidden",
            "clips_exitosos_en_nube": ["plano_00 (5s)", "plano_01 (20s)"],
            "clips_bloqueados": ["plano_02 a plano_09"]
        },
        "gemini_api": {
            "estado": "ACTIVO_Y_DISPONIBLE",
            "estatus_http": "200 OK",
            "modelos_disponibles": 50,
            "uso_recomendado": "Generación de guiones, auditorías, metadatos, prompts y backgrounds"
        },
        "groq_api": {
            "estado": "ACTIVO_Y_DISPONIBLE",
            "estatus_http": "200 OK",
            "modelos_disponibles": 13,
            "uso_recomendado": "Inferencia de texto ultra-rápida LPU"
        },
        "openai_api": {
            "estado": "PLACEHOLDER_NO_CONFIGURADA"
        }
    },
    "alternativas_tts_nube_evaluadas": [
        {"proveedor": "Google Cloud Text-to-Speech", "prueba_gratuita": "$300 USD créditos de bienvenida", "requiere_tarjeta": True},
        {"proveedor": "Azure Cognitive Services Speech", "prueba_gratuita": "500,000 caracteres/mes gratis", "requiere_tarjeta": True},
        {"proveedor": "Play.ht", "prueba_gratuita": "12,500 caracteres gratis", "requiere_tarjeta": False},
        {"proveedor": "Coqui TTS / Piper", "prueba_gratuita": "Open source local", "permitido_en_ecosistema": False, "motivo": "Prohibido TTS local por mandato canónico HBOS"}
    ],
    "estado": "COMPLETADO"
}

vec_op76 = generate_embedding("Tarea 1 operacion 76 Auditoria de APIs Cuotas ElevenLabs DashScope Gemini Groq Alternativas", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=76,
            vector=vec_op76,
            payload=audit_payload
        )
    ]
)
print("[OK] operation_id = 76 registrado en registro_ecosistema.")

# 2. Registrar operation_id = 77 (Reintento y Diagnóstico DashScope Wan 2.1)
dashscope_payload = {
    "operation_id": 77,
    "tarea": "TAREA 2 — INTENTAR REANUDAR PLANOS 02-09 EN DASHSCOPE",
    "episodio": "Ep04-MedicineAgentica",
    "resultado_intento_plano_02": "HTTP 403 AllocationQuota.FreeTierOnly",
    "detalle_error": "The free quota has been exhausted. To continue accessing the model on a paid basis, please complete your payment information.",
    "cumplimiento_guardrails": "No se aplicó ffmpeg -loop 1 ni ningún fallback ficticio. Producción pausada respetando integridad técnica 100% en Nube.",
    "estado": "PAUSADO_POR_CUOTA_NUBE"
}

vec_op77 = generate_embedding("Tarea 2 operacion 77 Diagnostico DashScope Wan 2.1 HTTP 403 FreeTierOnly Pausa de Produccion Nube", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=77,
            vector=vec_op77,
            payload=dashscope_payload
        )
    ]
)
print("[OK] operation_id = 77 registrado en registro_ecosistema.")
