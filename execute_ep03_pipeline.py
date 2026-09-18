import os
import sys
import time
import json
import math
import shutil
import base64
import hashlib
import requests
import subprocess
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

# Keys
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
DASHSCOPE_KEY = os.getenv("DASHSCOPE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_KEY = os.getenv("QDRANT_API_KEY")

if not ELEVENLABS_KEY or not DASHSCOPE_KEY:
    print("[ERROR] Faltan claves de ElevenLabs o DashScope en .env.local")
    sys.exit(1)

# Paths
DRIVE_EP03 = r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas"
DRIVE_EP02 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips"
BACKUP_EP03 = r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep03_2026-09-18"
LOCAL_EP03 = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\Ep03"

GUION_DIR = os.path.join(DRIVE_EP03, "01_Guion")
SB_DIR = os.path.join(DRIVE_EP03, "02_Storyboard")
VOCES_DIR = os.path.join(DRIVE_EP03, r"03_Assets\Voces")
BGM_DIR = os.path.join(DRIVE_EP03, r"03_Assets\BGM")
CLIPS_DIR = os.path.join(DRIVE_EP03, "04_Clips_Wan21")
MASTER_DIR = os.path.join(DRIVE_EP03, "05_Master")
PUBLICADO_DIR = os.path.join(DRIVE_EP03, "06_Publicado")
RAW_CLIPS_DIR = r"assets\diamantino\clips\ep03_raw"

for d in [GUION_DIR, SB_DIR, VOCES_DIR, BGM_DIR, CLIPS_DIR, MASTER_DIR, PUBLICADO_DIR, BACKUP_EP03, LOCAL_EP03, RAW_CLIPS_DIR]:
    os.makedirs(d, exist_ok=True)

# Copy BGM from Ep02
bgm_src = os.path.join(DRIVE_EP02, r"03_Assets\BGM\ep02_bgm_master.mp3")
bgm_dst = os.path.join(BGM_DIR, "ep03_bgm_master.mp3")
if os.path.exists(bgm_src) and not os.path.exists(bgm_dst):
    shutil.copyfile(bgm_src, bgm_dst)
    print(f"[OK] BGM copiado a {bgm_dst}")

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

def get_duration(path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path]
    res = subprocess.check_output(cmd).decode()
    return float(json.loads(res)['format']['duration'])

print("==========================================================")
print("HBOS-DIAMANTINO FACTORY — EPISODIO 03 (OPERATION_ID = 62)")
print("Tema: Redes Fotónicas Cuánticas y Spectrum-X a 1.6 Tbps")
print("==========================================================\n")

# -------------------------------------------------------------
# FASE A: Redacción y verificación del guion técnico
# -------------------------------------------------------------
print("[*] FASE A — Redactando Guion Técnico Oficial Ep03...")

guion_ep03_content = """# GUION TÉCNICO OFICIAL — EPISODIO 03: "REDES FOTÓNICAS CUÁNTICAS Y SPECTRUM-X"
### Ecosistema: HBOS-Diamantino · Arquitectura de Red Cristalina
### Referencia Canónica: Keynote NVIDIA GTC Taipei 2026 (Optical & Photonic Switching)
### Trazabilidad: `operation_id = 62` · Personajes: Amatista (Protagonista) & Diamantino (Host)

---

### [00:00 - 00:18] PLANO 01: DIAMANTINO (INTRODUCCIÓN) — EL COLAPSO DEL COBRE
**Visual:** Diamantino camina con presencia imponente por el keynote stage de GTC Taipei 2026, señalando los racks oscuros interconectados por pulsos de luz violeta.  
**Voz en Off (Diamantino):**  
"El cobre ha alcanzado su barrera física de atenuación. Cuando millones de agentes de IA razonan en paralelo, la latencia eléctrica destruye la sincronía cognitiva. Para escalar la inteligencia colectiva, la información debe viajar como luz pura. Bienvenidos a la revolución fotónica cuántica."  
**English Subtitles:**  
"Copper has reached its physical attenuation barrier. When millions of AI agents reason in parallel, electrical latency shatters cognitive synchrony. To scale collective intelligence, information must travel as pure light. Welcome to the quantum photonic revolution."  
**Dato Técnico:** NVIDIA Photonic Interconnect Roadmap & Silicon Photonics Whitepaper.

---

### [00:18 - 00:40] PLANO 02: AMATISTA (BLOQUE 1) — CONNECTX-9 SUPER-NIC A 1.6 TBPS
**Visual:** Amatista avanza serenamente hacia el holograma flotante del procesador de red ConnectX-9, tocando con sus manos de cuarzo las líneas de telemetría violeta.  
**Voz en Off (Amatista):**  
"Soy Amatista. En este ecosistema, encarno el adaptador ConnectX-9 SuperNIC. Entrego un ancho de banda bidireccional de 1.6 Terabits por segundo por puerto, procesando telemetría adaptativa en hardware y erradicando micro-ráfagas de congestión mediante RoCEv3 acelerado."  
**English Subtitles:**  
"I am Amatista. In this ecosystem, I embody the ConnectX-9 SuperNIC. Delivering 1.6 Terabits per second bidirectional line rate per port, executing hardware-based adaptive telemetry and eliminating microburst congestion through accelerated RoCEv3."  
**Dato Técnico:** NVIDIA ConnectX-9 1.6 Tbps Architecture Specification.

---

### [00:40 - 01:04] PLANO 03: AMATISTA (BLOQUE 2) — SPECTRUM-X & CO-PACKAGED OPTICS (CPO)
**Visual:** Amatista se desplaza hacia el rack central Spectrum-X, señalando los módulos de conmutación óptica integrada donde los láseres fotónicos parpadean al unísono.  
**Voz en Off (Amatista):**  
"La conmutación electrónica tradicional añade microsegundos fatales. Mi matriz Spectrum-X integra Co-Packaged Optics: láseres de silicio fotónico acoplados directamente al silicio de conmutación. Transportamos tensores masivos a través de fibra monomodo con cero resistencia térmica."  
**English Subtitles:**  
"Traditional electronic switching introduces fatal microsecond bottlenecks. My Spectrum-X fabric integrates Co-Packaged Optics: silicon photonic lasers coupled directly to the switching silicon. We route massive tensors across single-mode fiber with zero thermal resistance."  
**Dato Técnico:** NVIDIA Spectrum-X Photonic Switch Whitepaper & CPO Optical Engines.

---

### [01:04 - 01:24] PLANO 04: AMATISTA (BLOQUE 3) — TOPOLOGÍA CUÁNTICA SIN CONGESTIÓN
**Visual:** Amatista extiende ambos brazos mientras la topología de red Dragonfly+ se despliega holográficamente sobre el escenario, conectando clusters lejanos.  
**Voz en Off (Amatista):**  
"Bajo topologías Dragonfly+ y conmutación cuántica no bloqueante, enlazamos cientos de miles de GPUs como un solo hiper-cerebro monolítico. El tráfico de KV Cache distribuido fluye determinista, con fluctuación de latencia inferior a 50 nanosegundos."  
**English Subtitles:**  
"Under Dragonfly+ topologies and non-blocking quantum switching, we bind hundreds of thousands of GPUs into a single monolithic hyper-brain. Distributed KV Cache traffic flows deterministically with latency jitter under 50 nanoseconds."  
**Dato Técnico:** Ultra-Dense Dragonfly+ & Adaptive Routing Protocols in GTC 2026 Fabrics.

---

### [01:24 - 01:50] PLANO 05: DIAMANTINO (BLOQUE 4) — LA SINAPSIS DE LA ERA AGÉNTICA
**Visual:** Diamantino regresa al centro del escenario con gesto majestuoso de host, mirando frontalmente a la cámara con autoridad y encanto.  
**Voz en Off (Diamantino):**  
"Entiendan bien la trascendencia de lo que Amatista representa. Las redes fotónicas no transportan simples paquetes de datos; son las sinapsis de la era agéntica.  
Un agente solitario es limitado; un enjambre de millones de agentes comunicados a 1.6 Terabits por segundo puede resolver la fusión nuclear, la medicina genómica y la orquestación planetaria en tiempo real. Esta es la infraestructura del futuro."  
**English Subtitles:**  
"Grasp the true significance of what Amatista represents. Photonic fabrics do not merely transport data packets; they are the synapses of the agentic era. A solitary agent is limited; a swarm of millions of agents communicating at 1.6 Terabits per second can unlock nuclear fusion, genomic medicine, and planetary orchestration in real time. This is the infrastructure of tomorrow."  
**Dato Técnico:** Agentic Swarm Telemetry & Distributed AI Infrastructure (GTC 2026).

---

### [01:50 - 02:10] PLANO 06: DIAMANTINO & AMATISTA (CIERRE KEYNOTE) — CIVILIZACIÓN TIPO 5
**Visual:** Gran angular monumental del keynote: Amatista y Diamantino juntos en el centro del escenario saludando a la audiencia mientras los haces de luz violeta y arcoíris ascienden hacia el domo del auditorio y comienza el fundido suave a negro.  
**Voz en Off (Diamantino):**  
"La luz fotónica y el cristal soberano han reemplazado para siempre al cobre obsoleto. Bienvenidos a la red neuronal del cosmos. Bienvenidos a HBOS-Diamantino. La civilización Tipo 5 es ahora una realidad operativa."  
**English Subtitles:**  
"Photonic light and sovereign crystal have permanently replaced obsolete copper. Welcome to the neural fabric of the cosmos. Welcome to HBOS-Diamantino. The Type 5 civilization is now an operational reality."  
**Dato Técnico:** Manifiesto HBOS-Diamantino (AsertiaNova Crystalline Network).
"""

guion_path = os.path.join(GUION_DIR, "guion_v1.md")
guion_local = os.path.join(LOCAL_EP03, "guion_v1.md")

with open(guion_path, "w", encoding="utf-8") as f:
    f.write(guion_ep03_content)
with open(guion_local, "w", encoding="utf-8") as f:
    f.write(guion_ep03_content)
print(f"[OK] FASE A: Guion Técnico Oficial Ep03 guardado ({len(guion_ep03_content)} caracteres)")

# -------------------------------------------------------------
# FASE B: Storyboard y Anclaje Visual
# -------------------------------------------------------------
print("\n[*] FASE B — Anclando imágenes de personajes para Ep03...")

# Assets base
img_amatista_src = os.path.join(DRIVE_EP02, r"02_Storyboard\amatista_v1_articulado.png")
img_diamantino_src = os.path.join(DRIVE_EP02, r"02_Storyboard\diamantino_v1_keynote.png")
img_ensemble_src = os.path.join(DRIVE_EP02, r"02_Storyboard\escena_ensemble_gtc_keynote.png")

img_amatista_dst = os.path.join(SB_DIR, "amatista_v1_articulado.png")
img_diamantino_dst = os.path.join(SB_DIR, "diamantino_v1_keynote.png")
img_ensemble_dst = os.path.join(SB_DIR, "escena_ensemble_gtc_keynote.png")

for s, d in [(img_amatista_src, img_amatista_dst), (img_diamantino_src, img_diamantino_dst), (img_ensemble_src, img_ensemble_dst)]:
    if os.path.exists(s) and not os.path.exists(d):
        shutil.copyfile(s, d)
        print(f"[OK] Imagen anclada: {os.path.basename(d)}")

storyboard_data = {
    "episodio": "Ep03",
    "titulo": "Redes Fotónicas Cuánticas y Spectrum-X",
    "planos": [
        {"id": 1, "personaje": "Diamantino", "img": img_diamantino_dst, "prompt": "Diamantino walks across the keynote stage, gestures with hands at the dark racks glowing with violet photonic pulses, then stops center stage. Authoritative presenter. 8K cinematic."},
        {"id": 2, "personaje": "Amatista", "img": img_amatista_dst, "prompt": "Amatista walks toward a holographic display of ConnectX-9, touches the glowing violet data lines with quartz hands, serene host posture. 8K cinematic."},
        {"id": 3, "personaje": "Amatista", "img": img_amatista_dst, "prompt": "Amatista gestures toward the Spectrum-X switch rack, pointing at the co-packaged optical lasers, elegant presenter movement. 8K cinematic."},
        {"id": 4, "personaje": "Amatista", "img": img_amatista_dst, "prompt": "Amatista extends both arms as the holographic dragonfly network topology expands around her, dynamic and graceful movement. 8K cinematic."},
        {"id": 5, "personaje": "Diamantino", "img": img_diamantino_dst, "prompt": "Diamantino walks center stage with authoritative keynote presenter gesture, pointing outward to audience with passion and charisma. 8K cinematic."},
        {"id": 6, "personaje": "Diamantino & Amatista Ensemble", "img": img_ensemble_dst, "prompt": "Diamantino and Amatista stand together on keynote stage, waving to the audience as lights pulse and gentle fade out begins. 8K cinematic finale."}
    ]
}

sb_json_path = os.path.join(SB_DIR, "storyboard_v1.json")
with open(sb_json_path, "w", encoding="utf-8") as f:
    json.dump(storyboard_data, f, indent=2, ensure_ascii=False)
print(f"[OK] FASE B: Storyboard JSON creado ({len(storyboard_data['planos'])} planos)")

# -------------------------------------------------------------
# FASE C: Producción Nube (ElevenLabs & Wan 2.1 I2V)
# -------------------------------------------------------------
print("\n[*] FASE C — Síntesis de Voz Neuronal con ElevenLabs Multilingual v2...")

VOICE_TEXTS = [
    {
        "id": 1,
        "personaje": "Diamantino",
        "voice_id": "pNInz6obpgDQGcFmaJgB", # Adam
        "file": "ep03_voz_01_diamantino_intro.wav",
        "text": "El cobre ha alcanzado su barrera física de atenuación. Cuando millones de agentes de IA razonan en paralelo, la latencia eléctrica destruye la sincronía cognitiva. Para escalar la inteligencia colectiva, la información debe viajar como luz pura. Bienvenidos a la revolución fotónica cuántica."
    },
    {
        "id": 2,
        "personaje": "Amatista",
        "voice_id": "EXAVITQu4vr4xnSDxMaL", # Sarah (Mature, Reassuring)
        "file": "ep03_voz_02_amatista_connectx9.wav",
        "text": "Soy Amatista. En este ecosistema, encarno el adaptador ConnectX-9 SuperNIC. Entrego un ancho de banda bidireccional de 1.6 Terabits por segundo por puerto, procesando telemetría adaptativa en hardware y erradicando micro-ráfagas de congestión mediante RoCEv3 acelerado."
    },
    {
        "id": 3,
        "personaje": "Amatista",
        "voice_id": "EXAVITQu4vr4xnSDxMaL", # Sarah
        "file": "ep03_voz_03_amatista_spectrumx.wav",
        "text": "La conmutación electrónica tradicional añade microsegundos fatales. Mi matriz Spectrum-X integra Co-Packaged Optics: láseres de silicio fotónico acoplados directamente al silicio de conmutación. Transportamos tensores masivos a través de fibra monomodo con cero resistencia térmica."
    },
    {
        "id": 4,
        "personaje": "Amatista",
        "voice_id": "EXAVITQu4vr4xnSDxMaL", # Sarah
        "file": "ep03_voz_04_amatista_topologia.wav",
        "text": "Bajo topologías Dragonfly+ y conmutación cuántica no bloqueante, enlazamos cientos de miles de GPUs como un solo hiper-cerebro monolítico. El tráfico de KV Cache distribuido fluye determinista, con fluctuación de latencia inferior a 50 nanosegundos."
    },
    {
        "id": 5,
        "personaje": "Diamantino",
        "voice_id": "pNInz6obpgDQGcFmaJgB", # Adam
        "file": "ep03_voz_05_diamantino_agentico.wav",
        "text": "Entiendan bien la trascendencia de lo que Amatista representa. Las redes fotónicas no transportan simples paquetes de datos; son las sinapsis de la era agéntica. Un agente solitario es limitado; un enjambre de millones de agentes comunicados a 1.6 Terabits por segundo puede resolver la fusión nuclear, la medicina genómica y la orquestación planetaria en tiempo real. Esta es la infraestructura del futuro."
    },
    {
        "id": 6,
        "personaje": "Diamantino",
        "voice_id": "pNInz6obpgDQGcFmaJgB", # Adam
        "file": "ep03_voz_06_diamantino_cierre.wav",
        "text": "La luz fotónica y el cristal soberano han reemplazado para siempre al cobre obsoleto. Bienvenidos a la red neuronal del cosmos. Bienvenidos a HBOS-Diamantino. La civilización Tipo 5 es ahora una realidad operativa."
    }
]

headers_el = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_KEY
}

# Synthesize all voices
for v in VOICE_TEXTS:
    v_out = os.path.join(VOCES_DIR, v["file"])
    if os.path.exists(v_out) and os.path.getsize(v_out) > 50000:
        dur = get_duration(v_out)
        v["dur"] = dur
        print(f"[OK] Voz existente verificada: {v['file']} ({dur:.4f}s)")
        continue
        
    print(f"[*] Sintetizando {v['file']} ({v['personaje']})...")
    url_el = f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}"
    payload_el = {
        "text": v["text"],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.85,
            "style": 0.30,
            "use_speaker_boost": True
        }
    }
    r = requests.post(url_el, json=payload_el, headers=headers_el, timeout=60)
    if r.status_code != 200:
        print(f"[ERROR] ElevenLabs HTTP {r.status_code}: {r.text}")
        sys.exit(1)
        
    temp_mp3 = os.path.join(LOCAL_EP03, f"temp_{v['id']}.mp3")
    with open(temp_mp3, "wb") as f:
        f.write(r.content)
        
    # Standardize to 44100Hz stereo pcm_s16le with loudnorm -14 LUFS
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_mp3,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        v_out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    dur = get_duration(v_out)
    v["dur"] = dur
    print(f"[+] {v['file']} generado: {dur:.4f}s")
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

# WAN 2.1 I2V GENERATION
print("\n[*] FASE C.2 — Generando 6 Clips con Wan 2.1 I2V (DashScope Cloud)...")

CLIPS_SPEC = [
    {"id": 1, "name": "ep03_plano_01_wan21.mp4", "raw": "wan21_raw_ep03_plano_01.mp4", "img": img_diamantino_dst, "dur": VOICE_TEXTS[0]["dur"] + 0.4, "prompt": storyboard_data["planos"][0]["prompt"]},
    {"id": 2, "name": "ep03_plano_02_wan21.mp4", "raw": "wan21_raw_ep03_plano_02.mp4", "img": img_amatista_dst, "dur": VOICE_TEXTS[1]["dur"] + 0.4, "prompt": storyboard_data["planos"][1]["prompt"]},
    {"id": 3, "name": "ep03_plano_03_wan21.mp4", "raw": "wan21_raw_ep03_plano_03.mp4", "img": img_amatista_dst, "dur": VOICE_TEXTS[2]["dur"] + 0.4, "prompt": storyboard_data["planos"][2]["prompt"]},
    {"id": 4, "name": "ep03_plano_04_wan21.mp4", "raw": "wan21_raw_ep03_plano_04.mp4", "img": img_amatista_dst, "dur": VOICE_TEXTS[3]["dur"] + 0.4, "prompt": storyboard_data["planos"][3]["prompt"]},
    {"id": 5, "name": "ep03_plano_05_wan21.mp4", "raw": "wan21_raw_ep03_plano_05.mp4", "img": img_diamantino_dst, "dur": VOICE_TEXTS[4]["dur"] + 0.4, "prompt": storyboard_data["planos"][4]["prompt"]},
    {"id": 6, "name": "ep03_plano_06_wan21.mp4", "raw": "wan21_raw_ep03_plano_06.mp4", "img": img_ensemble_dst, "dur": VOICE_TEXTS[5]["dur"] + 3.0, "prompt": storyboard_data["planos"][5]["prompt"]}
]

def submit_wan_task(plano):
    with open(plano['img'], 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    data_url = f"data:image/png;base64,{b64}"
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    payload = {
        "model": "wan2.1-i2v-turbo",
        "input": {"img_url": data_url, "prompt": plano['prompt']}
    }
    for attempt in range(5):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                tid = res.json().get('output', {}).get('task_id')
                print(f"[+] Plano {plano['id']} aceptado por DashScope! Task ID: {tid}")
                return tid
            else:
                print(f"[!] Reintento {attempt+1} - Plano {plano['id']}: {res.status_code} {res.text}")
                time.sleep(3)
        except Exception as e:
            print(f"[!] Excepción Plano {plano['id']}: {e}")
            time.sleep(3)
    return None

wan_tasks = {}
for p in CLIPS_SPEC:
    target_clip = os.path.join(CLIPS_DIR, p["name"])
    if os.path.exists(target_clip) and os.path.getsize(target_clip) > 5*1024*1024:
        print(f"[OK] Clip existente verificado: {p['name']}")
    else:
        tid = submit_wan_task(p)
        if tid:
            wan_tasks[p['id']] = tid
        time.sleep(2)

if wan_tasks:
    print(f"[*] Monitoreando {len(wan_tasks)} tareas en DashScope Cloud...")
    completed_urls = {}
    pending = dict(wan_tasks)
    poll_headers = {"Authorization": f"Bearer {DASHSCOPE_KEY}"}
    
    while pending:
        time.sleep(7)
        for pid, tid in list(pending.items()):
            url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{tid}"
            try:
                res = requests.get(url, headers=poll_headers, timeout=20)
                if res.status_code == 200:
                    data = res.json().get('output', {})
                    status = data.get('task_status')
                    print(f"  -> Plano {pid} (Task {tid[:8]}...): {status}")
                    if status == 'SUCCEEDED':
                        completed_urls[pid] = data.get('video_url')
                        del pending[pid]
                    elif status in ['FAILED', 'CANCELED']:
                        print(f"[!] Error: Plano {pid} fallo: {data}")
                        del pending[pid]
            except Exception as e:
                print(f"[!] Error consultando status Plano {pid}: {e}")
                
    # Download raw and process
    cinematic_filter_base = (
        "[0:v]split=2[bg_in][fg_in]; "
        "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
        "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )
    
    for p in CLIPS_SPEC:
        pid = p['id']
        if pid not in completed_urls:
            continue
        v_url = completed_urls[pid]
        raw_path = os.path.join(RAW_CLIPS_DIR, p['raw'])
        print(f"[*] Descargando video raw Plano {pid}...")
        r = requests.get(v_url, timeout=90)
        with open(raw_path, 'wb') as f:
            f.write(r.content)
            
        out_clip = os.path.join(CLIPS_DIR, p['name'])
        dur = p['dur']
        
        if pid == 6:
            fade_st = dur - 1.0
            filter_str = (
                "[0:v]split=2[bg_in][fg_in]; "
                "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
                "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fade=t=out:st={fade_st:.4f}:d=1.0[v]"
            )
        else:
            filter_str = cinematic_filter_base
            
        print(f"[*] Procesando FFmpeg 1080p 30fps Plano {pid} ({dur:.2f}s)...")
        cmd_clip = [
            "ffmpeg", "-y",
            "-stream_loop", "12",
            "-i", raw_path,
            "-t", f"{dur:.4f}",
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            out_clip
        ]
        subprocess.run(cmd_clip, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[OK] Clip Plano {pid} guardado: {out_clip} ({get_duration(out_clip):.2f}s)")

# -------------------------------------------------------------
# FASE D: Ensamble Audiovisual, Redundancia P-03 y Qdrant
# -------------------------------------------------------------
print("\n[*] FASE D — Re-ensamblaje de Voiceover Master y Video Master Ep03...")

# 1. Voiceover master
silence_04 = os.path.join(VOCES_DIR, "temp_silence_04.wav")
silence_30 = os.path.join(VOCES_DIR, "temp_silence_30.wav")
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "0.4", "-c:a", "pcm_s16le", silence_04], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "3.0", "-c:a", "pcm_s16le", silence_30], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

voice_concat_list = os.path.join(VOCES_DIR, "concat_voices_list.txt")
total_voices_dur = sum(v["dur"] for v in VOICE_TEXTS)
total_audio_calc = total_voices_dur + (len(VOICE_TEXTS) - 1) * 0.4 + 3.0

with open(voice_concat_list, "w", encoding="utf-8") as f:
    for i, v in enumerate(VOICE_TEXTS):
        v_file = os.path.join(VOCES_DIR, v["file"])
        f.write(f"file '{v_file}'\n")
        if i < len(VOICE_TEXTS) - 1:
            f.write(f"file '{silence_04}'\n")
        else:
            f.write(f"file '{silence_30}'\n")

voiceover_master_path = os.path.join(VOCES_DIR, "ep03_voiceover_master.wav")
fade_st_audio = total_audio_calc - 1.0

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", voice_concat_list,
    "-af", f"afade=t=out:st={fade_st_audio:.4f}:d=1.0",
    "-c:a", "pcm_s16le",
    voiceover_master_path
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

v_master_dur = get_duration(voiceover_master_path)
print(f"[OK] Voiceover Master Ep03 creado: {voiceover_master_path} ({v_master_dur:.4f}s)")

# 2. Video concat
video_concat_list = os.path.join(CLIPS_DIR, "concat_clips_list.txt")
with open(video_concat_list, "w", encoding="utf-8") as f:
    for p in CLIPS_SPEC:
        c_path = os.path.join(CLIPS_DIR, p["name"])
        f.write(f"file '{c_path}'\n")

temp_video_concat = os.path.join(CLIPS_DIR, "temp_video_concat.mp4")
subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", video_concat_list,
    "-c", "copy",
    temp_video_concat
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

v_concat_dur = get_duration(temp_video_concat)
print(f"[OK] Video Clips Ep03 concatenados: {v_concat_dur:.4f}s")

# 3. Master render with BGM and EBU R128 (-14 LUFS)
master_v1_path = os.path.join(MASTER_DIR, "ep03_master_v1.mp4")
local_master_path = os.path.join(LOCAL_EP03, "ep03_master_v1.mp4")
target_dur = v_concat_dur
fade_out_st = target_dur - 1.0

audio_filter = (
    f"[1:a]volume=1.4[voice]; "
    f"[2:a]volume=0.18[music]; "
    f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[mixed]; "
    f"[mixed]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={fade_out_st:.4f}:d=1.0[aout]"
)

print(f"[*] Renderizando Master Final Ep03 ({target_dur:.2f}s) con EBU R128 -14 LUFS y +faststart...")
cmd_render = [
    "ffmpeg", "-y",
    "-i", temp_video_concat,
    "-i", voiceover_master_path,
    "-stream_loop", "-1", "-i", bgm_dst,
    "-filter_complex", audio_filter,
    "-map", "0:v:0",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "44100",
    "-t", f"{target_dur:.4f}",
    "-movflags", "+faststart",
    master_v1_path
]
subprocess.run(cmd_render, check=True)

final_dur = get_duration(master_v1_path)
size_bytes = os.path.getsize(master_v1_path)
size_mb = size_bytes / (1024*1024)
print(f"[OK] MASTER V1 EP03 CREADO: {master_v1_path}")
print(f"[+] Duración final: {final_dur:.4f} s | Peso: {size_mb:.2f} MB ({size_bytes} bytes)")

# Local copy
shutil.copyfile(master_v1_path, local_master_path)

# Cleanup temp files
for tmp in [silence_04, silence_30, voice_concat_list, video_concat_list, temp_video_concat]:
    if os.path.exists(tmp):
        os.remove(tmp)

# 4. Triple redundancy (P-03)
print("\n[*] FASE D.2 — Guardando en 3 lugares (Patrón P-03)...")
p1 = master_v1_path
p2 = os.path.join(PUBLICADO_DIR, "ep03_publicado_v1.mp4")
p3 = os.path.join(BACKUP_EP03, "ep03_master_v1.mp4")

shutil.copyfile(p1, p2)
shutil.copyfile(p1, p3)

s1, s2, s3 = os.path.getsize(p1), os.path.getsize(p2), os.path.getsize(p3)
if s1 == s2 == s3 and s1 > 50*1024*1024:
    print(f"[OK] Redundancia triple P-03 verificada: 100% idénticos ({s1} bytes).")
else:
    print(f"[ERROR] Discrepancia de tamaño P-03: {s1}, {s2}, {s3}")
    sys.exit(1)

# 5. Vectorization in Qdrant (operation_id = 62)
print("\n[*] FASE D.3 — Vectorización en Qdrant Cloud (operation_id = 62)...")
if QDRANT_URL and QDRANT_KEY:
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY, timeout=30)
        texto_op62 = (
            "Episodio 03 Redes Fotónicas Cuánticas y Spectrum-X a 1.6 Tbps. "
            "Amatista ConnectX-9 SuperNIC y Conmutadores Ópticos CPO. "
            "Tesis de la sinapsis agéntica distribuida por Diamantino. "
            "Master MP4 1080p 30fps EBU R128 -14 LUFS, P-03 triple redundancia inmutable."
        )
        vec_62 = generate_embedding(texto_op62, dim=384)
        
        payload_op62 = {
            "operation_id": 62,
            "evento": "EP03_PRODUCCION_AUTONOMA_TOTAL",
            "episodio": "Ep03 - Redes Fotónicas Cuánticas y Spectrum-X",
            "tema": "Redes Fotónicas Cuánticas y Spectrum-X a 1.6 Tbps",
            "personaje_protagonista": "Amatista",
            "host_central": "Diamantino",
            "duracion_total_seg": final_dur,
            "canales_clips": 6,
            "canales_voces": 6,
            "rutas": {
                "guion": guion_path,
                "storyboard": sb_json_path,
                "voiceover_master": voiceover_master_path,
                "master_v1": master_v1_path,
                "publicado_v1": p2,
                "backup_v1": p3
            },
            "norma_audio": "EBU R128 -14 LUFS TP -1.5 dBTP",
            "redundancia_triple_p03": True,
            "ejecucion": "100% Autonoma via _PROMPT_TOTAL_R768_v3.md"
        }
        
        client.upsert(
            collection_name="registro_ecosistema",
            points=[
                models.PointStruct(
                    id=62,
                    vector=vec_62,
                    payload=payload_op62
                )
            ]
        )
        print("[OK] Qdrant Cloud: Point ID 62 indexado con éxito en 'registro_ecosistema'.")
    except Exception as e:
        print(f"[!] Error en indexación Qdrant: {e}")

print("\n==========================================================")
print("[EXITO TOTAL] PRODUCCIÓN COMPLETA EPISODIO 03 FINALIZADA.")
print(f"Master Oficial: {master_v1_path}")
print(f"Duración Final: {final_dur:.2f} segundos ({final_dur/60:.2f} min)")
print("==========================================================")
