import os
import sys
import shutil
import hashlib
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

local_file = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_PROMPT_PARAMOUNT_v5.md"
drive_file = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_PROMPT_PARAMOUNT_v5.md"
backup_file = r"C:\Users\ipane\backup_hbos\_MAESTRO\_PROMPT_PARAMOUNT_v5.md"

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

# Vectorización en Qdrant (operation_id = 98)
def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    import math
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op98 = {
    "operation_id": 98,
    "tarea": "TAREA 1 — ACTUALIZAR PROMPT MAESTRO (INTEGRACIÓN DE FREELLMAPI)",
    "archivo": "_PROMPT_PARAMOUNT_v5.md",
    "version": "v5.0",
    "rutas": {
        "local": local_file,
        "drive": drive_file,
        "backup": backup_file
    },
    "tamano_bytes": s_local,
    "sha256": h_local,
    "elementos_integrados": [
        "1. Nuevo Componente: FreeLLMAPI (Router de modelos en Sandbox)",
        "2. Árbol de Decisión por Tarea (Texto, TTS, Imagen, Video)",
        "3. Prioridad de Proveedores (1. FreeLLMAPI, 2. Gemini, 3. Groq, 4. ElevenLabs, 5. DashScope, 6. Nano Banana)",
        "4. Matriz de Casos de Uso (Guion, Prompts, Verificación, Traducción, TTS, Imágenes, Video)",
        "5. Fallback en Cascada (FreeLLMAPI -> Gemini -> Groq; ElevenLabs -> CosyVoice2; DashScope)",
        "6. Compresión de Contexto (FreeLLMAPI + R768)",
        "7. Analítica y Trazabilidad Obligatoria (operation_id, modelo, latencia, tokens, éxito, ahorro vs pago)",
        "8. Privacidad por Nivel (Público, Interno, Privado, Crítico) y Reglas de Consumo"
    ],
    "redundancia_triple_verificada": True,
    "estado": "COMPLETADO"
}

vec_98 = generate_embedding("Tarea 1 operacion 98 Actualizacion Prompt Maestro Paramount v5 Integracion FreeLLMAPI Arbol Decision Casos Uso Analitica Privacidad", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=98,
            vector=vec_98,
            payload=payload_op98
        )
    ]
)
print("[OK] operation_id = 98 registrado exitosamente en registro_ecosistema de Qdrant.")
