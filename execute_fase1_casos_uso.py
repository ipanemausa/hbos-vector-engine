import os
import sys
import json
import time
import math
import hashlib
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

print("==========================================================================")
print(">>> [FASE 1] CREAR MATRIZ DE CASOS DE USO (operation_id=177) <<<")
print("==========================================================================")

collection_name = "diamantino_casos_uso"

# 1. Crear colección si no existe
for attempt in range(1, 4):
    try:
        collections = [c.name for c in client.get_collections().collections]
        if collection_name not in collections:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            print(f"[OK] Colección '{collection_name}' creada en Qdrant con dim 384 (Cosine).")
        else:
            print(f"[*] Colección '{collection_name}' ya existía en Qdrant.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 creando colección: {e}")
        time.sleep(2)

# 2. Definir las 7 tareas HBOS canónicas
tareas_casos = [
    {
        "id": 1,
        "tarea": "generar_voces",
        "modelo_principal": "cosyvoice2",
        "alternativas": ["elevenlabs", "openai_tts"],
        "compresion": "output_compression_on",
        "cuando_usar": "siempre / narraciones de episodios y diálogos de personajes",
        "costo_tokens": "~1500",
        "latencia_seg": "~30",
        "fallback": "elevenlabs",
        "arbitraje": "gratis",
        "operation_id": 177
    },
    {
        "id": 2,
        "tarea": "generar_video",
        "modelo_principal": "dashscope_wan21",
        "alternativas": ["kling_ai", "luma_dream_machine"],
        "compresion": "prompt_optimization_on",
        "cuando_usar": "planos cinematográficos y animación I2V 720p/1080p",
        "costo_tokens": "0 (API video)",
        "latencia_seg": "~60",
        "fallback": "dashscope_wan21_queue",
        "arbitraje": "gratis_freetier / pago",
        "operation_id": 177
    },
    {
        "id": 3,
        "tarea": "generar_imagen",
        "modelo_principal": "nano_banana",
        "alternativas": ["huggingface_sdxl", "flux1_dev"],
        "compresion": "context_deduplication_on",
        "cuando_usar": "storyboard, thumbnails, composiciones de fondo y personajes",
        "costo_tokens": "~500",
        "latencia_seg": "~10",
        "fallback": "huggingface_sdxl",
        "arbitraje": "gratis",
        "operation_id": 177
    },
    {
        "id": 4,
        "tarea": "generar_texto",
        "modelo_principal": "gemini_1_5_flash",
        "alternativas": ["groq_llama_3_3_70b", "deepseek_v3"],
        "compresion": "input_output_compression_r768",
        "cuando_usar": "guiones narrativos, prompts artísticos, análisis técnico y documentación",
        "costo_tokens": "~2000",
        "latencia_seg": "~2",
        "fallback": "groq_llama_3_3_70b",
        "arbitraje": "gratis (50 modelos Free API)",
        "operation_id": 177
    },
    {
        "id": 5,
        "tarea": "verificar_datos",
        "modelo_principal": "deepseek_r1",
        "alternativas": ["gemini_1_5_pro", "qwen_2_5_coder"],
        "compresion": "r768_reasoning_trace_on",
        "cuando_usar": "auditoría de guion P-15, consistencia científica y matemática médica",
        "costo_tokens": "~4000",
        "latencia_seg": "~15",
        "fallback": "gemini_1_5_pro",
        "arbitraje": "gratis",
        "operation_id": 177
    },
    {
        "id": 6,
        "tarea": "traducir",
        "modelo_principal": "groq_llama_3_3_70b",
        "alternativas": ["gemini_1_5_flash", "qwen_2_5"],
        "compresion": "context_deduplication_on",
        "cuando_usar": "localización multilingüe de guiones y subtítulos responsive",
        "costo_tokens": "~1200",
        "latencia_seg": "~1",
        "fallback": "gemini_1_5_flash",
        "arbitraje": "gratis (LPU ultra-fast)",
        "operation_id": 177
    },
    {
        "id": 7,
        "tarea": "ensamblar",
        "modelo_principal": "ffmpeg_pipeline_local",
        "alternativas": ["hbos_automator_script"],
        "compresion": "h264_aac_master_p04",
        "cuando_usar": "renderizado final de video, ducking de audio P-05 y responsive P-07",
        "costo_tokens": "0 (computación local CPU/GPU)",
        "latencia_seg": "~45",
        "fallback": "ffmpeg_pipeline_local",
        "arbitraje": "gratis (local puro)",
        "operation_id": 177
    }
]

# 3. Vectorizar e insertar
points = []
for t in tareas_casos:
    texto_vec = f"{t['tarea']} {t['modelo_principal']} {' '.join(t['alternativas'])} {t['compresion']} {t['cuando_usar']} {t['fallback']} {t['arbitraje']}"
    vec = generate_embedding(texto_vec)
    payload = {k: v for k, v in t.items() if k != 'id'}
    points.append(models.PointStruct(id=t["id"], vector=vec, payload=payload))

for attempt in range(1, 4):
    try:
        client.upsert(collection_name=collection_name, points=points)
        print(f"[OK] {len(points)} tareas de la matriz indexadas y vectorizadas en '{collection_name}'.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 indexando tareas: {e}")
        time.sleep(2)

# 4. Registrar en registro_ecosistema (op 177)
payload_op177 = {
    "operation_id": 177,
    "fase": "FASE 1 — CREAR MATRIZ DE CASOS DE USO",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "coleccion": collection_name,
    "tareas_indexadas": [t["tarea"] for t in tareas_casos],
    "total_tareas": len(tareas_casos),
    "estado": "COMPLETADO"
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=177,
                vector=generate_embedding("Matriz de casos de uso tareas modelos alternativas compresion arbitraje op 177"),
                payload=payload_op177
            )]
        )
        print("[OK] operation_id = 177 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 registrando op 177: {e}")
        time.sleep(2)

# 5. Actualizar hbos_estado
for attempt in range(1, 4):
    try:
        p = client.retrieve("hbos_estado", ids=[1])[0].payload
        p["operation_ids"] = "45 a 177"
        p["hecho_hoy"].append("Matriz de casos de uso (7 tareas) indexada en Qdrant (op 177)")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado op 177"), payload=p)]
        )
        print("[OK] hbos_estado actualizado a op 177.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 actualizando hbos_estado: {e}")
        time.sleep(2)
