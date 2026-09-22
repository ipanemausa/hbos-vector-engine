# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

import re
matches = [m.start() for m in re.finditer(r'["\']github["\']\s*:\s*\{', code)]
print("Matches github config:", len(matches))
for m in matches:
    print("--- MATCH ---")
    print(code[m:m+600])

pos_models = code.find('platform === "github"')
if pos_models != -1:
    print("--- GITHUB PLATFORM CHECK ---")
    print(code[pos_models-100:pos_models+300])

# Buscar URL asociada a github en providers
matches_url = re.findall(r'github[^\n]{0,50}(?:https://[^\s"\']+)', code, re.IGNORECASE)
print("\n--- GITHUB URLS ---")
for u in matches_url[:5]:
    print(" ", u)
