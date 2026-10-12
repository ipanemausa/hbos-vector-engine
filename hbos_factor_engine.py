import os, sys, time, zipfile, subprocess
from urllib.request import Request, urlopen
from urllib.parse import quote

print("=" * 60, flush=True)
print("  HBOS PROTOCOL EXECUTION: FACTORIZED INPUT/OUTPUT (768D)", flush=True)
print("=" * 60, flush=True)

work_dir = os.getcwd()
out_base = os.path.join(work_dir, "hbos_output")
audios_dir = os.path.join(out_base, "voice", "audios")
clones_dir = os.path.join(out_base, "voice", "clones")
raw_dir = os.path.join(out_base, "poses", "raw")
transp_dir = os.path.join(out_base, "poses", "transparent")
final_dir = os.path.join(out_base, "poses", "final")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# -------------------------------------------------------------
# FACTOR 1: VOICE SAMPLES (Google Drive Recovery Engine)
# -------------------------------------------------------------
print("\n[Factor 1/4] Acquiring master voice samples...", flush=True)
drive_files = {
    "audio_01.wav": "1-sSjbSlE365tzpR5DwgoNWoFNBxLvj4y",
    "audio_02.wav": "1XsjI3WoJGylFLcHxWThk6iF0XjPJyXDF",
    "audio_03.wav": "1YnmIC2E6zI-rILvx5DJnHloYh7aZXa8e",
    "audio_04.wav": "1cMS7rIhEwmh2rkKt4Xq9XF71G9rvKadY",
    "audio_05.wav": "1eaq1Mc1s4jpktdQKFg8kQuqzE6bQ-iZT",
    "audio_06.wav": "1h18rsyxJcPnpE7Ek7Pg8VOxjogt-mOBj",
    "audio_07.wav": "1koWlQQcCg5NaHHUmGW5X5S-QaQtm5E0H",
    "audio_08.wav": "1lmopohJ08Tql3VPPTmKLUAT-Im23WyLv",
    "audio_09.wav": "1mJ2jCFM0aO45i2pVppzpNv_SjxIHYpw-",
    "audio_10.wav": "1r1mQAAHcgIHBZLatqxm-FBukoznMd0Y0",
    "audio_11.wav": "1trwhuqQT7CF1fi8t17_WtkIZ8i0V6Q-W",
    "audio_12.wav": "1zfJyRwycT1Q-185K305L02tmf6INp1dU"
}

dl_count = 0
for name, f_id in drive_files.items():
    dest = os.path.join(audios_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"  [Cache] {name} present", flush=True)
        dl_count += 1
        continue
    url = f"https://drive.google.com/uc?export=download&id={f_id}"
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as r:
            with open(dest, "wb") as f:
                f.write(r.read())
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            print(f"  OK: {name} ({round(os.path.getsize(dest)/1024, 1)} KB)", flush=True)
            dl_count += 1
    except Exception:
        pass

print(f"  Audio factor ready: {dl_count}/12 files", flush=True)

# -------------------------------------------------------------
# FACTOR 2: VOICE SYNTHESIS (Zero-403 Arbitrated Cloud TTS)
# -------------------------------------------------------------
print("\n[Factor 2/4] Synthesizing Colombian-accent validation clips...", flush=True)
voice_scripts = [
    ("vibe_voice_01.mp3", "Sistema Vibe activado, operando con protocolos Qdrant 768D."),
    ("vibe_voice_02.mp3", "Todo el computo se ejecuta de manera fluida y sin costo."),
    ("vibe_voice_03.mp3", "El ecosistema HBOS responde de inmediato con factorizacion nativa.")
]

voice_ok = 0
for fname, text in voice_scripts:
    target = os.path.join(clones_dir, fname)
    if os.path.exists(target) and os.path.getsize(target) > 500:
        print(f"  [Cache] {fname} ready", flush=True)
        voice_ok += 1
        continue
    try:
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={quote(text)}&tl=es-CO&client=tw-ob"
        req = Request(tts_url, headers=headers)
        with urlopen(req, timeout=20) as resp:
            with open(target, "wb") as f:
                f.write(resp.read())
        if os.path.exists(target) and os.path.getsize(target) > 500:
            print(f"  OK: {fname}", flush=True)
            voice_ok += 1
    except Exception as e:
        print(f"  Voice error {fname}: {e}", flush=True)

print(f"  Clips synthesized: {voice_ok}/3", flush=True)

# -------------------------------------------------------------
# FACTOR 3: ENGLISH TOKEN VISUAL ENGINE (FLUX 768D Latent)
# -------------------------------------------------------------
print("\n[Factor 3/4] Generating visual poses via English tokens...", flush=True)

# Core Factor (Guillermo v6-0 locked identity)
CORE_IDENTITY = (
    "cinematic 8k photo of Guillermo, 1.87m tall, lean athletic physique, "
    "broad level square shoulders, upright posture, black rectangular framed glasses, "
    "short grey hair, subtle closed-mouth smile, natural sun-tanned skin, "
    "solid black t-shirt with small yellow chest logo, blue denim jeans, black sneakers, "
    "studio three-point lighting, pure chroma green screen background #00FF00"
)

# Atomic Pose Factors (English tokens)
POSE_ATOMS = [
    ("pose_0001", "standing centered, arms extended in T-pose, palms facing down, level posture"),
    ("pose_0002", "right arm pointing forward towards camera, confident posture, torso straight"),
    ("pose_0003", "wide athletic stance, arms crossed over chest, direct eye contact with camera"),
    ("pose_0004", "three-quarter dynamic right angle, torso angled 45 degrees, head facing camera")
]

pose_ok = 0
for pid, atom in POSE_ATOMS:
    raw = os.path.join(raw_dir, f"{pid}.png")
    transp = os.path.join(transp_dir, f"{pid}.png")
    if os.path.exists(transp) and os.path.getsize(transp) > 5000:
        print(f"  [Cache] {pid} transparent alpha ready", flush=True)
        pose_ok += 1
        continue
    
    dense_prompt = f"{CORE_IDENTITY}, {atom}"
    flux_url = f"https://image.pollinations.ai/prompt/{quote(dense_prompt)}?width=768&height=768&nologo=true&model=flux"
    try:
        req = Request(flux_url, headers=headers)
        with urlopen(req, timeout=90) as r:
            with open(raw, "wb") as f:
                f.write(r.read())
        
        # Zero-loss local chroma key to transparent PNG
        subprocess.run(
            ['ffmpeg', '-y', '-i', raw, '-vf', 'colorkey=0x00FF00:0.1:0.1', '-c:v', 'png', transp],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if os.path.exists(transp) and os.path.getsize(transp) > 5000:
            print(f"  OK: {pid} generated and keyed", flush=True)
            pose_ok += 1
    except Exception as e:
        print(f"  FLUX API timeout/error on {pid}: {e}", flush=True)
    time.sleep(0.5)

# Assembly animation clip if images exist
pngs = sorted([f for f in os.listdir(transp_dir) if f.endswith(".png")])
if pngs:
    list_txt = os.path.join(final_dir, "sequence.txt")
    with open(list_txt, "w") as f:
        for p in pngs:
            f.write(f"file '{os.path.join(transp_dir, p)}'\nduration 0.5\n")
    anim_file = os.path.join(final_dir, "animacion_vibe.mp4")
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_txt, '-vf', 'fps=24', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', anim_file],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("  Animation MP4 assembled successfully.", flush=True)

# -------------------------------------------------------------
# FACTOR 4: OUTPUT PACKAGING
# -------------------------------------------------------------
print("\n[Factor 4/4] Consolidating final deliverables...", flush=True)
zip_out = os.path.join(work_dir, "hbos_vibe_final.zip")
with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(out_base):
        for fl in files:
            full = os.path.join(root, fl)
            rel = os.path.relpath(full, work_dir)
            z.write(full, rel)

z_mb = round(os.path.getsize(zip_out) / (1024 * 1024), 2)
print("=" * 60, flush=True)
print(f"  HBOS FACTORIZED RUN COMPLETE", flush=True)
print(f"  - Voice clips: {voice_ok}/3", flush=True)
print(f"  - Visual alpha poses: {pose_ok}/{len(POSE_ATOMS)}", flush=True)
print(f"  - Package: {zip_out} ({z_mb} MB)", flush=True)
print("=" * 60, flush=True)
