# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import json
from dotenv import dotenv_values

env = dotenv_values(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
k = env.get("GROQ_API_KEY", "").strip('"').strip("'")

target_model = "qwen/qwen3.8-27b"
print(f"Probando chat completion con Groq: {target_model}")
req_chat = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    data=json.dumps({"model": target_model, "messages": [{"role": "user", "content": "hola en una palabra"}]}).encode("utf-8")
)
try:
    with urllib.request.urlopen(req_chat, timeout=20) as c_resp:
        c_data = json.loads(c_resp.read().decode("utf-8"))
        print("[GROQ INFERENCE VERIFIED]")
        print("  Model:", c_data.get("model"))
        print("  Answer:", c_data["choices"][0]["message"]["content"])
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8', errors='ignore')}")
except Exception as e:
    print("Error:", e)
