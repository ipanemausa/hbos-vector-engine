# -*- coding: utf-8 -*-
import sys, re, json
from pathlib import Path
import whisper

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

audio_path = r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion-equipo-agentes_raw.mp3"
print("[*] Cargando modelo Whisper (base) para transcripción y detección fonética...")
model = whisper.load_model("base")

print(f"[*] Transcribiendo {audio_path}...")
result = model.transcribe(
    audio_path,
    language="es",
    fp16=False,
    word_timestamps=True
)

segments = result.get("segments", [])
print(f"[+] Transcripción completada: {len(segments)} segmentos detectados.\n")

# Guardar transcripción completa con timestamps
out_json = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\narracion_transcripcion.json")
out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"[+] Transcripción guardada en: {out_json}")

print("\n=== BUSCANDO REPETICIONES Y CORTES ANÓMALOS ('eta', palabras duplicadas) ===")
anomalies = []

for s in segments:
    text = s["text"].strip()
    words = s.get("words", [])
    
    # Check for immediate word repetitions (e.g. "esta esta", "eta eta", "de de")
    for i in range(len(words) - 1):
        w1 = re.sub(r'[^\w]', '', words[i]["word"].lower())
        w2 = re.sub(r'[^\w]', '', words[i+1]["word"].lower())
        if w1 and w1 == w2 and len(w1) > 1:
            anomalies.append({
                "type": "REPETICIÓN_PALABRA",
                "word": w1,
                "start": words[i]["start"],
                "end": words[i+1]["end"],
                "segment_text": text
            })
            print(f"[!] Repetición de palabra '{w1}' detectada en {words[i]['start']:.2f}s - {words[i+1]['end']:.2f}s: \"{text}\"")

    # Check for phonetics like "eta" or "e-ta"
    if re.search(r'\b(eta|e-ta|esta|esta\s+esta)\b', text, re.IGNORECASE):
        print(f"[*] Coincidencia 'eta/esta' en [{s['start']:.2f}s -> {s['end']:.2f}s]: \"{text}\"")

print(f"\n[+] Total de anomalías/coincidencias encontradas: {len(anomalies)}")
