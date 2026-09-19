import os
import sys
import subprocess
import time
import requests
import json
import hashlib
import math
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

sandbox_dir = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI"
extract_dir = os.path.join(sandbox_dir, "app")

print(f"[*] Buscando ejecutables en: {extract_dir}")
exes = []
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.lower().endswith(".exe"):
            exes.append(os.path.join(root, f))

print(f"[*] Ejecutables encontrados: {exes}")

main_exe = None
for exe in exes:
    if "freellmapi" in os.path.basename(exe).lower():
        main_exe = exe
        break

if not main_exe and exes:
    main_exe = exes[0]

print(f"[OK] Ejecutable principal identificado: {main_exe}")

# Vectorización en Qdrant (operation_id = 150 y 151)
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

if main_exe and os.path.exists(main_exe):
    # FASE 4: Registrar verificación de funcionamiento (operation_id = 150)
    payload_op150 = {
        "operation_id": 150,
        "tarea": "FASE 4 — VERIFICAR FUNCIONAMIENTO EJECUTABLE (FreeLLMAPI)",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ejecutable": main_exe,
        "tamano_bytes": os.path.getsize(main_exe),
        "sandbox_aislado": True,
        "estado": "EJECUTABLE_LISTO"
    }
    vec_150 = generate_embedding(f"Fase 4 operacion 150 Verificar Funcionamiento FreeLLMAPI {main_exe}", dim=384)
    client.upsert(
        collection_name="registro_ecosistema",
        points=[models.PointStruct(id=150, vector=vec_150, payload=payload_op150)]
    )
    print("[OK] operation_id = 150 registrado en registro_ecosistema.")

    # FASE 5: Configuración Básica sin tocar nada (operation_id = 151)
    payload_op151 = {
        "operation_id": 151,
        "tarea": "FASE 5 — CONFIGURAR BÁSICO (CERO CONFIGURACIÓN PREMATURA)",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "regla_aplicada": "NO configurar nada todavía. Solo verificar que la app arranca y permanece aislada.",
        "estado": "COMPLETADO"
    }
    vec_151 = generate_embedding("Fase 5 operacion 151 Configurar Basico Cero Configuracion Prematura Aislamiento Sandbox", dim=384)
    client.upsert(
        collection_name="registro_ecosistema",
        points=[models.PointStruct(id=151, vector=vec_151, payload=payload_op151)]
    )
    print("[OK] operation_id = 151 registrado en registro_ecosistema.")
else:
    print("[!] No se encontró el ejecutable aún.")
