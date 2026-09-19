import os
import sys
import shutil
import hashlib
import json
import math
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

print("==========================================================================")
print(">>> [FASE 0] BACKUP TOTAL Y PROTECCIÓN ABSOLUTA DEL ECOSISTEMA (op 115) <<<")
print("==========================================================================")

local_maestro = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
drive_maestro = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
backup_maestro = r"C:\Users\ipane\backup_hbos\_MAESTRO"
backup_root = r"C:\Users\ipane\backup_hbos"
snapshot_root = r"C:\Users\ipane\backup_hbos_snapshots\snapshot_2026-09-19_pre_navigator"

os.makedirs(local_maestro, exist_ok=True)
os.makedirs(drive_maestro, exist_ok=True)
os.makedirs(backup_maestro, exist_ok=True)
os.makedirs(snapshot_root, exist_ok=True)

# 1. Sincronizar _MAESTRO en las 3 ubicaciones
print("[*] Sincronizando _MAESTRO local -> Drive y backup_hbos...")
maestro_files = os.listdir(local_maestro)
for f in maestro_files:
    src = os.path.join(local_maestro, f)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(drive_maestro, f))
        shutil.copy2(src, os.path.join(backup_maestro, f))
print(f"[OK] {len(maestro_files)} archivos de _MAESTRO sincronizados en triple redundancia.")

# 2. Snapshot de backup_hbos completo
print(f"[*] Creando snapshot completo de {backup_root} en {snapshot_root}...")
for item in os.listdir(backup_root):
    s = os.path.join(backup_root, item)
    d = os.path.join(snapshot_root, item)
    if os.path.isdir(s):
        if not os.path.exists(d):
            shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
print("[OK] Snapshot de backup_hbos completado.")

# 3. Snapshot de Qdrant (todas las colecciones y recuentos)
print("[*] Conectando a Qdrant Cloud para registrar snapshot de colecciones...")
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)
cols_res = client.get_collections()
qdrant_snapshot = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "operation_id": 115,
    "total_colecciones": len(cols_res.collections),
    "colecciones": {}
}

for c in cols_res.collections:
    c_info = client.get_collection(c.name)
    qdrant_snapshot["colecciones"][c.name] = {
        "status": str(c_info.status),
        "points_count": c_info.points_count,
        "indexed_vectors_count": getattr(c_info, "indexed_vectors_count", 0)
    }

print("[OK] Estado de colecciones en Qdrant:")
for cname, cstat in qdrant_snapshot["colecciones"].items():
    print(f"   - {cname}: {cstat['points_count']} puntos | status: {cstat['status']}")

# Guardar snapshot de Qdrant en _MAESTRO (local, drive, backup)
snap_filename = "_SNAPSHOT_QDRANT_2026-09-19.json"
snap_local = os.path.join(local_maestro, snap_filename)
snap_drive = os.path.join(drive_maestro, snap_filename)
snap_backup = os.path.join(backup_maestro, snap_filename)

with open(snap_local, "w", encoding="utf-8") as f:
    json.dump(qdrant_snapshot, f, indent=2, ensure_ascii=False)
shutil.copy2(snap_local, snap_drive)
shutil.copy2(snap_local, snap_backup)
print(f"[OK] Archivo de snapshot {snap_filename} guardado en triple redundancia.")

# 4. Verificación Test-Path de cada backup
print("[*] Verificando Test-Path de rutas críticas...")
rutas_a_verificar = [
    local_maestro,
    drive_maestro,
    backup_maestro,
    snapshot_root,
    snap_local,
    snap_drive,
    snap_backup,
    r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master",
    r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master",
    r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\01_Guion",
    r"C:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS"
]

verificaciones = {}
todos_ok = True
for r in rutas_a_verificar:
    exists = os.path.exists(r)
    verificaciones[r] = exists
    if not exists:
        todos_ok = False
    print(f"   - [{'OK' if exists else 'FALLO'}] {r}")

assert todos_ok, "Error: Alguna ruta crítica de backup no existe."
print("[OK] Test-Path de todos los backups: 100% VERIFICADO.")

# 5. Vectorización en Qdrant (operation_id = 115)
def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

payload_op115 = {
    "operation_id": 115,
    "tarea": "FASE 0 — BACKUP TOTAL Y PROTECCIÓN ABSOLUTA DEL SISTEMA PREVIO",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "git_commit": "183ff97",
    "maestro_archivos_sincronizados": len(maestro_files),
    "snapshot_qdrant": qdrant_snapshot,
    "snapshot_backup_hbos_ruta": snapshot_root,
    "test_path_verificado": True,
    "estado": "COMPLETADO_SIN_RIESGOS"
}

vec_115 = generate_embedding("Fase 0 operacion 115 Backup Total Proteccion Absoluta Sistema Previo Git Commit Maestro Qdrant Snapshot", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=115,
            vector=vec_115,
            payload=payload_op115
        )
    ]
)
print("[OK] operation_id = 115 registrado exitosamente en registro_ecosistema de Qdrant.")
