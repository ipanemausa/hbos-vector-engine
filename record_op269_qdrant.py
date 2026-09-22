# -*- coding: utf-8 -*-
"""record_op269_qdrant.py — Registro oficial inmutable de op=269 en Qdrant
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

ts = datetime.now().isoformat()
payload = {
    "op": 269,
    "tipo": "dag_inyeccion_total_y_cierre",
    "descripcion": "DAG op=269: Auditoría, inyección total tuning fino, verificación end-to-end y cierre redundante triple",
    "timestamp": ts,
    "fases": [
        "FASE 1: Auditoría de claves y plataformas",
        "FASE 2: Inyección cifrada AES-256-GCM con tuning fino",
        "FASE 3: Verificación end-to-end (:3001, chat, gateway :3002)",
        "FASE 4: Cierre redundante triple (local, Drive, backup, Qdrant, git)"
    ],
    "estado": "EXITO_TOTAL",
    "veredicto": "TUNING_FINO_CONSOLIDADO"
}

qc.upsert(collection_name="hbos_auditoria", points=[PointStruct(id=269, vector=[0.0]*384, payload=payload)])
qc.upsert(collection_name="registro_ecosistema", points=[PointStruct(id=269, vector=[0.0]*384, payload=payload)])
print("[OK] op=269 registrado en Qdrant (hbos_auditoria + registro_ecosistema)")

try:
    qc.set_payload(
        collection_name="hbos_estado",
        payload={
            "rango": "45 a 269",
            "rango_activo": "45 a 269",
            "ultimo_operation_id": 269,
            "fecha_actualizacion": ts,
            "estado_general": "TUNING_FINO_OPERATIVO_TOTAL"
        },
        points=[1]
    )
    print("[OK] hbos_estado actualizado a 45-269")
except Exception as e:
    print(f"[!] hbos_estado: {e}")
