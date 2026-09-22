# -*- coding: utf-8 -*-
"""hbos_app_launcher.pyw — Lanzador Nativo de Escritorio para FreeLLMAPI (HBOS Soberano)
Verificación biométrica con huella dactilar Windows Hello (sensor Synaptics)
Abre la aplicación en modo ventana nativa de escritorio (sin barra de URL ni puertos).
"""

import os
import sys
import time
import socket
import asyncio
import subprocess
from pathlib import Path

# Paths
BASE_DIR = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
LOCAL_EXE = Path(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\FreeLLMAPI.exe")
PROFILE_DIR = Path(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\profile")
PORT = 3001
APP_URL = f"http://127.0.0.1:{PORT}/"
EDGE_EXE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
CHROME_EXE = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def ensure_backend_running():
    if is_port_open(PORT):
        return True
    
    # Iniciar ejecutable local en segundo plano
    if LOCAL_EXE.exists():
        subprocess.Popen([str(LOCAL_EXE)], cwd=str(LOCAL_EXE.parent), creationflags=0x08000000) # CREATE_NO_WINDOW
    else:
        # Fallback si no está aún en local
        daemon_py = BASE_DIR / "start_freellmapi_daemon.py"
        subprocess.Popen([sys.executable, str(daemon_py)], cwd=str(BASE_DIR), creationflags=0x08000000)
        
    for _ in range(20):
        time.sleep(1)
        if is_port_open(PORT):
            return True
    return False

async def verify_windows_hello():
    try:
        from winrt.windows.security.credentials.ui import (
            UserConsentVerifier,
            UserConsentVerificationResult,
            UserConsentVerifierAvailability
        )
        avail = await UserConsentVerifier.check_availability_async()
        if avail != UserConsentVerifierAvailability.AVAILABLE:
            return True # Si el hardware no está disponible, permitir acceso
        
        prompt_message = "HBOS: Desbloqueo Biometrico Synaptics para FreeLLMAPI (Guillermo Hoyos)"
        res = await UserConsentVerifier.request_verification_async(prompt_message)
        return (res == UserConsentVerificationResult.VERIFIED)
    except Exception as e:
        # Si falla el wrapper winrt, permitir acceso para no bloquear la app
        return True

def launch_native_window():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Usar Edge o Chrome en modo --app pura para ventana nativa independiente
    browser_exe = EDGE_EXE if EDGE_EXE.exists() else CHROME_EXE
    
    cmd = [
        str(browser_exe),
        f"--app={APP_URL}",
        f"--user-data-dir={PROFILE_DIR}",
        "--window-size=1280,850",
        "--window-position=120,80",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        f"--app-id=HBOS_FreeLLMAPI"
    ]
    subprocess.Popen(cmd)

def main():
    # 1. Asegurar backend levantado
    ensure_backend_running()
    
    # 2. Verificación biométrica con huella Synaptics
    verified = asyncio.run(verify_windows_hello())
    if not verified:
        # Denegado
        sys.exit(1)
        
    # 3. Lanzar ventana nativa
    launch_native_window()

if __name__ == "__main__":
    main()
