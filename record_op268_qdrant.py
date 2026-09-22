# -*- coding: utf-8 -*-
"""record_op268_qdrant.py — Registro oficial inmutable de op=268 en Qdrant
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), prefer_grpc=False, timeout=25)

ts = datetime.now().isoformat()
payload_op268 = {
    "tipo": "auditoria_rrss_y_marketing",
    "op": 268,
    "operation_id": 268,
    "descripcion": "Auditoría exhaustiva de los 10 canales de redes sociales de HBOS, arquitectura de identidad (Capa A Sombrilla vs Capa B Núcleo), inventario de contenido audiovisual y estrategia comercial",
    "timestamp": ts,
    "canales_auditados": [
        "instagram", "tiktok", "facebook", "threads", "telegram", 
        "discord", "linkedin", "youtube", "x", "github"
    ],
    "handle_unificado": "@ipanemamarketingusa",
    "identidad_sombrilla": "IPANEMAMARKETINGUSA@gmail.com",
    "identidad_nucleo": "hbos@gmail.com (fallback: hbos.ecosystem@gmail.com)",
    "avatares": {
        "frente_comercial": "Álex (Silicon Valley, humano sintético)",
        "mascota_icono": "Diamantino (Entidad mineral consciente, no-humanizado)"
    },
    "inventario_resumen": {
        "videos": "Ep01, Ep02 (4 formatos), Ep03 (4 formatos), Ep04, Demis Hassabis v2",
        "audios": 45,
        "guiones_prompts": 39,
        "imagenes_thumbs": 95
    },
    "monetizacion_tiers": ["$0 Lead Magnet", "$27 Pack Operativo", "$97/mes Membresía", "$1,500 Consultoría B2B"],
    "estado": "AUDITORIA_COMPLETA",
    "veredicto": "ESTRATEGIA_CONSOLIDADA_OP268"
}

# 1. hbos_auditoria
qc.upsert(
    collection_name="hbos_auditoria",
    points=[PointStruct(id=268, vector=[0.0]*384, payload=payload_op268)]
)

# 2. registro_ecosistema
qc.upsert(
    collection_name="registro_ecosistema",
    points=[PointStruct(id=268, vector=[0.0]*384, payload=payload_op268)]
)

# 3. hbos_estado
qc.set_payload(
    collection_name="hbos_estado",
    payload={
        "ultimo_operation_id": 268,
        "rango_activo": "45 a 268",
        "fecha_actualizacion": ts,
        "estado_general": "MARKETING_Y_RRSS_AUDITADO",
        "posicionamiento": "Ecosistema Multicanal Blindado con Avatar Álex y Mascota Diamantino"
    },
    points=[1]
)

print(f"[OK] op=268 registrado en Qdrant con éxito. Rango activo: 45 a 268.")
