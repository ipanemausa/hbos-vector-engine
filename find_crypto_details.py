# -*- coding: utf-8 -*-
import os
import re

server_path = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\server.mjs"
with open(server_path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

print("File length:", len(code))

# Buscar funciones relacionadas con encriptación / desencriptación
enc_matches = re.findall(r"(.{0,100}(?:encrypt|decrypt|aes-256-gcm|createCipheriv|createDecipheriv).{0,100})", code)
print("\n--- CRYPTO SNIPPETS ---")
for m in enc_matches[:10]:
    print("MATCH:", m.strip())

# Buscar endpoints de keys
key_endpoints = re.findall(r"(.{0,80}(?:/api/keys|/keys|router\.post|router\.get).{0,80})", code)
print("\n--- KEY ENDPOINTS ---")
for k in key_endpoints[:10]:
    print("ROUTE:", k.strip())
