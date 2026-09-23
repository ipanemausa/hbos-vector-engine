# -*- coding: utf-8 -*-
"""Verificar descifrado de Kiro token en freeapi.db y probar contra la API"""
import sqlite3
import json
import urllib.request
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

FREEAPI_DB = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
ENC_KEY_FILE = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key")
KIRO_DB = Path(r"C:\Users\ipane\AppData\Local\Kiro-Cli\data.sqlite3")

print("=== VERIFICAR CIFRADO/DESCIFRADO ===")
master_key_hex = ENC_KEY_FILE.read_text().strip()
key_bytes = bytes.fromhex(master_key_hex)
aesgcm = AESGCM(key_bytes)

conn = sqlite3.connect(str(FREEAPI_DB))
cur = conn.cursor()
cur.execute("SELECT encrypted_key, iv, auth_tag, base_url, status FROM api_keys WHERE platform='kiro'")
row = cur.fetchone()
conn.close()
enc_key, iv_hex, auth_tag_hex, base_url, status = row
print(f"status: {status} | base_url: {base_url}")
print(f"enc_key len: {len(enc_key)} | iv: {iv_hex[:8]}... | tag: {auth_tag_hex[:8]}...")

# Descifrar - formato: ct + tag (como en encrypt)
ct_bytes = bytes.fromhex(enc_key)
tag_bytes = bytes.fromhex(auth_tag_hex)
iv_bytes = bytes.fromhex(iv_hex)
ct_with_tag = ct_bytes + tag_bytes  # AESGCM decrypt espera ct||tag
try:
    decrypted = aesgcm.decrypt(iv_bytes, ct_with_tag, None)
    plain = decrypted.decode("utf-8")
    print(f"[DECRYPT OK] {plain[:15]}...{plain[-8:]}")
except Exception as e:
    print(f"[DECRYPT ERROR] {e}")
    exit(1)

# Comparar con token original
conn2 = sqlite3.connect(str(KIRO_DB))
cur2 = conn2.cursor()
cur2.execute("SELECT value FROM auth_kv WHERE key='kirocli:social:token'")
kiro_val = json.loads(cur2.fetchone()[0])
conn2.close()
orig = kiro_val["access_token"]
print(f"[MATCH] {plain == orig} — Original: {orig[:15]}...{orig[-8:]}")

print("\n=== PROBAR TOKEN DIRECTO vs CODEWHISPERER ===")
# El access_token de Kiro es para AWS CodeWhisperer, no OpenAI.
# Probar si FreeLLMAPI tiene bridge configurado o si usa base_url
print(f"base_url de kiro en freeapi.db: {base_url}")
print("Si base_url='http://127.0.0.1:3005/v1', necesita kiro_bridge corriendo en :3005")
print("Si base_url=NULL o 'https://api.kiro.dev/v1', intenta llamar a la API de Kiro directamente")

print("\n=== PROBAR ENDPOINT KIRO BRIDGE :3005 ===")
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(2)
    result = s.connect_ex(("127.0.0.1", 3005))
    print(f"Puerto 3005: {'ABIERTO' if result == 0 else 'CERRADO (bridge no activo)'}")

print("\n=== MODELOS DISPONIBLES EN FREELLMAPI ===")
try:
    req = urllib.request.Request("http://127.0.0.1:3001/v1/models")
    with urllib.request.urlopen(req, timeout=5) as r:
        models = json.loads(r.read().decode())
        kiro_models = [m for m in models.get("data", []) if "kiro" in m.get("id", "").lower()]
        total = len(models.get("data", []))
        print(f"Total modelos: {total}")
        print(f"Modelos kiro: {kiro_models}")
except Exception as e:
    print(f"Error: {e}")
