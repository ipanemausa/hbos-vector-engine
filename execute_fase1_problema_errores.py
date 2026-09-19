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

local_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_PROBLEMA_ERRORES.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_PROBLEMA_ERRORES.md"
backup_file = r"C:\Users\ipane\backup_hbos\_MAESTRO\_PROBLEMA_ERRORES.md"

os.makedirs(os.path.dirname(drive_file), exist_ok=True)
os.makedirs(os.path.dirname(backup_file), exist_ok=True)

shutil.copy2(local_file, drive_file)
shutil.copy2(local_file, backup_file)

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest(), os.path.getsize(path)

h_local, s_local = get_hash(local_file)
h_drive, s_drive = get_hash(drive_file)
h_backup, s_backup = get_hash(backup_file)

print(f"Local:  {s_local} bytes | SHA256: {h_local}")
print(f"Drive:  {s_drive} bytes | SHA256: {h_drive}")
print(f"Backup: {s_backup} bytes | SHA256: {h_backup}")

assert h_local == h_drive == h_backup, "Error: Discrepancia de bytes en triple redundancia"
print("[OK] Verificación de bytes idénticos 100% exitosa.")

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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op127 = {
    "operation_id": 127,
    "tarea": "FASE 1 — DOCUMENTAR EL PROBLEMA REAL (DÍAS PERDIDOS POR ERRORES)",
    "archivo": "_PROBLEMA_ERRORES.md",
    "metricas_clave": {
        "escenario_todo_bien": "40 min/dia",
        "escenario_algo_falla": "3-8 horas/dia",
        "escenario_nada_funciona": "6-10 horas/dia (dia perdido)",
        "promedio_diario": "~4 horas/dia",
        "total_horas_perdidas_mes": "120 horas/mes",
        "meta_recuperacion": "10 horas/mes (20 min/dia)"
    },
    "rutas": {
        "local": local_file,
        "drive": drive_file,
        "backup": backup_file
    },
    "tamano_bytes": s_local,
    "sha256": h_local,
    "redundancia_triple_verificada": True,
    "estado": "COMPLETADO"
}

vec_127 = generate_embedding("Fase 1 operacion 127 Documentar el Problema Real Errores Dias Perdidos 120 horas mes depuracion manual resiliencia", dim=384)

# 1. Registrar en registro_ecosistema
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=127,
            vector=vec_127,
            payload=payload_op127
        )
    ]
)
print("[OK] operation_id = 127 registrado en registro_ecosistema.")

# 2. Registrar en diamantino_lecciones (Lección preliminar L-30)
l30_data = {
    "codigo": "L-30",
    "titulo": "Errores_Consumen_4_a_10_Horas_Dia",
    "descripcion": "La depuración reactiva sin memoria de fallos previos convierte tareas de 40 min en jornadas de 4 a 10 horas, sumando 120 horas/mes perdidas.",
    "tipo": "LECCION_APRENDIDA",
    "operation_id": 127
}
client.upsert(
    collection_name="diamantino_lecciones",
    points=[
        models.PointStruct(
            id=30,
            vector=generate_embedding(l30_data["descripcion"]),
            payload=l30_data
        )
    ]
)
print("[OK] Lección L-30 registrada en diamantino_lecciones.")
