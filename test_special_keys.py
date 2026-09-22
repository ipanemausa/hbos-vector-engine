# -*- coding: utf-8 -*-
"""test_special_keys.py — Verificación de ElevenLabs, Fal.ai, Replicate, Groq y Mistral
"""

import urllib.request
import urllib.error
import json
from dotenv import dotenv_values

env = dotenv_values(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")

print("=" * 75)
print("HBOS op=267 · FASE 1 & 2 · VERIFICACIÓN DE CLAVES Y PROVIDERS")
print("=" * 75)

# 1.1 Groq
groq_key = env.get("GROQ_API_KEY", "").strip('"').strip("'")
print(f"\n1.1 GROQ (Key: {groq_key[:8]}...{groq_key[-4:] if len(groq_key)>12 else ''}):")
try:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {groq_key}", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  [PASS] HTTP {resp.status} · Conexión válida")
except urllib.error.HTTPError as e:
    print(f"  [FAIL] HTTP {e.code} · {e.read().decode('utf-8', errors='ignore')[:150]}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 1.2 Mistral
mistral_key = env.get("MISTRAL_API_KEY", "").strip('"').strip("'")
print(f"\n1.2 MISTRAL (Key: '{mistral_key}'):")
try:
    req = urllib.request.Request(
        "https://api.mistral.ai/v1/models",
        headers={"Authorization": f"Bearer {mistral_key}", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  [PASS] HTTP {resp.status} · Conexión válida")
except urllib.error.HTTPError as e:
    print(f"  [FAIL] HTTP {e.code} · {e.read().decode('utf-8', errors='ignore')[:150]}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2.1 ElevenLabs (TTS)
eleven_key = env.get("ELEVENLABS_API_KEY", "").strip('"').strip("'")
print(f"\n2.1 ELEVENLABS (Key: {eleven_key[:8]}...{eleven_key[-4:] if len(eleven_key)>12 else ''}):")
try:
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": eleven_key, "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        sub = data.get("subscription", {})
        tier = sub.get("tier", "unknown")
        chars = sub.get("character_count", 0)
        limit = sub.get("character_limit", 0)
        print(f"  [PASS] HTTP {resp.status} · Cuenta activa: {data.get('email', 'OK')} · Tier: {tier} ({chars}/{limit} chars)")
except urllib.error.HTTPError as e:
    print(f"  [FAIL] HTTP {e.code} · {e.read().decode('utf-8', errors='ignore')[:150]}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2.2 Fal.ai (Video / Imagen)
fal_key = env.get("FAL_API_KEY", "").strip('"').strip("'")
print(f"\n2.2 FAL.AI (Key: {fal_key[:8]}...{fal_key[-4:] if len(fal_key)>12 else ''}):")
try:
    # Fal.ai API key test via REST or models endpoint
    req = urllib.request.Request(
        "https://api.fal.ai/models",
        headers={"Authorization": f"Key {fal_key}", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  [PASS] HTTP {resp.status} · Clave Fal.ai válida")
except urllib.error.HTTPError as e:
    print(f"  [HTTPError] {e.code} · {e.read().decode('utf-8', errors='ignore')[:150]}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2.3 Replicate
rep_token = env.get("REPLICATE_API_TOKEN", "").strip('"').strip("'")
print(f"\n2.3 REPLICATE (Key en .env.local: '{rep_token}'):")
if rep_token:
    try:
        req = urllib.request.Request(
            "https://api.replicate.com/v1/account",
            headers={"Authorization": f"Bearer {rep_token}", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  [PASS] HTTP {resp.status} · Cuenta: {data.get('username')}")
    except urllib.error.HTTPError as e:
        print(f"  [FAIL] HTTP {e.code} · {e.read().decode('utf-8', errors='ignore')[:150]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
else:
    print("  [NO CONFIGURADA] No existe REPLICATE_API_TOKEN en .env.local")

print("=" * 75)
