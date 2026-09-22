# -*- coding: utf-8 -*-
import urllib.request
import json

def test_model(model_name):
    url = "http://127.0.0.1:3001/v1/chat/completions"
    headers = {
        "Authorization": "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037",
        "Content-Type": "application/json"
    }
    payload = {"model": model_name, "messages": [{"role": "user", "content": "hola"}]}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ans = data["choices"][0]["message"]["content"].strip().replace("\n", " ")
            routed = data.get("model", "?")
            print(f"  [PASS] {model_name:25} -> {routed:20} : {ans[:60]}...")
            return True
    except Exception as e:
        print(f"  [FAIL] {model_name:25} -> {e}")
        return False

print("=== PROBANDO MODELOS EN FREELLMAPI :3001 ===")
for m in ["auto", "gemini-2.5-flash", "fusion"]:
    test_model(m)
