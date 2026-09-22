# -*- coding: utf-8 -*-
import subprocess
import json

payload = {"model": "auto", "messages": [{"role": "user", "content": "hola"}]}
with open("chat_req.json", "w", encoding="utf-8") as f:
    json.dump(payload, f)

cmd = [
    "curl.exe", "-s", "http://127.0.0.1:3001/v1/chat/completions",
    "-H", "Authorization: Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037",
    "-H", "Content-Type: application/json",
    "-d", "@chat_req.json"
]
out = subprocess.check_output(cmd).decode("utf-8")
print("CURL OUTPUT:")
print(out)
