# -*- coding: utf-8 -*-
"""test_phase1_keys.py — Verificación de las 6 API keys contra sus endpoints oficiales reales
"""

import urllib.request
import urllib.error
import json
from dotenv import dotenv_values

env = dotenv_values(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")

keys = {
    "openrouter": env.get("OPENROUTER_API_KEY", "").strip('"').strip("'"),
    "dashscope": env.get("DASHSCOPE_API_KEY", "").strip('"').strip("'"),
    "gemini": env.get("GEMINI_API_KEY", "").strip('"').strip("'"),
    "groq": env.get("GROQ_API_KEY", "").strip('"').strip("'"),
    "mistral": env.get("MISTRAL_API_KEY", "").strip('"').strip("'"),
    "huggingface": env.get("HF_API_TOKEN", "").strip('"').strip("'")
}

print("=" * 70)
print("1.1 EXTRACCIÓN DE KEYS DESDE .env.local")
print("=" * 70)
for k, v in keys.items():
    masked = v[:8] + "..." + v[-4:] if len(v) > 12 else f"(longitud {len(v)}: '{v}')"
    print(f"  {k:15}: {masked}")

print("\n" + "=" * 70)
print("1.2 VERIFICACIÓN DE CADA KEY CONTRA SU ENDPOINT REAL")
print("=" * 70)

results = {}

# 1. OpenRouter: GET https://openrouter.ai/api/v1/models (con Bearer)
try:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {keys['openrouter']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        count = len(data.get("data", []))
        print(f"  [PASS] OpenRouter: HTTP {resp.status} · {count} modelos disponibles")
        results["openrouter"] = {"status": "PASS", "code": resp.status, "desc": f"{count} modelos"}
except urllib.error.HTTPError as e:
    print(f"  [FAIL] OpenRouter: HTTP {e.code} · {e.read().decode()[:150]}")
    results["openrouter"] = {"status": "FAIL", "code": e.code, "desc": str(e)}
except Exception as e:
    print(f"  [ERROR] OpenRouter: {e}")
    results["openrouter"] = {"status": "ERROR", "code": 0, "desc": str(e)}

# 2. DashScope: GET https://dashscope-intl.aliyuncs.com/api/v1/models
try:
    req = urllib.request.Request(
        "https://dashscope-intl.aliyuncs.com/api/v1/models",
        headers={"Authorization": f"Bearer {keys['dashscope']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  [PASS] DashScope:  HTTP {resp.status} · Conexión válida")
        results["dashscope"] = {"status": "PASS", "code": resp.status, "desc": "OK"}
except urllib.error.HTTPError as e:
    print(f"  [FAIL] DashScope:  HTTP {e.code} · {e.read().decode()[:150]}")
    results["dashscope"] = {"status": "FAIL", "code": e.code, "desc": str(e)}
except Exception as e:
    print(f"  [ERROR] DashScope:  {e}")
    results["dashscope"] = {"status": "ERROR", "code": 0, "desc": str(e)}

# 3. Gemini: GET https://generativelanguage.googleapis.com/v1beta/models?key=KEY
try:
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={keys['gemini']}"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        count = len(data.get("models", []))
        print(f"  [PASS] Gemini:     HTTP {resp.status} · {count} modelos disponibles")
        results["gemini"] = {"status": "PASS", "code": resp.status, "desc": f"{count} modelos"}
except urllib.error.HTTPError as e:
    body = e.read().decode()[:150]
    print(f"  [FAIL] Gemini:     HTTP {e.code} · {body}")
    results["gemini"] = {"status": "FAIL", "code": e.code, "desc": body}
except Exception as e:
    print(f"  [ERROR] Gemini:     {e}")
    results["gemini"] = {"status": "ERROR", "code": 0, "desc": str(e)}

# 4. Groq: GET https://api.groq.com/openai/v1/models (con Bearer)
try:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {keys['groq']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        count = len(data.get("data", []))
        print(f"  [PASS] Groq:       HTTP {resp.status} · {count} modelos disponibles")
        results["groq"] = {"status": "PASS", "code": resp.status, "desc": f"{count} modelos"}
except urllib.error.HTTPError as e:
    body = e.read().decode()[:150]
    print(f"  [FAIL] Groq:       HTTP {e.code} · {body}")
    results["groq"] = {"status": "FAIL", "code": e.code, "desc": body}
except Exception as e:
    print(f"  [ERROR] Groq:       {e}")
    results["groq"] = {"status": "ERROR", "code": 0, "desc": str(e)}

# 5. Mistral: GET https://api.mistral.ai/v1/models (con Bearer)
try:
    req = urllib.request.Request(
        "https://api.mistral.ai/v1/models",
        headers={"Authorization": f"Bearer {keys['mistral']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        count = len(data.get("data", []))
        print(f"  [PASS] Mistral:    HTTP {resp.status} · {count} modelos disponibles")
        results["mistral"] = {"status": "PASS", "code": resp.status, "desc": f"{count} modelos"}
except urllib.error.HTTPError as e:
    body = e.read().decode()[:150]
    print(f"  [FAIL] Mistral:    HTTP {e.code} · {body}")
    results["mistral"] = {"status": "FAIL", "code": e.code, "desc": body}
except Exception as e:
    print(f"  [ERROR] Mistral:    {e}")
    results["mistral"] = {"status": "ERROR", "code": 0, "desc": str(e)}

# 6. HuggingFace: GET https://huggingface.co/api/models?limit=1 (con Bearer)
try:
    req = urllib.request.Request(
        "https://huggingface.co/api/models?limit=1",
        headers={"Authorization": f"Bearer {keys['huggingface']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  [PASS] HuggingFace: HTTP {resp.status} · Token válido")
        results["huggingface"] = {"status": "PASS", "code": resp.status, "desc": "OK"}
except urllib.error.HTTPError as e:
    body = e.read().decode()[:150]
    print(f"  [FAIL] HuggingFace: HTTP {e.code} · {body}")
    results["huggingface"] = {"status": "FAIL", "code": e.code, "desc": body}
except Exception as e:
    print(f"  [ERROR] HuggingFace: {e}")
    results["huggingface"] = {"status": "ERROR", "code": 0, "desc": str(e)}

print("=" * 70)
