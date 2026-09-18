import os
import sys
import time
import base64
import requests
import subprocess
import json
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    print("[!] ERROR: DASHSCOPE_API_KEY no encontrada")
    sys.exit(1)

SB_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard"
OUT_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\04_Clips_Wan21"
RAW_DIR = r"assets\diamantino\clips\ep02_raw"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

PLANOS = [
    {
        "id": 1,
        "name": "ep02_plano_01_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_01_v3.mp4",
        "img": os.path.join(SB_DIR, "diamantino_v1_keynote.png"),
        "dur": 17.40,
        "prompt": "Diamantino walks across the keynote stage from left to right, gesturing with hands, then stops center stage and turns toward the camera. Professional host movement. 8K cinematic."
    },
    {
        "id": 2,
        "name": "ep02_plano_02_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_02_v3.mp4",
        "img": os.path.join(SB_DIR, "rubin_v4_cabeza_bruto.png"),
        "dur": 19.77,
        "prompt": "Rubin walks toward the Vera Rubin server rack, points at the GPU components with her hand, then turns to camera. Professional host movement. 8K cinematic."
    },
    {
        "id": 3,
        "name": "ep02_plano_03_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_03_v3.mp4",
        "img": os.path.join(SB_DIR, "zafir_v1_articulado.png"),
        "dur": 24.08,
        "prompt": "Zafir walks across the stage toward the Vera CPU display, gestures at the holographic blueprint, then faces camera. Professional host movement. 8K cinematic."
    },
    {
        "id": 4,
        "name": "ep02_plano_04_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_04_v3.mp4",
        "img": os.path.join(SB_DIR, "esmeralda_v1_articulado.png"),
        "dur": 15.45,
        "prompt": "Esmeralda walks to the CUDA server racks, operates a holographic console, points at cascading code. Professional host movement. 8K cinematic."
    },
    {
        "id": 5,
        "name": "ep02_plano_05_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_05_v3.mp4",
        "img": os.path.join(SB_DIR, "citrilo_v1_articulado.png"),
        "dur": 16.19,
        "prompt": "Citrilo walks energetically across the stage, points upward at the RTX Spark hologram, dynamic host movement. 8K cinematic."
    },
    {
        "id": 6,
        "name": "ep02_plano_06_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_06_v3.mp4",
        "img": os.path.join(SB_DIR, "grafito_v1_articulado.png"),
        "dur": 23.43,
        "prompt": "Grafito steps forward from the shadows between racks, walks slowly toward the camera with silver eyes glowing. Mysterious host movement. 8K cinematic."
    },
    {
        "id": 7,
        "name": "ep02_plano_07_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_07_v3.mp4",
        "img": os.path.join(SB_DIR, "amatista_v1_articulado.png"),
        "dur": 18.19,
        "prompt": "Amatista walks toward a holographic neural network, extends hand to touch the data streams. Contemplative host movement. 8K cinematic."
    },
    {
        "id": 8,
        "name": "ep02_plano_08_wan21_v3.mp4",
        "raw_name": "wan21_raw_plano_08_v3.mp4",
        "img": os.path.join(SB_DIR, "escena_ensemble_gtc_keynote.png"),
        "dur": 21.77,
        "prompt": "Diamantino walks center stage, gestures outward to present all 7 components, then slowly steps back as fade out begins. Professional host finale. 8K cinematic."
    }
]

def submit_task(plano):
    print(f"[*] Despachando Plano {plano['id']} v3 ({os.path.basename(plano['img'])})...")
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
    
    for attempt in range(5):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                task_id = res.json().get('output', {}).get('task_id')
                print(f"[+] Plano {plano['id']} v3 aceptado por DashScope! Task ID: {task_id}")
                return task_id
            else:
                print(f"[!] Intento {attempt+1} - Error enviando Plano {plano['id']}: {res.status_code} {res.text}")
                time.sleep(3)
        except Exception as e:
            print(f"[!] Intento {attempt+1} - Excepción Plano {plano['id']}: {e}")
            time.sleep(3)
    return None

def poll_and_download(tasks):
    print("\n[*] Monitoreando renderizado de los 8 planos Wan 2.1 v3 en DashScope Cloud...")
    completed_urls = {}
    pending = dict(tasks)
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    while pending:
        time.sleep(8)
        for pid, tid in list(pending.items()):
            url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{tid}"
            try:
                res = requests.get(url, headers=headers, timeout=20)
                if res.status_code == 200:
                    data = res.json().get('output', {})
                    status = data.get('task_status')
                    print(f"  -> Plano {pid} v3 (Task {tid[:8]}...): {status}")
                    if status == 'SUCCEEDED':
                        v_url = data.get('video_url')
                        completed_urls[pid] = v_url
                        del pending[pid]
                    elif status in ['FAILED', 'CANCELED']:
                        print(f"[!] Error: Plano {pid} fallo con status {status}: {data}")
                        del pending[pid]
            except Exception as e:
                print(f"[!] Error consultando status Plano {pid}: {e}")
    return completed_urls

def process_clips(completed_urls):
    print("\n[*] Descargando y procesando los 8 clips v3 con FFmpeg (1080p Cinematic)...")
    cinematic_filter_base = (
        "[0:v]split=2[bg_in][fg_in]; "
        "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
        "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )
    
    for plano in PLANOS:
        pid = plano['id']
        url = completed_urls.get(pid)
        if not url:
            print(f"[!] No hay URL para Plano {pid}")
            continue
            
        raw_path = os.path.join(RAW_DIR, plano['raw_name'])
        print(f"[*] Descargando video raw para Plano {pid} v3...")
        for attempt in range(5):
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200:
                    with open(raw_path, 'wb') as f:
                        f.write(r.content)
                    print(f"[+] Guardado raw ({len(r.content)} bytes) en {raw_path}")
                    break
                else:
                    time.sleep(2)
            except Exception as e:
                print(f"[!] Reintento descarga Plano {pid}: {e}")
                time.sleep(2)
                
        out_path = os.path.join(OUT_DIR, plano['name'])
        dur = plano['dur']
        
        if pid == 8:
            fade_start = dur - 1.0
            filter_str = (
                "[0:v]split=2[bg_in][fg_in]; "
                "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
                "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fade=t=out:st={fade_start:.4f}:d=1.0[v]"
            )
        else:
            filter_str = cinematic_filter_base
            
        print(f"[*] Procesando FFmpeg 1080p 30fps para Plano {pid} v3 (duración: {dur:.2f}s)...")
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "5",
            "-i", raw_path,
            "-t", f"{dur:.4f}",
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Medir duración
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', out_path]
        res = subprocess.check_output(probe_cmd).decode()
        real_dur = float(json.loads(res)['format']['duration'])
        size_mb = os.path.getsize(out_path) / (1024*1024)
        print(f"[OK] Plano {pid} v3 generado: {out_path} ({size_mb:.2f} MB, {real_dur:.2f}s)")

if __name__ == "__main__":
    tasks = {}
    for p in PLANOS:
        tid = submit_task(p)
        if tid:
            tasks[p['id']] = tid
        time.sleep(2)
        
    print(f"\n[+] Total de tareas enviadas a DashScope: {len(tasks)}/8")
    if len(tasks) == len(PLANOS):
        urls = poll_and_download(tasks)
        process_clips(urls)
        print("\n[OK] FASE 1 (Re-animación de los 8 personajes v3 con desplazamiento) COMPLETADA.")
    else:
        print("[!] No se pudieron despachar todas las tareas a DashScope.")
