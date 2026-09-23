# -*- coding: utf-8 -*-
"""
HBOS · op=280 · CONFIGURAR CLAUDE EN OPENROUTER + DESHABILITAR KIRO
1. Agregar modelos claude via openrouter a FreeLLMAPI DB
2. Deshabilitar kiro (gated)
3. Verificar con la unified_api_key
4. Probar /v1/chat/completions con claude via openrouter
"""
import sqlite3
import json
import urllib.request
import urllib.error
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

FREEAPI_DB = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
ENC_KEY_FILE = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key"
UNIFIED_API_KEY = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
BASE = "http://127.0.0.1:3001"

conn = sqlite3.connect(FREEAPI_DB)
cur = conn.cursor()

# ================================================================
# PASO 1: Agregar modelos Claude vía OpenRouter
# ================================================================
print("=" * 65)
print("[1] AGREGAR MODELOS CLAUDE (openrouter) EN FREEAPI.DB")
print("=" * 65)

claude_models_or = [
    # (model_id, display_name, platform, intelligence_rank, speed_rank, size_label, context_window)
    ("anthropic/claude-3-haiku",       "Claude 3 Haiku (OpenRouter)",       "openrouter", 88, 92, "large",  200000),
    ("anthropic/claude-3-opus",        "Claude 3 Opus (OpenRouter)",        "openrouter", 96, 70, "xlarge", 200000),
    ("anthropic/claude-3-sonnet",      "Claude 3 Sonnet (OpenRouter)",      "openrouter", 93, 83, "large",  200000),
    ("anthropic/claude-3.5-haiku:latest", "Claude 3.5 Haiku Latest (OpenRouter)", "openrouter", 90, 90, "large", 200000),
]

for mid, name, plat, irank, srank, slabel, ctx in claude_models_or:
    cur.execute("SELECT id FROM models WHERE model_id=?", (mid,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO models (model_id, display_name, platform, intelligence_rank, speed_rank, size_label, context_window, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (mid, name, plat, irank, srank, slabel, ctx))
        print(f"  [ADDED] {mid}")
    else:
        cur.execute("""
            UPDATE models SET display_name=?, enabled=1, intelligence_rank=?, speed_rank=?
            WHERE model_id=?
        """, (name, irank, srank, mid))
        print(f"  [UPDATED] {mid}")

conn.commit()

# ================================================================
# PASO 2: Deshabilitar Kiro (gated) temporalmente
# ================================================================
print()
print("[2] DESHABILITAR KIRO (gated a Pro)")
cur.execute("UPDATE api_keys SET enabled=0 WHERE platform='kiro'")
cur.execute("UPDATE models SET enabled=0 WHERE platform='kiro'")
conn.commit()
print("  [OK] kiro: enabled=0 (pendiente upgrade Pro)")

# ================================================================
# PASO 3: Verificar /v1/models con unified_api_key
# ================================================================
print()
print("[3] VERIFICAR /v1/models CON UNIFIED_API_KEY")
headers_auth = {
    "Authorization": f"Bearer {UNIFIED_API_KEY}",
    "Content-Type": "application/json"
}
try:
    req = urllib.request.Request(f"{BASE}/v1/models", headers=headers_auth)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        models = data.get("data", [])
        claude_found = [m["id"] for m in models if "claude" in m.get("id", "").lower()]
        print(f"  Total modelos en FreeLLMAPI: {len(models)}")
        print(f"  Modelos Claude visibles: {claude_found}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:300]
    print(f"  HTTP {e.code}: {body}")
except Exception as e:
    print(f"  Error: {e}")

# ================================================================
# PASO 4: Probar Claude vía FreeLLMAPI con la key real
# ================================================================
print()
print("[4] TEST: /v1/chat/completions con anthropic/claude-3-haiku")
payload = json.dumps({
    "model": "anthropic/claude-3-haiku",
    "messages": [{"role": "user", "content": "Responde con exactamente: HBOS_CLAUDE_OP280_OK"}],
    "max_tokens": 30
}).encode("utf-8")
req2 = urllib.request.Request(
    f"{BASE}/v1/chat/completions",
    data=payload,
    headers=headers_auth,
    method="POST"
)
try:
    with urllib.request.urlopen(req2, timeout=30) as r:
        body = r.read().decode()
        parsed = json.loads(body)
        content = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
        model_used = parsed.get("model", "?")
        print(f"  HTTP 200 OK")
        print(f"  model_used : {model_used}")
        print(f"  response   : {content}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:500]
    print(f"  HTTP {e.code}: {body}")
except Exception as e:
    print(f"  Error: {e}")

# ================================================================
# PASO 5: Probar con 'auto'
# ================================================================
print()
print("[5] TEST: /v1/chat/completions con model='auto'")
payload2 = json.dumps({
    "model": "auto",
    "messages": [{"role": "user", "content": "Di: HBOS_AUTO_OK"}],
    "max_tokens": 20
}).encode("utf-8")
req3 = urllib.request.Request(
    f"{BASE}/v1/chat/completions",
    data=payload2,
    headers=headers_auth,
    method="POST"
)
try:
    with urllib.request.urlopen(req3, timeout=30) as r:
        body = r.read().decode()
        parsed = json.loads(body)
        content = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
        model_used = parsed.get("model", "?")
        print(f"  HTTP 200 OK | model_used={model_used} | response={content}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:500]
    print(f"  HTTP {e.code}: {body}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
print()
print("[DONE] Configuración completa.")
