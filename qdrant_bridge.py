import http.server
import socketserver
import os
import socket
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

DNS_MAP = {'38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io': '34.186.107.230'}
_orig_gai = socket.getaddrinfo
socket.getaddrinfo = lambda h, p, *a, **kw: _orig_gai(DNS_MAP.get(h, h), p, *a, **kw)

TARGET_URL = (os.getenv("QDRANT_URL") or "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io:6333").rstrip('/')
API_KEY = os.getenv("QDRANT_API_KEY", "")

class QdrantProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silent logging

    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")

    def do_PUT(self):
        self._proxy("PUT")

    def do_DELETE(self):
        self._proxy("DELETE")

    def do_PATCH(self):
        self._proxy("PATCH")

    def _proxy(self, method):
        target = f"{TARGET_URL}{self.path}"
        headers = {"api-key": API_KEY}
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        if "Content-Type" in self.headers:
            headers["Content-Type"] = self.headers["Content-Type"]

        try:
            resp = requests.request(method, target, headers=headers, data=body, timeout=30)
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() in ["content-type", "content-length"]:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))

if __name__ == "__main__":
    PORT = 6333
    with socketserver.TCPServer(("127.0.0.1", PORT), QdrantProxyHandler) as httpd:
        httpd.serve_forever()
