import os
import sys
import json
import requests
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

# Load .env.local
env_file = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local"
api_key = None
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ELEVENLABS_API_KEY="):
                api_key = line.strip().split("=", 1)[1]

if not api_key:
    print("[ERROR] ELEVENLABS_API_KEY no encontrada")
    sys.exit(1)

text = """Soy Diamantino, anfitrión central de esta presentación.

Permítanme recapitular lo que han visto: siete componentes, una sola red de trabajo agéntica.

Esto no es ciencia ficción — es la infraestructura que NVIDIA ha establecido en GTC Taipei 2026. Vera Rubin GPU, Vera CPU, CUDA Cores, RTX Spark, NVLink 6, ConnectX-9. Todos diseñados para una sola cosa: ejecutar agentes de IA que faciliten las tareas de los humanos.

Los nuevos PCs vendrán con tecnología agéntica integrada. Podrán orquestar agentes automáticamente. Freemium para quienes adquieran los nuevos equipos.

Los humanos ya no ejecutan tareas — orquestan agentes. Esta es la era de la computación para agentes."""

voice_id = "pNInz6obpgDQGcFmaJgB" # Adam
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

payload = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.55,
        "similarity_boost": 0.85,
        "style": 0.30,
        "use_speaker_boost": True
    }
}

print("[*] Sintetizando voz de Diamantino (Bloque 7) con ElevenLabs...")
resp = requests.post(url, json=payload, headers=headers, timeout=60)

if resp.status_code != 200:
    print(f"[ERROR] ElevenLabs HTTP {resp.status_code}: {resp.text}")
    sys.exit(1)

temp_mp3 = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\temp_bloque7.mp3"
with open(temp_mp3, "wb") as f:
    f.write(resp.content)
print(f"[OK] Audio descargado: {len(resp.content)} bytes")

# Output path
target_wav = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\03_Assets\Voces\ep02_voz_diamantino_bloque7.wav"
local_wav = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_voz_diamantino_bloque7.wav"

# Apply loudnorm I=-14, TP=-1.5 and save as 44100Hz stereo pcm_s16le wav
ffmpeg_cmd = [
    "ffmpeg", "-y", "-i", temp_mp3,
    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
    "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
    target_wav
]
print("[*] Normalizando a -14 LUFS / -1.5 TP y convirtiendo a WAV 44.1kHz...")
subprocess.run(ffmpeg_cmd, check=True)

# Also save local copy
subprocess.run(["ffmpeg", "-y", "-i", temp_mp3, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", local_wav], check=True)

# Measure exact duration
ffprobe_cmd = [
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", target_wav
]
duration = float(subprocess.check_output(ffprobe_cmd).decode('utf-8').strip())

print(f"[EXITO] Voz del Bloque 7 guardada en: {target_wav}")
print(f"[+] Duracion exacta de la voz: {duration:.4f} segundos")
with open("bloque7_duracion.json", "w", encoding="utf-8") as f:
    json.dump({"duracion": duration}, f)
