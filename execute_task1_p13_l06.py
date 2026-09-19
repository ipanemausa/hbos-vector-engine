import os
import sys
import math
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

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

qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

if not qdrant_url or not qdrant_key:
    print("[!] Credenciales Qdrant no configuradas")
    sys.exit(1)

client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=25)

print(">>> [TAREA 1] Iniciando operacion_id = 66...")

# FASE 1: P-13
p13_codigo = "P-13"
p13_nombre = "La Ventaja es la Creatividad, no el Costo"
p13_desc = "La IA generativa, el hardware y el software tienden a commoditizarse. La ventaja competitiva diferencial es la visión creativa, la narrativa única y la dirección de arte."
vec_p13 = generate_embedding(f"{p13_codigo} {p13_nombre} {p13_desc}", dim=384)

client.upsert(
    collection_name="diamantino_patrones",
    points=[
        models.PointStruct(
            id=13,
            vector=vec_p13,
            payload={
                "codigo": p13_codigo,
                "nombre": p13_nombre,
                "descripcion": p13_desc,
                "operation_id": 66
            }
        )
    ]
)
print("[OK] P-13 registrado en diamantino_patrones (id=13).")

# FASE 2: L-06
l06_codigo = "L-06"
l06_nombre = "Disciplina Diaria da Capacidad"
l06_desc = "El conocimiento no viene del estudio teórico, sino del hacer disciplinado. Cada iteración diaria mejora el sistema."
vec_l06 = generate_embedding(f"{l06_codigo} {l06_nombre} {l06_desc}", dim=384)

client.upsert(
    collection_name="diamantino_lecciones",
    points=[
        models.PointStruct(
            id=6,
            vector=vec_l06,
            payload={
                "codigo": l06_codigo,
                "nombre": l06_nombre,
                "descripcion": l06_desc,
                "operation_id": 66
            }
        )
    ]
)
print("[OK] L-06 registrado en diamantino_lecciones (id=6).")

# FASE 3: Actualizar _MANIFIESTO_HBOS_DIAMANTINO.md
local_manifest = r"_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"
drive_manifest = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"

with open(local_manifest, 'r', encoding='utf-8') as f:
    content = f.read()

seccion_creatividad = """
---

## 5. LA VENTAJA ES LA CREATIVIDAD, NO EL COSTO
La IA generativa, el hardware y el software tienden a commoditizarse. La ventaja competitiva diferencial es la visión creativa, la narrativa única y la dirección de arte.

- **Patrón Canónico:** P-13 (La Ventaja es la Creatividad).
- **Lección Aprendida:** L-06 (Disciplina Diaria da Capacidad). El conocimiento no proviene de la elucubración pasiva, sino del hacer sistemático y la iteración diaria en producción viva.
"""

if "## 5. LA VENTAJA ES LA CREATIVIDAD" not in content:
    content = content.strip() + "\n" + seccion_creatividad

with open(local_manifest, 'w', encoding='utf-8') as f:
    f.write(content)

os.makedirs(os.path.dirname(drive_manifest), exist_ok=True)
with open(drive_manifest, 'w', encoding='utf-8') as f:
    f.write(content)

size_local = os.path.getsize(local_manifest)
size_drive = os.path.getsize(drive_manifest)
print(f"[OK] Manifiesto actualizado. Local: {size_local} bytes, Drive: {size_drive} bytes. Iguales: {size_local == size_drive}")

# Registrar operation_id = 66 en registro_ecosistema
vec_op66 = generate_embedding("Tarea 1 operacion 66 Patrón P-13 y Lección L-06 Manifiesto Creatividad", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=66,
            vector=vec_op66,
            payload={
                "operation_id": 66,
                "tarea": "TAREA 1 — P-13 + L-06 (INSIGHT DE AYER)",
                "p13": {"codigo": p13_codigo, "nombre": p13_nombre},
                "l06": {"codigo": l06_codigo, "nombre": l06_nombre},
                "manifiesto_local": local_manifest,
                "manifiesto_drive": drive_manifest,
                "bytes_verificados": size_local == size_drive,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 66 registrado en registro_ecosistema.")
