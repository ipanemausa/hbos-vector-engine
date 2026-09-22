from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", "http://127.0.0.1:3001/")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b"<html><head><meta http-equiv='refresh' content='0;url=http://127.0.0.1:3001/'></head><body>Redirigiendo a FreeLLMAPI...</body></html>")

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 3000), RedirectHandler)
    server.serve_forever()
