# -*- coding: utf-8 -*-
import sqlite3
import os
import json
import requests

db_path = os.path.expandvars(r"%APPDATA%\FreeLLMAPI\freeapi.db")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cur = conn.cursor()

# 1.1 api_keys kiro
cur.execute("SELECT id, platform, label, status, enabled, created_at FROM api_keys WHERE platform='kiro'")
row1 = cur.fetchone()
print("1.1 api_keys kiro row:", row1)

cur.execute("SELECT id, length(encrypted_key), length(iv), length(auth_tag), last_health_error FROM api_keys WHERE platform='kiro'")
row2 = cur.fetchone()
print("1.1 key lengths (id, len(enc), len(iv), len(tag), error):", row2)
conn.close()

# 1.2 kiro_config.json
cfg_path = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\kiro_config.json"
with open(cfg_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)
print("1.2 kiro_config.json:", cfg)

# 1.3 /v1/models
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
}
r_m = requests.get("http://127.0.0.1:3001/v1/models", headers=headers, timeout=5)
kiro_models = [m["id"] for m in r_m.json().get("data", []) if "kiro" in m["id"]]
print("1.3 kiro models in /v1/models:", kiro_models)

# 1.4 /v1/chat/completions model='kiro/claude-opus'
r_c = requests.post(
    "http://127.0.0.1:3001/v1/chat/completions",
    headers=headers,
    json={"model": "kiro/claude-opus", "messages": [{"role": "user", "content": "Test"}]},
    timeout=5
)
print("1.4 chat completions status:", r_c.status_code)
print("1.4 chat completions response:", r_c.text[:250])
