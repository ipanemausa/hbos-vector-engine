import os
import sys
import time
import subprocess
import socket
import urllib.request
import psutil

exe_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe"
work_dir = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app"

print(f"[*] Verificando existencia de binario: {exe_path}")
if not os.path.exists(exe_path):
    print(f"[ERROR] No existe el binario en: {exe_path}")
    sys.exit(1)

print("[*] Lanzando FreeLLMAPI.exe...")
# Lanzamos desacoplado
proc = subprocess.Popen([exe_path], cwd=work_dir, shell=False)
print(f"[*] Proceso iniciado con PID: {proc.pid}")

# Esperamos 12 segundos para que Electron / Express inicialice
print("[*] Esperando 12 segundos a que el proceso levante servicios...")
time.sleep(12)

# Verificar si sigue corriendo
is_running = proc.poll() is None
print(f"[*] ¿Proceso principal PID {proc.pid} sigue activo?: {is_running}")

# Buscar subprocesos hijos de FreeLLMAPI
child_procs = []
try:
    p = psutil.Process(proc.pid)
    child_procs = p.children(recursive=True)
    print(f"[*] Procesos secundarios detectados: {len(child_procs)}")
    for cp in child_procs:
        print(f"    - PID {cp.pid}: {cp.name()}")
except Exception as e:
    print(f"[!] Info psutil: {e}")

# Verificar puerto 3001
port_3001_open = False
for attempt in range(1, 6):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', 3001))
        s.close()
        port_3001_open = True
        print(f"[OK] Puerto 3001 RESPONDE en el intento {attempt}.")
        break
    except Exception as e:
        print(f"[*] Intento {attempt}: Puerto 3001 aun no responde ({e}), esperando 3s...")
        time.sleep(3)

# Verificar UI HTTP
ui_status = None
if port_3001_open:
    try:
        req = urllib.request.Request("http://localhost:3001", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            ui_status = response.status
            content = response.read(500).decode('utf-8', errors='ignore')
            print(f"[OK] UI respondió con status {ui_status}")
            print(f"[*] Fragmento de respuesta HTML:\n{content[:200]}...")
    except Exception as e:
        print(f"[!] Error consultando UI http://localhost:3001: {e}")
else:
    print("[!] Puerto 3001 no respondió en el tiempo límite.")

# Si no abrió el puerto 3001, verificar si abrió otro puerto o qué puertos están escuchando
if not port_3001_open:
    print("[*] Escaneando qué puertos locales abrieron los procesos de FreeLLMAPI...")
    all_pids = [proc.pid] + [cp.pid for cp in child_procs]
    for conn in psutil.net_connections(kind='inet'):
        if conn.pid in all_pids:
            print(f"    - PID {conn.pid} escuchando en {conn.laddr} (status={conn.status})")
