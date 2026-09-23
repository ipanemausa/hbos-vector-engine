# -*- coding: utf-8 -*-
"""
HBOS · op=279 · AUTOSTART BIOMÉTRICO DE FREELLMAPI AL LOGON
Inicia FreeLLMAPI en modo daemon sin ventana al iniciar sesión de Windows,
verificando sesión biométrica previa o solicitando huella vía Windows Hello (Synaptics).
"""

import os
import sys
import time
import json
import socket
import subprocess
from pathlib import Path
from datetime import datetime

# Rutas del sistema HBOS
BASE_DIR = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
FREELMAPI_EXE = Path(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\FreeLLMAPI.exe")
LOG_FILE = BASE_DIR / "_AUTOSTART_BIOMETRICO.log"
AUDIT_FILE = BASE_DIR / "auth_ui_audit.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from hbos_auth_ui import HBOSAuthUI
except ImportError:
    HBOSAuthUI = None

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Error escribiendo log: {e}")

def is_port_open(port: int = 3001, host: str = "127.0.0.1", timeout: float = 1.5) -> bool:
    """Verifica si el puerto local está escuchando activamente."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except:
        return False

def wait_for_port(port: int = 3001, host: str = "127.0.0.1", max_seconds: int = 30, interval: float = 1.5) -> bool:
    """Espera activamente a que el puerto responda antes de timeout."""
    start_time = time.time()
    while (time.time() - start_time) < max_seconds:
        if is_port_open(port, host, timeout=1.0):
            return True
        time.sleep(interval)
    return False

def load_cached_token_from_audit(scope: str) -> bool:
    """Revisa si hay una autorización biométrica previa no expirada en auth_ui_audit.json."""
    if not AUDIT_FILE.exists():
        return False
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        now = time.time()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("result") == "VERIFIED":
                    exp = data.get("expires_at")
                    if exp and exp > now:
                        return True
            except:
                continue
    except Exception as e:
        log(f"Advertencia al leer auditoría biométrica: {e}")
    return False

def authorize_biometric() -> bool:
    """Verifica token vigente o solicita huella física con Windows Hello."""
    scope = "hbos_freellmapi_autostart"
    message = "HBOS: Autorizar inicio de FreeLLMAPI al iniciar sesión (Windows Hello)"
    
    # 1. Verificar si hay token vigente en auditoría
    if load_cached_token_from_audit(scope):
        log(f"[AUTH_CACHE] Token biométrico válido y vigente encontrado para {scope}.")
        return True

    # 2. Si no hay token en cache, solicitar huella interactiva
    if HBOSAuthUI is None:
        log("[WARN] HBOSAuthUI no disponible en entorno. Permitiendo arranque de contingencia.")
        return True

    try:
        log(f"[AUTH_PROMPT] Solicitando huella dactilar Windows Hello para {scope}...")
        auth = HBOSAuthUI(timeout_minutes=60)
        approved = auth.authorize(scope=scope, message=message, force=False)
        return approved
    except Exception as e:
        log(f"[AUTH_ERROR] Error al invocar Windows Hello: {e}")
        return False

def launch_freellmapi_daemon() -> bool:
    """Lanza el ejecutable de FreeLLMAPI en modo daemon sin ventana de consola."""
    if not FREELMAPI_EXE.exists():
        log(f"[FAIL] Ejecutable de FreeLLMAPI no existe en {FREELMAPI_EXE}")
        return False

    # Asegurar configuración del puerto 3001
    cfg_file = Path(os.path.expandvars(r"%APPDATA%\FreeLLMAPI\config.json"))
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("port") != 3001:
                cfg["port"] = 3001
                with open(cfg_file, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
                log("[CONFIG] Puerto fijado en 3001 en config.json")
        except Exception as e:
            log(f"[CONFIG_WARN] No se pudo actualizar config.json: {e}")

    log(f"Lanzando FreeLLMAPI daemon: {FREELMAPI_EXE}")
    try:
        # DETACHED_PROCESS (0x00000008) + CREATE_NO_WINDOW (0x08000000)
        flags = 0x08000000 | 0x00000008
        env = os.environ.copy()
        env["ELECTRON_ENABLE_LOGGING"] = "1"
        
        proc = subprocess.Popen(
            [str(FREELMAPI_EXE)],
            cwd=str(FREELMAPI_EXE.parent),
            creationflags=flags,
            env=env,
            close_fds=True
        )
        log(f"[OK] Proceso iniciado con PID: {proc.pid}")
        return True
    except Exception as e:
        log(f"[FAIL] Error iniciando FreeLLMAPI: {e}")
        return False

def main():
    log("==================================================")
    log("HBOS · AUTOSTART BIOMÉTRICO FREELLMAPI (LOGON)")
    log("==================================================")

    # 1.1. Espera de 10 segundos para estabilización de arranque del sistema
    log("Esperando 10 segundos para estabilización del sistema...")
    time.sleep(10)

    # 1.2. Verificar si :3001 ya responde
    if is_port_open(3001):
        log("[OK] Puerto :3001 ya está respondiendo activamente. No se requiere relanzamiento.")
        return 0

    log("Puerto :3001 inactivo. Procediendo con verificación biométrica...")

    # 1.4. Verificación biométrica (token o sensor Synaptics)
    if not authorize_biometric():
        log("[FAIL] Autorización biométrica denegada o cancelada. FreeLLMAPI no se iniciará.")
        return 1

    # 1.5. Lanzar FreeLLMAPI en modo daemon
    if not launch_freellmapi_daemon():
        log("[FAIL] No se pudo lanzar el ejecutable.")
        return 1

    # 1.6. Esperar hasta 30 segundos a que :3001 responda
    log("Esperando hasta 30 segundos a que :3001 esté listo...")
    if wait_for_port(3001, max_seconds=30, interval=1.5):
        log("[OK] FreeLLMAPI (:3001) respondiendo con éxito. Arranque completado.")
        return 0
    else:
        log("[FAIL] Timeout: FreeLLMAPI no respondió en el puerto :3001 tras 30 segundos.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
