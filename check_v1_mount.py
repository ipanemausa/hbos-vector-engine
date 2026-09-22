# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

import re
matches = [m.start() for m in re.finditer(r'app\.use\(\s*["\']\/v1["\']', code)]
print("app.use('/v1') occurrences:", len(matches))
for m in matches:
    print("--- MATCH AT", m, "---")
    print(code[m-50:m+400])

print("\n--- chat/completions inside server.mjs ---")
matches_chat = [m.start() for m in re.finditer(r'post\(\s*["\']\/chat\/completions["\']', code)]
for m in matches_chat:
    print("--- CHAT ROUTE AT", m, "---")
    print(code[m-50:m+400])
