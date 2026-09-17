import subprocess
import os
import shutil
import json
import urllib.request

print("===============================================================================")
print("   HBOS SOVEREIGN AI — PRODUCCION DIAMANTINO EP.01 (ANIMACION REAL + BGM)     ")
print("                          EXPERTO ALEJAVI · OPERATION_ID=33                   ")
print("===============================================================================\n")

# 1. Rutas maestras
CLIPS_DIR = "assets/diamantino/clips"
AUDIO_DIR = "assets/diamantino/audio"
EPISODES_DIR = "assets/diamantino/episodes"
MEDIA_DIR = "media/diamantino"
PUBLIC_MEDIA_DIR = "public/media/diamantino"

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(EPISODES_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(PUBLIC_MEDIA_DIR, exist_ok=True)

# 2. Procesar Plano 01 con video real de Wan 2.1
wan21_raw = os.path.join(CLIPS_DIR, "wan21_plano_01.mp4")
plano01_animado = os.path.join(CLIPS_DIR, "ep01_plano_01_wan21.mp4")
aud01 = os.path.join(AUDIO_DIR, "ep01_voz_plano_01.wav")

if os.path.exists(wan21_raw):
    print("[*] FASE B/C: Procesando Plano 01 con Wan 2.1 real (1080p, 15.0s, fondo cinemático)...")
    # Loop the 5.37s Wan 2.1 video to 15.0s, split into blurred 1080p background + centered video
    filter_p1 = (
        "[0:v]split=2[bg_in][fg_in];"
        "[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.15[bg];"
        "[fg_in]scale=1080:1080[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )
    cmd_p1 = [
        "ffmpeg", "-y",
        "-stream_loop", "3",
        "-i", wan21_raw,
        "-i", aud01,
        "-filter_complex", filter_p1,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-t", "15.0",
        "-shortest",
        plano01_animado
    ]
    res_p1 = subprocess.run(cmd_p1, capture_output=True, text=True)
    if res_p1.returncode != 0:
        print("[!] Error en Plano 01:", res_p1.stderr)
    else:
        sz = os.path.getsize(plano01_animado) / (1024 * 1024)
        print(f"[OK] Plano 01 animado Wan 2.1 generado con éxito: {plano01_animado} ({sz:.2f} MB)")
else:
    print("[!] Wan 2.1 raw no encontrado, usando plano base.")
    plano01_animado = os.path.join(CLIPS_DIR, "ep01_plano_01.mp4")

# 3. Lista de los 6 clips
clips_master = [
    plano01_animado,
    os.path.join(CLIPS_DIR, "ep01_plano_02.mp4"),
    os.path.join(CLIPS_DIR, "ep01_plano_03.mp4"),
    os.path.join(CLIPS_DIR, "ep01_plano_04.mp4"),
    os.path.join(CLIPS_DIR, "ep01_plano_05.mp4"),
    os.path.join(CLIPS_DIR, "ep01_plano_06.mp4")
]

# 4. Crear lista de concatenación para video_animado.mp4
concat_list = os.path.join(CLIPS_DIR, "concat_master_v2.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for c in clips_master:
        f.write(f"file '{os.path.abspath(c).replace(chr(92), '/')}'\n")

# 5. Ensamblar video_animado.mp4 (solo pista de video pura, 90s, 1080p)
video_animado = os.path.join(EPISODES_DIR, "video_animado.mp4")
print("[*] FASE D: Ensamblando video_animado.mp4 (90s, 1080p, H.264)...")
cmd_concat_v = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_list,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-an",
    "-t", "90.0",
    video_animado
]
res_v = subprocess.run(cmd_concat_v, capture_output=True, text=True)
if res_v.returncode != 0:
    print("[!] Error concatenando video:", res_v.stderr)
else:
    sz_v = os.path.getsize(video_animado) / (1024 * 1024)
    print(f"[OK] video_animado.mp4 generado: {sz_v:.2f} MB")

# 6. Crear voiceover_master.wav unificando las 6 pistas de voz (90s exactos)
voice_files = [
    os.path.join(AUDIO_DIR, f"ep01_voz_plano_0{i}.wav") for i in range(1, 7)
]
voice_concat_list = os.path.join(AUDIO_DIR, "voice_concat.txt")
with open(voice_concat_list, "w", encoding="utf-8") as f:
    for v in voice_files:
        f.write(f"file '{os.path.abspath(v).replace(chr(92), '/')}'\n")

voiceover_master = os.path.join(AUDIO_DIR, "voiceover_master.wav")
print("[*] Generando voiceover_master.wav de 90s...")
cmd_v_cat = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", voice_concat_list,
    "-ar", "48000",
    "-ac", "2",
    "-t", "90.0",
    voiceover_master
]
subprocess.run(cmd_v_cat, capture_output=True, text=True)

# 7. EJECUTAR EL COMANDO EXACTO CURADO POR EL USUARIO:
# ffmpeg -i video_animado.mp4 -i voiceover.wav -i music.mp3 \
#   -filter_complex "[1:a]volume=1.0[voice]; [2:a]volume=0.18[music]; [voice][music]amix=inputs=2:duration=first[aout]" \
#   -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 320k -shortest ep01_FINAL_v2.mp4
music_file = os.path.join(MEDIA_DIR, "music.mp3")
out_final_v2 = os.path.join(EPISODES_DIR, "ep01_FINAL_v2.mp4")

print("[*] Ejecutando Mezcla Maestra FFmpeg (Voice 1.0 + BGM 0.18 + amix + copy video)...")
cmd_master_mix = [
    "ffmpeg", "-y",
    "-i", video_animado,
    "-i", voiceover_master,
    "-i", music_file,
    "-filter_complex", "[1:a]volume=1.0[voice]; [2:a]volume=0.18[music]; [voice][music]amix=inputs=2:duration=first[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "320k",
    "-shortest",
    "-movflags", "+faststart",
    out_final_v2
]
res_mix = subprocess.run(cmd_master_mix, capture_output=True, text=True)
if res_mix.returncode != 0:
    print("[!] Error en mezcla final:", res_mix.stderr)
else:
    sz_final = os.path.getsize(out_final_v2) / (1024 * 1024)
    print(f"\n[OK] MASTER FINAL GENERADO EXITOSAMENTE: {out_final_v2} ({sz_final:.2f} MB)")

    # Copiar a rutas públicas para streaming
    dest1 = os.path.join(MEDIA_DIR, "ep01.mp4")
    dest2 = os.path.join(PUBLIC_MEDIA_DIR, "ep01.mp4")
    shutil.copyfile(out_final_v2, dest1)
    shutil.copyfile(out_final_v2, dest2)
    print(f"[+] Distribuido a:\n    - {dest1}\n    - {dest2}")

print("\n[OK] Proceso completado con éxito.")
