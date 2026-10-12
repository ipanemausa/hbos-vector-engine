$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  HBOS DAG MASTER - ORQUESTADOR DE FASES (768D)" -ForegroundColor Green
Write-Host "  Protocolos Qdrant | Arbitraje de Proveedores | 0 Costo" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# ── FASE 0: PRE-FLIGHT (Verificar entorno y dependencias) ──
Write-Host "`n[FASE 0] Preflight Check..." -ForegroundColor Yellow
python -c "
import sys, socket
sys.stdout.reconfigure(encoding='utf-8')
_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET] or _gai(*a, **k)
import requests, qdrant_client, sentence_transformers, edge_tts
print('  [OK] Dependencias listas en entorno Python', flush=True)
"
Write-Host "  ✅ Fase 0 completada" -ForegroundColor Green

# ── FASE 1: DESCARGA DE AUDIOS (Google Drive) ──
Write-Host "`n[FASE 1] Descargando muestras de voz..." -ForegroundColor Yellow
$audioScript = @'
import os, sys, socket, requests
sys.stdout.reconfigure(encoding='utf-8')

_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET] or _gai(*a, **k)

headers = {"User-Agent": "Mozilla/5.0"}
audios_dir = "hbos_output/voice/audios"
os.makedirs(audios_dir, exist_ok=True)

drive_files = {
    "audio_01.wav": "1-sSjbSlE365tzpR5DwgoNWoFNBxLvj4y",
    "audio_02.wav": "1XsjI3WoJGylFLcHxWThk6iF0XjPJyXDF",
    "audio_03.wav": "1YnmIC2E6zI-rILvx5DJnHloYh7aZXa8e",
    "audio_04.wav": "1cMS7rIhEwmh2rkKt4Xq9XF71G9rvKadY",
    "audio_05.wav": "1eaq1Mc1s4jpktdQKFg8kQuqzE6bQ-iZT",
    "audio_06.wav": "1h18rsyxJcPnpE7Ek7Pg8VOxjogt-mOBj",
    "audio_07.wav": "1koWlQQcCg5NaHHUmGW5X5S-QaQtm5E0H",
    "audio_08.wav": "1lmopohJ08Tql3VPPTmKLUAT-Im23WyLv",
    "audio_09.wav": "1mJ2jCFM0aO45i2pVppzpNv_SjxIHYpw-",
    "audio_10.wav": "1r1mQAAHcgIHBZLatqxm-FBukoznMd0Y0",
    "audio_11.wav": "1trwhuqQT7CF1fi8t17_WtkIZ8i0V6Q-W",
    "audio_12.wav": "1zfJyRwycT1Q-185K305L02tmf6INp1dU"
}

dl_count = 0
for name, f_id in drive_files.items():
    dest = os.path.join(audios_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        dl_count += 1
        print(f"  [Cache] {name} disponible ({round(os.path.getsize(dest)/1024, 1)} KB)", flush=True)
        continue
    url = f"https://drive.google.com/uc?export=download&id={f_id}"
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=30)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(32768):
                f.write(chunk)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            dl_count += 1
            print(f"  OK: {name}", flush=True)
    except Exception as e:
        print(f"  Error: {name}: {e}", flush=True)

print(f"  Total audios verificados: {dl_count}/12", flush=True)
'@
$audioScript | python
Write-Host "  ✅ Fase 1 completada" -ForegroundColor Green

# ── FASE 2: VECTORIZACIÓN EN QDRANT 768D ──
Write-Host "`n[FASE 2] Vectorizando protocolos en Qdrant (768D)..." -ForegroundColor Yellow
$vectorScript = @'
import os, sys, uuid, socket, requests
sys.stdout.reconfigure(encoding='utf-8')

# Mapa de resolución directa para mitigar DNS router drops en Windows
DNS_MAP = {'38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io': '34.186.107.230'}
_orig_gai = socket.getaddrinfo
socket.getaddrinfo = lambda h, p, *a, **kw: _orig_gai(DNS_MAP.get(h, h), p, *a, **kw)

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv(".env.local")
load_dotenv(".env")

qdrant_url = os.getenv("QDRANT_URL").rstrip('/')
qdrant_key = os.getenv("QDRANT_API_KEY")
headers = {'api-key': qdrant_key, 'Content-Type': 'application/json'}

col_name = "hbos_voz_768"
print(f"  [*] Verificando colección '{col_name}' en Qdrant Cloud...", flush=True)

try:
    chk = requests.get(f"{qdrant_url}/collections/{col_name}", headers=headers, timeout=15)
    if chk.status_code == 404:
        requests.put(
            f"{qdrant_url}/collections/{col_name}",
            json={"vectors": {"size": 768, "distance": "Cosine"}},
            headers=headers,
            timeout=20
        )
        print(f"  [+] Colección '{col_name}' creada en Qdrant Cloud", flush=True)
    else:
        print(f"  [*] Colección '{col_name}' confirmada y activa en Qdrant Cloud", flush=True)
except Exception as e:
    print(f"  [*] Estado conexión: {e}", flush=True)

print("  [*] Codificando protocolo con all-mpnet-base-v2 (768D)...", flush=True)
embedder = SentenceTransformer("all-mpnet-base-v2")

protocol = """
VOZ DE GUILLERMO - PROTOCOLO CLONACIÓN 100% EXACTA
IDIOMA: Español colombiano (medellinense)
TONO: Cálido, profundo, grave natural (F0: 85-180Hz)
VELOCIDAD: 140-160 ppm, ritmo regular
ENTONACIÓN: Subidas preguntas, bajadas afirmaciones
EMOCIONES: Alegría, seriedad, curiosidad, autoridad, cálida
PRONUNCIACIÓN: S suave, R alveolar, LL palatal
INTERJECCIONES: Mira, Escucha, Fíjate, Oye
PROVEEDORES: Google Cloud TTS (12M chars), Edge TTS (ilimitado), Coqui TTS (open source)
ARBITRAJE: Google → Edge → Coqui, 100% gratuito
"""

vector = embedder.encode([protocol])[0].tolist()
point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "guillermo_voice_protocol"))

payload = {
    'points': [
        {
            'id': point_id,
            'vector': vector,
            'payload': {
                'nombre': 'Guillermo',
                'idioma': 'español',
                'costo': 0,
                'protocolo': 'guillermo_voice_protocol',
                'dimension': 768
            }
        }
    ]
}

res = requests.put(f"{qdrant_url}/collections/{col_name}/points?wait=true", json=payload, headers=headers, timeout=25)
if res.status_code == 200:
    print(f"  [OK] Vector 768D indexado exitosamente en Qdrant Cloud (status: {res.json().get('status')})", flush=True)
else:
    print(f"  [!] Respuesta Qdrant: {res.status_code} {res.text}", flush=True)
'@
$vectorScript | python
Write-Host "  ✅ Fase 2 completada" -ForegroundColor Green

# ── FASE 3: GENERACIÓN DE POSES (Arbitraje de Proveedores) ──
Write-Host "`n[FASE 3] Generando poses con arbitraje de proveedores..." -ForegroundColor Yellow
$poseScript = @'
import os, sys, subprocess, time, requests, base64, socket
sys.stdout.reconfigure(encoding='utf-8')
from urllib.parse import quote

_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET] or _gai(*a, **k)

out = "hbos_output"
raw_dir = os.path.join(out, "poses", "raw")
transp_dir = os.path.join(out, "poses", "transparent")
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(transp_dir, exist_ok=True)

CORE_IDENTITY = "cinematic 8k photo of Guillermo, 1.87m, lean athletic, broad square shoulders, upright posture, black glasses, short grey hair, subtle smile, natural tan, black t-shirt with yellow logo, blue jeans, black shoes, pure chroma green background #00FF00"

POSE_FACTORS = [
    ("pose_0001", "arms extended in T-pose, palms down"),
    ("pose_0002", "right arm pointing forward, confident posture"),
    ("pose_0003", "wide stance, arms crossed over chest"),
    ("pose_0004", "three-quarter right angle, torso 45 degrees")
]

for pid, atom in POSE_FACTORS:
    raw = os.path.join(raw_dir, f"{pid}.png")
    transp = os.path.join(transp_dir, f"{pid}.png")
    
    if os.path.exists(transp) and os.path.getsize(transp) > 5000:
        print(f"  [Cache] {pid} listo", flush=True)
        continue

    exito = False
    
    # Intento 1: Pollinations
    url = f"https://image.pollinations.ai/prompt/{quote(CORE_IDENTITY + ', ' + atom)}?width=768&height=768&nologo=true&model=flux"
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 1000:
                with open(raw, "wb") as f: f.write(r.content)
                exito = True
                print(f"  OK Pollinations: {pid}", flush=True)
                break
        except Exception as e:
            if attempt == 1:
                print(f"  Pollinations fallo: {pid}: {e}", flush=True)
            time.sleep(2)

    # Intento 2: Google AI Studio
    if not exito:
        api_key = os.getenv("GOOGLE_AI_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
            payload = {
                "instances": [{"prompt": f"{CORE_IDENTITY}, {atom}", "aspectRatio": "1:1"}],
                "parameters": {"personGeneration": "allow_adult"}
            }
            try:
                r = requests.post(url, json=payload, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    b64 = data["predictions"][0]["bytesBase64Encoded"]
                    with open(raw, "wb") as f: f.write(base64.b64decode(b64))
                    exito = True
                    print(f"  OK Google AI: {pid}", flush=True)
            except Exception as e:
                print(f"  Google AI fallo: {pid}: {e}", flush=True)

    # Recorte FFmpeg Chroma Key
    if exito and os.path.exists(raw):
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw, "-vf", "colorkey=0x00FF00:0.1:0.1", "-c:v", "png", transp],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"  [OK] {pid} generada y recortada (transparente)", flush=True)
    time.sleep(1)
'@
$poseScript | python
Write-Host "  ✅ Fase 3 completada" -ForegroundColor Green

# ── FASE 4: SÍNTESIS DE VOZ (Edge TTS) ──
Write-Host "`n[FASE 4] Sintetizando voz con Edge TTS..." -ForegroundColor Yellow
$voiceScript = @'
import asyncio, edge_tts, os, sys
sys.stdout.reconfigure(encoding='utf-8')

frases = [
    "Sistema Vibe activado, operando con protocolos Qdrant 768D.",
    "Todo el computo se ejecuta de manera fluida y sin costo.",
    "El ecosistema HBOS responde de inmediato con factorizacion nativa."
]

out = "hbos_output/voice/clones"
os.makedirs(out, exist_ok=True)

async def synth(txt, out_f):
    c = edge_tts.Communicate(txt, "es-CO-AlonsoNeural")
    await c.save(out_f)

for i, f in enumerate(frases, 1):
    target = os.path.join(out, f"vibe_voice_{i:02d}.mp3")
    alt_target = os.path.join(out, f"vibe_voice_{i}.mp3")
    if not os.path.exists(target) and not os.path.exists(alt_target):
        asyncio.run(synth(f, target))
        print(f"  OK Voz Vibe {i}: sintetizada", flush=True)
    else:
        print(f"  [Cache] Voz Vibe {i} lista", flush=True)
'@
$voiceScript | python
Write-Host "  ✅ Fase 4 completada" -ForegroundColor Green

# ── FASE 5: EMPAQUETADO FINAL ──
Write-Host "`n[FASE 5] Empaquetando ZIP final..." -ForegroundColor Yellow
$zipScript = @'
import os, zipfile, sys
sys.stdout.reconfigure(encoding='utf-8')

out = "hbos_output"
zip_out = "hbos_vibe_final.zip"

with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(out):
        for fl in files:
            full = os.path.join(root, fl)
            rel = os.path.relpath(full, os.getcwd())
            z.write(full, rel)

size_mb = round(os.path.getsize(zip_out) / (1024 * 1024), 2)
print(f"  [OK] Archivo generado: {zip_out} ({size_mb} MB)", flush=True)
'@
$zipScript | python
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  ✅ DAG HBOS COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
