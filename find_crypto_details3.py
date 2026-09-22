# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

pos = code.find("// ../server/src/services/crypto.ts")
print("--- CRYPTO.TS BODY ---")
print(code[pos+2500:pos+5500])

print("\n--- KEYS ROUTER POST ---")
pos_keys = code.find("// ../server/src/routes/keys.ts")
pos_post = code.find('router.post("/"', pos_keys)
if pos_post == -1:
    pos_post = code.find("router.post(", pos_keys)
print(code[pos_post:pos_post+2500])
