# -*- coding: utf-8 -*-
"""execute_op265.py — Registro en Qdrant de Cierre Canónico op=265
Push, verificación daemon, consolidación referencias, redundancia triple
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
load_dotenv(BASE / ".env.local")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def register_op265():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, prefer_grpc=False, timeout=25)
    ts = datetime.now().isoformat()
    
    hash_ref = "EF20A5CD20FF71673D739255646141C30A10FD3FD0C33EBBCD95251DA525D28C"
    archivos_tocados = [
        "start_freellmapi_daemon.py",
        "_HBOS_REFERENCIAS.md",
        "_MAESTRO/_HBOS_REFERENCIAS.md",
        "backup_hbos/_MAESTRO/_HBOS_REFERENCIAS.md",
        "_MAESTRO/archive/hbos_gatekeeper.py",
        "hbos_app_launcher.pyw",
        "install_hbos_app.py",
        "execute_op264.py",
        "execute_op265.py"
    ]
    
    payload = {
        "op": 265,
        "operation_id": 265,
        "tipo": "cierre_soberano",
        "descripcion": "Cierre op=264->op=265: push, verificación daemon, consolidación referencias, redundancia triple",
        "timestamp": ts,
        "archivos": archivos_tocados,
        "hashes": {
            "_HBOS_REFERENCIAS.md": hash_ref,
            "_FACTORIZACION_MAESTRA.md": "89BC0D0D8C2E7C16B6270E35A1542312D13E20E4C39CBEB0C07DA1646D15AE74"
        },
        "verificaciones": {
            "daemon_path": r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\FreeLLMAPI.exe",
            "port_3001": "RESPONDING_HTTP_200",
            "gatekeeper_status": "ARCHIVADO_EN__MAESTRO_ARCHIVE",
            "auth_ui_audit": "FUENTE_ACTIVA_AUDITORIA_MANTENIDA",
            "redundancia_triple": "CONFIRMADA_100_COINCIDENCIA"
        },
        "estado": "EXITO",
        "veredicto": "CIERRE_SOBERANO_CONFIRMADO"
    }

    print("[*] Insertando op=265 en 'hbos_auditoria'...")
    client.upsert(
        collection_name="hbos_auditoria",
        points=[PointStruct(id=265, vector=[0.0]*384, payload=payload)]
    )

    print("[*] Insertando op=265 en 'registro_ecosistema'...")
    client.upsert(
        collection_name="registro_ecosistema",
        points=[PointStruct(id=265, vector=[0.0]*384, payload=payload)]
    )

    print("[*] Actualizando 'hbos_estado' (ID=1)...")
    client.set_payload(
        collection_name="hbos_estado",
        payload={
            "ultimo_operation_id": 265,
            "rango_activo": "45 a 265",
            "fecha_actualizacion": ts,
            "estado_general": "OPERATIVO_CIERRE_COMPLETO_REDUNDANCIA_TRIPLE",
            "posicionamiento": "Operador de Apps Open Source con Biometria Soberana y Despliegue Local",
            "app_local_status": "INSTALADA_C_PROGRAMS",
            "email_sombrilla_activo": "ipanemamarketingusa@gmail.com"
        },
        points=[1]
    )

    print("[*] Verificando retrieve de ID 265 en 'hbos_auditoria'...")
    pts = client.retrieve(collection_name="hbos_auditoria", ids=[265])
    if pts:
        print(f"[OK] Retrieve op=265 exitoso: {pts[0].payload.get('descripcion')}")
        return True
    else:
        raise RuntimeError("No se pudo recuperar el punto op=265 de hbos_auditoria")

if __name__ == "__main__":
    register_op265()
