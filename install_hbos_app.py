# -*- coding: utf-8 -*-
"""install_hbos_app.py — Instalador Local de FreeLLMAPI en PC con Biometría y Email Sombrilla
Gobernanza HBOS · op=264
"""

import os
import sys
import shutil
import sqlite3
import subprocess
from pathlib import Path

SOURCE_DIR = Path(r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app")
LOCAL_INSTALL_DIR = Path(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI")
DESKTOP_DIR = Path(os.path.expanduser(r"~\Desktop"))
START_MENU_DIR = Path(os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"))
DB_PATH = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
SOMBRIL_EMAIL = "ipanemamarketingusa@gmail.com"

def step1_copy_binaries():
    print(f"[PASO 1] Instalando archivos en disco local: {LOCAL_INSTALL_DIR}...")
    LOCAL_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copiar con robocopy para velocidad y preservar estructura
    cmd = f'robocopy "{SOURCE_DIR}" "{LOCAL_INSTALL_DIR}" /E /NFL /NDL /NJH /NJS /nc /ns /np'
    res = subprocess.run(cmd, shell=True)
    # Robocopy return codes < 8 indicate success
    if res.returncode < 8:
        print(f"[OK] Binarios instalados exitosamente en {LOCAL_INSTALL_DIR}")
    else:
        print(f"[WARN] Robocopy retorno codigo {res.returncode}, verificando exe...")
    
    exe = LOCAL_INSTALL_DIR / "FreeLLMAPI.exe"
    if exe.exists():
        print(f"[OK] Ejecutable verificado: {exe} ({exe.stat().st_size / (1024*1024):.1f} MB)")
    else:
        raise RuntimeError(f"No se encontro el ejecutable en {exe}")

def step2_update_database():
    print(f"\n[PASO 2] Configurando email sombrilla en base de datos: {DB_PATH}...")
    if not DB_PATH.exists():
        print(f"[!] No existe la base de datos aun en {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Verificar usuario actual
    cur.execute("SELECT id, email FROM users")
    users = cur.fetchall()
    print(f"[*] Usuarios actuales: {users}")
    
    if users:
        cur.execute("UPDATE users SET email = ? WHERE id = ?", (SOMBRIL_EMAIL, users[0][0]))
        conn.commit()
        print(f"[OK] Usuario ID {users[0][0]} actualizado a: {SOMBRIL_EMAIL}")
    else:
        print("[*] No habia usuarios previos.")
    
    cur.execute("SELECT id, email FROM users")
    print(f"[OK] Usuarios tras actualizacion: {cur.fetchall()}")
    conn.close()

def step3_create_shortcuts(launcher_path):
    print(f"\n[PASO 3] Creando accesos directos en Escritorio y Menu Inicio...")
    ico_path = LOCAL_INSTALL_DIR / "FreeLLMAPI.exe"
    
    shortcuts = [
        (DESKTOP_DIR / "FreeLLMAPI (HBOS Soberano).lnk", "FreeLLMAPI · Ecosistema HBOS Soberano"),
        (START_MENU_DIR / "FreeLLMAPI (HBOS Soberano).lnk", "FreeLLMAPI · Ecosistema HBOS Soberano")
    ]
    
    # Pythonw launcher command
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = sys.executable
        
    for lnk_path, desc in shortcuts:
        ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{lnk_path}")
$Shortcut.TargetPath = "{pythonw_exe}"
$Shortcut.Arguments = '"{launcher_path}"'
$Shortcut.WorkingDirectory = "{launcher_path.parent}"
$Shortcut.IconLocation = "{ico_path},0"
$Shortcut.Description = "{desc}"
$Shortcut.Save()
"""
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
        if lnk_path.exists():
            print(f"[OK] Acceso directo creado: {lnk_path}")
        else:
            print(f"[!] Error creando {lnk_path}: {res.stderr}")

if __name__ == "__main__":
    step1_copy_binaries()
    step2_update_database()
    base_dir = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
    launcher = base_dir / "hbos_app_launcher.pyw"
    step3_create_shortcuts(launcher)
    print("\n[FIN INSTALACION LOCAL] Todo preparado exitosamente.")
