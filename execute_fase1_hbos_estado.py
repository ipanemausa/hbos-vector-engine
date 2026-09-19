import os
import sys
import math
import hashlib
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

col_name = "hbos_estado"
collections_res = client.get_collections()
existing_names = [c.name for c in collections_res.collections]

print(f"[*] Colecciones existentes en Qdrant: {len(existing_names)}")

if col_name not in existing_names:
    print(f"[*] Creando colección '{col_name}' con dimensión 384 y métrica Cosine...")
    client.create_collection(
        collection_name=col_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    print(f"[OK] Colección '{col_name}' creada exitosamente.")
else:
    print(f"[OK] La colección '{col_name}' ya existe.")

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

# Payload canónico integral de estado
payload_estado_hoy = {
    "fecha": "2026-09-19",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "estado_general": "OPERATIVO",
    "episodios": {
        "ep02": "Masters v3/v4/v5 consolidados + 4 formatos responsive (16:9, 9:16, 1:1, 4:5) + GIFs preview + HTML5 embed",
        "ep03": "Masters v1/v2 consolidados + 4 formatos responsive (16:9, 9:16, 1:1, 4:5) + GIF preview + HTML5 embed",
        "ep04": "Preproducción 100% (guion v2 auditado P-15, storyboard v2 10 planos, composiciones Wan 2.1, BGM master 180s, thumbnails). Clips Wan 2.1 00 y 01 listos. Planos 02-09 pausados por cuota."
    },
    "patrones_activos": "P-01 a P-52",
    "lecciones_activas": "L-01 a L-38",
    "operation_ids": "45 a 160",
    "agentes_activos": [
        "ALEJAVI (ID=1, Orquestador Supremo)",
        "HBOS NAVIGATOR (ID=2, Navegación Visual Playwright)",
        "HBOS ORCHESTRATOR (ID=3, Selección de Proveedores)",
        "HBOS VAULT (ID=4, Seguridad AES-256-GCM)",
        "HBOS MEMORY (ID=5, Memoria Persistente)",
        "HBOS AUTOMATOR (ID=6, Tareas Desatendidas)",
        "Manus AI (ID=9, Automatización Generalista)",
        "DeepSeek Harness (ID=10, Proveedor Razonamiento MoE)"
    ],
    "cuotas": {
        "elevenlabs": "9 créditos restantes (agotada ciclo mensual)",
        "dashscope": "HTTP 403 FreeTierOnly (agotada en Wan 2.1)",
        "gemini": "HTTP 200 OK (50 modelos activos)",
        "freellmapi": "Instalado portable v0.11.0 en Sandbox (285 archivos)"
    },
    "pendientes": [
        "Reanudar planos 02 al 09 de Ep04 tras renovación de cuota Wan 2.1",
        "Sintetizar voces de Ep04 en ElevenLabs o CosyVoice2",
        "Ensamblado final de Ep04 con ducking P-05 y master -14 LUFS P-04 v2",
        "Generar formatos responsive y kit de thumbnails de Ep04"
    ],
    "hecho_hoy": [
        "Auditoría técnica de cuotas ElevenLabs, DashScope y Gemini (op 89)",
        "Investigación oficial FreeLLMAPI en GitHub (27,312 ⭐, MIT) (op 97)",
        "Actualización Prompt Maestro Paramount v5 con 8 elementos canónicos (op 98)",
        "Actualización Manifiesto Sección 10: Anchors Difusión IA tipo Alejavi (op 103)",
        "Creación de colección diamantino_apps para Agente Navegador (op 114)",
        "Backup Total del sistema previo, snapshot Qdrant y verificación Test-Path (op 115)",
        "Git commit y sincronización total push a origin/main (op 116)",
        "Patrón P-17 v2, P-34 y Lección L-20 de Anchors (op 117)",
        "Diseño de HBOS-API Key Vault, Orquestador y Tareas Automáticas (ops 121-124)",
        "Documentación del problema de 120 hrs/mes por depuración manual y lección L-30 (op 127)",
        "Descarga portable (140.93 MB) y descompresión de FreeLLMAPI v0.11.0 en Sandbox (ops 147-151)",
        "Estandarización de colección diamantino_agentes e indexación de agentes 1 al 6 (ops 147-148)",
        "Documentación e indexación de Manus AI y DeepSeek Harness (ops 155-158)"
    ]
}

text_embedding = (
    f"hbos_estado {payload_estado_hoy['fecha']} {payload_estado_hoy['estado_general']} "
    f"patrones {payload_estado_hoy['patrones_activos']} lecciones {payload_estado_hoy['lecciones_activos'] if 'lecciones_activos' in payload_estado_hoy else payload_estado_hoy['lecciones_activas']} "
    f"ep02 ep03 ep04 {len(payload_estado_hoy['hecho_hoy'])} tareas completadas"
)
vec_hoy = generate_embedding(text_embedding, dim=384)

client.upsert(
    collection_name=col_name,
    points=[
        models.PointStruct(
            id=1,
            vector=vec_hoy,
            payload=payload_estado_hoy
        )
    ]
)
print(f"[OK] Punto de estado ID=1 indexado exitosamente en '{col_name}'.")

# Registrar operation_id = 160 en registro_ecosistema
payload_op160 = {
    "operation_id": 160,
    "tarea": "FASE 1 — CREAR COLECCIÓN hbos_estado (HBOS MEMORY)",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "coleccion": col_name,
    "dimension": 384,
    "metrica": "Cosine",
    "estado_indexado": {
        "fecha": payload_estado_hoy["fecha"],
        "estado_general": payload_estado_hoy["estado_general"],
        "patrones": payload_estado_hoy["patrones_activos"],
        "lecciones": payload_estado_hoy["lecciones_activas"],
        "agentes_activos": len(payload_estado_hoy["agentes_activos"]),
        "hecho_hoy": len(payload_estado_hoy["hecho_hoy"]),
        "pendientes": len(payload_estado_hoy["pendientes"])
    },
    "estado": "COMPLETADO"
}

vec_160 = generate_embedding("Fase 1 operacion 160 Crear Coleccion hbos_estado Memoria Persistente entre Sesiones HBOS Memory", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=160,
            vector=vec_160,
            payload=payload_op160
        )
    ]
)
print("[OK] operation_id = 160 registrado exitosamente en registro_ecosistema.")

col_info = client.get_collection(col_name)
print(f"[OK] Colección '{col_name}': {col_info.points_count} puntos activos en Qdrant Cloud.")
