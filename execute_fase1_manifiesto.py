import os
import sys
import shutil
import hashlib
import json
import math
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

local_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"
backup_file = r"C:\Users\ipane\backup_hbos\_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"

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

assert h_local == h_drive == h_backup, "Error: Discrepancia de bytes entre copias de redundancia triple"
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

payload_op103 = {
    "operation_id": 103,
    "tarea": "FASE 1 — ACTUALIZAR MANIFIESTO (HBOS-DIAMANTINO COMO CANAL DE DIFUSIÓN DE IA)",
    "archivo": "_MANIFIESTO_HBOS_DIAMANTINO.md",
    "seccion_anadida": "10. CANAL DE DIFUSIÓN DE IA: ANCHORS Y PEDAGOGÍA DE CONOCIMIENTO (ESTILO ALEJAVI)",
    "conceptos_clave": [
        "HBOS-Diamantino como canal de difusión de IA",
        "Hosts cristalinos como Anchors de noticias y pedagogía",
        "Contenido: noticias de IA, descubrimientos científicos, instrucción, análisis de tendencias",
        "Estilo Alejavi: claro, analítico, instructivo, sin metáforas, sin apropiación, con análisis riguroso",
        "Eliminación de riesgos de autoría y escalabilidad para producción diaria (L-20)"
    ],
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

vec_103 = generate_embedding("Fase 1 operacion 103 Actualizar Manifiesto HBOS Diamantino Canal de Difusion de IA Anchors Estilo Alejavi Noticias Instruccion", dim=384)

# 1. Registrar en registro_ecosistema
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=103,
            vector=vec_103,
            payload=payload_op103
        )
    ]
)
print("[OK] operation_id = 103 registrado exitosamente en registro_ecosistema.")

# 2. Registrar en diamantino_universo
client.upsert(
    collection_name="diamantino_universo",
    points=[
        models.PointStruct(
            id=103,
            vector=vec_103,
            payload={
                "tipo": "MANIFIESTO_CANONICO_V2",
                "titulo": "Manifiesto HBOS-Diamantino — Canal de Difusión de IA",
                "seccion_10": "Canal de Difusión de IA: Anchors y Pedagogía de Conocimiento (Estilo Alejavi)",
                "operation_id": 103
            }
        )
    ]
)
print("[OK] operation_id = 103 registrado exitosamente en diamantino_universo.")
