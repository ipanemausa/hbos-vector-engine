import os
import sys
import json
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

# Estado detallado de Ep04
base_local = "Ep04"
base_drive = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica"

estado_ep04 = {
    "episodio": "Ep04-MedicineAgentica",
    "titulo": "La Era Agéntica en Medicina: Nobel de Química 2024",
    "modelo_narrativo": "Voz Única Narrativa (Diamantino / Adam) con los 7 Hosts Visuales (P-18)",
    "preproduccion_completada": {
        "guion_v2": {
            "local": os.path.exists(os.path.join(base_local, r"01_Guion\guion_v2.md")),
            "drive": os.path.exists(os.path.join(base_drive, r"01_Guion\guion_v2.md"))
        },
        "storyboard_v2": {
            "local": os.path.exists(os.path.join(base_local, r"02_Storyboard\storyboard_v2.json")),
            "drive": os.path.exists(os.path.join(base_drive, r"02_Storyboard\storyboard_v2.json"))
        },
        "background_biocuantico": {
            "local": os.path.exists(os.path.join(base_local, r"02_Storyboard\backgrounds\bg_ep04_biocuantico_1080p.png")),
            "drive": os.path.exists(os.path.join(base_drive, r"02_Storyboard\backgrounds\bg_ep04_biocuantico_1080p.png"))
        },
        "storyboard_10_images_wan21": {
            "local": len(os.listdir(os.path.join(base_local, r"02_Storyboard\images_wan21"))) == 10,
            "drive": len(os.listdir(os.path.join(base_drive, r"02_Storyboard\images_wan21"))) == 10
        },
        "thumbnails_p11": {
            "local": len(os.listdir(os.path.join(base_local, r"06_Publicado\thumbnails"))) == 3,
            "drive": len(os.listdir(os.path.join(base_drive, r"06_Publicado\thumbnails"))) == 3
        },
        "nota_referencia_p17": True,
        "bgm_master_180s": {
            "local": os.path.exists(os.path.join(base_local, r"03_Assets\BGM\ep04_bgm_master.mp3")),
            "drive": os.path.exists(os.path.join(base_drive, r"03_Assets\BGM\ep04_bgm_master.mp3"))
        }
    },
    "clips_wan21_nube": {
        "plano_00": {
            "archivo": "ep04_plano_00_wan21.mp4",
            "duracion": 5.0,
            "estado": "GENERADO_EN_DASHSCOPE_CLOUD",
            "local": os.path.exists(os.path.join(base_local, r"04_Clips_Wan21\ep04_plano_00_wan21.mp4")),
            "drive": os.path.exists(os.path.join(base_drive, r"04_Clips_Wan21\ep04_plano_00_wan21.mp4"))
        },
        "plano_01": {
            "archivo": "ep04_plano_01_wan21.mp4",
            "duracion": 20.0,
            "estado": "GENERADO_EN_DASHSCOPE_CLOUD",
            "local": os.path.exists(os.path.join(base_local, r"04_Clips_Wan21\ep04_plano_01_wan21.mp4")),
            "drive": os.path.exists(os.path.join(base_drive, r"04_Clips_Wan21\ep04_plano_01_wan21.mp4"))
        },
        "planos_02_a_09": {
            "total_pendientes": 8,
            "estado": "PENDIENTE_RECARGA_CUOTA_DASHSCOPE",
            "error_cloud": "AllocationQuota.FreeTierOnly: The free quota has been exhausted."
        }
    },
    "voces_elevenlabs_nube": {
        "estado": "PENDIENTE_RECARGA_CUOTA_ELEVENLABS",
        "error_cloud": "quota_exceeded: 25 credits remaining out of 10000",
        "modelo_listo": "generate_ep04_voices.py listo con guion_v2 (Diamantino/Adam única voz) para síntesis inmediata al recargar"
    },
    "estado_general": "Listo para producir cuando se renueven créditos"
}

# Guardar estado en Ep04
json_estado_local = os.path.join(base_local, "estado_produccion_ep04.json")
json_estado_drive = os.path.join(base_drive, "estado_produccion_ep04.json")

with open(json_estado_local, "w", encoding="utf-8") as f:
    json.dump(estado_ep04, f, indent=2, ensure_ascii=False)
with open(json_estado_drive, "w", encoding="utf-8") as f:
    json.dump(estado_ep04, f, indent=2, ensure_ascii=False)

print(f"[OK] Estado de producción guardado en {json_estado_local} y en Drive")

# Registrar operation_id = 74 en registro_ecosistema
vec_op74 = generate_embedding("Tarea 8 operacion 74 Preparar Ep04 Estado Auditoria Cuotas Nube Listo para Producir", dim=384)
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=74,
            vector=vec_op74,
            payload={
                "operation_id": 74,
                "tarea": "TAREA 8 — PREPARAR EP04 PARA CUANDO SE RENUEVEN CRÉDITOS",
                "episodio": "Ep04-MedicineAgentica",
                "estado": "Listo para producir cuando se renueven créditos",
                "diagnostico_nube": {
                    "elevenlabs": "Cuota agotada (25 créditos restantes de 10,000)",
                    "dashscope": "Cuota FreeTier agotada (AllocationQuota.FreeTierOnly)"
                },
                "assets_completados": [
                    "01_Guion/guion_v2.md (Voz Única P-18)",
                    "02_Storyboard/storyboard_v2.json (10 planos P-14/P-16)",
                    "02_Storyboard/backgrounds/bg_ep04_biocuantico_1080p.png",
                    "02_Storyboard/images_wan21/ (10 composiciones 1080p)",
                    "03_Assets/BGM/ep04_bgm_master.mp3 (180s -14 LUFS)",
                    "04_Clips_Wan21/ep04_plano_00_wan21.mp4 (5s 1080p Nube)",
                    "04_Clips_Wan21/ep04_plano_01_wan21.mp4 (20s 1080p Nube)",
                    "06_Publicado/thumbnails/ (3 thumbnails 16:9, 9:16, 1:1)"
                ]
            }
        )
    ]
)
print("[OK] operation_id = 74 registrado en registro_ecosistema.")
