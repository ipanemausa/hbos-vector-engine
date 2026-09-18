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

# Get exact duration from audio
with open("bloque7_duracion.json", "r", encoding="utf-8") as f:
    dur_data = json.load(f)
dur = float(dur_data["duracion"])
print(f"[*] Duración objetivo para Bloque 7: {dur:.4f} s")

SB_IMG = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\diamantino_v1_keynote.png"
OUT_FILE_1 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\04_Clips_Wan21\ep02_plano_07b_wan21.mp4"
OUT_FILE_2 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\04_Clips_Wan21_v2\ep02_plano_07b_v2.mp4"
LOCAL_OUT = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_plano_07b_wan21.mp4"
RAW_FILE = r"assets\diamantino\clips\ep02_raw\wan21_raw_plano_07b.mp4"
os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
os.makedirs(os.path.dirname(OUT_FILE_1), exist_ok=True)
os.makedirs(os.path.dirname(OUT_FILE_2), exist_ok=True)

prompt = (
    "Diamantino walks center stage, gestures at all 7 racks with both hands, "
    "then turns to camera with authoritative keynote host pose. "
    "Professional presenter movement. 8K cinematic. Non-repetitive motion."
)

print(f"[*] Codificando imagen {SB_IMG}...")
with open(SB_IMG, 'rb') as f:
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
        "prompt": prompt
    }
}

task_id = None
print("[*] Despachando tarea a DashScope Cloud (Wan 2.1 I2V)...")
for attempt in range(5):
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            task_id = res.json().get('output', {}).get('task_id')
            print(f"[+] Tarea aceptada! Task ID: {task_id}")
            break
        else:
            print(f"[!] Intento {attempt+1} - Status {res.status_code}: {res.text}")
            time.sleep(3)
    except Exception as e:
        print(f"[!] Intento {attempt+1} - Excepción: {e}")
        time.sleep(3)

if not task_id:
    print("[ERROR] No se pudo obtener Task ID de DashScope")
    sys.exit(1)

# Polling
video_url = None
poll_headers = {"Authorization": f"Bearer {api_key}"}
poll_url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}"

print("[*] Monitoreando generación de video en DashScope...")
for _ in range(120): # up to 10 minutes
    time.sleep(6)
    try:
        res = requests.get(poll_url, headers=poll_headers, timeout=20)
        if res.status_code == 200:
            data = res.json().get('output', {})
            status = data.get('task_status')
            print(f"  -> Task status: {status}")
            if status == 'SUCCEEDED':
                video_url = data.get('video_url')
                print(f"[+] Video URL lista: {video_url}")
                break
            elif status in ['FAILED', 'CANCELED']:
                print(f"[!] Error: Falló con status {status}: {data}")
                sys.exit(1)
    except Exception as e:
        print(f"[!] Error consultando estado: {e}")

if not video_url:
    print("[ERROR] Timeout esperando render de Wan 2.1")
    sys.exit(1)

# Download raw
print("[*] Descargando video raw...")
r = requests.get(video_url, timeout=90)
with open(RAW_FILE, 'wb') as f:
    f.write(r.content)
print(f"[+] Video raw guardado ({len(r.content)} bytes)")

# Process FFmpeg
cinematic_filter = (
    "[0:v]split=2[bg_in][fg_in]; "
    "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg]; "
    "[fg_in]scale=1920:1080:force_original_aspect_ratio=decrease[fg]; "
    "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
)

print(f"[*] Procesando clip a 1080p 30fps libx264 crf 18 (duración: {dur:.2f}s)...")
cmd = [
    "ffmpeg", "-y",
    "-stream_loop", "15",
    "-i", RAW_FILE,
    "-t", f"{dur:.4f}",
    "-filter_complex", cinematic_filter,
    "-map", "[v]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    OUT_FILE_1
]
subprocess.run(cmd, check=True)

# Copy to OUT_FILE_2 and LOCAL_OUT
import shutil
shutil.copyfile(OUT_FILE_1, OUT_FILE_2)
shutil.copyfile(OUT_FILE_1, LOCAL_OUT)

# Verify duration
probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', OUT_FILE_1]
res = subprocess.check_output(probe_cmd).decode()
real_dur = float(json.loads(res)['format']['duration'])
size_mb = os.path.getsize(OUT_FILE_1) / (1024*1024)
print(f"[EXITO] Clip del Bloque 7 generado con éxito:")
print(f"  -> {OUT_FILE_1} ({size_mb:.2f} MB, {real_dur:.2f}s)")
print(f"  -> {OUT_FILE_2}")
