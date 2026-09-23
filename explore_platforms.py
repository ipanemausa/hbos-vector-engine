# -*- coding: utf-8 -*-
"""Explorar plataformas, cadenas y alternativas de Claude en freeapi.db"""
import sqlite3
import json
import urllib.request
import urllib.error

FREEAPI_DB = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
BASE = "http://127.0.0.1:3001"

conn = sqlite3.connect(FREEAPI_DB)
cur = conn.cursor()

print("=" * 65)
print("=== API KEYS EN FREEAPI.DB ===")
cur.execute("SELECT id, platform, label, status, enabled, base_url FROM api_keys ORDER BY id")
for row in cur.fetchall():
    print(f"  ID={row[0]:2d} | {str(row[1]):15s} | {str(row[3]):9s} | enabled={row[4]} | {str(row[5] or '')[:35]}")

print()
print("=== MODELOS HABILITADOS POR PLATAFORMA ===")
cur.execute("SELECT platform, count(*) FROM models WHERE enabled=1 GROUP BY platform ORDER BY count(*) DESC")
for row in cur.fetchall():
    print(f"  {str(row[0]):15s}: {row[1]} modelos")

print()
print("=== MODELOS CLAUDE DISPONIBLES ===")
cur.execute("SELECT model_id, display_name, platform, enabled FROM models WHERE model_id LIKE '%claude%' ORDER BY platform")
for row in cur.fetchall():
    print(f"  [{row[3]}] {row[0]:45s} | {row[2]}")

print()
try:
    cur.execute("SELECT name, description FROM chains LIMIT 20")
    chains = cur.fetchall()
    print("=== CADENAS (CHAINS) ===")
    for c in chains:
        print(f"  {str(c[0]):28s}: {str(c[1] or '')[:55]}")
except Exception as e:
    print(f"(No hay tabla chains o error: {e})")

conn.close()

print()
print("=== TEST: /v1/models EN FREELLMAPI (sin auth) ===")
try:
    req = urllib.request.Request(f"{BASE}/v1/models")
    with urllib.request.urlopen(req, timeout=5) as r:
        models = json.loads(r.read().decode())
        data = models.get("data", [])
        print(f"Total modelos: {len(data)}")
        claude_models = [m["id"] for m in data if "claude" in m.get("id", "").lower()]
        print(f"Claude models: {claude_models}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:300]
    print(f"HTTP {e.code}: {body}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=== TEST: /v1/chat con 'auto' (sin auth) ===")
payload = json.dumps({
    "model": "auto",
    "messages": [{"role": "user", "content": "Say: HBOS_OK_v2"}],
    "max_tokens": 10
}).encode("utf-8")
req2 = urllib.request.Request(f"{BASE}/v1/chat/completions", data=payload,
                               headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req2, timeout=20) as r:
        body = r.read().decode()
        parsed = json.loads(body)
        content = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
        model_used = parsed.get("model", "?")
        print(f"HTTP 200 OK | model_used={model_used} | reply={content}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:400]
    print(f"HTTP {e.code}: {body}")
except Exception as e:
    print(f"Error: {e}")
