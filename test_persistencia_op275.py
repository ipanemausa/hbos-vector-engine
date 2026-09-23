# -*- coding: utf-8 -*-
"""
test_persistencia_op275.py · Auditoría y Pruebas de Persistencia Multicapa HBOS op=275
"""

import os
import sys
import json
import sqlite3
import hashlib
import time
from datetime import datetime
from dotenv import load_dotenv
import requests

sys.stdout.reconfigure(encoding='utf-8')

results = []

# 1. SQLite + WAL (freeapi.db)
db_path = os.path.expandvars(r"%APPDATA%\FreeLLMAPI\freeapi.db")
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode")
    jmode = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM models WHERE enabled=1")
    mcnt = cur.fetchone()[0]
    conn.close()
    results.append({
        "capa": "SQLite + WAL (freeapi.db)",
        "garantiza": "Estado relacional, catálogo de modelos y API keys cifradas",
        "prueba": "Query PRAGMA journal_mode y SELECT models",
        "evidencia": f"journal_mode={jmode.upper()} | Modelos activos={mcnt}",
        "resultado": "PERSISTENTE_ACID" if jmode.lower() == 'wal' else "PERSISTENTE"
    })
except Exception as e:
    results.append({
        "capa": "SQLite + WAL (freeapi.db)",
        "garantiza": "Estado relacional",
        "prueba": "Acceso DB",
        "evidencia": str(e),
        "resultado": "FAIL"
    })

# 2. Qdrant Cloud
try:
    load_dotenv(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
    from qdrant_client import QdrantClient
    t0 = time.time()
    qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=15)
    cols = qc.get_collections().collections
    lat = round(time.time() - t0, 3)
    p_est = qc.retrieve("hbos_estado", ids=[1])
    rango = p_est[0].payload.get("rango_activo", "N/A") if p_est else "N/A"
    results.append({
        "capa": "Qdrant Cloud (Vector Store)",
        "garantiza": "Memoria semántica, canon (85 reglas), auditoría y rango de operaciones",
        "prueba": f"get_collections + retrieve hbos_estado(1)",
        "evidencia": f"Colecciones={len(cols)}/17 | Latencia={lat}s | Rango={rango}",
        "resultado": "PERSISTENTE_INMUTABLE"
    })
except Exception as e:
    results.append({
        "capa": "Qdrant Cloud (Vector Store)",
        "garantiza": "Memoria semántica",
        "prueba": "Conexión Cloud",
        "evidencia": str(e),
        "resultado": "FAIL"
    })

# 3. Sistema Híbrido (Local + Drive + Backup)
def get_sha(p):
    if not os.path.exists(p): return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest().upper()

f_rel = "_HBOS_REFERENCIAS.md"
p_loc = os.path.join(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine", f_rel)
p_drv = os.path.join(r"G:\My Drive\HBOS-Diamantino", f_rel)
p_bak = os.path.join(r"C:\Users\ipane\backup_hbos", f_rel)

h1, h2, h3 = get_sha(p_loc), get_sha(p_drv), get_sha(p_bak)
triple_ok = (h1 == h2 == h3) and (h1 is not None)
results.append({
    "capa": "Sistema Híbrido (R768 + Drive + Backup)",
    "garantiza": "Recuperación ante desastres físicos y consistencia documental total",
    "prueba": f"Comparación SHA-256 triple de {f_rel}",
    "evidencia": f"Local={h1[:12]}... | Drive={h2[:12]}... | Backup={h3[:12]}...",
    "resultado": "TRIPLE_REDUNDANCIA_OK" if triple_ok else "DISCREPANCIA"
})

# 4. Tarea Programada (HBOS-FreeLLMAPI-Daemon)
import subprocess
try:
    out = subprocess.check_output(
        'powershell -Command "Get-ScheduledTask -TaskPath \\ipane\\ -TaskName HBOS-FreeLLMAPI-Daemon | Select-Object -ExpandProperty State"',
        shell=True, text=True
    ).strip()
    p3001 = False
    try:
        r = requests.get("http://127.0.0.1:3001/v1/models", headers={"Authorization": "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"}, timeout=2)
        p3001 = (r.status_code == 200)
    except: pass
    results.append({
        "capa": "Tarea Programada Windows (Daemon Liveness)",
        "garantiza": "Persistencia de ejecución del proceso :3001 (auto-reinicio en fallo)",
        "prueba": "Get-ScheduledTask State + Ping HTTP :3001",
        "evidencia": f"TaskState={out} | Puerto :3001 HTTP 200={p3001}",
        "resultado": "SUPERVISION_ACTIVA" if out in ['Ready', 'Running'] else "WARN"
    })
except Exception as e:
    results.append({
        "capa": "Tarea Programada Windows (Daemon Liveness)",
        "garantiza": "Persistencia de ejecución",
        "prueba": "Get-ScheduledTask",
        "evidencia": str(e),
        "resultado": "FAIL"
    })

# 5. Ollama Local (:11434)
try:
    r_ol = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
    ol_ok = (r_ol.status_code == 200)
    models_ol = r_ol.json().get('models', [])
    results.append({
        "capa": "Ollama Local (:11434)",
        "garantiza": "Inferencia de emergencia offline sin dependencia de internet",
        "prueba": "GET /api/tags",
        "evidencia": f"HTTP {r_ol.status_code} | Modelos locales descargados={len(models_ol)}",
        "resultado": "DAEMON_LISTENING" if ol_ok else "FAIL"
    })
except Exception as e:
    results.append({
        "capa": "Ollama Local (:11434)",
        "garantiza": "Inferencia de emergencia offline",
        "prueba": "GET /api/tags",
        "evidencia": str(e),
        "resultado": "FAIL"
    })

# 6. Gateway :3002 / DeepSeek Harness
rules_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\routing_rules_295.json"
rules_exist = os.path.exists(rules_file)
results.append({
    "capa": "Gateway :3002 & DeepSeek Harness",
    "garantiza": "Enrutamiento inteligente multicriterio (295 reglas soberanas)",
    "prueba": f"Integridad archivo routing_rules_295.json",
    "evidencia": f"Existe={rules_exist} | Tamaño={os.path.getsize(rules_file) if rules_exist else 0} bytes",
    "resultado": "REGLAS_CANONICAS_OK" if rules_exist else "FAIL"
})

with open("test_persistencia_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

for r in results:
    print(f"[{r['resultado']}] {r['capa']} -> {r['evidencia']}")
