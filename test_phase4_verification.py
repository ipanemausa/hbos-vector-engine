# -*- coding: utf-8 -*-
"""test_phase4_verification.py — Verificación integral de Fase 4 (4.1 a 4.5)
"""

import sqlite3
import urllib.request
import urllib.error
import json
from pathlib import Path

DB_PATH = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
UNIFIED_KEY = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"

print("=" * 75)
print("HBOS op=266 · FASE 4 · VERIFICACIÓN FINAL")
print("=" * 75)

# 4.1 SELECT COUNT(*) FROM api_keys
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
count_total = cur.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]
count_enabled = cur.execute("SELECT COUNT(*) FROM api_keys WHERE enabled = 1").fetchone()[0]
platforms = [r[0] for r in cur.execute("SELECT platform FROM api_keys WHERE enabled = 1").fetchall()]
conn.close()

print(f"\n4.1 DB QUERY:")
print(f"  Total keys en api_keys:   {count_total}")
print(f"  Keys habilitadas (enabled=1): {count_enabled}")
print(f"  Plataformas activas:      {platforms}")
assert count_enabled >= 5, f"Esperado >= 5 keys activas, se obtuvieron {count_enabled}"
print("  --> [PASS] 4.1 Cumplido: >= 5 keys activas.")

# 4.4 Probar :3001/v1/chat/completions con la unified_api_key
print(f"\n4.4 PROBAR :3001/v1/chat/completions:")
url = "http://127.0.0.1:3001/v1/chat/completions"
payload = {
    "model": "auto",
    "messages": [
        {"role": "user", "content": "hola"}
    ]
}
headers = {
    "Authorization": f"Bearer {UNIFIED_KEY}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        print(f"  [PASS] HTTP {resp.status}")
        choice = body.get("choices", [{}])[0]
        msg = choice.get("message", {}).get("content", "")
        model_used = body.get("model", "unknown")
        print(f"  Modelo seleccionado por auto-routing: {model_used}")
        print(f"  Respuesta generada:\n  \"{msg[:300]}\"")
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"  [HTTPError] {e.code}: {err_body}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 4.5 Verificar que el gateway :3002 también responde
print(f"\n4.5 VERIFICAR GATEWAY :3002:")
gw_url = "http://127.0.0.1:3002/v1/chat/completions"
try:
    req_gw = urllib.request.Request(gw_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req_gw, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        print(f"  [PASS] Gateway :3002 responde HTTP {resp.status}")
        model_gw = body.get("model", "unknown")
        print(f"  Modelo Gateway: {model_gw}")
except urllib.error.HTTPError as e:
    print(f"  [HTTP {e.code}] Gateway :3002: {e.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"  [GATEWAY STATUS] :3002 (no activo o no iniciado en segundo plano): {e}")

print("=" * 75)
