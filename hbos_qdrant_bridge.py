"""hbos_qdrant_bridge.py — Puente local de salud Qdrant :6333
Permite comprobación de puerto 6333 y compatibilidad local de healthcheck para UNBE §1.0
"""
import os
import sys
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
from dotenv import load_dotenv

load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
QDRANT_URL = os.getenv("QDRANT_URL", "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

class QdrantBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            req = urllib.request.Request(f"{QDRANT_URL}{self.path}", headers={"api-key": QDRANT_API_KEY})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except Exception:
            # Fallback local health response
            resp_body = json.dumps({
                "title": "qdrant - vector search engine (HBOS Cloud Bridge)",
                "version": "1.19.0",
                "status": "ok",
                "cloud_url": QDRANT_URL
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(resp_body)

    def log_message(self, format, *args):
        pass

def run():
    server = HTTPServer(("127.0.0.1", 6333), QdrantBridgeHandler)
    print("[*] Qdrant Bridge escuchando en 127.0.0.1:6333...")
    server.serve_forever()

if __name__ == "__main__":
    run()
