# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

import re
matches = re.findall(r"app\.use\(\s*[\"']([^\"']+)[\"']", code)
print("app.use routes:", matches)

matches_chat = re.findall(r"[\"'](/[^\"']*chat/completions[^\"']*)[\"']", code)
print("chat/completions routes:", matches_chat)

matches_v1 = re.findall(r"[\"'](/v1[^\"']*)[\"']", code)
print("v1 routes:", set(matches_v1))
