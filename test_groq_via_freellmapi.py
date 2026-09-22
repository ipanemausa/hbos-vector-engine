# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:3001/v1/chat/completions"
headers = {
    "Authorization": "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037",
    "Content-Type": "application/json"
}

# Probamos modelos disponibles de Groq en FreeLLMAPI
models_to_test = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "auto"]

for m in models_to_test:
    payload = {"model": m, "messages": [{"role": "user", "content": "hola en 3 palabras"}]}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ans = data["choices"][0]["message"]["content"].strip().replace("\n", " ")
            routed = data.get("model", "?")
            via = data.get("_routed_via", {})
            print(f"[PASS] Solicitado: {m:25} | Enrutado a: {routed:25} | Platform: {via.get('platform')} -> {ans[:60]}...")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {m:25}: {e.read().decode('utf-8', errors='ignore')[:150]}")
    except Exception as e:
        print(f"[ERROR] {m:25}: {e}")
