# -*- coding: utf-8 -*-
"""
HBOS · KIRO AI BRIDGE & CONECTOR DE FRONTERA
Conector local OpenAI-compatible para Kiro AI (Claude 3.7 / Claude Opus)
Permite a FreeLLMAPI (:3001) y Antigravity enrutar prompts hacia Kiro AI.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PORT_BRIDGE = 3005
DB_PATH = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
ENC_KEY_FILE = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key")
CONFIG_PATH = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\kiro_config.json")

def encrypt_key_aes256gcm(master_key_hex, plain_text):
    key_bytes = bytes.fromhex(master_key_hex)
    aesgcm = AESGCM(key_bytes)
    iv = os.urandom(16)
    data = plain_text.encode('utf-8')
    ciphertext_and_tag = aesgcm.encrypt(iv, data, None)
    ciphertext = ciphertext_and_tag[:-16].hex()
    auth_tag = ciphertext_and_tag[-16:].hex()
    return ciphertext, iv.hex(), auth_tag

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "api_key": "PENDIENTE_TOKEN_USUARIO",
        "base_url": "https://api.kiro.dev/v1",
        "default_model": "claude-3-7-sonnet",
        "status": "CONFIGURADO_ESPERANDO_TOKEN",
        "instrucciones": "Registrarse en https://kiro.dev, copiar session token / API key y pegarlo en kiro_config.json"
    }

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def inject_kiro_in_freellmapi():
    """Inyecta Kiro AI como plataforma y modelos de frontera en freeapi.db con cifrado AES-256-GCM"""
    if not DB_PATH.exists():
        print(f"[!] Base de datos FreeLLMAPI no encontrada en {DB_PATH}")
        return False
        
    master_key_hex = ENC_KEY_FILE.read_text(encoding="utf-8").strip() if ENC_KEY_FILE.exists() else None
    if not master_key_hex:
        print("[!] No se encontró master encryption key")
        return False

    cfg = load_config()
    token_to_encrypt = cfg.get("api_key", "PENDIENTE_TOKEN")
    c, iv, tag = encrypt_key_aes256gcm(master_key_hex, token_to_encrypt)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Registrar o actualizar api_keys
    cur.execute("SELECT id FROM api_keys WHERE platform='kiro'")
    row = cur.fetchone()
    if not row:
        cur.execute("""
            INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled, base_url)
            VALUES ('kiro', 'Kiro AI (Claude 3.7 / Opus)', ?, ?, ?, 'ready', 1, 'http://127.0.0.1:3005/v1')
        """, (c, iv, tag))
        print("[OK] Plataforma 'kiro' inyectada en api_keys")
    else:
        cur.execute("""
            UPDATE api_keys 
            SET label='Kiro AI (Claude 3.7 / Opus)', encrypted_key=?, iv=?, auth_tag=?, status='ready', enabled=1, base_url='http://127.0.0.1:3005/v1'
            WHERE platform='kiro'
        """, (c, iv, tag))
        print("[OK] Plataforma 'kiro' actualizada en api_keys")
        
    # 2. Registrar modelos en tabla models
    modelos_kiro = [
        ("kiro/claude-3-7-sonnet", "Claude 3.7 Sonnet (Kiro AI)", "kiro", 100, 95, "xlarge", 200000, 1),
        ("kiro/claude-opus", "Claude Opus 3.5 (Kiro AI)", "kiro", 102, 85, "xlarge", 200000, 1)
    ]
    for mid, name, plat, irank, srank, slabel, ctx, en in modelos_kiro:
        cur.execute("SELECT id FROM models WHERE model_id=?", (mid,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO models (model_id, display_name, platform, intelligence_rank, speed_rank, size_label, context_window, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mid, name, plat, irank, srank, slabel, ctx, en))
            print(f"[OK] Modelo '{mid}' registrado en tabla models")
        else:
            cur.execute("""
                UPDATE models 
                SET display_name=?, intelligence_rank=?, speed_rank=?, context_window=?, enabled=1
                WHERE model_id=?
            """, (name, irank, srank, ctx, mid))
            print(f"[OK] Modelo '{mid}' actualizado en tabla models")
            
    conn.commit()
    conn.close()
    save_config(cfg)
    return True

if __name__ == "__main__":
    print("=== HBOS KIRO AI CONECTOR ===")
    cfg = load_config()
    print(f"Estado de configuración Kiro: {cfg.get('status')}")
    print(f"Inyectando modelos en FreeLLMAPI DB...")
    res = inject_kiro_in_freellmapi()
    print(f"Resultado de inyección en freeapi.db: {'EXITOSO' if res else 'FALLO'}")
