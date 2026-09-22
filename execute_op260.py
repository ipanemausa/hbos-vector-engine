import os, time, hashlib, math, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv('.env.local')

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), prefer_grpc=False, timeout=25)

desc_op260 = (
    "Auditoría de integridad total del ecosistema HBOS en 9 planos (op=260). "
    "Verificación empírica de hbos_canon (85 pts: R1-R76 + 9 doctrina), diamantino_movimientos (321 pts), "
    "hbos_anchor_vivo.py (motor armónico R62 autónomo de 420 pasos por ciclo), 5 servidores MCP y 5 tools de hbos-chat-context, "
    "arbitraje FreeLLMAPI/OpenRouter, detección de brechas en fuentes externas (links DH y Chibi) y falta de índice físico maestro de videos."
)
vec_op260 = generate_embedding(f"op=260 AUDITORIA_INTEGRIDAD_9_CAPAS {desc_op260}")

# 1. Registrar op=260 en registro_ecosistema
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=260,
            vector=vec_op260,
            payload={
                "operation_id": 260,
                "op": 260,
                "tipo": "AUDITORIA_INTEGRIDAD_9_CAPAS",
                "fecha": "2026-09-22",
                "timestamp": "2026-09-22T13:30:00Z",
                "estado": "EXITO",
                "descripcion": desc_op260,
                "canon_puntos": 85,
                "diamantino_movimientos_puntos": 321,
                "mcps_count": 5,
                "drift": 0
            }
        )
    ]
)

# 2. Actualizar hbos_estado a rango "45 a 260"
client.set_payload(
    collection_name="hbos_estado",
    payload={
        "ultimo_operation_id": 260,
        "rango_activo": "45 a 260",
        "fecha_actualizacion": "2026-09-22T13:30:00Z",
        "estado_general": "OPERATIVO_CANONICO_DEFINITIVO",
        "total_reglas_canon": 85
    },
    points=[1]
)

# 3. Registrar auditoria op=260 en hbos_auditoria
vec_audit = generate_embedding("audit op=260 integridad 9 capas ecosistema hbos")
client.upsert(
    collection_name="hbos_auditoria",
    points=[
        models.PointStruct(
            id=260,
            vector=vec_audit,
            payload={
                "audit_id": "audit_op260_integridad_9_capas",
                "operation_id": 260,
                "op": 260,
                "timestamp": "2026-09-22T13:30:00Z",
                "tipo_auditoria": "INTEGRIDAD_9_CAPAS",
                "capas_auditadas": [
                    "canon_factorizacion",
                    "vectorizacion_movimientos",
                    "agente_420_movimientos",
                    "mcp_y_tools",
                    "arbitraje_proveedores",
                    "fuentes_externas",
                    "coherencia_recursos",
                    "organizacion_archivos",
                    "estado_global_drift"
                ],
                "veredicto": "AUDITADO_CON_BRECHAS_IDENTIFICADAS"
            }
        )
    ]
)

print("[OK] op=260 registrada, hbos_estado actualizado a 45 a 260 y auditoría registrada.")
