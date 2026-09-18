import os
import sys
import time
import base64
import requests
import subprocess
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    print("[!] ERROR: DASHSCOPE_API_KEY no encontrada en .env.local")
    sys.exit(1)

SB_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard"
OUT_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\04_Clips_Wan21"
RAW_DIR = r"assets\diamantino\clips\ep02_raw"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

PLANOS = [
    {
        "id": 1,
        "name": "ep02_plano_01_wan21.mp4",
        "img": os.path.join(SB_DIR, "diamantino_v1_keynote.png"),
        "dur": 12.0,
        "prompt": "Diamantino entidad humanoide de diamante hiperluminoso gesticulando en keynote GTC, movimiento sutil de cabeza y hombros, parpadeo y respiracion, animacion cinematografica 3D 8K"
    },
    {
        "id": 2,
        "name": "ep02_plano_02_wan21.mp4",
        "img": os.path.join(SB_DIR, "rubin_v4_cabeza_bruto.png"),
        "dur": 14.0,
        "prompt": "Rubin humanoide de rubi rojo cristalino moviendo los brazos interactuando con racks Vera Rubin, articulaciones dinamicas, respiracion de gema"
    },
    {
        "id": 3,
        "name": "ep02_plano_03_wan21.mp4",
        "img": os.path.join(SB_DIR, "zafir_v1_articulado.png"),
        "dur": 13.0,
        "prompt": "Zafir entidad de zafiro azul tallado moviendo la cabeza con autoridad y serenidad, gesticulando frente a servidores Vera CPU Olympus"
    },
    {
        "id": 4,
        "name": "ep02_plano_04_wan21.mp4",
        "img": os.path.join(SB_DIR, "esmeralda_v1_articulado.png"),
        "dur": 13.0,
        "prompt": "Esmeralda gema verde cristalina operando tensores CUDA, moviendo dedos y girando la mirada con precision ejecutiva"
    },
    {
        "id": 5,
        "name": "ep02_plano_05_wan21.mp4",
        "img": os.path.join(SB_DIR, "citrilo_v1_articulado.png"),
        "dur": 12.0,
        "prompt": "Citrilo entidad ambarina agil y dinamica gesticulando con energia, moviendo hombros y cabeza explicando la arquitectura RTX Spark"
    },
    {
        "id": 6,
        "name": "ep02_plano_06_wan21.mp4",
        "img": os.path.join(SB_DIR, "grafito_v1_articulado.png"),
        "dur": 13.0,
        "prompt": "Grafito humanoide de carbono y grafito oscuro moviendo la cabeza con sobriedad y firmeza, observando el enlace NVLink 6"
    },
    {
        "id": 7,
        "name": "ep02_plano_07_wan21.mp4",
        "img": os.path.join(SB_DIR, "amatista_v1_articulado.png"),
        "dur": 13.0,
        "prompt": "Amatista figura de cuarzo purpura luminosa contemplando redes Spectrum-X, movimiento elegante de brazos y expresion serena"
    },
    {
        "id": 8,
        "name": "ep02_plano_08_wan21.mp4",
        "img": os.path.join(SB_DIR, "escena_ensemble_gtc_keynote.png"),
        "dur": 12.0,
        "prompt": "Los 7 personajes de gemas y silicio en el escenario GTC keynote, movimientos sutiles de respiracion y luces pulsantes en los racks de servidores"
    }
]

def submit_task(plano):
    print(f"[*] Despachando Plano {plano['id']} ({os.path.basename(plano['img'])})...")
    with open(plano['img'], 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    data_url = f"data:image/png;base64,{b64}"
    
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    payload = {
        "model": "wan2.1-i2v-turbo",
        "input": {
            "img_url": data_url,
            "prompt": plano['prompt']
        }
    }
    
    for attempt in range(3):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                task_id = res.json().get('output', {}).get('task_id')
                print(f"[+] Plano {plano['id']} aceptado por DashScope! Task ID: {task_id}")
                return task_id
            else:
                print(f"[!] Error enviando Plano {plano['id']}: {res.status_code} {res.text}")
                time.sleep(2)
        except Exception as e:
            print(f"[!] Excepción Plano {plano['id']}: {e}")
            time.sleep(2)
    return None

def poll_and_download(tasks):
    print("\n[*] Monitoreando renderizado Wan 2.1 en DashScope Cloud...")
    completed_urls = {}
    pending = dict(tasks)
    
    while pending:
        time.sleep(10)
        for pid in list(pending.keys()):
            tid = pending[pid]
            url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{tid}"
            try:
                res = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=15)
                if res.status_code == 200:
                    out = res.json().get('output', {})
                    status = out.get('task_status')
                    print(f"  -> Plano {pid} (Task {tid[:8]}...): {status}")
                    if status == "SUCCEEDED":
                        video_url = out.get('video_url')
                        completed_urls[pid] = video_url
                        del pending[pid]
                    elif status in ["FAILED", "CANCELED"]:
                        print(f"[!] Plano {pid} falló en DashScope: {out.get('message')}")
                        del pending[pid]
            except Exception as e:
                print(f"[!] Error sondeando Plano {pid}: {e}")
    return completed_urls

def process_and_extend(plano, video_url):
    raw_path = os.path.join(RAW_DIR, f"wan21_raw_plano_{plano['id']:02d}.mp4")
    out_path = os.path.join(OUT_DIR, plano['name'])
    
    print(f"\n[*] Descargando video generado para Plano {plano['id']}...")
    r = requests.get(video_url)
    with open(raw_path, 'wb') as f:
        f.write(r.content)
    print(f"[+] Guardado crudo ({len(r.content)} bytes) en {raw_path}")
    
    # Adaptar a 1080p con duración exacta usando técnica cinematográfica P-01 (split + boxblur de fondo + overlay centrado)
    print(f"[*] Procesando con FFmpeg a 1080p Full HD @ 30fps (duración: {plano['dur']}s)...")
    filter_str = (
        "[0:v]split=2[bg_in][fg_in];"
        "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg];"
        "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )
    
    # Repetir el loop de 5.37s para cubrir los 12-14s requeridos
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "3",
        "-i", raw_path,
        "-filter_complex", filter_str,
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-t", str(plano['dur']),
        out_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error procesando Plano {plano['id']}: {res.stderr}", flush=True)
    else:
        sz = os.path.getsize(out_path) / (1024 * 1024)
        print(f"[OK] Plano {plano['id']} animado Wan 2.1 generado exitosamente: {out_path} ({sz:.2f} MB)", flush=True)

def main():
    print("===============================================================================", flush=True)
    print("   HBOS SOVEREIGN AI — FASE 2.1: GENERACION REAL WAN 2.1 I2V (8 PLANOS)       ", flush=True)
    print("                        EXPERTO ALEJAVI · OPERATION_ID=56                      ", flush=True)
    print("===============================================================================\n", flush=True)
    
    tasks = {}
    
    # Plano 2 ya fue generado en la prueba previa
    task_rubin = "9f6a05db-d8d6-4ead-9b37-656efb2fb163"
    tasks[2] = task_rubin
    print(f"[+] Plano 2 reusando task completada: {task_rubin}")
    
    # Despachar los 7 planos restantes
    for p in PLANOS:
        if p['id'] != 2:
            tid = submit_task(p)
            if tid:
                tasks[p['id']] = tid
            time.sleep(1)
            
    print(f"\n[+] Total de tareas activas: {len(tasks)}")
    completed_urls = poll_and_download(tasks)
    
    print("\n[*] Procesando los 8 clips finales con FFmpeg...")
    for p in PLANOS:
        if p['id'] in completed_urls:
            process_and_extend(p, completed_urls[p['id']])
        else:
            print(f"[!] No se pudo procesar Plano {p['id']} (URL no disponible)")
            
    print("\n[OK] FASE 2.1 COMPLETADA.")

if __name__ == "__main__":
    main()
