# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

import re
matches = [m.start() for m in re.finditer(r'\.listen\(', code)]
print(".listen matches:", len(matches))
for m in matches:
    print("--- LISTEN AT", m, "---")
    print(code[m-100:m+500])
