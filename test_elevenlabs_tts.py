# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import json
from dotenv import dotenv_values

k = dotenv_values(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")["ELEVENLABS_API_KEY"].strip('"').strip("'")
req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": k, "User-Agent": "Mozilla/5.0"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        voices = data.get("voices", [])
        print(f"[ELEVENLABS SUCCESS] HTTP {resp.status} · {len(voices)} voces disponibles!")
        print("Sample voices:", [v["name"] for v in voices[:4]])
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8', errors='ignore')}")
except Exception as e:
    print("Error:", e)
