import os
import sys
import math
import hashlib
import json
import time
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

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

print("==========================================================================")
print(">>> [TAREA 4] CREAR PATRONES P-53, P-54 Y LECCIONES L-39, L-40 (op 165) <<<")
print("==========================================================================")

# 1. P-53 y P-54 en diamantino_patrones
p53_data = {
    "codigo": "P-53",
    "nombre": "Memoria_Externa_Unificada_HBOS",
    "descripcion": "Estado del sistema consultable en 1 comando. Qdrant almacena estado diario. Script hbos_estado.py consulta en <1 seg. Elimina 120 horas/mes de reconstrucción de contexto.",
    "tipo": "PATRON_CANONICO",
    "operation_id": 165
}

p54_data = {
    "codigo": "P-54",
    "nombre": "R768_Obligatorio",
    "descripcion": "Sin R768: errores (~20-40%) + alucinaciones (~15-30%) + gastos (~$15/mes). Con R768: errores (~1-2%) + alucinaciones (~1-2%) + gastos (~$2/mes). Ahorro: ~87% tokens.",
    "tipo": "PATRON_CANONICO",
    "operation_id": 165
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="diamantino_patrones",
            points=[
                models.PointStruct(id=53, vector=generate_embedding(p53_data["descripcion"]), payload=p53_data),
                models.PointStruct(id=54, vector=generate_embedding(p54_data["descripcion"]), payload=p54_data)
            ]
        )
        print("[OK] P-53 (ID=53) y P-54 (ID=54) insertados en diamantino_patrones.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 en patrones por red: {e}")
        time.sleep(2)

# 2. L-39 y L-40 en diamantino_lecciones
l39_data = {
    "codigo": "L-39",
    "titulo": "Sin_HBOS_MEMORY_120_Horas_Mes_Perdidas",
    "descripcion": "Sin memoria persistente, cada sesión requiere reconstrucción de contexto. 4 horas/día × 30 días = 120 horas/mes.",
    "tipo": "LECCION_APRENDIDA",
    "operation_id": 165
}

l40_data = {
    "codigo": "L-40",
    "titulo": "R768_Previene_Errores_Alucinaciones_Gastos",
    "descripcion": "La factorización R768 es obligatoria en todo prompt. Sin ella: errores, alucinaciones, gastos. Con ella: estabilidad.",
    "tipo": "LECCION_APRENDIDA",
    "operation_id": 165
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="diamantino_lecciones",
            points=[
                models.PointStruct(id=39, vector=generate_embedding(l39_data["descripcion"]), payload=l39_data),
                models.PointStruct(id=40, vector=generate_embedding(l40_data["descripcion"]), payload=l40_data)
            ]
        )
        print("[OK] L-39 (ID=39) y L-40 (ID=40) insertadas en diamantino_lecciones.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 en lecciones por red: {e}")
        time.sleep(2)

# 3. Registrar operation_id = 165 en registro_ecosistema
payload_op165 = {
    "operation_id": 165,
    "tarea": "TAREA 4 — CREAR P-53, P-54, L-39, L-40",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "patrones_nuevos": [
        {"codigo": "P-53", "id": 53, "nombre": p53_data["nombre"]},
        {"codigo": "P-54", "id": 54, "nombre": p54_data["nombre"]}
    ],
    "lecciones_nuevas": [
        {"codigo": "L-39", "id": 39, "titulo": l39_data["titulo"]},
        {"codigo": "L-40", "id": 40, "titulo": l40_data["titulo"]}
    ],
    "rango_actualizado": {
        "patrones": "P-01 a P-54",
        "lecciones": "L-01 a L-40"
    },
    "estado": "COMPLETADO"
}

for attempt in range(1, 4):
    try:
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(
                id=165,
                vector=generate_embedding("Tarea 4 operacion 165 Crear P-53 P-54 L-39 L-40 Memoria R768 Obligatorio"),
                payload=payload_op165
            )]
        )
        print("[OK] operation_id = 165 registrado en registro_ecosistema.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 en registro_ecosistema: {e}")
        time.sleep(2)

# 4. Actualizar punto 1 de hbos_estado para reflejar el nuevo rango P-01 a P-54 y L-01 a L-40
for attempt in range(1, 4):
    try:
        punto = client.retrieve("hbos_estado", ids=[1])[0].payload
        punto["patrones_activos"] = "P-01 a P-54"
        punto["lecciones_activas"] = "L-01 a L-40"
        punto["operation_ids"] = "45 a 165"
        punto["hecho_hoy"].append("Creación de P-53, P-54, L-39, L-40 (op 165)")
        client.upsert(
            collection_name="hbos_estado",
            points=[models.PointStruct(id=1, vector=generate_embedding("hbos_estado P-01 a P-54 L-01 a L-40"), payload=punto)]
        )
        print("[OK] Punto 1 de 'hbos_estado' actualizado con P-01 a P-54 y L-01 a L-40.")
        break
    except Exception as e:
        print(f"[!] Reintento {attempt}/3 actualizando hbos_estado: {e}")
        time.sleep(2)
