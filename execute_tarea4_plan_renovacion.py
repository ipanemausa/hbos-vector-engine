import os
import sys
import math
import hashlib
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

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

content_plan = """# PLAN ESTRATÉGICO DE RENOVACIÓN Y EJECUCIÓN (OCTUBRE 2026)
### Ecosistema: HBOS-Diamantino · Arquitectura Agéntica Soberana
### Trazabilidad: `operation_id = 79` · Ciclo Mensual de Cuotas Nube
### Fecha de Emisión: 2026-09-19

---

## 1. CALENDARIO Y VENTANA DE RENOVACIÓN DE CUOTAS NUBE

| Proveedor Nube | Tipo de Cuenta / Asignación | Fecha Estimada de Reseteo | Capacidad Esperada al Renovar |
|---|---|---|---|
| **ElevenLabs Cloud** | Free Tier (10,000 créditos/mes) | 1° de Octubre de 2026 (00:00 UTC) | 10,000 créditos (~20-25 minutos de habla en v2) |
| **Alibaba DashScope** | Free Tier Asignado (Wan 2.1 I2V) | 1° de Octubre de 2026 (00:00 UTC) | ~50-100 segundos de video generativo Wan 2.1 |
| **Google Gemini API** | Free Tier Pay-as-you-go | Diario (Activo continuamente) | Inferencia ilimitada dentro de rate limits |

---

## 2. CAPACIDAD DE PRODUCCIÓN CON CRÉDITOS RENOVADOS

### Con 10,000 créditos en ElevenLabs:
- **Ep04 (Voz Narrativa Única P-18):** Consumo estimado de **~1,800 créditos** (3 minutos de locución con Diamantino / Adam).
- **Margen restante para Ep05 y Ep06:** ~8,200 créditos suficientes para producir 4 episodios completos adicionales bajo el Patrón P-18.

### Con cuota renovada en DashScope (Wan 2.1):
- **Ep04 Planos Pendientes:** 8 clips de 5s base (escalados con cinemática continua P-14 a 20s).
- **Consumo total requerido:** 8 llamadas de inferencia a `wan2.1-i2v-turbo`.

---

## 3. PROTOCOLO DE EJECUCIÓN SECUENCIAL (DÍA DE RENOVACIÓN)

```
[DÍA 1 - HORA 00:05]
│
├── 1. Verificación automática de cuota HTTP 200 en ElevenLabs & DashScope
│
├── 2. Ejecución de `produce_ep04_final.py`:
│   ├── Fase A: Síntesis de la voz narrativa unificada (10 bloques, Adam/Diamantino)
│   ├── Fase B: Normalización acústica EBU R128 (-14 LUFS, TP -1.0 dBTP)
│   ├── Fase C: Despacho concurrente de Planos 02 a 09 en Wan 2.1 I2V Cloud
│   ├── Fase D: Descarga de videos raw y post-procesamiento a 1080p 30fps H.264
│   └── Fase E: Concatenación de los 10 clips + Voiceover + BGM (-14 LUFS, Ducking P-05)
│
├── 3. Generación de los 4 Formatos Responsive (16:9, 9:16, 1:1, 4:5)
│
└── 4. Replicación triple P-03 y publicación oficial
```

---

## 4. PREPARACIÓN ANTICIPADA
Todos los insumos creativos, composiciones 1080p, pistas BGM y scripts de orquestación ya se encuentran programados, probados y listos en local y Google Drive para ejecutarse sin demora en cuanto se detecte saldo en las APIs.
"""

path_local = os.path.join("_MAESTRO", "_PLAN_RENOVACION_OCTUBRE.md")
path_drive = os.path.join(r"G:\My Drive\HBOS-Diamantino\_MAESTRO", "_PLAN_RENOVACION_OCTUBRE.md")

os.makedirs(os.path.dirname(path_local), exist_ok=True)
os.makedirs(os.path.dirname(path_drive), exist_ok=True)

with open(path_local, "w", encoding="utf-8") as f:
    f.write(content_plan)
with open(path_drive, "w", encoding="utf-8") as f:
    f.write(content_plan)

print(f"[OK] Plan de renovación guardado en {path_local} y en Drive")

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)
vec_op79 = generate_embedding("Tarea 4 operacion 79 Plan de Renovacion Octubre 2026 Cuotas ElevenLabs DashScope Hoja de Ruta", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=79,
            vector=vec_op79,
            payload={
                "operation_id": 79,
                "tarea": "TAREA 4 — PREPARAR PLAN DE RENOVACIÓN (1° OCTUBRE)",
                "episodio": "Ep04-MedicineAgentica",
                "documento": "_PLAN_RENOVACION_OCTUBRE.md",
                "ruta_local": path_local,
                "ruta_drive": path_drive,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 79 registrado en registro_ecosistema.")
