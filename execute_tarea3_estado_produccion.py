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

content_estado = """# ESTADO DE PRODUCCIÓN CANÓNICO — EPISODIO 04: "LA ERA AGÉNTICA EN MEDICINA"
### Ecosistema: HBOS-Diamantino · Arquitectura Agéntica Soberana
### Trazabilidad: `operation_id = 78` · Protocolo Editorial P-17 / Patrón P-18 (Voz Narrativa Única)
### Fecha de Auditoría: 2026-09-19

---

## 1. RESUMEN DE ACTIVOS COMPLETADOS AL 100%

| Componente | Versión / Formato | Ubicación Drive | Ubicación Local | Estado Técnico |
|---|---|---|---|---|
| **Guion Técnico** | v2 (Voz Única Diamantino / Adam) | `01_Guion\guion_v2.md` | `Ep04\01_Guion\guion_v2.md` | ✅ 10 Bloques Bilingües (13,128 caracteres) |
| **Storyboard** | v2 (10 Planos Parametrizados) | `02_Storyboard\storyboard_v2.json` | `Ep04\02_Storyboard\storyboard_v2.json` | ✅ P-14 (Articular) y P-16 (Desplazamiento) |
| **Background** | Bio-cuántico Temático 1080p | `02_Storyboard\backgrounds\` | `Ep04\02_Storyboard\backgrounds\` | ✅ 1920x1080 PNG puro |
| **Composiciones Planos** | 10 Imágenes de Planos | `02_Storyboard\images_wan21\` | `Ep04\02_Storyboard\images_wan21\` | ✅ 10 PNGs 1080p listos para I2V |
| **Thumbnails** | 3 Formatos P-11 | `06_Publicado\thumbnails\` | `Ep04\06_Publicado\thumbnails\` | ✅ 16:9, 9:16 y 1:1 generados |
| **BGM Master** | 180s Cinematográfico | `03_Assets\BGM\ep04_bgm_master.mp3` | `Ep04\03_Assets\BGM\ep04_bgm_master.mp3` | ✅ EBU R128 (-14 LUFS, TP -1.0 dBTP) |
| **Clip Wan 2.1 (Plano 00)** | Nota de Referencia P-17 (5.0s) | `04_Clips_Wan21\ep04_plano_00_wan21.mp4` | `Ep04\04_Clips_Wan21\ep04_plano_00_wan21.mp4` | ✅ Generado en DashScope Cloud (2.57 MB) |
| **Clip Wan 2.1 (Plano 01)** | Diamantino Intro Keynote (20.0s) | `04_Clips_Wan21\ep04_plano_01_wan21.mp4` | `Ep04\04_Clips_Wan21\ep04_plano_01_wan21.mp4` | ✅ Generado en DashScope Cloud (19.92 MB) |

---

## 2. ACTIVOS EN ESPERA DE DESBLOQUEO DE CUOTA

1. **Clips Wan 2.1 (Planos 02 al 09):**
   - **Diagnóstico:** DashScope Cloud retornó `HTTP 403 (AllocationQuota.FreeTierOnly)`.
   - **Causa:** Agotamiento de la asignación gratuita mensual para el modelo `wan2.1-i2v-turbo`.
   - **Restricción:** Prohibido realizar animaciones estáticas locales (`ffmpeg -loop 1`). Se mantiene en espera de render real en nube.
2. **Voz Narrativa Central (Diamantino / Adam):**
   - **Diagnóstico:** ElevenLabs Cloud API retornó `HTTP 401 (quota_exceeded)`.
   - **Causa:** Saldo residual de 21 caracteres frente a ~1,800 caracteres requeridos para los 10 bloques narrativos.
   - **Restricción:** Prohibido utilizar motores TTS locales obsoletos (SAPI).
3. **Ensamblado Técnico Final:**
   - Concatenación de los 10 clips, sincronización con voz off master, mezcla de BGM al 30% y masterización EBU R128 programada para ejecutarse inmediatamente tras la obtención de los clips y el audio en nube.

---

## 3. VÍAS DE DESBLOQUEO DISPONIBLES

- **Opción A (Recomendada para Video):** Recargar créditos en consola Alibaba Cloud DashScope ($5 - $10 USD) o habilitar facturación por consumo (post-pago), eliminando la restricción `FreeTierOnly`.
- **Opción B (Recomendada para Voz):** Actualizar o recargar la suscripción en ElevenLabs ($5 USD / Starter Plan = 30,000 caracteres), suficiente para 5 episodios completos.
- **Opción C (Espera de Ciclo):** Esperar la renovación automática del ciclo gratuito el 1° de octubre.
- **Opción D (Alternativa Cloud sin costo inmediato):** Evaluar Google Cloud Text-to-Speech ($300 créditos gratuitos de bienvenida) para la voz narrativa.
"""

path_local = os.path.join("_MAESTRO", "_ESTADO_PRODUCCION_EP04.md")
path_drive = os.path.join(r"G:\My Drive\HBOS-Diamantino\_MAESTRO", "_ESTADO_PRODUCCION_EP04.md")

os.makedirs(os.path.dirname(path_local), exist_ok=True)
os.makedirs(os.path.dirname(path_drive), exist_ok=True)

with open(path_local, "w", encoding="utf-8") as f:
    f.write(content_estado)
with open(path_drive, "w", encoding="utf-8") as f:
    f.write(content_estado)

print(f"[OK] Documento de estado guardado en {path_local} y sincronizado en Drive")

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)
vec_op78 = generate_embedding("Tarea 3 operacion 78 Estado de Produccion Ep04 Continuidad Auditoria Activos Listos y Bloqueos", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=78,
            vector=vec_op78,
            payload={
                "operation_id": 78,
                "tarea": "TAREA 3 — PREPARAR DOCUMENTO DE CONTINUIDAD",
                "episodio": "Ep04-MedicineAgentica",
                "documento": "_ESTADO_PRODUCCION_EP04.md",
                "ruta_local": path_local,
                "ruta_drive": path_drive,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 78 registrado en registro_ecosistema.")
