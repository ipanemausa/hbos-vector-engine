import os, requests, subprocess, base64, time, zipfile
from urllib.parse import quote

print("=== ARBITRAJE AUTOMATICO: CORRECCION DE POSES ===", flush=True)

identidad = "Guillermo, man 1.87m, lean athletic, broad square shoulders, upright posture, black-framed glasses, short grey hair, subtle closed-lip smile, moderate natural bronze skin, black t-shirt with small yellow HB.OS logo, blue jeans, black shoes, pure chroma green background #00FF00, photorealistic, 8k"

faltantes = [
    ("pose_0002", "right arm pointing forward towards camera, confident posture, torso straight"),
    ("pose_0004", "three-quarter dynamic right angle, torso angled 45 degrees, head facing camera")
]

out = "hbos_output"
raw_dir = os.path.join(out, "poses", "raw")
transp_dir = os.path.join(out, "poses", "transparent")
final_dir = os.path.join(out, "poses", "final")

api_key = os.getenv("GOOGLE_AI_KEY")

for pid, atom in faltantes:
    raw = os.path.join(raw_dir, f"{pid}.png")
    transp = os.path.join(transp_dir, f"{pid}.png")
    
    if os.path.exists(transp) and os.path.getsize(transp) > 5000:
        print(f"  [Cache] {pid} ya completada", flush=True)
        continue

    exito = False
    
    # Intento 1: Google Imagen 3 si hay API key
    if api_key:
        print(f"  [Google] Generando {pid}...", flush=True)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
        payload = {
            "instances": [{"prompt": f"{identidad}, {atom}", "aspectRatio": "1:1", "sampleCount": 1}],
            "parameters": {"personGeneration": "allow_adult"}
        }
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                b64 = data["predictions"][0]["bytesBase64Encoded"]
                with open(raw, "wb") as f:
                    f.write(base64.b64decode(b64))
                exito = True
        except Exception as e:
            print(f"    Google fallo: {e}", flush=True)

    # Intento 2: Fallback Pollinations (modelo alternativo turboflux/sdxl para evitar 402)
    if not exito:
        print(f"  [Fallback Nube] Generando {pid}...", flush=True)
        url = f"https://image.pollinations.ai/prompt/{quote(identidad + ', pose: ' + atom)}?width=768&height=768&nologo=true"
        try:
            r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                with open(raw, "wb") as f:
                    f.write(r.content)
                exito = True
        except Exception as e:
            print(f"    Fallback fallo: {e}", flush=True)

    # Recorte FFmpeg si se genero la imagen base
    if exito and os.path.exists(raw):
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw, "-vf", "colorkey=0x00FF00:0.1:0.1", "-c:v", "png", transp],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"  OK {pid} procesada con transparencia", flush=True)
    time.sleep(1)

# Reensamblado de video y actualizacion del paquete final
pngs = sorted([f for f in os.listdir(transp_dir) if f.endswith(".png")])
if pngs:
    list_path = os.path.join(final_dir, "sequence.txt")
    with open(list_path, "w") as f:
        for p in pngs:
            f.write(f"file '{os.path.join(transp_dir, p)}'\nduration 0.5\n")
    anim_file = os.path.join(final_dir, "animacion_vibe.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-vf", "fps=24", "-c:v", "libx264", "-pix_fmt", "yuv420p", anim_file],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("  Video reensamblado con todas las poses.", flush=True)

zip_out = "hbos_vibe_final.zip"
with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(out):
        for fl in files:
            full = os.path.join(root, fl)
            rel = os.path.relpath(full, os.getcwd())
            z.write(full, rel)

print(f"Paquete final actualizado: {zip_out} ({round(os.path.getsize(zip_out)/(1024*1024), 2)} MB)", flush=True)
