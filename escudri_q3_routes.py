# -*- coding: utf-8 -*-
import re
import os

appExtracted = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build"
server_file = os.path.join(appExtracted, "server.mjs")
if os.path.exists(server_file):
    with open(server_file, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    routes = set(re.findall(r'[\"\'`](/(?:api|v1)/[a-zA-Z0-9_/\-]+)[\"\'`]', code))
    for r in sorted(routes)[:80]:
        print(f'  {r}')
else:
    print(f"  [!] No existe {server_file}")
