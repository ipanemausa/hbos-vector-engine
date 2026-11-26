# -*- coding: utf-8 -*-
import sys, re, json, time
from pathlib import Path
import torch
import whisper

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
torch.set_num_threads(8)

audio_path = r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion-equipo-agentes_raw.mp3"
print(f"[*] Cargando modelo Whisper (tiny) con 8 hilos CPU...")
t0 = time.time()
model = whisper.load_model("tiny")
print(f"[+] Modelo cargado en {time.time()-t0:.2f}s")

print(f"[*] Transcribiendo {audio_path}...")
t1 = time.time()
result = model.transcribe(audio_path, language="es", fp16=False)
print(f"[+] Transcripción completada en {time.time()-t1:.2f}s!")

segments = result.get("segments", [])
print(f"[+] {len(segments)} segmentos encontrados.")

out_json = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion_segmentos.json")
out_json.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")

print("\n=== ANÁLISIS DE SEGMENTOS DETECTADOS ===")
for idx, s in enumerate(segments):
    txt = s["text"].strip()
    start_s = s["start"]
    end_s = s["end"]
    
    # Check for duplicate words in sequence
    words = [re.sub(r'[^\w]', '', w.lower()) for w in txt.split()]
    duplicates = []
    for i in range(len(words)-1):
        if words[i] and words[i] == words[i+1] and len(words[i]) > 1:
            duplicates.append(words[i])
            
    has_eta = bool(re.search(r'\b(eta|e-ta|esta\s+esta)\b', txt, re.IGNORECASE))
    
    if duplicates or has_eta:
        print(f"\n>>> [ALERTA CORTE {idx:03d}] [{start_s:.2f}s -> {end_s:.2f}s]")
        print(f"    Texto: \"{txt}\"")
        if duplicates:
            print(f"    Palabras duplicadas: {duplicates}")
        if has_eta:
            print(f"    Coincidencia 'eta/esta': SI")
