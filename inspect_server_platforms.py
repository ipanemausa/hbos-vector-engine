# -*- coding: utf-8 -*-
import os
import re

appExtracted = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build"
server_file = os.path.join(appExtracted, "server.mjs")

with open(server_file, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

platforms = [
    "cerebras", "sail", "electronhub", "experiential", "router9", "septor",
    "clod", "speechify", "blaze", "lucidity", "logfare", "bai", "radeon",
    "nvidia", "mistral", "cohere", "cloudflare", "zhipu", "pollinations", "opencode"
]

print("=== INSPECTING PLATFORMS IN server.mjs ===")
for p in platforms:
    # search for platform definition or handler
    pattern = rf'platform === ["\']{p}["\']|platform: ["\']{p}["\']|case ["\']{p}["\']'
    matches = list(re.finditer(pattern, code))
    print(f"\nPlatform '{p}': {len(matches)} handler matches")
    for m in matches[:2]:
        start = max(0, m.start() - 100)
        end = min(len(code), m.end() + 200)
        snippet = code[start:end].replace('\n', ' ')
        print(f"   ... {snippet[:250]} ...")
