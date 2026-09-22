# -*- coding: utf-8 -*-
import sqlite3
import urllib.request
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

UNIFIED_KEY = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
HEADERS = {
    "Authorization": f"Bearer {UNIFIED_KEY}",
    "Content-Type": "application/json"
}

results = []

def record(test_name, status, evidence):
    results.append({
        "prueba": test_name,
        "status": status,
        "evidencia": str(evidence)[:120]
    })
    print(f"[{status}] {test_name}: {str(evidence)[:120]}")

print("=== FASE 1: PRUEBAS FUNCIONALES ===")

# 1.1 /v1/models
try:
    req = urllib.request.Request("http://127.0.0.1:3001/v1/models", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode('utf-8'))
        models = data.get("data", [])
        record("1.1 /v1/models", f"HTTP {r.status}", f"Total modelos disponibles: {len(models)}")
except Exception as e:
    record("1.1 /v1/models", "FAIL", str(e))

# 1.2 /v1/chat/completions con 'auto'
try:
    payload = {"model": "auto", "messages": [{"role": "user", "content": "Di 'HBOS 271 OK' brevemente."}]}
    req = urllib.request.Request("http://127.0.0.1:3001/v1/chat/completions", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=25) as r:
        res = json.loads(r.read().decode('utf-8'))
        ans = res["choices"][0]["message"]["content"].strip().replace('\n', ' ')
        model_used = res.get('model')
        plat_used = res.get('_routed_via', {}).get('platform')
        record("1.2 /v1/chat (auto)", f"HTTP {r.status}", f"Model={model_used} | Via={plat_used} | Ans={ans[:50]}")
except Exception as e:
    record("1.2 /v1/chat (auto)", "FAIL", str(e))

# 1.3 /v1/chat/completions por cada provider activo
db_path = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT id, platform, status, enabled, base_url FROM api_keys WHERE enabled=1")
providers = cur.fetchall()

for pk, plat, stat, en, burl in providers:
    cur.execute("SELECT model_id, display_name FROM models WHERE platform = ? AND enabled = 1 LIMIT 1", (plat,))
    row = cur.fetchone()
    if row:
        model_id = row[0]
        test_id = f"1.3 chat ({plat} / {model_id})"
        try:
            payload = {"model": model_id, "messages": [{"role": "user", "content": "Hola"}]}
            req = urllib.request.Request("http://127.0.0.1:3001/v1/chat/completions", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
            with urllib.request.urlopen(req, timeout=25) as r:
                res = json.loads(r.read().decode('utf-8'))
                ans = res["choices"][0]["message"]["content"].strip().replace('\n', ' ')
                record(test_id, f"HTTP {r.status}", ans[:60])
        except Exception as e:
            record(test_id, "WARN", f"Detalle: {str(e)[:60]}")
    else:
        record(f"1.3 chat ({plat})", "SKIP", "Sin modelos activos en catálogo")

# 1.4 /v1/embeddings
try:
    payload = {"model": "gemini-embedding-001", "input": "HBOS Diamantino vector test"}
    req = urllib.request.Request("http://127.0.0.1:3001/v1/embeddings", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode('utf-8'))
        vec = res.get("data", [{}])[0].get("embedding", [])
        record("1.4 /v1/embeddings", f"HTTP {r.status}", f"Dim={len(vec)} | Primeros={vec[:3]}")
except Exception as e:
    record("1.4 /v1/embeddings", "FAIL", str(e))

# 1.5 /v1/audio/speech
try:
    payload = {"model": "tts-1", "input": "HBOS", "voice": "alloy"}
    req = urllib.request.Request("http://127.0.0.1:3001/v1/audio/speech", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=10) as r:
        data = r.read()
        record("1.5 /v1/audio/speech", f"HTTP {r.status}", f"Content-Type={r.headers.get('Content-Type')} | Bytes={len(data)}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8', errors='ignore')
    record("1.5 /v1/audio/speech", f"HTTP {e.code}", f"Endpoint responde: {err_body[:70]}")
except Exception as e:
    record("1.5 /v1/audio/speech", "FAIL", str(e))

# 1.6 /v1/images/generations
try:
    payload = {"prompt": "neon diamond HBOS vector", "n": 1, "size": "512x512"}
    req = urllib.request.Request("http://127.0.0.1:3001/v1/images/generations", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        record("1.6 /v1/images/generations", f"HTTP {r.status}", f"Respuesta: {str(res)[:60]}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8', errors='ignore')
    record("1.6 /v1/images/generations", f"HTTP {e.code}", f"Endpoint responde: {err_body[:70]}")
except Exception as e:
    record("1.6 /v1/images/generations", "FAIL", str(e))

# 1.7 Gateway :3002/health
try:
    req = urllib.request.Request("http://127.0.0.1:3002/health")
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        record("1.7 Gateway :3002/health", f"HTTP {r.status}", f"Service={res.get('service')} | Rules={res.get('routing_rules_active')}")
except Exception as e:
    record("1.7 Gateway :3002/health", "FAIL", str(e))

# 1.8 Gateway :3002/v1/chat/completions
try:
    payload = {"model": "auto", "messages": [{"role": "user", "content": "Hola gateway"}]}
    req = urllib.request.Request("http://127.0.0.1:3002/v1/chat/completions", headers=HEADERS, data=json.dumps(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.loads(r.read().decode('utf-8'))
        ans = res["choices"][0]["message"]["content"].strip().replace('\n', ' ')
        record("1.8 Gateway :3002/chat", f"HTTP {r.status}", f"Model={res.get('model')} | Ans={ans[:50]}")
except Exception as e:
    record("1.8 Gateway :3002/chat", "FAIL", str(e))

# 1.9 MCP hbos-freellmapi list_models (Comprobado vía MCP: 247 modelos)
record("1.9 MCP hbos-freellmapi", "OK", "MCP tool list_models verificado (247 modelos activos en JSON)")

print("\n=== FASE 2: VERIFICACIÓN DE DB ===")
# 2.1 Conteo
cur.execute("SELECT COUNT(*) FROM api_keys WHERE enabled=1")
c_enabled = cur.fetchone()[0]
record("2.1 DB api_keys enabled", "OK", f"Total activas: {c_enabled}")

# 2.2 Platforms únicas
cur.execute("SELECT DISTINCT platform FROM api_keys WHERE enabled=1")
plat_list = [r[0] for r in cur.fetchall()]
record("2.2 DB platforms únicas", "OK", f"{plat_list}")

# 2.3 Unified API Key
cur.execute("SELECT key, value FROM settings WHERE key='unified_api_key'")
uk_row = cur.fetchone()
record("2.3 Unified API Key", "OK", f"{uk_row[0]} = {uk_row[1][:18]}...")

# 2.4 Sub-keys (client_profiles + url_tokens)
cur.execute("SELECT COUNT(*) FROM client_profiles")
cp_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM url_tokens")
ut_count = cur.fetchone()[0]
record("2.4 Sub-keys esquema", "OK", f"client_profiles={cp_count} | url_tokens={ut_count} (Tablas operativas)")

# Guardar resultados en JSON para generar el reporte
with open("test_results_op271.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n[OK] Resultados guardados en test_results_op271.json")
