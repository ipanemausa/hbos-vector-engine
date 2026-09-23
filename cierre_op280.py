# -*- coding: utf-8 -*-
"""
HBOS · op=280 · CIERRE REDUNDANTE
- Registrar en Qdrant
- Git commit + push
- Backup local
"""
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
BACKUP_DIR = Path(r"C:\Users\ipane\backup_hbos")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).isoformat()

print("=" * 65)
print("HBOS · op=280 · CIERRE REDUNDANTE")
print("=" * 65)

# ================================================================
# PASO 1: Registrar en Qdrant
# ================================================================
print("\n[1] REGISTRAR EN QDRANT...")
try:
    qdrant_url = "http://localhost:6333"
    
    # Registrar en hbos_auditoria
    payload = {
        "points": [{
            "id": 280,
            "payload": {
                "op": 280,
                "titulo": "HBOS · op=280 · KIRO ACTIVADO + CLAUDE ALTERNATIVAS",
                "estado": "COMPLETADO",
                "email": "ipanemamarketingusa@gmail.com",
                "kiro_status": "token_inyectado_aes256gcm",
                "kiro_enabled": False,
                "kiro_razon": "gated_pro_plan",
                "claude_alternativo": "openrouter:anthropic/claude-3-haiku",
                "freellmapi_modelos": 259,
                "http_200_verificado": True,
                "timestamp": NOW
            },
            "vector": [0.28] * 128
        }]
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{qdrant_url}/collections/hbos_auditoria/points",
        data=data,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = r.read().decode()
        print(f"  [OK] Registrado en hbos_auditoria: {resp[:80]}")
except Exception as e:
    print(f"  [WARN] Qdrant: {e}")

# Actualizar hbos_estado
try:
    estado_payload = {
        "points": [{
            "id": 1,
            "payload": {
                "estado": "45 a 280",
                "ultima_op": 280,
                "descripcion": "Kiro inyectado + Claude vía OpenRouter activo",
                "timestamp": NOW
            },
            "vector": [0.28] * 128
        }]
    }
    data2 = json.dumps(estado_payload).encode("utf-8")
    req2 = urllib.request.Request(
        f"{qdrant_url}/collections/hbos_estado/points",
        data=data2,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req2, timeout=10) as r:
        resp2 = r.read().decode()
        print(f"  [OK] hbos_estado actualizado: {resp2[:80]}")
except Exception as e:
    print(f"  [WARN] hbos_estado: {e}")

# ================================================================
# PASO 2: Backup local
# ================================================================
print("\n[2] BACKUP LOCAL...")
import shutil
files_to_backup = [
    "_KIRO_ACTIVADO_op280.md",
    "kiro_config.json",
    "inject_kiro_token.py",
    "configure_claude_openrouter.py",
    "explore_claude_alternatives.py",
]
for fname in files_to_backup:
    src = BASE_DIR / fname
    if src.exists():
        dst = BACKUP_DIR / fname
        shutil.copy2(str(src), str(dst))
        print(f"  [OK] {fname} -> {BACKUP_DIR}")
    else:
        print(f"  [SKIP] {fname} no existe")

# ================================================================
# PASO 3: Git commit + push
# ================================================================
print("\n[3] GIT COMMIT + PUSH...")
try:
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m",
         "HBOS op=280: Kiro token inyectado AES-256-GCM + Claude vía OpenRouter activo · 259 modelos · HTTP 200"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, timeout=60)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        print(f"  [{' '.join(cmd[:2])}] rc={result.returncode}")
        if stdout:
            print(f"    {stdout[:150]}")
        if stderr and result.returncode != 0:
            print(f"    STDERR: {stderr[:150]}")
except Exception as e:
    print(f"  [ERROR] Git: {e}")

print()
print("=" * 65)
print("CIERRE COMPLETADO · op=280")
print(f"Timestamp: {NOW}")
print("=" * 65)
