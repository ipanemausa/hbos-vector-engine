import os
import sys
import json
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

BASE_EP02 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips"
VOCES_DIR = os.path.join(BASE_EP02, r"03_Assets\Voces")

VOICES = [
    {"id": "01", "name": "ep02_voz_diamantino_intro.wav", "label": "Diamantino (Intro)"},
    {"id": "02", "name": "ep02_voz_rubin.wav", "label": "Rubín"},
    {"id": "03", "name": "ep02_voz_zafir.wav", "label": "Zafir"},
    {"id": "04", "name": "ep02_voz_esmeralda.wav", "label": "Esmeralda"},
    {"id": "05", "name": "ep02_voz_citrilo.wav", "label": "Citrilo"},
    {"id": "06", "name": "ep02_voz_grafito.wav", "label": "Grafito"},
    {"id": "07", "name": "ep02_voz_amatista.wav", "label": "Amatista"},
    {"id": "07b", "name": "ep02_voz_diamantino_bloque7.wav", "label": "Diamantino (Bloque 7 Agéntico)"},
    {"id": "08", "name": "ep02_voz_diamantino_cierre.wav", "label": "Diamantino (Cierre)"}
]

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', file_path]
    res = subprocess.check_output(cmd).decode()
    return float(json.loads(res)['format']['duration'])

print("==========================================================")
print("FASE 4 — RE-ENSAMBLAJE DE VOICEOVER MASTER V2 (9 BLOQUES)")
print("==========================================================")

total_voz = 0.0
for v in VOICES:
    p = os.path.join(VOCES_DIR, v["name"])
    if not os.path.exists(p):
        print(f"[ERROR] No existe {p}")
        sys.exit(1)
    dur = get_duration(p)
    v["dur"] = dur
    total_voz += dur
    print(f"[{v['id']}] {v['label']}: {dur:.4f}s ({v['name']})")

silence_inter = 0.4 # 8 silencios de 0.4s
silence_final = 3.0 # 2s respiro + 1s fade out

total_silencios = (len(VOICES) - 1) * silence_inter + silence_final
total_calculado = total_voz + total_silencios

print(f"[*] Suma de 9 voces: {total_voz:.4f}s")
print(f"[*] Suma de silencios (8 x 0.4s + 3.0s final): {total_silencios:.4f}s")
print(f"[*] Duración esperada Voiceover Master v2: {total_calculado:.4f}s")

# Crear clips de silencio estandarizados 44100Hz stereo pcm_s16le
silence_04 = os.path.join(VOCES_DIR, "temp_silence_04.wav")
silence_30 = os.path.join(VOCES_DIR, "temp_silence_30.wav")

subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
    "-t", "0.4", "-c:a", "pcm_s16le", silence_04
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
    "-t", "3.0", "-c:a", "pcm_s16le", silence_30
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Convertir cada voz a un WAV estéreo 44100Hz pcm_s16le uniforme
temp_wavs = []
for v in VOICES:
    v_in = os.path.join(VOCES_DIR, v['name'])
    v_std = os.path.join(VOCES_DIR, f"temp_std_{v['id']}.wav")
    cmd_std = ["ffmpeg", "-y", "-i", v_in, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", v_std]
    subprocess.run(cmd_std, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_wavs.append(v_std)

out_master_v2 = os.path.join(VOCES_DIR, "ep02_voiceover_master_v2.wav")
local_master_v2 = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_voiceover_master_v2.wav"

audio_concat_list = os.path.join(VOCES_DIR, "concat_voice_v2_list.txt")
with open(audio_concat_list, "w", encoding="utf-8") as f:
    for i, v in enumerate(VOICES):
        f.write(f"file 'temp_std_{v['id']}.wav'\n")
        if i < len(VOICES) - 1:
            f.write(f"file 'temp_silence_04.wav'\n")
        else:
            f.write(f"file 'temp_silence_30.wav'\n")

fade_start = total_calculado - 1.0
cmd_voice_concat = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", audio_concat_list,
    "-af", f"afade=t=out:st={fade_start:.4f}:d=1.0",
    "-c:a", "pcm_s16le",
    out_master_v2
]
print("[*] Concatenando 9 pistas de voz con silencios y fade out final...")
subprocess.run(cmd_voice_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Local copy
import shutil
shutil.copyfile(out_master_v2, local_master_v2)

# Verify
real_dur = get_duration(out_master_v2)
size_mb = os.path.getsize(out_master_v2) / (1024*1024)
print(f"[OK] Voiceover Master v2 creado: {out_master_v2}")
print(f"[+] Duración real: {real_dur:.4f}s ({real_dur/60:.2f} min) | Tamaño: {size_mb:.2f} MB")

# Cleanup temp
for tmp in [silence_04, silence_30, audio_concat_list] + temp_wavs:
    if os.path.exists(tmp):
        os.remove(tmp)

with open("voiceover_v2_duracion.json", "w", encoding="utf-8") as f:
    json.dump({"duracion": real_dur}, f)
print("[EXITO] FASE 4 COMPLETADA.")
