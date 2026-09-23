# -*- coding: utf-8 -*-
"""
HBOS · op=280 · EXPLORAR CLAUDE EN OPENROUTER Y GITHUB
Probar si anthropic/claude-* o claude-* están disponibles free.
"""
import sqlite3
import json
import urllib.request
import urllib.error
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

FREEAPI_DB = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
ENC_KEY_FILE = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key"

# Descifrar keys
master_key_hex = open(ENC_KEY_FILE).read().strip()
key_bytes = bytes.fromhex(master_key_hex)
aesgcm = AESGCM(key_bytes)

conn = sqlite3.connect(FREEAPI_DB)
cur = conn.cursor()

def decrypt_platform(platform):
    cur.execute("SELECT encrypted_key, iv, auth_tag FROM api_keys WHERE platform=?", (platform,))
    row = cur.fetchone()
    if not row:
        return None
    enc, iv_hex, tag_hex = row
    ct = bytes.fromhex(enc) + bytes.fromhex(tag_hex)
    iv = bytes.fromhex(iv_hex)
    return aesgcm.decrypt(iv, ct, None).decode("utf-8")

OR_KEY = decrypt_platform("openrouter")
GH_KEY = decrypt_platform("github")
HF_KEY = decrypt_platform("huggingface")

print(f"OpenRouter key: {OR_KEY[:12]}... (len={len(OR_KEY)})")
print(f"GitHub key: {GH_KEY[:12]}... (len={len(GH_KEY)})")
print(f"HuggingFace key: {HF_KEY[:12]}... (len={len(HF_KEY)})")
print()

# ================================================================
# TEST 1: OpenRouter - buscar Claude free
# ================================================================
print("=" * 65)
print("TEST 1: OpenRouter /models - filtrar claude")
print("=" * 65)
try:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
        models = data.get("data", [])
        claude_models = [m for m in models if "claude" in m.get("id", "").lower()]
        print(f"Total modelos en OpenRouter: {len(models)}")
        print(f"Modelos claude encontrados: {len(claude_models)}")
        for m in claude_models[:15]:
            pricing = m.get("pricing", {})
            prompt_cost = pricing.get("prompt", "?")
            is_free = str(m.get("id", "")).endswith(":free") or prompt_cost == "0"
            print(f"  {'[FREE]' if is_free else '[PAID]':7s} {m['id']}")
except Exception as e:
    print(f"Error OpenRouter models: {e}")

print()

# ================================================================
# TEST 2: OpenRouter - probar claude-3.5-sonnet
# ================================================================
print("=" * 65)
print("TEST 2: OpenRouter - POST claude-3.5-sonnet")
print("=" * 65)
for model_id in ["anthropic/claude-3.5-haiku", "anthropic/claude-3-haiku", "anthropic/claude-3.5-sonnet"]:
    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "Say: HBOS_CLAUDE_OK"}],
        "max_tokens": 20
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OR_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hbos.local",
            "X-Title": "HBOS"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            parsed = json.loads(body)
            content = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"  [{model_id}] HTTP 200: {content}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"  [{model_id}] HTTP {e.code}: {body}")
    except Exception as e:
        print(f"  [{model_id}] Error: {e}")

print()

# ================================================================
# TEST 3: GitHub Models - listar y probar claude
# ================================================================
print("=" * 65)
print("TEST 3: GitHub Models /models")
print("=" * 65)
try:
    req = urllib.request.Request(
        "https://models.github.ai/inference/v1/models",
        headers={"Authorization": f"Bearer {GH_KEY}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
        models = data.get("data", [])
        claude_models = [m for m in models if "claude" in m.get("id", "").lower()]
        print(f"Total GitHub Models: {len(models)}")
        print(f"Claude models en GitHub: {len(claude_models)}")
        for m in claude_models[:10]:
            print(f"  {m['id']}")
        if not claude_models:
            # Mostrar todos los disponibles
            print("  Primeros 20 modelos disponibles en GitHub:")
            for m in models[:20]:
                print(f"    {m.get('id', m.get('name', '?'))}")
except Exception as e:
    print(f"Error GitHub Models: {e}")

print()

# ================================================================
# TEST 4: HuggingFace - modelos claude
# ================================================================
print("=" * 65)
print("TEST 4: HuggingFace - modelos claude disponibles")
print("=" * 65)
cur.execute("SELECT model_id, display_name FROM models WHERE platform='huggingface' AND model_id LIKE '%claude%' AND enabled=1")
hf_claude = cur.fetchall()
print(f"Claude models en HuggingFace DB: {len(hf_claude)}")

# También buscar modelos de razonamiento disponibles en HF
print()
print("TOP modelos HuggingFace disponibles:")
cur.execute("SELECT model_id FROM models WHERE platform='huggingface' AND enabled=1 ORDER BY intelligence_rank DESC NULLS LAST LIMIT 15")
for row in cur.fetchall():
    print(f"  {row[0]}")

conn.close()
print()
print("[DONE] Exploración completa.")
