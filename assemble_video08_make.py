import os
import sys
import subprocess
import time
from pathlib import Path

audio = Path(r"G:\My Drive\HBOS-fabrica\2026-10-07\voz-guillermo-video08-LIMPIA-FINAL-v3.m4a")
if not audio.exists():
    audio = Path(r"G:\My Drive\HBOS-fabrica\2026-10-07\voz-guillermo-video08-v2-limpia.m4a")

bg_image = Path(r"G:\My Drive\HBOS-fabrica\2026-10-07\Triunfo-de-Cristal-wallpaper-16x9.jpg")
if not bg_image.exists():
    bg_image = Path(r"G:\My Drive\HBOS-fabrica\2026-10-07\Triunfo-de-Cristal-imagen-16x9.webp")

output_dir = Path(r"G:\My Drive\Sistema")
output_dir.mkdir(parents=True, exist_ok=True)
output_video = output_dir / "video_08_make_VERIFICADO.mp4"

print("========================================================================")
print("[FL] ENSAMBLE VISUAL REAL CON FFMPEG (VIDEO #8 MAKE)")
print("========================================================================")
print(f" - Audio real:      {audio} ({audio.stat().st_size if audio.exists() else 0} bytes)")
print(f" - Fondo visual:    {bg_image} ({bg_image.stat().st_size if bg_image.exists() else 0} bytes)")
print(f" - Archivo destino: {output_video}")

if not audio.exists():
    print("[ERROR] Falta el archivo de audio fuente.")
    sys.exit(1)

if not bg_image.exists():
    print("[ERROR] Falta el fondo visual de Make.")
    sys.exit(1)

# Usar libx264 ultrafast con framerate 24fps
cmd = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-framerate", "24",
    "-i", str(bg_image),
    "-i", str(audio),
    "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "stillimage",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest",
    "-movflags", "+faststart",
    str(output_video)
]

print("\n[FL] Ejecutando FFmpeg optimizado (ultrafast stillimage + copy audio)...")
start_time = time.time()
res = subprocess.run(cmd, capture_output=True, text=True)
elapsed = time.time() - start_time

if res.returncode == 0 and output_video.exists():
    out_size = output_video.stat().st_size
    print(f"\n[ÉXITO] Video #8 renderizado con imagen y voz real en la ruta de destino.")
    print(f" - Ruta: {output_video}")
    print(f" - Tamaño: {out_size} bytes ({round(out_size / (1024*1024), 2)} MB)")
    print(f" - Tiempo de ensamble: {round(elapsed, 2)} segundos")
else:
    print(f"\n[ERROR] FFmpeg falló con código {res.returncode}")
    print(res.stderr[-1000:])
    sys.exit(1)
