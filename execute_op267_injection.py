# -*- coding: utf-8 -*-
"""execute_op267_injection.py — Inyección de Groq y proveedores completados en FreeLLMAPI
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import dotenv_values
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENV_LOCAL = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
ENC_KEY_FILE = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key")
DB_PATH = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")

def encrypt_key_aes256gcm(master_key_hex, plain_text):
    key_bytes = bytes.fromhex(master_key_hex)
    aesgcm = AESGCM(key_bytes)
    iv = os.urandom(16)
    data = plain_text.encode('utf-8')
    ciphertext_and_tag = aesgcm.encrypt(iv, data, None)
    ciphertext = ciphertext_and_tag[:-16].hex()
    auth_tag = ciphertext_and_tag[-16:].hex()
    return ciphertext, iv.hex(), auth_tag

def main():
    print("=" * 75)
    print("HBOS op=267 · FASE 3 · INYECCIÓN DE PROVIDERS RECUPERADOS")
    print("=" * 75)

    master_key_hex = ENC_KEY_FILE.read_text(encoding="utf-8").strip()
    env_vars = dotenv_values(ENV_LOCAL)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. INYECTAR GROQ
    groq_raw = env_vars.get("GROQ_API_KEY", "").strip('"').strip("'")
    if groq_raw:
        cur.execute("SELECT id FROM api_keys WHERE platform = 'groq'")
        row = cur.fetchone()
        
        c, iv, tag = encrypt_key_aes256gcm(master_key_hex, groq_raw)
        
        if row:
            cur.execute("""
                UPDATE api_keys 
                SET encrypted_key = ?, iv = ?, auth_tag = ?, status = 'healthy', enabled = 1, label = 'HBOS Groq Key (Ultra-Fast)'
                WHERE platform = 'groq'
            """, (c, iv, tag))
            print(f"[ACTUALIZADO] Groq (ID {row[0]}) activado con éxito.")
        else:
            cur.execute("""
                INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled)
                VALUES ('groq', 'HBOS Groq Key (Ultra-Fast)', ?, ?, ?, 'healthy', 1)
            """, (c, iv, tag))
            print(f"[INSERTADO] Groq insertado y activado con éxito.")

    # 2. INYECTAR GITHUB MODELS (si token presente)
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        cur.execute("SELECT id FROM api_keys WHERE platform = 'github'")
        row_gh = cur.fetchone()
        c_gh, iv_gh, tag_gh = encrypt_key_aes256gcm(master_key_hex, gh_token)
        if row_gh:
            cur.execute("""
                UPDATE api_keys
                SET encrypted_key = ?, iv = ?, auth_tag = ?, status = 'healthy', enabled = 1, label = 'HBOS GitHub Models'
                WHERE platform = 'github'
            """, (c_gh, iv_gh, tag_gh))
            print(f"[ACTUALIZADO] GitHub Models (ID {row_gh[0]}) activado con éxito.")
        else:
            cur.execute("""
                INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled, base_url)
                VALUES ('github', 'HBOS GitHub Models', ?, ?, ?, 'healthy', 1, 'https://models.github.ai/inference')
            """, (c_gh, iv_gh, tag_gh))
            print(f"[INSERTADO] GitHub Models insertado y activado con éxito.")

    conn.commit()

    # Verificar estado completo
    print("\n" + "=" * 75)
    print("ESTADO ACTUAL DE api_keys EN freeapi.db:")
    print("=" * 75)
    rows = cur.execute("SELECT id, platform, label, status, enabled, created_at FROM api_keys ORDER BY id ASC").fetchall()
    for r in rows:
        print(f"  ID {r[0]:2} | {r[1]:15} | {r[3]:8} | enabled={r[4]} | {r[2]}")

    total_enabled = cur.execute("SELECT COUNT(*) FROM api_keys WHERE enabled = 1").fetchone()[0]
    total_platforms = cur.execute("SELECT COUNT(DISTINCT platform) FROM api_keys WHERE enabled = 1").fetchone()[0]
    print(f"\nTotal API Keys habilitadas: {total_enabled}")
    print(f"Total Plataformas activas:  {total_platforms}")
    conn.close()

if __name__ == "__main__":
    main()
