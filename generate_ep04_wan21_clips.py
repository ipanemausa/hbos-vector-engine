import os
import sys
import time
import json
import base64
import math
import hashlib
import requests
import subprocess
import shutil
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

api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    print("[!] ERROR: DASHSCOPE_API_KEY no encontrada")
    sys.exit(1)

with open(r"Ep04\02_Storyboard\storyboard_v2.json", "r", encoding="utf-8") as f:
    sb_data = json.load(f)

planos = sb_data["planos"]

dir_local_clips = r"Ep04\04_Clips_Wan21"
dir_drive_clips = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\04_Clips_Wan21"
dir_raw = r"Ep04\04_Clips_Wan21\raw"
os.makedirs(dir_local_clips, exist_ok=True)
os.makedirs(dir_drive_clips, exist_ok=True)
os.makedirs(dir_raw, exist_ok=True)

img_map = {
    0: r"Ep04\02_Storyboard\images_wan21\plano_00_nota_referencia.png",
    1: r"Ep04\02_Storyboard\images_wan21\plano_01_diamantino_intro.png",
    2: r"Ep04\02_Storyboard\images_wan21\plano_02_rubin.png",
    3: r"Ep04\02_Storyboard\images_wan21\plano_03_zafir.png",
    4: r"Ep04\02_Storyboard\images_wan21\plano_04_esmeralda.png",
    5: r"Ep04\02_Storyboard\images_wan21\plano_05_citrilo.png",
    6: r"Ep04\02_Storyboard\images_wan21\plano_06_grafito.png",
    7: r"Ep04\02_Storyboard\images_wan21\plano_07_amatista.png",
    8: r"Ep04\02_Storyboard\images_wan21\plano_08_diamantino_recap.png",
    9: r"Ep04\02_Storyboard\images_wan21\plano_09_ensemble_cierre.png"
}

url_dispatch = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
headers_dispatch = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable"
}
headers_poll = {"Authorization": f"Bearer {api_key}"}

cinematic_filter = (
    "[0:v]split=2[bg_in][fg_in]; "
    "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
    "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
    "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
)

reporte_clips = []

# Revisar si plano 0 ya tiene task_id en curso
existing_task_p0 = "dbbcb687-a41b-44ef-a017-0c5c71f93ed1"

for p in planos:
    pid = p["plano"]
    target_dur = float(p["duracion_seg"])
    clip_name = f"ep04_plano_{pid:02d}_wan21.mp4"
    out_local_clip = os.path.join(dir_local_clips, clip_name)
    out_drive_clip = os.path.join(dir_drive_clips, clip_name)
    raw_clip = os.path.join(dir_raw, f"raw_ep04_plano_{pid:02d}.mp4")
    
    # Si ya existe en Drive y es válido, registrar y continuar
    if os.path.exists(out_drive_clip) and os.path.getsize(out_drive_clip) > 500000:
        print(f"[*] Plano {pid:02d} ya existe en Drive: {out_drive_clip}")
        if not os.path.exists(out_local_clip):
            shutil.copyfile(out_drive_clip, out_local_clip)
        ffprobe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", out_local_clip
        ]
        real_dur = float(subprocess.check_output(ffprobe_cmd).decode('utf-8').strip())
        reporte_clips.append({
            "plano": pid,
            "archivo": clip_name,
            "duracion_seg": real_dur,
            "bytes": os.path.getsize(out_local_clip),
            "ruta_drive": out_drive_clip
        })
        continue

    print(f"\n=======================================================")
    print(f"[*] Procesando Plano {pid:02d} ({p['personaje_visual']}) | Target: {target_dur}s")
    print(f"=======================================================")

    task_id = None
    if pid == 0 and existing_task_p0:
        task_id = existing_task_p0
        print(f"[*] Usando task_id previo para Plano 0: {task_id}")
    else:
        src_img = img_map[pid]
        print(f"[*] Codificando imagen {src_img}...")
        with open(src_img, 'rb') as f_img:
            b64 = base64.b64encode(f_img.read()).decode('utf-8')
        data_url = f"data:image/png;base64,{b64}"
        
        prompt_text = p["prompt_wan21"]
        payload = {
            "model": "wan2.1-i2v-turbo",
            "input": {
                "img_url": data_url,
                "prompt": prompt_text
            }
        }
        
        print("[*] Despachando a DashScope Cloud (Wan 2.1 I2V)...")
        for attempt in range(5):
            try:
                res = requests.post(url_dispatch, headers=headers_dispatch, json=payload, timeout=60)
                if res.status_code == 200:
                    task_id = res.json().get('output', {}).get('task_id')
                    print(f"[+] Tarea aceptada en la Nube! Task ID: {task_id}")
                    break
                else:
                    print(f"[!] Intento {attempt+1} falló ({res.status_code}): {res.text}")
                    time.sleep(4)
            except Exception as e:
                print(f"[!] Intento {attempt+1} excepción: {e}")
                time.sleep(4)
                
    if not task_id:
        print(f"[ERROR] No se pudo obtener task_id para Plano {pid}")
        sys.exit(1)
        
    # Polling DashScope Cloud
    video_url = None
    poll_url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}"
    print(f"[*] Monitoreando render en DashScope Cloud (task: {task_id})...")
    
    for cycle in range(120): # Hasta 10 minutos
        time.sleep(6)
        try:
            r_poll = requests.get(poll_url, headers=headers_poll, timeout=20)
            if r_poll.status_code == 200:
                out_data = r_poll.json().get('output', {})
                st = out_data.get('task_status')
                if cycle % 3 == 0 or st != 'RUNNING':
                    print(f"  -> Task status: {st} (espera: {(cycle+1)*6}s)")
                if st == 'SUCCEEDED':
                    video_url = out_data.get('video_url')
                    print(f"[+] Video URL disponible en nube: {video_url[:80]}...")
                    break
                elif st in ['FAILED', 'CANCELED']:
                    print(f"[ERROR] Falló generación en nube con status {st}: {out_data}")
                    sys.exit(1)
        except Exception as ex:
            print(f"[!] Error de polling: {ex}")
            
    if not video_url:
        print(f"[ERROR] Timeout esperando render en nube de Plano {pid}")
        sys.exit(1)
        
    # Descargar raw
    print(f"[*] Descargando clip raw de Wan 2.1 ({raw_clip})...")
    resp_v = requests.get(video_url, timeout=90)
    with open(raw_clip, 'wb') as f_raw:
        f_raw.write(resp_v.content)
    raw_size = len(resp_v.content)
    print(f"[+] Clip raw guardado ({raw_size} bytes)")
    
    # Procesar con FFmpeg para ajustar duración exacta del plano (1080p 30fps H.264)
    # Sin ffmpeg -loop 1 de imagen: se utiliza stream_loop sobre el video cinemático animado por Wan 2.1
    print(f"[*] Post-procesando a 1080p 30fps ({target_dur}s) con cinemática continua...")
    cmd_proc = [
        "ffmpeg", "-y",
        "-stream_loop", "10",
        "-i", raw_clip,
        "-t", f"{target_dur:.3f}",
        "-filter_complex", cinematic_filter,
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        out_local_clip
    ]
    subprocess.run(cmd_proc, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Sincronizar en Google Drive
    shutil.copyfile(out_local_clip, out_drive_clip)
    
    # Medir duración y tamaño
    ffprobe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", out_local_clip
    ]
    real_dur = float(subprocess.check_output(ffprobe_cmd).decode('utf-8').strip())
    final_size = os.path.getsize(out_local_clip)
    
    print(f"[OK] Plano {pid:02d} completado: {real_dur:.2f}s | {final_size/(1024*1024):.2f} MB")
    print(f"     Drive: {out_drive_clip}")
    
    reporte_clips.append({
        "plano": pid,
        "personaje": p["personaje_visual"],
        "archivo": clip_name,
        "duracion_seg": round(real_dur, 3),
        "bytes": final_size,
        "ruta_local": out_local_clip,
        "ruta_drive": out_drive_clip
    })

# Guardar duraciones_clips_ep04.json
json_dur_local = os.path.join(dir_local_clips, "duraciones_clips_ep04.json")
json_dur_drive = os.path.join(dir_drive_clips, "duraciones_clips_ep04.json")
with open(json_dur_local, "w", encoding="utf-8") as f:
    json.dump({"total_clips": len(reporte_clips), "clips": reporte_clips}, f, indent=2, ensure_ascii=False)
with open(json_dur_drive, "w", encoding="utf-8") as f:
    json.dump({"total_clips": len(reporte_clips), "clips": reporte_clips}, f, indent=2, ensure_ascii=False)

duracion_total = sum(c["duracion_seg"] for c in reporte_clips)
print(f"\n[ÉXITO TAREA 4] 10 Clips Wan 2.1 generados en la Nube y sincronizados en Drive. Duración total: {duracion_total:.2f} s.")

# Registrar operation_id = 70 en registro_ecosistema
vec_op70 = generate_embedding("Tarea 4 operacion 70 Generacion 10 Clips Wan 2.1 DashScope Cloud Ep04 Medicina Agentica P-14 P-16 P-17", dim=384)
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=70,
            vector=vec_op70,
            payload={
                "operation_id": 70,
                "tarea": "TAREA 4 — CLIPS WAN 2.1 PARA EP04 (SIN VOZ)",
                "episodio": "Ep04-MedicineAgentica",
                "modelo_video": "Wan 2.1 I2V Turbo (DashScope Cloud)",
                "total_clips": len(reporte_clips),
                "duracion_acumulada_seg": duracion_total,
                "clips_detalle": reporte_clips,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 70 registrado en registro_ecosistema.")
