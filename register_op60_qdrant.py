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

texto_evento = (
    "Episodio 02 Los 7 Chips Master v3 con Bloque 7 Extra de Diamantino Agéntico. "
    "NVIDIA GTC Taipei 2026 computación para agentes. "
    "9 bloques audiovisuales completos con desplazamiento de host, Wan 2.1 I2V, "
    "audio -14 LUFS EBU R128 y redundancia triple P-03."
)
vec_60 = generate_embedding(texto_evento, dim=384)

payload_meta = {
    "operation_id": 60,
    "evento": "EP02_V3_BLOQUE_7_AGENTICO",
    "episodio": "Ep02 - Los 7 Chips",
    "version": "v3",
    "duracion_total_seg": 209.03,
    "bloque_extra_seg": 52.6164,
    "canales_clips": 9,
    "canales_voces": 9,
    "rutas": {
        "guion_v2": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\01_Guion\guion_v2.md",
        "voz_bloque7": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\03_Assets\Voces\ep02_voz_diamantino_bloque7.wav",
        "clip_bloque7": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\04_Clips_Wan21\ep02_plano_07b_wan21.mp4",
        "voiceover_master_v2": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\03_Assets\Voces\ep02_voiceover_master_v2.wav",
        "master_v3": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v3.mp4",
        "publicado_v3": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\06_Publicado\ep02_publicado_v3.mp4",
        "backup_v3": r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v3.mp4"
    },
    "norma_audio": "EBU R128 -14 LUFS TP -1.5 dBTP",
    "redundancia_triple_p03": True,
    "masters_protegidos": ["v1", "v2", "v3"]
}

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=60,
            vector=vec_60,
            payload=payload_meta
        )
    ]
)
print("[OK] Qdrant Cloud: Point ID 60 registrado en 'registro_ecosistema'.")
