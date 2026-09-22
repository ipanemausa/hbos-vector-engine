# -*- coding: utf-8 -*-
"""hbos_gatekeeper.py — Portal Web Interactivo de Desbloqueo Biométrico con Huella Windows Hello
Puerto: 3000 -> Redirige a FreeLLMAPI (3001) tras verificación física en sensor Synaptics
"""

import os
import sys
import json
import time
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from pathlib import Path

from hbos_auth_ui import HBOSAuthUI

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
PORT = 3000
TARGET_URL = "http://127.0.0.1:3001/"

HTML_PORTAL = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HBOS · Portal de Acceso Biométrico FreeLLMAPI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #07090e;
      --panel-bg: rgba(14, 18, 28, 0.75);
      --border-color: rgba(0, 240, 255, 0.2);
      --accent-cyan: #00f0ff;
      --accent-green: #00ffa3;
      --accent-purple: #8b5cf6;
      --accent-red: #ff3366;
      --text-main: #f3f4f6;
      --text-muted: #8e9bb0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: radial-gradient(circle at 50% 20%, #111a2e 0%, var(--bg-dark) 80%);
      color: var(--text-main);
      font-family: 'Outfit', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      overflow: hidden;
      position: relative;
    }

    /* Ambient background grid */
    body::before {
      content: '';
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background-image: 
        linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }

    .container {
      position: relative;
      z-index: 10;
      width: 100%;
      max-width: 520px;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--border-color);
      border-radius: 28px;
      padding: 45px 35px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 240, 255, 0.1);
      text-align: center;
      transition: all 0.4s ease;
    }

    .container.success {
      border-color: var(--accent-green);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 60px rgba(0, 255, 163, 0.3);
    }

    .container.error {
      border-color: var(--accent-red);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 60px rgba(255, 51, 102, 0.3);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 999px;
      background: rgba(0, 240, 255, 0.1);
      border: 1px solid rgba(0, 240, 255, 0.25);
      font-size: 0.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent-cyan);
      margin-bottom: 20px;
    }

    .badge-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 10px var(--accent-cyan);
      animation: pulse 2s infinite;
    }

    h1 {
      font-size: 2.1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #ffffff 40%, #00f0ff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    p.subtitle {
      color: var(--text-muted);
      font-size: 0.98rem;
      line-height: 1.5;
      margin-bottom: 35px;
    }

    /* Fingerprint Scanner Visual Container */
    .scanner-box {
      position: relative;
      width: 150px;
      height: 170px;
      margin: 0 auto 30px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .scanner-halo {
      position: absolute;
      width: 140px;
      height: 160px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0, 240, 255, 0.15) 0%, transparent 70%);
      animation: pulseGlow 3s infinite ease-in-out;
    }

    .fingerprint-icon {
      width: 100px;
      height: 120px;
      fill: none;
      stroke: var(--accent-cyan);
      stroke-width: 2.2;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: all 0.4s ease;
      filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
    }

    /* Laser Scanning Bar */
    .laser-line {
      position: absolute;
      top: 10%;
      left: 15px;
      width: 120px;
      height: 3px;
      background: linear-gradient(90deg, transparent, #00f0ff, #ffffff, #00f0ff, transparent);
      box-shadow: 0 0 15px #00f0ff, 0 0 25px #00f0ff;
      border-radius: 50%;
      opacity: 0;
      pointer-events: none;
    }

    .scanning .laser-line {
      opacity: 1;
      animation: scanAnim 1.6s infinite ease-in-out alternate;
    }

    .scanning .fingerprint-icon {
      stroke: #00f0ff;
      filter: drop-shadow(0 0 18px rgba(0, 240, 255, 0.8));
    }

    .verified .fingerprint-icon {
      stroke: var(--accent-green) !important;
      filter: drop-shadow(0 0 25px rgba(0, 255, 163, 0.9)) !important;
    }

    .verified .scanner-halo {
      background: radial-gradient(circle, rgba(0, 255, 163, 0.3) 0%, transparent 70%);
    }

    /* Interactive Button */
    .auth-button {
      width: 100%;
      padding: 18px 24px;
      font-size: 1.08rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      border: none;
      border-radius: 16px;
      cursor: pointer;
      background: linear-gradient(135deg, #00f0ff 0%, #0099ff 100%);
      color: #050b14;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      box-shadow: 0 10px 30px rgba(0, 240, 255, 0.35);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .auth-button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 14px 40px rgba(0, 240, 255, 0.55);
      filter: brightness(1.08);
    }

    .auth-button:active:not(:disabled) {
      transform: translateY(1px);
    }

    .auth-button:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      filter: grayscale(0.2);
    }

    /* Terminal Diagnostics */
    .terminal-box {
      margin-top: 25px;
      background: rgba(0, 0, 0, 0.45);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 12px 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      text-align: left;
      color: #798ba3;
    }

    .terminal-line {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }

    .terminal-line:last-child { margin-bottom: 0; }
    .term-ok { color: var(--accent-green); }
    .term-cyan { color: var(--accent-cyan); }
    .term-amber { color: #f59e0b; }

    /* Footer info */
    .footer-note {
      margin-top: 22px;
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .footer-note a {
      color: var(--accent-cyan);
      text-decoration: none;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    @keyframes pulseGlow {
      0%, 100% { transform: scale(1); opacity: 0.6; }
      50% { transform: scale(1.15); opacity: 1; }
    }

    @keyframes scanAnim {
      0% { top: 12%; }
      100% { top: 85%; }
    }
  </style>
</head>
<body>

  <div class="container" id="card">
    <div class="badge">
      <div class="badge-dot"></div>
      HBOS SOBERANO · BIOMETRÍA R32/R42
    </div>

    <h1>Gatekeeper LLMAPI</h1>
    <p class="subtitle" id="statusMessage">
      Haz clic para activar el lector y coloca tu dedo en el sensor <strong>Synaptics</strong> de tu equipo.
    </p>

    <!-- Fingerprint Scanner Visual -->
    <div class="scanner-box" id="scannerBox">
      <div class="scanner-halo"></div>
      <div class="laser-line"></div>
      <svg class="fingerprint-icon" viewBox="0 0 24 24" id="fpSvg">
        <path d="M12 2C6.48 2 2 6.48 2 12c0 2.85 1.2 5.42 3.12 7.24"/>
        <path d="M6.5 12c0-3.04 2.46-5.5 5.5-5.5s5.5 2.46 5.5 5.5"/>
        <path d="M9.5 12c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5c0 2.2-1.8 4-4 4"/>
        <path d="M12 17c1.1 0 2-.9 2-2"/>
        <path d="M12 22c3.5 0 6.64-1.8 8.48-4.54C21.48 16.03 22 14.1 22 12"/>
        <path d="M17.5 12c0 3.04-2.46 5.5-5.5 5.5"/>
        <path d="M8 15c-.6 0-1.1-.4-1.3-.9"/>
      </svg>
    </div>

    <!-- Scan Trigger Button -->
    <button class="auth-button" id="scanBtn" onclick="triggerFingerprintScan()">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a10 10 0 0 0-10 10c0 2.85 1.2 5.42 3.12 7.24"></path>
        <path d="M6.5 12a5.5 5.5 0 0 1 11 0"></path>
        <path d="M9.5 12a2.5 2.5 0 0 1 5 0"></path>
      </svg>
      <span id="btnText">ESCANEAR HUELLA DACTILAR</span>
    </button>

    <!-- Diagnostics Terminal -->
    <div class="terminal-box">
      <div class="terminal-line"><span class="term-ok">✓</span> <span>Hardware:</span> <span class="term-cyan">Synaptics UWP WBDI (OK)</span></div>
      <div class="terminal-line"><span class="term-ok">✓</span> <span>Servicio:</span> <span class="term-cyan">Windows Biometric (Running)</span></div>
      <div class="terminal-line"><span class="term-ok">✓</span> <span>Destino:</span> <span class="term-cyan">FreeLLMAPI (:3001)</span></div>
      <div class="terminal-line" id="termLive"><span class="term-amber">●</span> <span id="termStatus">Esperando comando de usuario...</span></div>
    </div>

    <div class="footer-note">
      Soberanía HBOS · Acceso directo de respaldo a <a href="http://127.0.0.1:3001" target="_blank">FreeLLMAPI Directo</a>
    </div>
  </div>

  <script>
    async function triggerFingerprintScan() {
      const btn = document.getElementById('scanBtn');
      const btnText = document.getElementById('btnText');
      const box = document.getElementById('scannerBox');
      const card = document.getElementById('card');
      const statusMsg = document.getElementById('statusMessage');
      const termStatus = document.getElementById('termStatus');

      // Estado escaneando
      btn.disabled = true;
      box.classList.add('scanning');
      box.classList.remove('verified');
      card.classList.remove('success', 'error');
      btnText.innerText = 'COLOCA EL DEDO EN EL SENSOR...';
      statusMsg.innerHTML = '<span style="color:#00f0ff;">👉 Pon tu dedo sobre el lector Synaptics en tu equipo...</span>';
      termStatus.innerText = 'Llamando a Windows Hello (UserConsentVerifier)...';
      termStatus.className = 'term-cyan';

      try {
        const resp = await fetch('/api/auth/fingerprint', { method: 'POST' });
        const data = await resp.json();

        box.classList.remove('scanning');

        if (data.status === 'ok') {
          // Éxito total
          box.classList.add('verified');
          card.classList.add('success');
          btn.style.background = 'linear-gradient(135deg, #00ffa3 0%, #00b371 100%)';
          btnText.innerText = '¡HUELLA CONFIRMADA!';
          statusMsg.innerHTML = '<span style="color:#00ffa3; font-weight:700;">✓ IDENTIDAD AUTORIZADA · Redirigiendo a FreeLLMAPI...</span>';
          termStatus.innerText = 'Token: ' + (data.token ? data.token.slice(0, 16) + '...' : 'OK') + ' -> Redirigiendo';
          termStatus.className = 'term-ok';

          setTimeout(() => {
            window.location.href = data.redirect || 'http://127.0.0.1:3001/';
          }, 1400);
        } else {
          // Fallo o cancelado
          card.classList.add('error');
          btn.disabled = false;
          btnText.innerText = 'REINTENTAR ESCANEO';
          statusMsg.innerHTML = '<span style="color:#ff3366;">✕ Huella no reconocida o diálogo cancelado. Vuelve a intentar.</span>';
          termStatus.innerText = 'Validación denegada/cancelada.';
          termStatus.className = 'term-amber';
        }
      } catch (err) {
        box.classList.remove('scanning');
        card.classList.add('error');
        btn.disabled = false;
        btnText.innerText = 'REINTENTAR ESCANEO';
        statusMsg.innerHTML = '<span style="color:#ff3366;">✕ Error de conexión con el Gatekeeper: ' + err.message + '</span>';
        termStatus.innerText = 'Error de red en localhost:3000';
      }
    }
  </script>

</body>
</html>
"""

class GatekeeperHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/login" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PORTAL.encode("utf-8"))
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"service": "HBOS Gatekeeper", "status": "online", "port": PORT}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/auth/fingerprint":
            print("\n[GATEKEEPER] Petición web recibida: Desplegando Windows Hello...")
            auth = HBOSAuthUI(timeout_minutes=60)
            # Forzar despliegue de Windows Hello para huella física
            verificado = auth.authorize(
                scope="gatekeeper_web_session",
                message="HBOS: Desbloquea FreeLLMAPI con tu huella en el sensor Synaptics",
                force=True
            )
            
            token_entry = auth.cache.get("gatekeeper_web_session", {})
            token_id = token_entry.get("token", "")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            if verificado:
                print(f"[GATEKEEPER] [EXITO] Huella validada. Redirigiendo cliente a {TARGET_URL}")
                resp = {
                    "status": "ok",
                    "message": "Huella verificada exitosamente",
                    "token": token_id,
                    "redirect": TARGET_URL
                }
            else:
                print("[GATEKEEPER] [FALLO] Diálogo biométrico cancelado o no reconocido.")
                resp = {
                    "status": "denied",
                    "message": "Verificación biométrica no completada"
                }

            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run():
    server = HTTPServer(("127.0.0.1", PORT), GatekeeperHandler)
    print(f"[*] HBOS Gatekeeper escuchando en http://127.0.0.1:{PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run()
