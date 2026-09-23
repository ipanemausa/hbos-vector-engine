# -*- coding: utf-8 -*-
"""Descifrar API keys de OpenRouter y GitHub, inspeccionar tablas de FreeLLMAPI"""
import sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

FREEAPI_DB = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
ENC_KEY_FILE = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key"

master_key_hex = open(ENC_KEY_FILE).read().strip()
key_bytes = bytes.fromhex(master_key_hex)
aesgcm = AESGCM(key_bytes)

conn = sqlite3.connect(FREEAPI_DB)
cur = conn.cursor()

print("=== TABLAS EN FREEAPI.DB ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(tables)

print()
print("=== DESCIFRAR KEYS DE PLATAFORMAS ===")
for platform in ("openrouter", "github", "groq", "google", "huggingface"):
    cur.execute("SELECT platform, encrypted_key, iv, auth_tag FROM api_keys WHERE platform=?", (platform,))
    row = cur.fetchone()
    if row:
        _, enc, iv_hex, tag_hex = row
        ct = bytes.fromhex(enc) + bytes.fromhex(tag_hex)
        iv = bytes.fromhex(iv_hex)
        try:
            plain = aesgcm.decrypt(iv, ct, None).decode("utf-8")
            print(f"  {platform:15s}: {plain[:12]}...{plain[-6:]} (len={len(plain)})")
        except Exception as e:
            print(f"  {platform:15s}: DECRYPT ERROR - {e}")
    else:
        print(f"  {platform:15s}: No encontrado")

print()
print("=== SETTINGS ===")
for tname in ["settings", "config", "app_config", "app_settings"]:
    if tname in tables:
        try:
            cur.execute(f"SELECT * FROM {tname} LIMIT 20")
            for row in cur.fetchall():
                print(f"  {row}")
        except Exception as e:
            print(f"  Error en {tname}: {e}")

print()
print("=== MODELOS DE OPENROUTER ===")
cur.execute("SELECT model_id, display_name FROM models WHERE platform='openrouter' AND enabled=1 ORDER BY model_id")
for row in cur.fetchall():
    print(f"  {row[0]}")

print()
print("=== MODELOS DE GITHUB ===")
cur.execute("SELECT model_id, display_name FROM models WHERE platform='github' AND enabled=1 ORDER BY model_id")
for row in cur.fetchall():
    print(f"  {row[0]}")

conn.close()
