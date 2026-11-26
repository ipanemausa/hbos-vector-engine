import whisper
import subprocess
import os

source_audio = r"G:\My Drive\HBOS-fabrica\2026-10-07\voz-guillermo-video08-LIMPIA-FINAL-v3.m4a"
target_ref_dir = r"G:\My Drive\HBOS_Creative\02_Voice_Profiles"
os.makedirs(target_ref_dir, exist_ok=True)
target_ref = os.path.join(target_ref_dir, "ref-video08-15s-16k.wav")

# Also local copy in workspace for fast access
local_ref = os.path.abspath(r"ref-video08-15s-16k.wav")

print("Loading whisper base...")
model = whisper.load_model("base")
# Transcribe just the first 40 seconds to be super fast
# We can extract a 40s temp wav first
temp_chunk = os.path.abspath("temp_chunk_40s.wav")
subprocess.run(["ffmpeg", "-y", "-ss", "15", "-t", "25", "-i", source_audio, "-ar", "16000", "-ac", "1", temp_chunk], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

res = model.transcribe(temp_chunk, word_timestamps=True, language="es")
words = []
for seg in res.get("segments", []):
    for w in seg.get("words", []):
        words.append(w)
        print(f"{w['start']:.2f} - {w['end']:.2f}: {w['word']}")

# Find 'y' or 'publica' and 'gratis'
start_sec = None
end_sec = None

for i, w in enumerate(words):
    txt = w['word'].strip().lower()
    if 'publica' in txt and start_sec is None:
        # Check previous word if it is 'lo' or 'y'
        if i > 0 and words[i-1]['word'].strip().lower() in ['lo', 'y']:
            if i > 1 and words[i-2]['word'].strip().lower() in ['y']:
                start_sec = words[i-2]['start']
            else:
                start_sec = words[i-1]['start']
        else:
            start_sec = w['start']

    if 'gratis' in txt and start_sec is not None:
        end_sec = w['end']
        break

print(f"Detected range: start={start_sec}, end={end_sec}")

# The temp chunk started at 15s in original audio
if start_sec is None:
    # fallback
    abs_start = 20.5
    abs_duration = 10.5
else:
    abs_start = 15.0 + start_sec - 0.2
    abs_duration = (end_sec - start_sec) + 0.4
    if abs_duration > 15.0:
        abs_duration = 15.0

print(f"Extracting: ss={abs_start:.2f}, t={abs_duration:.2f}")

# Extract exactly 16k mono PCM wav
for out_path in [target_ref, local_ref]:
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{abs_start:.2f}",
        "-t", f"{abs_duration:.2f}",
        "-i", source_audio,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        out_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes)")

if os.path.exists(temp_chunk):
    os.remove(temp_chunk)
