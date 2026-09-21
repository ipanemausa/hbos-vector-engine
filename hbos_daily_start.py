"""
hbos_daily_start.py — Protocolo de Arranque Diario Soberano en Segundos (< 5s)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=232 · Canon FAM@-T · No-Regresión (§7.3)
"""

import os
import sys
import time
import socket
import urllib.request
import subprocess
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_port(port, host="127.0.0.1", timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def check_qdrant():
    url = os.getenv("QDRANT_URL")
    key = os.getenv("QDRANT_API_KEY")
    if not url:
        return False, 0.0
    t0 = time.time()
    try:
        req = urllib.request.Request(
            f"{url.rstrip('/')}/collections",
            headers={"api-key": key, "User-Agent": "HBOS-DailyStart/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status == 200, time.time() - t0
    except Exception:
        return False, 0.0

def start_freellmapi():
    print("  [!] FreeLLMAPI :3001 inactivo. Auto-iniciando daemon...")
    script = os.path.join(BASE_DIR, "start_freellmapi_daemon.py")
    subprocess.Popen([sys.executable, script], cwd=BASE_DIR, creationflags=0x00000008 | 0x00000200, close_fds=True)
    time.sleep(3)
    return check_port(3001)

def start_gateway():
    print("  [!] HBOS Gateway :3002 inactivo. Auto-iniciando uvicorn...")
    script = os.path.join(BASE_DIR, "hbos_unified_gateway.py")
    subprocess.Popen([sys.executable, script], cwd=BASE_DIR, creationflags=0x00000008 | 0x00000200, close_fds=True)
    time.sleep(3)
    return check_port(3002)

def main():
    t0 = time.time()
    print("=" * 70)
    print(">>> [HBOS-DIAMANTINO] PROTOCOLO DE ARRANQUE DIARIO EN SEGUNDOS <<<")
    print("=" * 70)

    # 1. Verificar / Levantar FreeLLMAPI :3001
    flm_ok = check_port(3001)
    if not flm_ok:
        flm_ok = start_freellmapi()
    print(f"  • FreeLLMAPI Daemon (:3001): {'[OK] (235 Modelos)' if flm_ok else '[FAIL]'}")

    # 2. Verificar / Levantar Gateway :3002
    gw_ok = check_port(3002)
    if not gw_ok:
        gw_ok = start_gateway()
    print(f"  • HBOS Gateway (:3002):     {'[OK] (FastAPI + /dashboard)' if gw_ok else '[FAIL]'}")

    # 3. Verificar Qdrant Cloud
    qdrant_ok, lat_q = check_qdrant()
    print(f"  • Qdrant Cloud (Vectores):   {'[OK]' if qdrant_ok else '[FAIL]'} (Latencia: {lat_q:.3f}s)")

    # 4. Verificar Redundancia Rápida
    loc = os.path.join(BASE_DIR, r"_MAESTRO\_FACTORIZACION_MAESTRA.md")
    drv = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_FACTORIZACION_MAESTRA.md"
    bak = r"c:\Users\ipane\backup_hbos\_MAESTRO\_FACTORIZACION_MAESTRA.md"
    red_ok = os.path.exists(loc) and os.path.exists(drv) and os.path.exists(bak)
    print(f"  • Triple Redundancia Física: {'[OK] (Local, Drive, Backup)' if red_ok else '[FAIL]'}")

    elapsed = time.time() - t0
    all_ok = flm_ok and gw_ok and qdrant_ok and red_ok

    print("=" * 70)
    if all_ok:
        print(f"[OK] SISTEMA OPERATIVO. Listo para trabajar en {elapsed:.2f}s.")
        print("     Dashboard activo en: http://localhost:3002/dashboard")
        print("     Marketplace activo en: http://localhost:3002/marketplace")
    else:
        print(f"[!] ALERTA: Subsistemas con incidentes. Ejecute hbos_watchdog.py para auto-reparación.")
    print("=" * 70)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
