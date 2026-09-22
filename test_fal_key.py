# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
from dotenv import dotenv_values

k = dotenv_values(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")["FAL_API_KEY"].strip('"').strip("'")
req = urllib.request.Request(
    "https://queue.fal.run/fal-ai/flux/dev",
    data=b"{}",
    headers={"Authorization": f"Key {k}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"[FAL.AI SUCCESS] HTTP {resp.status}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="ignore")
    print(f"[FAL.AI RESPONSE] HTTP {e.code}: {body[:200]}")
except Exception as e:
    print("Error:", e)
