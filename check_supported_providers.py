# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

import re

# Buscar definición de PLATFORMS
pos_plat = code.find("var PLATFORMS =")
if pos_plat == -1:
    pos_plat = code.find("const PLATFORMS =")
if pos_plat != -1:
    print("--- PLATFORMS DEFINITION ---")
    print(code[pos_plat:pos_plat+500])

# Buscar proveedores mencionados en el código
providers_to_search = [
    "elevenlabs", "fal", "replicate", "github", "azure", 
    "cohere", "together", "sambanova", "cerebras", "cloudflare", "nvidia"
]

print("\n--- PROVIDER OCCURRENCES IN server.mjs ---")
for p in providers_to_search:
    count = len(re.findall(r"\b" + p + r"\b", code, re.IGNORECASE))
    print(f"  {p:15}: {count} occurrences")
