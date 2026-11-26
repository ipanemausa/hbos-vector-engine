import whisper
import os

files_to_check = [
    r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_Pista3_Video08_Make_menos14LUFS.wav",
    r"G:\My Drive\HBOS-fabrica\2026-10-07\voz-guillermo-video08-LIMPIA-FINAL-v3.m4a"
]

model = whisper.load_model("tiny") # fast

for f in files_to_check:
    if os.path.exists(f):
        print(f"--- Checking {os.path.basename(f)} ---")
        res = model.transcribe(f, language="es")
        for seg in res.get("segments", []):
            print(f"{seg['start']:.1f}s - {seg['end']:.1f}s: {seg['text']}")
