import os
import sys
import shutil
import hashlib
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

local_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_DEEPSEEK_INTEGRACION.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_DEEPSEEK_INTEGRACION.md"
backup_file = r"C:\Users\ipane\backup_hbos\_MAESTRO\_DEEPSEEK_INTEGRACION.md"

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
    import math
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

# 1. Registrar operation_id = 156 (Documentar DeepSeek Harness)
payload_op156 = {
    "operation_id": 156,
    "tarea": "FASE 2 — DOCUMENTAR DEEPSEEK HARNESS CON FREELMAPI",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "archivo": "_DEEPSEEK_INTEGRACION.md",
    "modelos_principales": ["DeepSeek V3", "DeepSeek R1", "DeepSeek Coder", "Qwen 2.5", "GLM-4/5"],
    "rutas": {"local": local_file, "drive": drive_file, "backup": backup_file},
    "tamano_bytes": s_local,
    "sha256": h_local,
    "redundancia_triple_verificada": True,
    "estado": "COMPLETADO"
}
vec_156 = generate_embedding("Fase 2 operacion 156 Documentar DeepSeek Harness FreeLLMAPI Razonamiento Modelos Chinos", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=156, vector=vec_156, payload=payload_op156)]
)
print("[OK] operation_id = 156 registrado en registro_ecosistema.")

# 2. Registrar operation_id = 157 (Crear P-52 y L-38)
p52_data = {
    "codigo": "P-52",
    "nombre": "DeepSeek_Harness_Como_Proveedor",
    "descripcion": "Integración de DeepSeek Harness como proveedor de razonamiento profundo MoE y síntesis de código para HBOS.",
    "tipo": "PATRON_CANONICO"
}
client.upsert(
    collection_name="diamantino_patrones",
    points=[models.PointStruct(id=52, vector=generate_embedding(p52_data["descripcion"]), payload=p52_data)]
)
print("[OK] Patrón P-52 (ID=52) registrado en diamantino_patrones.")

l38_data = {
    "codigo": "L-38",
    "titulo": "DeepSeek_Harness_FreeLLMAPI_Modelos_Chinos_Gratis",
    "descripcion": "DeepSeek Harness + FreeLLMAPI = acceso agregado y soberano a los mejores modelos de razonamiento abiertos chinos a coste cero.",
    "tipo": "LECCION_APRENDIDA"
}
client.upsert(
    collection_name="diamantino_lecciones",
    points=[models.PointStruct(id=38, vector=generate_embedding(l38_data["descripcion"]), payload=l38_data)]
)
print("[OK] Lección L-38 (ID=38) registrada en diamantino_lecciones.")

payload_op157 = {
    "operation_id": 157,
    "tarea": "FASE 3 — CREAR PATRÓN P-52 Y LECCIÓN L-38",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "patron_creado": "P-52",
    "leccion_creada": "L-38",
    "estado": "COMPLETADO"
}
vec_157 = generate_embedding("Fase 3 operacion 157 Crear Patron P-52 y Leccion L-38 DeepSeek Harness", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=157, vector=vec_157, payload=payload_op157)]
)
print("[OK] operation_id = 157 registrado en registro_ecosistema.")

# 3. Registrar operation_id = 158 (Indexar DeepSeek Harness en diamantino_agentes ID=10)
deepseek_agent = {
    "agente": "DeepSeek Harness",
    "tipo": "externo",
    "categoria": "proveedor",
    "funcion": "Acceso a modelos chinos y razonamiento profundo MoE/R1",
    "estado": "pendiente",
    "fecha_creacion": "2026-09-19",
    "operation_id": "158",
    "dependencias": ["FreeLLMAPI", "openweight-models-hub"],
    "rutas": {"maestro": drive_file},
    "documentacion": "_MAESTRO/_DEEPSEEK_INTEGRACION.md"
}
client.upsert(
    collection_name="diamantino_agentes",
    points=[models.PointStruct(
        id=10,
        vector=generate_embedding(f"DeepSeek Harness agente externo proveedor {deepseek_agent['funcion']}"),
        payload=deepseek_agent
    )]
)
print("[OK] DeepSeek Harness indexado como Agente Externo (ID=10) en diamantino_agentes.")

payload_op158 = {
    "operation_id": 158,
    "tarea": "FASE 4 — INDEXAR DEEPSEEK HARNESS EN diamantino_agentes",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "agente_indexado": "DeepSeek Harness",
    "punto_id": 10,
    "estado": "COMPLETADO"
}
vec_158 = generate_embedding("Fase 4 operacion 158 Indexar DeepSeek Harness en diamantino_agentes ID=10", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=158, vector=vec_158, payload=payload_op158)]
)
print("[OK] operation_id = 158 registrado en registro_ecosistema.")

info = client.get_collection("diamantino_agentes")
print(f"\n[OK] Estado final de 'diamantino_agentes': {info.points_count} puntos activos.")
