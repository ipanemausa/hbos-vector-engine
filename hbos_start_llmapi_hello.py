# -*- coding: utf-8 -*-
"""hbos_start_llmapi_hello.py — Inicio Soberano de LLMAPI con Windows Hello (R32 / R37 / R42)
Trazabilidad: operation_id = 263
"""

import os
import sys
import json
import time
import socket
import urllib.request
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

from hbos_auth_ui import HBOSAuthUI

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
load_dotenv(BASE / ".env.local")

PORT_FREELLMAPI = 3001
FREELLMAPI_URL = f"http://127.0.0.1:{PORT_FREELLMAPI}"
API_KEY = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
DAEMON_SCRIPT = BASE / "start_freellmapi_daemon.py"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("127.0.0.1", port)) == 0

def ensure_daemon_running():
    if is_port_open(PORT_FREELLMAPI):
        print(f"[*] Daemon FreeLLMAPI ya se encuentra escuchando en :{PORT_FREELLMAPI}")
        return True
    print(f"[*] Lanzando daemon FreeLLMAPI en :{PORT_FREELLMAPI}...")
    subprocess.Popen([sys.executable, str(DAEMON_SCRIPT)], cwd=str(BASE))
    for _ in range(15):
        time.sleep(1)
        if is_port_open(PORT_FREELLMAPI):
            print(f"[OK] Daemon FreeLLMAPI levantado exitosamente en :{PORT_FREELLMAPI}")
            return True
    return False

def verify_llmapi_models():
    req = urllib.request.Request(
        f"{FREELLMAPI_URL}/v1/models",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("data", [])
            return len(models), [m.get("id") for m in models[:5]]
    except Exception as e:
        print(f"[!] Error consultando modelos: {e}")
        return 0, []

def register_qdrant_op263(models_count, auth_token):
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
        qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=15)
        
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        desc = (
            f"Inicio soberano de sesion LLMAPI autorizado biometricamente con Windows Hello (op=263). "
            f"FreeLLMAPI activo en :{PORT_FREELLMAPI} con {models_count} modelos disponibles. "
            f"Canon R32 (UI nativa), R37 (token TTL 60m), R42 (biometria winbio real)."
        )
        
        payload = {
            "op": 263,
            "operation_id": 263,
            "tipo": "INICIO_LLMAPI_WINDOWS_HELLO",
            "timestamp": ts,
            "descripcion": desc,
            "puerto": PORT_FREELLMAPI,
            "modelos_disponibles": models_count,
            "biometric_token_active": bool(auth_token),
            "estado": "EXITO",
            "veredicto": "LLMAPI_INICIADO_SOBERANO"
        }
        
        # 1. hbos_auditoria
        qc.upsert(
            collection_name="hbos_auditoria",
            points=[PointStruct(id=263, vector=[0.0]*384, payload=payload)]
        )
        
        # 2. registro_ecosistema
        qc.upsert(
            collection_name="registro_ecosistema",
            points=[PointStruct(id=263, vector=[0.0]*384, payload=payload)]
        )
        
        # 3. hbos_estado
        qc.set_payload(
            collection_name="hbos_estado",
            payload={
                "ultimo_operation_id": 263,
                "rango_activo": "45 a 263",
                "fecha_actualizacion": ts,
                "estado_general": "OPERATIVO_LLMAPI_AUTORIZADO",
                "posicionamiento": "Operador de Apps Open Source con Biometria Soberana"
            },
            points=[1]
        )
        print("[OK] Qdrant op=263 registrado (auditoría, registro_ecosistema y hbos_estado 45 a 263)")
        return True
    except Exception as e:
        print(f"[!] Error registrando en Qdrant: {e}")
        return False

def main():
    print("=" * 70)
    print(">>> HBOS · INICIO SOBERANO DE LLMAPI CON WINDOWS HELLO (op=263) <<<")
    print("=" * 70)
    
    auth = HBOSAuthUI(timeout_minutes=60)
    scope = "llmapi_sovereign_session"
    message = "HBOS R32/R42: Autorizar inicio soberano de sesión LLMAPI op=263"
    
    print("\n[PASO 1] Solicitando autorización biométrica nativa Windows Hello...")
    print(">>> Por favor, toca el sensor de huella dactilar o ingresa tu PIN de Windows Hello <<<")
    
    approved = auth.authorize(scope=scope, message=message)
    
    if not approved:
        print("\n[FALLO] Autorización biométrica denegada o cancelada. LLMAPI no iniciado.")
        sys.exit(1)
        
    print("\n[PASO 2] Autorización biométrica VERIFICADA exitosamente.")
    token_data = auth.cache.get(scope, {})
    print(f"[OK] Token de sesión activo: {token_data.get('token', 'N/A')}")
    
    print("\n[PASO 3] Verificando daemon FreeLLMAPI (:3001)...")
    if not ensure_daemon_running():
        print("[FALLO] No se pudo levantar el daemon FreeLLMAPI en :3001")
        sys.exit(1)
        
    print("\n[PASO 4] Consultando modelos y catálogo activo...")
    count, sample_models = verify_llmapi_models()
    print(f"[OK] Total de modelos disponibles: {count}")
    print(f"[OK] Muestra de modelos: {', '.join(sample_models)}")
    
    print("\n[PASO 5] Registrando operación 263 en Qdrant...")
    register_qdrant_op263(count, token_data.get('token'))
    
    print("\n[PASO 6] Abriendo consola UI de FreeLLMAPI en navegador local...")
    try:
        webbrowser.open(FREELLMAPI_URL)
        print(f"[OK] Navegador dirigido a: {FREELLMAPI_URL}")
    except Exception as e:
        print(f"[!] No se pudo abrir navegador automáticamente: {e}")
        
    print("\n" + "=" * 70)
    print(f"[ÉXITO TOTAL] LLMAPI iniciado bajo gobernanza soberana Windows Hello (op=263)")
    print(f"URL Local: {FREELLMAPI_URL}")
    print(f"Modelos Listos: {count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
