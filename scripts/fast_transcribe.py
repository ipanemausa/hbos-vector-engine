# -*- coding: utf-8 -*-
import sys, json, re
from pathlib import Path
import whisper

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

audio_path = r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion-equipo-agentes_raw.mp3"
print("[*] Cargando modelo Whisper (tiny o base) rápido...")
model = whisper.load_model("base")

print("[*] Transcribiendo segmentos (modo rápido)...")
result = model.transcribe(audio_path, language="es", fp16=False)

segments = result.get("segments", [])
print(f"[+] Transcripción completada: {len(segments)} segmentos encontrados.")

out_json = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion_segmentos.json")
out_json.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")

print("\n=== REVISIÓN DE SEGMENTOS CON POSIBLES REPETICIONES / 'ETA' ===")
for idx, s in enumerate(segments):
    txt = s["text"].strip()
    start_s = s["start"]
    end_s = s["end"]
    
    # Imprimir segmentos con repeticiones de palabras o palabras dudosas
    words = [re.sub(r'[^\w]', '', w.lower()) for w in txt.split()]
    has_dup = False
    for i in range(len(words)-1):
        if words[i] and words[i] == words[i+1] and len(words[i]) > 1:
            has_dup = True
            break
            
    is_suspicious = has_dup or re.search(r'\b(eta|e-ta|esta\s+esta|que\s+que|de\s+de)\b', txt, re.IGNORECASE)
    if is_suspicious:
        print(f"[{idx:03d}] ALERTA en {start_s:.2f}s -> {end_s:.2f}s: \"{txt}\"")
    else:
        # Imprimir también segmentos para referencia
        if idx % 10 == 0:
            print(f"[{idx:03d}] Ref en {start_s:.2f}s -> {end_s:.2f}s: \"{txt[:60]}...\"")
