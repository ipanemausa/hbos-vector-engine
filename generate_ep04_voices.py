import os
import sys
import json
import time
import math
import shutil
import hashlib
import requests
import subprocess
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

api_key = os.getenv('ELEVENLABS_API_KEY')
if not api_key:
    print("[ERROR] ELEVENLABS_API_KEY no encontrada")
    sys.exit(1)

print(">>> [FASE 1] Iniciando Síntesis de 10 Voces en ElevenLabs para Ep04 (R775 / P-04 v2)...")

# Mapping de voces canónicas verificadas en cuenta
voice_map = {
    "adam": "pNInz6obpgDQGcFmaJgB",
    "brian": "nPczCjzI2devNBz1zQrb",
    "daniel": "onwK4e9ZLuTAKqWW03F9",
    "bella": "hpp4J3VqNfWAUOO0d1Us",
    "liam": "TX3LPaxmHKxFdv7VOQHJ",
    "callum": "N2lVS1w4EtoT3dr4eOWO",
    "sarah": "EXAVITQu4vr4xnSDxMaL"
}

bloques = [
    {
        "id": "00",
        "personaje": "diamantino_ref",
        "voice_key": "adam",
        "voice_name": "Adam (Autoridad, Placa Editorial)",
        "text": "NOTA DE REFERENCIA: Los descubrimientos presentados en este video son propiedad de sus respectivos autores. AlphaFold y modelos derivados pertenecen a Google DeepMind; el Premio Nobel de Química 2024 a Demis Hassabis, John Jumper y David Baker. HBOS-Diamantino actúa exclusivamente como host y agencia de divulgación científica. Nuestros avatares explican, no descubren."
    },
    {
        "id": "01",
        "personaje": "diamantino_intro",
        "voice_key": "adam",
        "voice_name": "Adam (Host Central)",
        "text": "El nueve de octubre de dos mil veinticuatro, la Real Academia de las Ciencias de Suecia otorgó el Premio Nobel de Química a Demis Hassabis, John Jumper y David Baker. No fue un premio al azar: fue el reconocimiento oficial de que la inteligencia artificial ha descifrado el misterio biológico de cincuenta años del plegamiento proteico. Como Demis Hassabis declaró: AlphaFold es como un telescopio para la biología; la IA es la herramienta definitiva para la ciencia. Bienvenidos a la era agéntica en medicina."
    },
    {
        "id": "02",
        "personaje": "rubin",
        "voice_key": "brian",
        "voice_name": "Brian (Razonamiento / Cómputo Masivo)",
        "text": "Soy Rubín. AlphaFold ha predicho la estructura tridimensional de más de doscientos millones de proteínas: prácticamente todo el catálogo proteico conocido por la humanidad. Lo que antes requería años de cristalografía de rayos X por cada estructura, hoy se resuelve en minutos en clústeres tensoriales acelerados, abriendo la base de datos de libre acceso más monumental de la biología molecular."
    },
    {
        "id": "03",
        "personaje": "zafir",
        "voice_key": "daniel",
        "voice_name": "Daniel (Analítico, Estructuras Genéticas)",
        "text": "Soy Zafir. AlphaMissense ha clasificado setenta y un millones de variantes genéticas humanas, categorizando el ochenta y nueve por ciento de las mutaciones de aminoácidos como benignas o probablemente patogénicas. Y con AlphaProteo, los agentes no solo leen la biología: diseñan proteínas sintéticas de novo con afinidades de unión hasta trescientas veces superiores, dirigidas a combatir virus y factores tumorales."
    },
    {
        "id": "04",
        "personaje": "esmeralda",
        "voice_key": "bella",
        "voice_name": "Bella (Precisión Técnica, Atención Matricial)",
        "text": "Soy Esmeralda. El motor subyacente de AlphaFold combina redes de atención evolutiva con transformadores geométricos en arquitecturas GPU masivas. Millones de operaciones matriciales simultáneas procesan co-evolución de secuencias y coordenadas atómicas euclidianas, demostrando que la biología es un lenguaje, y la inteligencia artificial es el decodificador de su gramática universal."
    },
    {
        "id": "05",
        "personaje": "citrilo",
        "voice_key": "liam",
        "voice_name": "Liam (Entusiasta, Velocidad Farmacológica)",
        "text": "Soy Citrilo. Isomorphic Labs, nacida de DeepMind, traslada este cómputo al descubrimiento directo de fármacos. Con asociaciones estratégicas junto a Eli Lilly y Novartis que superan los tres mil millones de dólares, los agentes químicos reducen el diseño de moléculas candidatas de cinco años a escasos meses, erradicando los callejones sin salida en ensayos preclínicos."
    },
    {
        "id": "06",
        "personaje": "grafito",
        "voice_key": "callum",
        "voice_name": "Callum (Solemne, Acceso Abierto)",
        "text": "Soy Grafito. Más de dos millones de investigadores en ciento noventa países ya utilizan la base de datos de AlphaFold de manera abierta y gratuita. Por primera vez en la historia, las enfermedades huérfanas —aquellas ignoradas por falta de viabilidad comercial— reciben candidatas terapéuticas modeladas por agentes autónomos soberanos."
    },
    {
        "id": "07",
        "personaje": "amatista",
        "voice_key": "sarah",
        "voice_name": "Sarah (Contemplativa, Salud Global)",
        "text": "Soy Amatista. En alianza con la Fundación Gates, el consorcio DNDi y universidades globales, AlphaFold combate la malaria, la tuberculosis y la resistencia antimicrobiana. Estamos en la era de la ciencia asistida por IA, donde enjambres de agentes cristalinos aceleran vacunas y tratamientos en regiones históricamente desatendidas."
    },
    {
        "id": "08",
        "personaje": "diamantino_recap",
        "voice_key": "adam",
        "voice_name": "Adam (Síntesis Agéntica)",
        "text": "Soy Diamantino. Comprendan la magnitud del salto cuántico: el Nobel de dos mil veinticuatro no premió un algoritmo estático, sino la victoria de la inteligencia guiada por principios físicos. La medicina ya no es una disciplina de ensayo y error empírico; es una ciencia de cómputo vectorial predictivo. En la era agéntica, los humanos no memorizan secuencias: los humanos orquestan enjambres de agentes de IA para erradicar el sufrimiento biológico."
    },
    {
        "id": "09",
        "personaje": "diamantino_cierre",
        "voice_key": "adam",
        "voice_name": "Adam (Cierre Ensemble)",
        "text": "Siete componentes. Una sola misión: curar. La biología ha encontrado a su decodificador definitivo. Bienvenidos a HBOS-Diamantino. La transición de la salud hacia una civilización Tipo 5 es ahora imparable."
    }
]

dir_local_voces = r"Ep04\03_Assets\Voces"
dir_drive_voces = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\03_Assets\Voces"
os.makedirs(dir_local_voces, exist_ok=True)
os.makedirs(dir_drive_voces, exist_ok=True)

reporte_voces = []
total_caracteres = 0

for b in bloques:
    vid = voice_map[b["voice_key"]]
    print(f"\n[*] Generando Bloque {b['id']} ({b['personaje']}) con {b['voice_name']}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    payload = {
        "text": b["text"],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.85,
            "style": 0.30,
            "use_speaker_boost": True
        }
    }
    
    total_caracteres += len(b["text"])
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        print(f"[ERROR] Bloque {b['id']} falló (HTTP {resp.status_code}): {resp.text}")
        sys.exit(1)
        
    temp_mp3 = f"temp_ep04_{b['id']}.mp3"
    with open(temp_mp3, "wb") as f:
        f.write(resp.content)
        
    # Normalizar a P-04 v2: -14 LUFS, TP -1.0 dBTP, 44.1kHz estéreo PCM 16-bit
    filename_wav = f"ep04_voz_{b['id']}_{b['personaje']}.wav"
    out_local_wav = os.path.join(dir_local_voces, filename_wav)
    out_drive_wav = os.path.join(dir_drive_voces, filename_wav)
    
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-i", temp_mp3,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
        "-ar", "44100",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        out_local_wav
    ]
    subprocess.run(cmd_ffmpeg, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copyfile(out_local_wav, out_drive_wav)
    
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)
        
    # Medir duración exacta
    ffprobe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", out_local_wav
    ]
    dur = float(subprocess.check_output(ffprobe_cmd).decode('utf-8').strip())
    size = os.path.getsize(out_local_wav)
    
    print(f"[OK] Bloque {b['id']} ({b['personaje']}): {dur:.3f} s | {size} bytes")
    reporte_voces.append({
        "bloque": b["id"],
        "personaje": b["personaje"],
        "voz": b["voice_name"],
        "archivo": filename_wav,
        "duracion_seg": round(dur, 3),
        "bytes": size,
        "ruta_local": out_local_wav,
        "ruta_drive": out_drive_wav
    })
    time.sleep(0.5)

# Guardar duraciones_voces_ep04.json
json_dur_local = os.path.join(dir_local_voces, "duraciones_voces_ep04.json")
json_dur_drive = os.path.join(dir_drive_voces, "duraciones_voces_ep04.json")
with open(json_dur_local, "w", encoding="utf-8") as f:
    json.dump({"total_voces": len(reporte_voces), "total_caracteres": total_caracteres, "voces": reporte_voces}, f, indent=2, ensure_ascii=False)
with open(json_dur_drive, "w", encoding="utf-8") as f:
    json.dump({"total_voces": len(reporte_voces), "total_caracteres": total_caracteres, "voces": reporte_voces}, f, indent=2, ensure_ascii=False)

duracion_total_voces = sum(v["duracion_seg"] for v in reporte_voces)
print(f"\n[ÉXITO FASE 1] 10 Voces generadas y normalizadas (-14 LUFS). Duración acumulada de habla: {duracion_total_voces:.2f} s.")

# Registrar operation_id = 76 en registro_ecosistema
vec_op76 = generate_embedding("Tarea 8 Fase 1 operacion 76 Sintesis 10 Voces ElevenLabs Ep04 Medicina Agentica P-04 v2", dim=384)
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=76,
            vector=vec_op76,
            payload={
                "operation_id": 76,
                "tarea": "TAREA 8 — PRODUCCIÓN EP04 (FASE 1: SÍNTESIS DE VOCES)",
                "episodio": "Ep04-MedicineAgentica",
                "total_voces": 10,
                "caracteres_consumidos": total_caracteres,
                "duracion_total_habla_seg": duracion_total_voces,
                "norma_audio": "EBU R128 -14 LUFS TP -1.0 dBTP",
                "voces_detalle": reporte_voces,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 76 registrado en registro_ecosistema.")
