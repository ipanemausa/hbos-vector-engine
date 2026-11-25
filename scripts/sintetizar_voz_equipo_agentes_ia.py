# -*- coding: utf-8 -*-
"""
Sintetizador Canónico de Voz para Equipo de Agentes de IA
Extrae los 10 bloques de guion_equipo_agentes_ia.md, sintetiza cada bloque con SAPI / Microsoft Spanish,
aplica la cadena de masterización HBOS:
highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.5:LRA=11 a 48kHz mono,
concatena con silencios naturales y genera:
1. G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\equipo_agentes_ia_guiahoy.wav
2. Manifiesto de tiempos por bloque (JSON)
3. 2026-11-25_Equipo_Agentes_IA_10min.srt sincronizado
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

PROD_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25")
VOZ_DIR = PROD_DIR / "02_voz_guiahoy"
GUION_FILE = PROD_DIR / "guion_equipo_agentes_ia.md"
TARGET_WAV = VOZ_DIR / "equipo_agentes_ia_guiahoy.wav"
TIMINGS_JSON = PROD_DIR / "block_timings.json"
SRT_FILE = PROD_DIR / "2026-11-25_Equipo_Agentes_IA_10min.srt"

TEMP_DIR = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\temp_sintesis")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
VOZ_DIR.mkdir(parents=True, exist_ok=True)

def parse_guion():
    content = GUION_FILE.read_text(encoding="utf-8")
    pattern = r"### BLOQUE (\d\d).*?\n\*\s+\*\*Fondo:\*\*\s+`([^`]+)`\s+\|\s+\*\*Avatar:\*\*\s+`([^`]+)`\s*\n\*\s+\*\*Módulo:\*\*\s+(.*?)\n\n(.*?)(?=(?:### BLOQUE|\Z))"
    raw_blocks = re.findall(pattern, content, re.DOTALL)
    blocks = []
    for b_num, bg, av, mod, body in raw_blocks:
        lines = [l.strip().lstrip('> ').strip() for l in body.strip().split("\n") if l.strip().startswith('>')]
        clean_narr = " ".join(lines).replace('"', '').strip()
        blocks.append({
            "block_id": int(b_num),
            "fondo": bg.strip(),
            "avatar": av.strip(),
            "modulo": mod.strip(),
            "text": clean_narr
        })
    return blocks

def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def synthesize():
    blocks = parse_guion()
    print(f"[*] Parseados {len(blocks)} bloques desde {GUION_FILE.name}")
    
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # Seleccionar voz en español (Sabina o Helena)
    selected_voice = None
    for v in speaker.GetVoices():
        desc = v.GetDescription()
        if "Spanish" in desc:
            selected_voice = v
            print(f"[+] Voz seleccionada: {desc}")
            break
            
    if selected_voice:
        speaker.Voice = selected_voice
    speaker.Rate = -1 # Ritmo pausado y tranquilo institucional
    
    block_files = []
    block_timings = []
    current_time = 0.0
    
    # Generar silencio de 0.8s para pausas entre bloques
    silence_file = TEMP_DIR / "silence_08.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
        "-t", "0.8", str(silence_file)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    srt_entries = []
    
    for b in blocks:
        b_id = b["block_id"]
        raw_wav = TEMP_DIR / f"raw_block_{b_id:02d}.wav"
        norm_wav = TEMP_DIR / f"norm_block_{b_id:02d}.wav"
        
        # Sintetizar con SAPI
        fs = win32com.client.Dispatch("SAPI.SpFileStream")
        fs.Open(str(raw_wav), 3) # SSFMCreateForWrite
        speaker.AudioOutputStream = fs
        speaker.Speak(b["text"])
        fs.Close()
        
        # Masterizar con la cadena canónica HBOS (-14 LUFS, 48k mono)
        # highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.5:LRA=11
        cmd = [
            "ffmpeg", "-y", "-i", str(raw_wav),
            "-af", "highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "48000", "-ac", "1", str(norm_wav)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Medir duración real con ffprobe
        pcmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(norm_wav)]
        res = subprocess.run(pcmd, capture_output=True, text=True, check=True)
        dur = float(json.loads(res.stdout)["format"]["duration"])
        
        start_t = current_time
        end_t = current_time + dur
        
        block_timings.append({
            "block_id": b_id,
            "fondo": b["fondo"],
            "avatar": b["avatar"],
            "modulo": b["modulo"],
            "text": b["text"],
            "start": round(start_t, 3),
            "end": round(end_t, 3),
            "duration": round(dur, 3),
            "norm_wav": str(norm_wav)
        })
        
        # SRT Entry
        srt_entries.append(
            f"{b_id}\n"
            f"{format_timestamp(start_t)} --> {format_timestamp(end_t)}\n"
            f"[Bloque {b_id:02d}: {b['modulo']}]\n"
            f"{b['text']}\n"
        )
        
        print(f"    Bloque {b_id:02d}: {b['modulo'][:35]}... ({dur:.2f}s) [{start_t:.1f}s -> {end_t:.1f}s]")
        block_files.append(str(norm_wav))
        
        current_time = end_t + 0.8
        
    # Concatenar todos los bloques intercalando silencios
    concat_list_file = TEMP_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for idx, bfile in enumerate(block_files):
            f.write(f"file '{bfile.replace(os.sep, '/')}'\n")
            if idx < len(block_files) - 1:
                f.write(f"file '{str(silence_file).replace(os.sep, '/')}'\n")
                
    print("[*] Concatenando audio maestro con concat demuxer...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1",
        str(TARGET_WAV)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Escribir manifiesto de tiempos
    TIMINGS_JSON.write_text(json.dumps({
        "project": "Equipo de Agentes de IA",
        "date": "2026-11-25",
        "total_duration_sec": round(current_time, 3),
        "target_wav": str(TARGET_WAV),
        "blocks": block_timings
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Escribir SRT sincronizado
    SRT_FILE.write_text("\n".join(srt_entries), encoding="utf-8")
    
    # Comprobar audio final
    pcmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(TARGET_WAV)]
    res = subprocess.run(pcmd, capture_output=True, text=True, check=True)
    tot_dur = float(json.loads(res.stdout)["format"]["duration"])
    
    print(f"\n[+] SINTESIS FINALIZADA EXITOSAMENTE:")
    print(f"    Ruta WAV: {TARGET_WAV}")
    print(f"    Duración total: {tot_dur:.2f} segundos ({tot_dur/60:.2f} min)")
    print(f"    Timings JSON: {TIMINGS_JSON}")
    print(f"    SRT generado: {SRT_FILE}")

if __name__ == "__main__":
    synthesize()
