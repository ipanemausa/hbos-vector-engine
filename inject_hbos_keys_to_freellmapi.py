# -*- coding: utf-8 -*-
"""inject_hbos_keys_to_freellmapi.py — Inyector de Llaves y Activación de Modelos en FreeLLMAPI
Conecta el inventario de claves de HBOS (.env.local) con la base de datos de FreeLLMAPI
utilizando el cifrado nativo AES-256-GCM.
"""

import os
import sys
import json
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
    print("=" * 70)
    print(">>> CONECTANDO INVENTARIO HBOS CON FreeLLMAPI (ACTIVACIÓN DE MODELOS) <<<")
    print("=" * 70)

    if not ENC_KEY_FILE.exists():
        raise FileNotFoundError(f"No existe .encryption-key en: {ENC_KEY_FILE}")
    master_key_hex = ENC_KEY_FILE.read_text(encoding="utf-8").strip()
    print(f"[*] Clave maestra de cifrado FreeLLMAPI cargada: {master_key_hex[:8]}...{master_key_hex[-8:]}")

    if not ENV_LOCAL.exists():
        raise FileNotFoundError(f"No existe .env.local en: {ENV_LOCAL}")
    env_vars = dotenv_values(ENV_LOCAL)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Mapeo de proveedores HBOS -> Plataformas de FreeLLMAPI
    providers_to_register = []

    # 1. Groq
    if env_vars.get("GROQ_API_KEY"):
        providers_to_register.append({
            "platform": "groq",
            "label": "HBOS Groq Key",
            "key": env_vars["GROQ_API_KEY"].strip('"'),
            "base_url": None
        })

    # 2. OpenRouter
    if env_vars.get("OPENROUTER_API_KEY"):
        providers_to_register.append({
            "platform": "openrouter",
            "label": "HBOS OpenRouter Key",
            "key": env_vars["OPENROUTER_API_KEY"].strip('"'),
            "base_url": None
        })

    # 3. Google / Gemini
    gemini_key = env_vars.get("GEMINI_API_KEY") or env_vars.get("GOOGLE_API_KEY")
    if gemini_key:
        providers_to_register.append({
            "platform": "google",
            "label": "HBOS Google Gemini Key",
            "key": gemini_key.strip('"'),
            "base_url": None
        })

    # 4. Hugging Face
    if env_vars.get("HF_API_TOKEN"):
        providers_to_register.append({
            "platform": "huggingface",
            "label": "HBOS HuggingFace Hub Token",
            "key": env_vars["HF_API_TOKEN"].strip('"'),
            "base_url": None
        })

    # 5. ModelScope / DashScope (Alibaba)
    if env_vars.get("DASHSCOPE_API_KEY"):
        providers_to_register.append({
            "platform": "modelscope",
            "label": "HBOS DashScope / Alibaba Key",
            "key": env_vars["DASHSCOPE_API_KEY"].strip('"'),
            "base_url": None
        })

    # 6. Ollama Local (http://127.0.0.1:11434)
    providers_to_register.append({
        "platform": "ollama",
        "label": "HBOS Ollama Local (localhost:11434)",
        "key": "ollama-local-bearer",
        "base_url": "http://127.0.0.1:11434"
    })

    # 7. Plataformas Keyless sin clave (kilo, ovh, llm7)
    for keyless in ["kilo", "ovh", "llm7"]:
        providers_to_register.append({
            "platform": keyless,
            "label": f"FreeLLMAPI {keyless.upper()} (Keyless Free Tier)",
            "key": "no-key",
            "base_url": None
        })

    print(f"\n[*] Insertando {len(providers_to_register)} proveedores cifrados en 'api_keys'...")

    for p in providers_to_register:
        platform = p["platform"]
        label = p["label"]
        raw_key = p["key"]
        base_url = p["base_url"]

        # Verificar si ya existe
        cur.execute("SELECT id FROM api_keys WHERE platform = ?", (platform,))
        existing = cur.fetchone()

        encrypted, iv, auth_tag = encrypt_key_aes256gcm(master_key_hex, raw_key)

        if existing:
            cur.execute("""
                UPDATE api_keys 
                SET label = ?, encrypted_key = ?, iv = ?, auth_tag = ?, status = 'healthy', enabled = 1, base_url = ?
                WHERE id = ?
            """, (label, encrypted, iv, auth_tag, base_url, existing[0]))
            print(f"  [ACTUALIZADO] {platform:15} (ID {existing[0]}) -> {label}")
        else:
            cur.execute("""
                INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled, base_url)
                VALUES (?, ?, ?, ?, ?, 'healthy', 1, ?)
            """, (platform, label, encrypted, iv, auth_tag, base_url))
            print(f"  [INSERTADO]   {platform:15} -> {label}")

    conn.commit()

    # Contar modelos activados en base de datos
    cur.execute("SELECT COUNT(*) FROM api_keys WHERE enabled = 1")
    keys_count = cur.fetchone()[0]
    print(f"\n[OK] Total de API Keys activas en FreeLLMAPI: {keys_count}")

    # Verificar cantidad de modelos que pertenecen a estas plataformas
    platforms = [p["platform"] for p in providers_to_register]
    placeholders = ",".join(["?"] * len(platforms))
    cur.execute(f"SELECT COUNT(*) FROM models WHERE platform IN ({placeholders}) AND enabled = 1", platforms)
    models_unlocked = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM embedding_models WHERE platform IN ({placeholders}) AND enabled = 1", platforms)
    embeds_unlocked = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM media_models WHERE platform IN ({placeholders}) AND enabled = 1", platforms)
    media_unlocked = cur.fetchone()[0]

    conn.close()

    print(f"[OK] Modelos de Chat/Completions Desbloqueados: {models_unlocked}")
    print(f"[OK] Modelos de Embeddings Desbloqueados:      {embeds_unlocked}")
    print(f"[OK] Modelos Multimedia/Video/Voz Desbloqueados: {media_unlocked}")
    print(f"--> TOTAL MODELOS HBOS DIRECTAMENTE ACTIVOS EN LOCAL: {models_unlocked + embeds_unlocked + media_unlocked}")
    print("=" * 70)

if __name__ == "__main__":
    main()
