"""
hbos_bootstrap.py — ARRANQUE LIMPIO Y PREPARACIÓN DE ENTORNO SOBERANO
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Gobernanza: DAG R768 · Autopilot Total
"""

import os
import sys
import json
import time
import socket
import subprocess
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine"
SANDBOX_DIR = r"G:\My Drive\HBOS-Diamantino\_SANDBOX"
BACKUP_DIR = r"C:\Users\ipane\backup_hbos"
MCP_CONFIG = r"C:\Users\ipane\.gemini\config\mcp_config.json"

def check_port(host="127.0.0.1", port=3001, timeout=0.8):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def bootstrap():
    print("=" * 65)
    print(">>> [HBOS BOOTSTRAP] INICIANDO PREPARACIÓN DEL ENTORNO SOBERANO <<<")
    print("=" * 65)

    # 1. Verificar directorios troncales
    print("\n[1/5] Verificando estructura de directorios físicos...")
    dirs_to_ensure = [
        WORKSPACE_DIR,
        os.path.join(WORKSPACE_DIR, "_MAESTRO"),
        os.path.join(WORKSPACE_DIR, "diamantino"),
        os.path.join(BACKUP_DIR, "_MAESTRO"),
        r"C:\Users\ipane\.gemini\config\hbos-freellmapi"
    ]
    for d in dirs_to_ensure:
        os.makedirs(d, exist_ok=True)
    print("  [OK] Estructura de directorios asegurada.")

    # 2. Verificar .env.local
    print("\n[2/5] Verificando variables de entorno (.env.local)...")
    env_path = os.path.join(WORKSPACE_DIR, ".env.local")
    if not os.path.exists(env_path):
        print(f"  [!] ALERTA CRÍTICA: No se encontró {env_path}")
        return 1
    load_dotenv(env_path)
    
    req_keys = ["QDRANT_URL", "QDRANT_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]
    for k in req_keys:
        val = os.getenv(k)
        print(f"  • {k}: {'CONFIGURADO' if val else 'FALTANTE'}")
    print("  [OK] Variables de entorno cargadas.")

    # 3. Verificar MCP Config
    print("\n[3/5] Verificando configuración de servidores MCP...")
    if os.path.exists(MCP_CONFIG):
        with open(MCP_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        srvs = list(cfg.get("mcpServers", {}).keys())
        print(f"  [OK] mcp_config.json válido con {len(srvs)} servidores: {srvs}")
    else:
        print(f"  [!] ALERTA: {MCP_CONFIG} no existe.")

    # 4. Verificar o iniciar FreeLLMAPI en localhost:3001
    print("\n[4/5] Verificando daemon FreeLLMAPI en puerto 3001...")
    if check_port("127.0.0.1", 3001):
        print("  [OK] FreeLLMAPI ya está corriendo en http://127.0.0.1:3001")
    else:
        print("  [*] FreeLLMAPI no detectado en puerto 3001. Intentando arranque...")
        exe_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe"
        if os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)
                if check_port("127.0.0.1", 3001):
                    print("  [OK] FreeLLMAPI lanzado con éxito en puerto 3001.")
                else:
                    print("  [!] FreeLLMAPI iniciado pero el puerto 3001 aún no responde.")
            except Exception as e:
                print(f"  [!] Error al iniciar FreeLLMAPI: {e}")
        else:
            print(f"  [!] Ejecutable FreeLLMAPI no hallado en {exe_path}")

    # 5. Ejecutar Healthcheck rápido
    print("\n[5/5] Ejecutando healthcheck preliminar...")
    res = subprocess.run(["python", "hbos_healthcheck.py", "--fast"], capture_output=True, text=True, encoding="utf-8")
    for l in res.stdout.splitlines():
        print(" ", l)

    print("\n" + "=" * 65)
    print("[OK] HBOS BOOTSTRAP COMPLETADO CON ÉXITO")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(bootstrap())
