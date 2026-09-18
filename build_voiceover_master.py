import os
import subprocess
import shutil

VOCES_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\03_Assets\Voces"
OUT_WAV = os.path.join(VOCES_DIR, "ep02_voiceover_master.wav")
LOCAL_OUT = r"assets\diamantino\audio\ep02_voiceover_master.wav"
os.makedirs(os.path.dirname(LOCAL_OUT), exist_ok=True)

TRACKS = [
    "ep02_voz_diamantino_intro.wav",
    "ep02_voz_rubin.wav",
    "ep02_voz_zafir.wav",
    "ep02_voz_esmeralda.wav",
    "ep02_voz_citrilo.wav",
    "ep02_voz_grafito.wav",
    "ep02_voz_amatista.wav",
    "ep02_voz_diamantino_cierre.wav"
]

# 1. Crear silencio de 400ms (0.4s) en formato 48kHz stereo pcm_s16le
silence_wav = "silence_400ms.wav"
cmd_silence = [
    "ffmpeg", "-y",
    "-f", "lavfi",
    "-i", "anullsrc=r=48000:cl=stereo",
    "-t", "0.4",
    "-c:a", "pcm_s16le",
    silence_wav
]
subprocess.run(cmd_silence, check=True)

# 2. Convertir cada pista de voz a formato uniforme 48kHz stereo pcm_s16le
norm_tracks = []
for i, t in enumerate(TRACKS):
    src = os.path.join(VOCES_DIR, t)
    norm_f = f"norm_voice_{i:02d}.wav"
    cmd_norm = [
        "ffmpeg", "-y",
        "-i", src,
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        norm_f
    ]
    subprocess.run(cmd_norm, check=True)
    norm_tracks.append(norm_f)

# 3. Construir archivo de concatenacion alternando voz y 400ms de silencio
concat_txt = "voice_concat_p02.txt"
with open(concat_txt, "w", encoding="utf-8") as f:
    for i, nt in enumerate(norm_tracks):
        abs_p = os.path.abspath(nt).replace("\\", "/")
        f.write(f"file '{abs_p}'\n")
        if i < len(norm_tracks) - 1:
            abs_sil = os.path.abspath(silence_wav).replace("\\", "/")
            f.write(f"file '{abs_sil}'\n")

# 4. Concatenar linealmente en ep02_voiceover_master.wav
cmd_cat = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_txt,
    "-c:a", "pcm_s16le",
    LOCAL_OUT
]
subprocess.run(cmd_cat, check=True)

# Copiar a Drive
shutil.copyfile(LOCAL_OUT, OUT_WAV)

# Medir duracion y verificar
res = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", OUT_WAV],
    capture_output=True, text=True
)
dur = float(res.stdout.strip())
sz_mb = os.path.getsize(OUT_WAV) / (1024 * 1024)

print(f"[OK] ep02_voiceover_master.wav generado exitosamente!")
print(f"     Ruta Drive: {OUT_WAV}")
print(f"     Duración: {dur:.2f} segundos")
print(f"     Tamaño: {sz_mb:.2f} MB")
print(f"     Silencios intercalados: 7 pausas de 400ms (2.8s total de silencios naturales)")
print(f"     Superposición de voces: 0.00% (Garantía matemática por concatenación secuencial P-02)")
