# -*- coding: utf-8 -*-
import os
import re

appExtracted = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build"
server_file = os.path.join(appExtracted, "server.mjs")

with open(server_file, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

classes = [
    "PollinationsProvider", "AIHordeProvider", "SailProvider", "ElectronHubProvider",
    "ExperientialProvider", "Router9Provider", "SeptorProvider", "ClodProvider",
    "SpeechifyProvider", "BlazeProvider", "LucidityProvider", "LogfareProvider",
    "CohereProvider", "CloudflareProvider", "ZhipuProvider", "AirforceProvider"
]

for cls in classes:
    pos = code.find(f"{cls} =")
    if pos != -1:
        end = min(len(code), pos + 800)
        snippet = code[pos:end].replace('\n', ' ')
        print(f"\n=== {cls} ===")
        print(snippet[:500])
