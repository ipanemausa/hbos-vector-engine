# -*- coding: utf-8 -*-
"""execute_op264.py — Registro en Qdrant de la Operación Canónica 264
Instalación local en PC, email sombrilla y lanzador nativo con biometría
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
load_dotenv(BASE / ".env.local")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def register_op264():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, prefer_grpc=False, timeout=25)
    ts = datetime.now().isoformat()
    
    payload = {
        "op": 264,
        "operation_id": 264,
        "tipo": "instalacion_app_local_biometrica",
        "descripcion": (
            "Instalacion local de FreeLLMAPI en C:\\Users\\ipane\\AppData\\Local\\Programs\\FreeLLMAPI, "
            "configuracion de cuenta bajo email sombrilla ipanemamarketingusa@gmail.com, "
            "despliegue de lanzador hbos_app_launcher.pyw con biometria Windows Hello (Synaptics), "
            "modo ventana nativa independiente (sin ingreso por puerto) y accesos directos en Escritorio y Menu Inicio."
        ),
        "timestamp": ts,
        "email_sombrilla": "ipanemamarketingusa@gmail.com",
        "ruta_instalacion": r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI",
        "acceso_directo": r"C:\Users\ipane\OneDrive\Escritorio\FreeLLMAPI (HBOS Soberano).lnk",
        "menu_inicio": r"C:\Users\ipane\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\FreeLLMAPI (HBOS Soberano).lnk",
        "modo_ejecucion": "NATIVE_APP_WINDOW_NO_PORT",
        "biometria": "WINDOWS_HELLO_SYNAPTICS_R32_R42",
        "estado": "EXITO",
        "veredicto": "OPERATIVO_LOCAL_BLINDADO"
    }

    print("[*] Registrando op=264 en coleccion 'hbos_auditoria'...")
    client.upsert(
        collection_name="hbos_auditoria",
        points=[PointStruct(id=264, vector=[0.0]*384, payload=payload)]
    )

    print("[*] Registrando op=264 en coleccion 'registro_ecosistema'...")
    client.upsert(
        collection_name="registro_ecosistema",
        points=[PointStruct(id=264, vector=[0.0]*384, payload=payload)]
    )

    print("[*] Actualizando 'hbos_estado' (ID=1)...")
    client.set_payload(
        collection_name="hbos_estado",
        payload={
            "ultimo_operation_id": 264,
            "rango_activo": "45 a 264",
            "fecha_actualizacion": ts,
            "estado_general": "OPERATIVO_APP_LOCAL_INSTALADA",
            "posicionamiento": "Operador de Apps Open Source con Biometria Soberana y Despliegue Local",
            "app_local_status": "INSTALADA_C_PROGRAMS",
            "email_sombrilla_activo": "ipanemamarketingusa@gmail.com"
        },
        points=[1]
    )

    print("[OK] Operación 264 registrada exitosamente en Qdrant.")

if __name__ == "__main__":
    register_op264()
