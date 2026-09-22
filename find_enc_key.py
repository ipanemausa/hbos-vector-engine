# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

pos = 0
while True:
    pos = code.find(".encryption-key", pos)
    if pos == -1:
        break
    print(f"--- MATCH .encryption-key at {pos} ---")
    print(code[pos-200:pos+1500])
    pos += 15
