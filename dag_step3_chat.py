# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

headers = {
    "Authorization": "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037",
    "Content-Type": "application/json"
}

# 1. Models
print("--- 3.2 /v1/models ---")
try:
    req = urllib.request.Request("http://127.0.0.1:3001/v1/models", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        models = data.get("data", [])
        print(f"  [OK] Modelos disponibles en API: {len(models)}")
except Exception as e:
    print(f"  [FAIL] :3001/models: {e}")

# 2. Chat
print("\n--- 3.3 /v1/chat/completions ---")
try:
    payload = {"model": "auto", "messages": [{"role": "user", "content": "hola"}]}
    req_chat = urllib.request.Request(
        "http://127.0.0.1:3001/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload).encode("utf-8")
    )
    with urllib.request.urlopen(req_chat, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"  [OK] Inferencia Exitosa (HTTP {resp.status})")
        print(f"  Modelo: {res.get('model')}")
        print(f"  Ruta: {res.get('_routed_via', {}).get('platform')}")
        ans = res["choices"][0]["message"]["content"].strip().replace("\n", " ")
        print(f"  Respuesta: {ans[:80]}")
except Exception as e:
    print(f"  [FAIL] Inferencia :3001: {e}")

# 3. Gateway :3002
print("\n--- 3.4 Gateway :3002/health ---")
try:
    req_gw = urllib.request.Request("http://127.0.0.1:3002/health")
    with urllib.request.urlopen(req_gw, timeout=10) as resp:
        res_gw = json.loads(resp.read().decode("utf-8"))
        print(f"  [OK] Gateway :3002 responde HTTP {resp.status}")
        print(f"  Servicio: {res_gw.get('service')} | Puerto: {res_gw.get('port')} | Reglas Activas: {res_gw.get('routing_rules_active')}")
except Exception as e:
    print(f"  [FAIL] Gateway :3002: {e}")
