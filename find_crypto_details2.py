# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Buscar la sección de ../server/src/services/crypto.ts o similar
import re
pos = code.find("// ../server/src/services/crypto.ts")
if pos == -1:
    pos = code.find("crypto.ts")

if pos != -1:
    print("Found crypto.ts at position:", pos)
    print(code[pos:pos+2500])
else:
    print("crypto.ts not found directly, searching for encryptKey...")
    pos2 = code.find("function encryptKey(")
    if pos2 == -1:
        pos2 = code.find("encryptKey =")
    if pos2 != -1:
        print("Found encryptKey around:", code[pos2-100:pos2+1000])
    else:
        # buscar "aes-256-gcm"
        idx = 0
        while True:
            idx = code.find("aes-256-gcm", idx)
            if idx == -1:
                break
            print(f"--- MATCH at {idx} ---")
            print(code[idx-100:idx+300])
            idx += 11

print("\n--- ROUTES IN keys.ts ---")
pos_routes = code.find("// ../server/src/routes/keys.ts")
if pos_routes != -1:
    print(code[pos_routes:pos_routes+3000])
