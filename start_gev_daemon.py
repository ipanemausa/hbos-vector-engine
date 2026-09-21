"""
start_gev_daemon.py — Daemon de Frontend GEV (God's Eye View) en Puerto :4173
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=230 · Desacoplamiento por Capas (§D)
"""

import os
import sys
import http.server
import socketserver

PORT = 4173
DIRECTORY = os.path.join(os.path.dirname(__file__), "gev-app")

class GEVHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    os.chdir(os.path.dirname(__file__))
    
    # Permitir reutilización rápida de socket
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), GEVHandler) as httpd:
            print(f"[*] GEV Frontend servidor activo en http://0.0.0.0:{PORT}")
            sys.stdout.flush()
            httpd.serve_forever()
    except Exception as e:
        print(f"[!] Error iniciando GEV daemon en {PORT}: {e}")
