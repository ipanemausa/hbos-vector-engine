# -*- coding: utf-8 -*-
import os

appExtracted = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build"
server_file = os.path.join(appExtracted, "server.mjs")
if os.path.exists(server_file):
    with open(server_file, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    for pattern in ['var PLATFORMS =', 'PLATFORMS =', 'const PLATFORMS =']:
        pos = code.find(pattern)
        if pos != -1:
            end = code.find('];', pos)
            if end != -1:
                print(code[pos:end+2][:5000])
            break
else:
    print(f"  [!] No existe {server_file}")
