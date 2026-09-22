# -*- coding: utf-8 -*-
"""solicitar_huella.py — Despliegue interactivo directo de Windows Hello para huella dactilar Synaptics
"""
import sys
import webbrowser
from hbos_auth_ui import HBOSAuthUI

def main():
    print("=" * 70)
    print(">>> HBOS · VALIDACIÓN BIOMÉTRICA CON HUELLA DACTILAR WINDOWS HELLO <<<")
    print("=" * 70)
    print("\nDesplegando diálogo de seguridad del sistema operativo...")
    print(">>> COLOCA TU DEDO EN EL SENSOR SYNAPTICS EN TU TECLADO O CHASIS <<<\n")
    sys.stdout.flush()

    auth = HBOSAuthUI(timeout_minutes=60)
    # force=True para que siempre muestre la ventana emergente de Windows Hello
    verificado = auth.authorize(
        scope="llmapi_user_verification",
        message="HBOS: Coloca tu dedo en el sensor de huella Synaptics para autorizar LLMAPI",
        force=True
    )

    if verificado:
        print("\n" + "=" * 70)
        print("¡HUELLA DACTILAR CONFIRMADA Y AUTORIZADA EXITOSAMENTE!")
        print("Acceso soberano concedido. Abriendo FreeLLMAPI...")
        print("=" * 70)
        try:
            webbrowser.open("http://127.0.0.1:3001/")
        except Exception:
            pass
    else:
        print("\n" + "=" * 70)
        print("[!] No se detectó la huella o el diálogo fue cancelado.")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
