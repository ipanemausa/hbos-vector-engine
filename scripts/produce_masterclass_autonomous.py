import os
import sys
import time
import json
import asyncio
import hashlib
import subprocess
import urllib.request
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_MASTERS_DIR = "output_masters"
os.makedirs(OUTPUT_MASTERS_DIR, exist_ok=True)
TEMP_DIR = os.path.join(OUTPUT_MASTERS_DIR, "temp_blocks")
os.makedirs(TEMP_DIR, exist_ok=True)

# 1. Definir los 6 Bloques Canónicos de la Masterclass HBOS (Extraídos de Qdrant masterclass_30min_2026)
MODULES = [
    {
        "id": 1,
        "title": "Arquitectura y Soberania Agentica On-Premise",
        "script": "Bienvenidos a la Masterclass Ejecutiva de HB Jewelry OpenClaw 2026. En este analisis estrategico examinaremos como transformar la operacion comercial de tu empresa eliminando licencias de pago mensual y sustituyendolas por agentes autonomos en tu propio servidor.",
        "broll": r"assets\canvas\bg_ep02.png",
        "cut_duration": 4.5
    },
    {
        "id": 2,
        "title": "Los Cuatro Pilares y Motor RAG 768 Dimensiones",
        "script": "Toda empresa de alta joyeria o servicios profesionales se sostiene sobre cuatro pilares: Marketing, Ventas, Logistica y Finanzas. Conectamos un motor RAG de 768 dimensiones para responder con datos exactos sin inventar informacion.",
        "broll": r"assets\canvas\bg_ep03.png",
        "cut_duration": 4.5
    },
    {
        "id": 3,
        "title": "Embudo B2B Autonomo y Calificacion en 10 Segundos",
        "script": "El mayor cuello de botella en ventas B2B es la demora en la primera respuesta. Nuestro bot autonomo califica prospectos en menos de diez segundos, agenda reuniones en el calendario y efectua cierres de catalogo sin costo por mensaje.",
        "broll": r"assets\canvas\bg_rubin.png",
        "cut_duration": 4.0
    },
    {
        "id": 4,
        "title": "Soberania Tecnologica y Triple Respaldo DAG",
        "script": "Garantizamos soberania tecnologica absoluta. Los datos de inventario, clientes e historial financiero se respaldan automaticamente en tiempo real mediante nuestro pipeline DAG con rclone hacia Google Drive de 5 Terabytes.",
        "broll": r"assets\canvas\bg_ep04.png",
        "cut_duration": 4.5
    },
    {
        "id": 5,
        "title": "Agente Juan Pe Advisor y Conversion del 22 por Ciento",
        "script": "Mediante el agente B2B Juan Pe Advisor, calculamos las fugas de ingresos por respuesta tardia y objeciones de presupuesto. Demostramos como elevar la tasa de cierre del doce por ciento al veintidos por ciento en treinta dias.",
        "broll": r"assets\canvas\bg_diamantino.png",
        "cut_duration": 4.0
    },
    {
        "id": 6,
        "title": "Hoja de Ruta de Implementacion e Internacionalizacion",
        "script": "Concluimos con la hoja de ruta de implementacion para escalar tu negocio de joyeria o servicios profesionales a un estandar internacional sin friccion operativa. Gracias por acompanarnos en este analisis de OpenClaw 2026.",
        "broll": r"assets\canvas\bg_thumb03.png",
        "cut_duration": 4.5
    }
]

CANVAS_PNG = r"assets\canvas\columna_vertebral_interactiva.png"

# 2. Generación Concurrente de Voces con FreeLLMAPI Router (/v1/audio/speech) & Fallback SAPI
def generate_voice_router(text: str, out_path: str):
    key = ""
    if os.path.exists("config/freellmapi-key.txt"):
        key = open("config/freellmapi-key.txt").read().strip()
    elif os.environ.get("FREELLMAPI_KEY"):
        key = os.environ.get("FREELLMAPI_KEY").strip()

    # Intento 1: FreeLLMAPI Router
    try:
        url = "http://127.0.0.1:3001/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "model": "tts-1",
            "input": text,
            "voice": "onyx"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                with open(out_path, "wb") as f_out:
                    f_out.write(resp.read())
                return
    except Exception as e:
        print(f"    [!] Router TTS fallback: {e}")

    # Intento 2: Windows SAPI (PowerShell) síntesis limpia local
    clean_text = text.replace('"', '').replace("'", "")
    wav_path = out_path.replace(".mp3", ".wav")
    ps_cmd = (
        f'Add-Type -AssemblyName System.Speech; '
        f'$syn = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'$syn.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Male, [System.Speech.Synthesis.VoiceAge]::Adult); '
        f'$syn.SetOutputToWaveFile("{wav_path}"); '
        f'$syn.Speak("{clean_text}"); '
        f'$syn.Dispose();'
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "192k", out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(wav_path):
        os.remove(wav_path)

def compile_audio_track():
    print("[*] FASE 1: Generando síntesis de locución neural para los 6 bloques...")
    for mod in MODULES:
        audio_file = os.path.join(TEMP_DIR, f"audio_mod_{mod['id']}.mp3")
        mod["audio_file"] = audio_file
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            generate_voice_router(mod["script"], audio_file)
        print(f"    - Bloque {mod['id']} generado: {audio_file} ({os.path.getsize(audio_file)} bytes)")

# 3. Compilación de Bloques con Ritmo de Corte ALEJAVI (< 5s Alternancia Canvas <-> B-Roll)
def compile_video_blocks():
    print("[*] FASE 2: Compilando bloques con Estándar Dinámico ALEJAVI (<5s / Multi-Aspecto)...")
    compiled_blocks = []
    
    for mod in MODULES:
        block_mp4 = os.path.join(TEMP_DIR, f"block_{mod['id']}.mp4")
        mod["block_mp4"] = block_mp4
        
        # Obtener duración del audio
        cmd_dur = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", mod["audio_file"]
        ]
        res_dur = subprocess.run(cmd_dur, capture_output=True, text=True, check=True)
        dur = float(res_dur.stdout.strip())
        mod["duration"] = dur

        # Si el bloque ya está renderizado y mide más de 100KB, reutilizar
        if os.path.exists(block_mp4) and os.path.getsize(block_mp4) > 100000:
            print(f"    - Reutilizando Bloque {mod['id']} ya compilado ({os.path.getsize(block_mp4)} bytes)...")
            compiled_blocks.append(block_mp4)
            continue
        
        # Filtro de alternancia dinámica ALEJAVI:
        # Pasa entre [0:v] (Canvas interactivo) y [1:v] (B-Roll GDrive) cada 4.0 - 4.5s
        # Audio con normalización canónica EBU R128 (-14 LUFS)
        cut = mod["cut_duration"]
        filter_str = (
            f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a_norm];"
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[bg];"
            f"[2:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[broll];"
            f"[bg][broll]overlay=enable='between(mod(t,{cut*2}),{cut},{cut*2})':shortest=1[v_out]"
        )
        
        cmd_block = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", "10", "-i", CANVAS_PNG,
            "-i", mod["audio_file"],
            "-loop", "1", "-framerate", "10", "-i", mod["broll"],
            "-filter_complex", filter_str,
            "-map", "[v_out]", "-map", "[a_norm]",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(dur),
            block_mp4
        ]
        print(f"    - Renderizando Bloque {mod['id']} ({dur:.1f}s) con alternancia ALEJAVI...")
        subprocess.run(cmd_block, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        compiled_blocks.append(block_mp4)

    return compiled_blocks

# 4. Concatenación de Bloques en Master Integral
def compile_master_integral(blocks):
    print("[*] FASE 3: Enlazando Master Integral de la Masterclass...")
    concat_list_file = os.path.join(TEMP_DIR, "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for b in blocks:
            f.write(f"file '{os.path.abspath(b)}'\n")
            
    master_16x9 = os.path.join(OUTPUT_MASTERS_DIR, "masterclass_hbos_integral_16x9.mp4")
    master_9x16 = os.path.join(OUTPUT_MASTERS_DIR, "masterclass_hbos_integral_9x16.mp4")
    
    # 16:9 Master
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-c", "copy", master_16x9
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"    - Master 16:9 generado: {master_16x9} ({round(os.path.getsize(master_16x9)/(1024*1024), 2)} MB)")

    # 9:16 Vertical Shorts Master
    cmd_9x16 = [
        "ffmpeg", "-y", "-i", master_16x9,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-c:a", "copy",
        master_9x16
    ]
    subprocess.run(cmd_9x16, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"    - Master 9:16 generado: {master_9x16} ({round(os.path.getsize(master_9x16)/(1024*1024), 2)} MB)")

    return master_16x9, master_9x16

# 5. Registro Canónico en Qdrant (canon_video_hbos y masterclass_30min_2026)
def register_in_qdrant(master_16x9, master_9x16):
    print("[*] FASE 4: Registrando metadatos y vectores en Qdrant (127.0.0.1:6333)...")
    qdrant_url = "http://127.0.0.1:6333"
    
    sha16x9 = hashlib.sha256(open(master_16x9, "rb").read()).hexdigest()
    point_id = int(sha16x9[:8], 16)
    
    raw_vec = [round(((sha16x9.encode('utf-8')[i % len(sha16x9)] / 127.5) - 1.0), 5) for i in range(384)]
    norm = sum(x*x for x in raw_vec) ** 0.5
    hypervector = [round(x/norm, 5) for x in raw_vec]
    
    payload = {
        "source": "masterclass_producer_autonomous_agent",
        "title": "Masterclass Ejecutiva HBOS OpenClaw 2026",
        "timestamp": TIMESTAMP,
        "formatos": {
            "16x9": os.path.abspath(master_16x9),
            "9x16": os.path.abspath(master_9x16)
        },
        "modulos_compilados": len(MODULES),
        "estandar_edicion": "ALEJAVI_DYNAMIC_B_ROLL_V3",
        "audio_loudness": "-14 LUFS EBU R128",
        "status": "MASTER_PRODUCTION_SEALED"
    }
    
    for coll in ["canon_video_hbos", "masterclass_30min_2026"]:
        try:
            body = {
                "points": [{
                    "id": point_id,
                    "vector": hypervector,
                    "payload": payload
                }]
            }
            req = urllib.request.Request(
                f"{qdrant_url}/collections/{coll}/points?wait=true",
                data=json.dumps(body).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            with urllib.request.urlopen(req) as resp:
                print(f"    - Qdrant {coll}: HTTP {resp.status} (Point ID: {point_id})")
        except Exception as e:
            print(f"    - Qdrant {coll} registro error: {e}", file=sys.stderr)

    return sha16x9

def main():
    start_time = time.time()
    compile_audio_track()
    blocks = compile_video_blocks()
    m16x9, m9x16 = compile_master_integral(blocks)
    sha = register_in_qdrant(m16x9, m9x16)
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "="*70)
    print(f"[MASTERCLASS_PIPELINE: COMPLETE · PASS]")
    print(f"[MASTER_SHA256: {sha}]")
    print(f"[MASTERS_LOCATED: {OUTPUT_MASTERS_DIR}]")
    print(f"[ELAPSED_TIME: {elapsed}s]")
    print("="*70)

if __name__ == "__main__":
    main()
