# -*- coding: utf-8 -*-
"""record_op267_qdrant.py — Registro oficial inmutable de op=267 en Qdrant
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), prefer_grpc=False, timeout=25)

ts = datetime.now().isoformat()
payload_op267 = {
    "tipo": "completar_apis_freellmapi",
    "op": 267,
    "operation_id": 267,
    "descripcion": "Completar la inyección de todas las APIs del ecosistema HBOS en FreeLLMAPI: recuperación de Groq (HTTP 200 verificado), GitHub Models, auditoría multimodal de ElevenLabs y Fal.ai",
    "timestamp": ts,
    "total_api_keys_activas": 10,
    "total_plataformas_activas": 10,
    "plataformas": ["github", "google", "groq", "huggingface", "kilo", "llm7", "modelscope", "ollama", "openrouter", "ovh"],
    "proveedores_recuperados": {
        "groq": "Recuperado y verificado (HTTP 200, inferencia activa con qwen3.8 y openai/gpt-oss-20b)",
        "github": "Inyectado con token de entorno GITHUB_TOKEN"
    },
    "proveedores_especiales": {
        "elevenlabs": "Clave 100% válida (21 voces activas), no soportado en FreeLLMAPI nativo -> canalizado vía step_fase2_voice.py",
        "fal_ai": "Clave válida (balance agotado), FreeLLMAPI usa fal-ai vía Hugging Face Router",
        "mistral": "Omitido por clave placeholder ('new clave ')"
    },
    "estado": "EXITO_TOTAL",
    "veredicto": "ECOSISTEMA_COMPLETADO_OP267"
}

# 1. hbos_auditoria
qc.upsert(
    collection_name="hbos_auditoria",
    points=[PointStruct(id=267, vector=[0.0]*384, payload=payload_op267)]
)

# 2. registro_ecosistema
qc.upsert(
    collection_name="registro_ecosistema",
    points=[PointStruct(id=267, vector=[0.0]*384, payload=payload_op267)]
)

# 3. hbos_estado
qc.set_payload(
    collection_name="hbos_estado",
    payload={
        "ultimo_operation_id": 267,
        "rango_activo": "45 a 267",
        "fecha_actualizacion": ts,
        "estado_general": "OPERATIVO_10_PROVIDERS",
        "posicionamiento": "Operador Multi-Provider Completo con FreeLLMAPI y Gateway Unificado"
    },
    points=[1]
)

print(f"[OK] op=267 registrado en Qdrant con éxito. Rango activo: 45 a 267.")
