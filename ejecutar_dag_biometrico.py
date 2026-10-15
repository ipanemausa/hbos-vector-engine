# -*- coding: utf-8 -*-
"""
ejecutar_dag_biometrico.py — Validación biométrica nativa Windows Hello (Huella Synaptics)
y ejecución inmediata del Master DAG v7.0
"""
import sys
import subprocess
from hbos_auth_ui import HBOSAuthUI

def main():
    print("=" * 75)
    print(">>> HBOS: VALIDACIÓN BIOMÉTRICA CON HUELLA DACTILAR WINDOWS HELLO <<<")
    print("=" * 75)

    auth = HBOSAuthUI(timeout_minutes=60)
    # Si el token ya fue validado en los últimos 60 minutos, lo usa directamente; si no, pide huella
    verificado = auth.authorize(
        scope="master_dag_v7",
        message="HBOS: Coloca tu dedo en el sensor Synaptics para autorizar Master DAG v7.0",
        force=False
    )

    if verificado:
        print("\n" + "=" * 75)
        print("¡AUTORIZACIÓN BIOMÉTRICA ACTIVA Y CONFIRMADA!")
        print("Iniciando ejecución de los 7 Protocolos del Master DAG v7.0...")
        print("=" * 75 + "\n")
        sys.stdout.flush()

        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", "C:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine\\Master_DAG_v7.ps1"
        ]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    else:
        print("\n" + "=" * 75)
        print("[!] No se detectó la huella o el diálogo biométrico fue cancelado.")
        print("=" * 75)
        sys.exit(1)

if __name__ == "__main__":
    main()
