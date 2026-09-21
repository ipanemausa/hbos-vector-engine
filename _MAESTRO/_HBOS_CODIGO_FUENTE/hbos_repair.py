"""
hbos_repair.py — AUTO-REPARACIÓN SOBERANA DE TRIPLE REDUNDANCIA Y QDRANT
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Gobernanza: DAG R768 · Autopilot Total
Reglas: R1 (Idempotencia), R3 (Atomicidad), R6 (Triple Redundancia)
"""

import os
import sys
import shutil
import hashlib
import time
import json
import math
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

LOCAL_DIR = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
DRIVE_DIR = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
BACKUP_DIR = r"C:\Users\ipane\backup_hbos\_MAESTRO"

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

def reparar_triple_redundancia():
    print("\n[*] Sincronizando y reparando Triple Redundancia Física...")
    os.makedirs(LOCAL_DIR, exist_ok=True)
    os.makedirs(DRIVE_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Conjunto global de archivos .md
    files_local = set(f for f in os.listdir(LOCAL_DIR) if f.endswith('.md'))
    files_drive = set(f for f in os.listdir(DRIVE_DIR) if f.endswith('.md')) if os.path.exists(DRIVE_DIR) else set()
    files_backup = set(f for f in os.listdir(BACKUP_DIR) if f.endswith('.md')) if os.path.exists(BACKUP_DIR) else set()

    all_files = files_local | files_drive | files_backup
    print(f"[*] Total documentos únicos encontrados en el universo de réplicas: {len(all_files)}")

    reparados = []
    
    for f in sorted(all_files):
        p_loc = os.path.join(LOCAL_DIR, f)
        p_drv = os.path.join(DRIVE_DIR, f)
        p_bak = os.path.join(BACKUP_DIR, f)

        # Identificar la fuente autoritativa más reciente
        candidates = []
        if os.path.exists(p_loc):
            candidates.append((os.path.getmtime(p_loc), p_loc))
        if os.path.exists(p_drv):
            candidates.append((os.path.getmtime(p_drv), p_drv))
        if os.path.exists(p_bak):
            candidates.append((os.path.getmtime(p_bak), p_bak))

        if not candidates:
            continue

        candidates.sort(reverse=True)
        source_path = candidates[0][1]
        source_hash = get_hash(source_path)

        # Propagar a local si falta o difiere
        if not os.path.exists(p_loc) or get_hash(p_loc) != source_hash:
            shutil.copy2(source_path, p_loc)
            reparados.append(f"Actualizado Local: {f}")

        # Propagar a Drive si falta o difiere
        if not os.path.exists(p_drv) or get_hash(p_drv) != source_hash:
            try:
                shutil.copy2(source_path, p_drv)
                reparados.append(f"Actualizado Drive: {f}")
            except Exception as e:
                print(f"  [!] Alerta en Drive stream para {f}: {e}")

        # Propagar a Backup si falta o difiere
        if not os.path.exists(p_bak) or get_hash(p_bak) != source_hash:
            shutil.copy2(source_path, p_bak)
            reparados.append(f"Actualizado Backup: {f}")

    if reparados:
        print(f"[OK] Se corrigieron {len(reparados)} inconsistencias de redundancia:")
        for r in reparados[:10]:
            print("  +", r)
        if len(reparados) > 10:
            print(f"  ... y {len(reparados) - 10} más.")
    else:
        print("[OK] Triple Redundancia 100% idéntica e idempotente. Cero drift.")

    return reparados

def reparar_qdrant_colecciones(client):
    print("\n[*] Auditando y reparando colecciones de Qdrant Cloud...")
    cols_res = client.get_collections().collections
    existing_cols = set(c.name for c in cols_res)

    required_cols = [
        "diamantino_patrones", "diamantino_lecciones", "diamantino_agentes",
        "hbos_estado", "hbos_directorio", "diamantino_casos_uso",
        "hbos_metricas", "diamantino_movimientos", "registro_ecosistema", "diamantino_apps"
    ]

    creadas = []
    for rc in required_cols:
        if rc not in existing_cols:
            print(f"  [+] Recreando colección faltante: '{rc}' (384-dim COSINE)...")
            client.create_collection(
                collection_name=rc,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            creadas.append(rc)

    if creadas:
        print(f"[OK] Colecciones restauradas: {creadas}")
    else:
        print("[OK] Todas las colecciones troncales ({len(required_cols)}) presentes y saludables.")
    return creadas

def ejecutar_reparacion():
    t0 = time.time()
    print("=" * 65)
    print(">>> [HBOS REPAIR] INICIANDO PROTOCOLO DE AUTO-REPARACIÓN <<<")
    print("=" * 65)

    reps_redundancia = reparar_triple_redundancia()

    url = os.getenv("QDRANT_URL")
    key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=url, api_key=key, timeout=25)
    reps_qdrant = reparar_qdrant_colecciones(client)

    elapsed = round(time.time() - t0, 3)
    total_reparaciones = len(reps_redundancia) + len(reps_qdrant)

    print("=" * 65)
    print(f"[OK] AUTO-REPARACIÓN COMPLETADA en {elapsed}s | Total arreglos: {total_reparaciones}")
    print("=" * 65)
    return total_reparaciones

if __name__ == "__main__":
    ejecutar_reparacion()
