import os
import sys
import time
import socket
import subprocess
import urllib.request
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    import hashlib, math
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

print("==========================================================================")
print(">>> [FASE 2] EJECUTAR APP FREELMAPI EN SANDBOX (operation_id=167) <<<")
print("==========================================================================")

# TAREA 2.1 — Verificar procesos previos
import psutil
prev_procs = [p.info for p in psutil.process_iter(['pid', 'name']) if 'freellm' in (p.info['name'] or '').lower()]
print(f"[*] Tarea 2.1: Procesos previos encontrados: {len(prev_procs)}")
for p in prev_procs:
    print(f"    - PID {p['pid']}: {p['name']}")

# TAREA 2.2 — Ejecutar FreeLLMAPI.exe
exe_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe"
work_dir = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app"

# Asegurar config port 3001 en AppData
appdata_cfg = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\config.json"
if os.path.exists(appdata_cfg):
    try:
        with open(appdata_cfg, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["port"] = 3001
        with open(appdata_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        print("[*] Configurado port: 3001 en C:\\Users\\ipane\\AppData\\Roaming\\FreeLLMAPI\\config.json")
    except Exception as e:
        print(f"[!] Aviso config: {e}")

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

print(f"[*] Tarea 2.2: Lanzando FreeLLMAPI.exe desacoplado...")
proc = subprocess.Popen(
    [exe_path],
    cwd=work_dir,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    close_fds=True
)
print(f"[*] Proceso lanzado. PID inicial: {proc.pid}")
print("[*] Esperando 15 segundos a que Electron y servicios inicialicen...")
time.sleep(15)

# Verificar que los procesos siguen activos
active_procs = [p.info for p in psutil.process_iter(['pid', 'name']) if 'freellm' in (p.info['name'] or '').lower()]
proceso_activo = len(active_procs) > 0
print(f"[*] ¿Procesos activos de FreeLLMAPI?: {proceso_activo} (Total detectados: {len(active_procs)})")
for p in active_procs:
    print(f"    - PID {p['pid']}: {p['name']}")

# TAREA 2.3 — Verificar puerto
puerto_detectado = None
puerto_activo_str = "inactivo"

# Escanear qué puertos tienen abiertos los procesos de FreeLLMAPI
freellm_pids = [p['pid'] for p in active_procs]
for conn in psutil.net_connections(kind='inet'):
    if conn.pid in freellm_pids and conn.status == 'LISTEN':
        print(f"[*] Proceso FreeLLMAPI PID {conn.pid} está escuchando en {conn.laddr}")
        puerto_detectado = conn.laddr.port

# Probar primero puerto 3001
for port_candidate in ([3001, puerto_detectado] if puerto_detectado and puerto_detectado != 3001 else [3001, 31415]):
    if not port_candidate:
        continue
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', port_candidate))
        s.close()
        print(f"[OK] Tarea 2.3: Puerto {port_candidate} RESPONDE exitosamente.")
        puerto_detectado = port_candidate
        puerto_activo_str = f"activo (puerto {port_candidate})"
        break
    except Exception as e:
        print(f"[*] Puerto {port_candidate} no respondió: {e}")

# TAREA 2.4 — Verificar UI
ui_responde = False
ui_status_code = None
if puerto_detectado:
    url = f"http://localhost:{puerto_detectado}"
    print(f"[*] Tarea 2.4: Verificando UI en {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            ui_status_code = response.status
            if response.status == 200:
                ui_responde = True
                content = response.read(200).decode('utf-8', errors='ignore')
                print(f"[OK] UI respondió status 200. Snippet: {content[:100]}...")
    except Exception as e:
        print(f"[!] Error consultando UI: {e}")

# VALIDACIÓN FASE 2
estado_fase2 = "OK" if (proceso_activo and puerto_detectado and ui_responde) else "FAIL"
print(f"\n=======================================================")
print(f"VALIDACIÓN FASE 2: {estado_fase2}")
print(f"  - ¿Proceso activo?: {proceso_activo}")
print(f"  - ¿Puerto responde?: {puerto_activo_str}")
print(f"  - ¿UI responde (HTTP 200)?: {ui_responde}")
print(f"=======================================================")

# TAREA 2.5 — VECTORIZAR (operation_id=167)
payload_op167 = {
    "operation_id": 167,
    "fase": "FASE 2 — EJECUTAR APP FREELMAPI",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "binario": "FreeLLMAPI.exe",
    "ruta": exe_path,
    "proceso_activo": proceso_activo,
    "puerto_3001": puerto_activo_str,
    "puerto_utilizado": puerto_detectado,
    "ui_responde": ui_responde,
    "ui_status": ui_status_code,
    "pids": [p['pid'] for p in active_procs],
    "estado": estado_fase2
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=167,
                vector=generate_embedding(f"FreeLLMAPI Fase 2 Ejecutar App proceso {proceso_activo} puerto {puerto_detectado} ui {ui_responde} {estado_fase2}"),
                payload=payload_op167
            )]
        )
        print("[OK] operation_id = 167 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento registro op 167: {e}")
        time.sleep(2)

# Actualizar hbos_estado
for attempt in range(1, 4):
    try:
        p = client.retrieve("hbos_estado", ids=[1])[0].payload
        p["operation_ids"] = "45 a 167"
        p["hecho_hoy"].append(f"Ejecución y validación FreeLLMAPI en Sandbox (op 167) - {estado_fase2}")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado op 167"), payload=p)]
        )
        print("[OK] hbos_estado actualizado a op 167.")
        break
    except Exception as e:
        print(f"[!] Reintento hbos_estado: {e}")
        time.sleep(2)
