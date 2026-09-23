# -*- coding: utf-8 -*-
"""
HBOS · op=280 · INYECTAR TOKEN REAL DE KIRO EN FREELLMAPI
Cifrado AES-256-GCM. Leer de Kiro CLI SQLite. Inyectar en freeapi.db.
"""
import sqlite3
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from datetime import datetime, timezone
from pathlib import Path

KIRO_DB = Path(r"C:\Users\ipane\AppData\Local\Kiro-Cli\data.sqlite3")
FREEAPI_DB = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
ENC_KEY_FILE = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key")
CONFIG_PATH = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\kiro_config.json")

print("=" * 65)
print("HBOS · op=280 · INYECCIÓN TOKEN KIRO")
print("=" * 65)

# ================================================================
# PASO 1: EXTRAER TOKEN REAL DE KIRO CLI
# ================================================================
print("\n[1] Extrayendo token de Kiro CLI SQLite...")
conn = sqlite3.connect(str(KIRO_DB))
cur = conn.cursor()
cur.execute("SELECT value FROM auth_kv WHERE key='kirocli:social:token'")
row = cur.fetchone()
conn.close()

if not row:
    print("[ERROR] No se encontró kirocli:social:token en auth_kv")
    exit(1)

val = json.loads(row[0])
access_token = val["access_token"]
refresh_token = val.get("refresh_token", "")
expires_at = val.get("expires_at", "")
profile_arn = val.get("profile_arn", "")
provider = val.get("provider", "google")

print(f"  access_token  : {access_token[:12]}...{access_token[-6:]}")
print(f"  refresh_token : {refresh_token[:12]}...{refresh_token[-6:]}")
print(f"  expires_at    : {expires_at}")
print(f"  profile_arn   : {profile_arn}")

# Verificar expiración
exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
now = datetime.now(timezone.utc)
remaining = exp - now
print(f"  Tiempo restante: {remaining}")

if remaining.total_seconds() < 0:
    print("[WARN] TOKEN EXPIRADO. Intentar renovación con refresh_token.")
else:
    print(f"[OK] Token válido por {int(remaining.total_seconds() // 60)} minutos.")

# ================================================================
# PASO 2: CIFRAR CON AES-256-GCM
# ================================================================
print("\n[2] Cifrando access_token con AES-256-GCM...")
master_key_hex = ENC_KEY_FILE.read_text(encoding="utf-8").strip()
key_bytes = bytes.fromhex(master_key_hex)
aesgcm = AESGCM(key_bytes)
iv = os.urandom(16)
data = access_token.encode("utf-8")
ct_and_tag = aesgcm.encrypt(iv, data, None)
ciphertext_hex = ct_and_tag[:-16].hex()
auth_tag_hex = ct_and_tag[-16:].hex()
iv_hex = iv.hex()

print(f"  encrypted_key : {len(ciphertext_hex)} chars")
print(f"  iv            : {iv_hex[:8]}...{iv_hex[-4:]}")
print(f"  auth_tag      : {auth_tag_hex[:8]}...{auth_tag_hex[-4:]}")

# ================================================================
# PASO 3: INYECTAR EN FREEAPI.DB
# ================================================================
print("\n[3] Inyectando en freeapi.db (plataforma kiro)...")
conn2 = sqlite3.connect(str(FREEAPI_DB))
cur2 = conn2.cursor()

cur2.execute("""
    UPDATE api_keys 
    SET encrypted_key=?, iv=?, auth_tag=?, status='healthy', last_health_error=NULL, enabled=1
    WHERE platform='kiro'
""", (ciphertext_hex, iv_hex, auth_tag_hex))
rows_updated = cur2.rowcount
conn2.commit()

# Verificar
cur2.execute("SELECT id, platform, status, enabled, length(encrypted_key) FROM api_keys WHERE platform='kiro'")
row = cur2.fetchone()
conn2.close()

print(f"  Filas actualizadas: {rows_updated}")
print(f"  [VERIFICADO] id={row[0]} | platform={row[1]} | status={row[2]} | enabled={row[3]} | enc_len={row[4]}")

# ================================================================
# PASO 4: GUARDAR REFRESH_TOKEN EN kiro_config.json
# ================================================================
print("\n[4] Guardando kiro_config.json (con refresh_token)...")
cfg = {
    "api_key": access_token,
    "refresh_token": refresh_token,
    "expires_at": expires_at,
    "profile_arn": profile_arn,
    "provider": provider,
    "auto_refresh": True,
    "status": "INYECTADO_OP280",
    "scopes": val.get("scopes", []),
    "updated_at": now.isoformat(),
    "instrucciones_renovacion": (
        "Ejecutar inject_kiro_token.py para re-inyectar. "
        "Si token expirado, primero ejecutar kiro-cli.exe login."
    )
}
CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  [OK] {CONFIG_PATH.name} actualizado.")

print("\n" + "=" * 65)
print("RESULTADO FINAL:")
print(f"  - Token inyectado: {access_token[:12]}...{access_token[-6:]}")
print(f"  - encrypted_key  : {len(ciphertext_hex)} chars")
print(f"  - status         : healthy")
print(f"  - enabled        : 1")
print(f"  - kiro_config    : refresh_token guardado")
print("=" * 65)
print("[DONE] INYECCIÓN COMPLETA — VERIFICAR EN FASE SIGUIENTE")
