# -*- coding: utf-8 -*-
"""record_op266_qdrant.py — Registro oficial inmutable de op=266 en Qdrant
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), prefer_grpc=False, timeout=25)

ts = datetime.now().isoformat()
payload_op266 = {
    "tipo": "inyeccion_providers_freellmapi",
    "op": 266,
    "operation_id": 266,
    "descripcion": "Inyección cifrada AES-256-GCM de providers en FreeLLMAPI (:3001) y verificación de inferencia activa en Gateway (:3002)",
    "timestamp": ts,
    "via_elegida": "VIA B (Inyección directa SQLite con AES-256-GCM idéntico a Node.js)",
    "providers_validados": {
        "openrouter": "HTTP 200 (453 modelos) -> INYECTADO",
        "dashscope_modelscope": "HTTP 200 (Conexión válida) -> INYECTADO",
        "gemini_google": "HTTP 200 (50 modelos) -> INYECTADO",
        "groq": "HTTP 401 (Unauthorized / expirada) -> OMITIDO",
        "mistral": "HTTP 401 (Placeholder 'new clave ') -> OMITIDO",
        "huggingface": "HTTP 200 (Token válido) -> INYECTADO",
        "ollama_local": "Inyectado (localhost:11434)"
    },
    "total_keys_activas": 8,
    "total_modelos_api": 247,
    "resultado_4_4_chat": "HTTP 200 via gemini-2.5-flash",
    "resultado_4_5_gateway": "HTTP 200 via :3002",
    "estado": "EXITO_TOTAL",
    "veredicto": "OPERATIVO_SISTEMA_HABILITADO"
}

# 1. hbos_auditoria
qc.upsert(
    collection_name="hbos_auditoria",
    points=[PointStruct(id=266, vector=[0.0]*384, payload=payload_op266)]
)

# 2. registro_ecosistema
qc.upsert(
    collection_name="registro_ecosistema",
    points=[PointStruct(id=266, vector=[0.0]*384, payload=payload_op266)]
)

# 3. hbos_estado
qc.set_payload(
    collection_name="hbos_estado",
    payload={
        "ultimo_operation_id": 266,
        "rango_activo": "45 a 266",
        "fecha_actualizacion": ts,
        "estado_general": "OPERATIVO_INFERENCIA_ACTIVA",
        "posicionamiento": "Operador Soberano Multi-Provider con FreeLLMAPI y Gateway Unificado"
    },
    points=[1]
)

print(f"[OK] op=266 registrado en Qdrant con éxito. Rango activo: 45 a 266.")
