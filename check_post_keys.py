# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

pos_post = code.find('keysRouter.post("/",')
if pos_post != -1:
    print("--- POST /api/keys handler ---")
    print(code[pos_post:pos_post+2000])
