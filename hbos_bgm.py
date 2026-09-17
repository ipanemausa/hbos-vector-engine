import numpy as np
from scipy.io import wavfile
import subprocess
import os

SAMPLE_RATE = 48000
TOTAL_DURATION = 90.0  # seconds
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

t = np.linspace(0, TOTAL_DURATION, TOTAL_SAMPLES, endpoint=False)

# Left and Right stereo channels
left = np.zeros(TOTAL_SAMPLES)
right = np.zeros(TOTAL_SAMPLES)

print("[*] Sintetizando Banda Sonora Original HBOS (6 bloques de 15s)...")

# Helper envelope generators
def get_block_env(start_s, end_s, attack=1.5, release=1.5):
    idx_start = int(start_s * SAMPLE_RATE)
    idx_end = int(end_s * SAMPLE_RATE)
    length = idx_end - idx_start
    env = np.ones(length)
    att_samples = int(attack * SAMPLE_RATE)
    rel_samples = int(release * SAMPLE_RATE)
    if att_samples > 0 and att_samples < length:
        env[:att_samples] = np.sin(np.linspace(0, np.pi / 2, att_samples)) ** 2
    if rel_samples > 0 and rel_samples < length:
        env[-rel_samples:] = np.cos(np.linspace(0, np.pi / 2, rel_samples)) ** 2
    full_env = np.zeros(TOTAL_SAMPLES)
    full_env[idx_start:idx_end] = env
    return full_env

# ── BLOQUE 1: 0s - 15s (Tensión Cuántica Subarmónica) ──────────────────
print("  - Generando Bloque 1: Tensión (0 - 15s)...")
env1 = get_block_env(0, 16.0, attack=0.1, release=2.0)
drone_base = 73.416  # D2
drone_l = np.sin(2 * np.pi * drone_base * t) + 0.4 * np.sin(2 * np.pi * drone_base * 2 * t)
drone_r = np.sin(2 * np.pi * (drone_base + 0.5) * t) + 0.4 * np.sin(2 * np.pi * (drone_base * 2 + 0.8) * t)
# Add subtle sub pulse at 60 bpm (1 Hz)
pulse = (0.5 + 0.5 * np.sin(2 * np.pi * 1.0 * t)) ** 3
left += 0.35 * drone_l * pulse * env1
right += 0.35 * drone_r * pulse * env1

# ── BLOQUE 2: 15s - 30s (Revelación Armónica del Átomo) ─────────────────
print("  - Generando Bloque 2: Revelación Armónica (15 - 30s)...")
env2 = get_block_env(14.0, 31.0, attack=2.0, release=2.0)
# Harmonic resonance: D3 (146.8), F#3 (185.0), A3 (220.0), C#4 (277.18)
harm_freqs = [146.83, 185.0, 220.0, 277.18, 587.33]
for i, f in enumerate(harm_freqs):
    pan = 0.5 + 0.4 * np.sin(2 * np.pi * 0.15 * t + i)
    osc_l = np.sin(2 * np.pi * f * t) * (1 - pan)
    osc_r = np.sin(2 * np.pi * (f * 1.002) * t) * pan
    left += 0.18 * osc_l * env2
    right += 0.18 * osc_r * env2

# ── BLOQUE 3: 30s - 45s (Ascenso Energético Toroidal) ──────────────────
print("  - Generando Bloque 3: Ascenso Energético (30 - 45s)...")
env3 = get_block_env(29.0, 46.0, attack=2.5, release=2.0)
# Rising pitch glide simulation
sweep_freq = 220.0 + (t - 30.0) * 18.0
sweep_freq = np.clip(sweep_freq, 110.0, 880.0)
sweep = np.sin(2 * np.pi * sweep_freq * t)
# Shimmer arpeggiator (8 Hz pulse)
arp = (0.5 + 0.5 * np.sin(2 * np.pi * 8.0 * t)) ** 2
left += 0.22 * sweep * arp * env3
right += 0.22 * np.roll(sweep * arp * env3, int(0.04 * SAMPLE_RATE))

# ── BLOQUE 4: 45s - 60s (Dualidad Grafito vs Diamante) ─────────────────
print("  - Generando Bloque 4: Dualidad Grafito / Diamante (45 - 60s)...")
env4 = get_block_env(44.0, 61.0, attack=1.5, release=2.0)
# Deep tectonic low pulse (Grafito: 45 Hz)
tectonic = np.clip(1.5 * np.sin(2 * np.pi * 45.0 * t), -0.7, 0.7)
# High crystalline diamond sparkle (Diamante: 2093 Hz C7 + 2349 Hz D7)
sparkle = (
    np.sin(2 * np.pi * 2093.0 * t) * np.sin(2 * np.pi * 3.0 * t) +
    np.sin(2 * np.pi * 2349.0 * t) * np.cos(2 * np.pi * 4.0 * t)
)
left += (0.30 * tectonic + 0.15 * sparkle) * env4
right += (0.30 * tectonic + 0.15 * np.roll(sparkle, int(0.02 * SAMPLE_RATE))) * env4

# ── BLOQUE 5: 60s - 75s (Salto Tecnológico Microchip Diamantino) ────────
print("  - Generando Bloque 5: Salto Tecnológico (60 - 75s)...")
env5 = get_block_env(59.0, 76.0, attack=1.5, release=2.0)
# Fast sequenced cyber rhythm (16th notes at 120 bpm = 8 Hz)
clock_hz = 8.0
step_pulse = (np.sin(2 * np.pi * clock_hz * t) > 0.0).astype(float)
synth_tones = [440.0, 523.25, 659.25, 783.99, 880.0]
cyber_wave_l = np.zeros(TOTAL_SAMPLES)
cyber_wave_r = np.zeros(TOTAL_SAMPLES)
for idx, freq in enumerate(synth_tones):
    gate = (np.sin(2 * np.pi * (clock_hz / 4) * t + idx * np.pi / 2) > 0.2).astype(float)
    cyber_wave_l += np.sin(2 * np.pi * freq * t) * gate
    cyber_wave_r += np.sin(2 * np.pi * (freq * 1.004) * t) * np.roll(gate, int(0.05 * SAMPLE_RATE))
left += 0.18 * cyber_wave_l * step_pulse * env5
right += 0.18 * cyber_wave_r * step_pulse * env5

# ── BLOQUE 6: 75s - 90s (Manifiesto Cósmico y Clímax) ──────────────────
print("  - Generando Bloque 6: Manifiesto Cósmico (75 - 90s)...")
env6 = get_block_env(74.0, 90.0, attack=2.0, release=3.5)
# Full orchestral chord: Dmaj9 (D2, A2, D3, F#3, A3, C#4, E4)
chord_freqs = [73.42, 110.0, 146.83, 185.0, 220.0, 277.18, 329.63]
chord_l = np.zeros(TOTAL_SAMPLES)
chord_r = np.zeros(TOTAL_SAMPLES)
for i, f in enumerate(chord_freqs):
    w = 1.0 / (1.0 + 0.15 * i)
    chord_l += w * np.sin(2 * np.pi * f * t)
    chord_r += w * np.sin(2 * np.pi * (f + 0.3 * (i % 2 - 0.5)) * t)
left += 0.24 * chord_l * env6
right += 0.24 * chord_r * env6

# Normalize floating point
max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
left = (left / max_val) * 0.90
right = (right / max_val) * 0.90

stereo = np.column_stack((left, right))
raw_wav = "assets/diamantino/audio/music_raw.wav"
os.makedirs("assets/diamantino/audio", exist_ok=True)
os.makedirs("media/diamantino", exist_ok=True)
os.makedirs("public/media/diamantino", exist_ok=True)

wavfile.write(raw_wav, SAMPLE_RATE, (stereo * 32767).astype(np.int16))
print(f"[+] Archivo WAV crudo generado: {raw_wav}")

# ── Normalización profesional FFmpeg: 320k, 48kHz, loudnorm I=-16, TP=-1.5 ──
out_mp3_asset = "assets/diamantino/audio/music.mp3"
out_mp3_media = "media/diamantino/music.mp3"
out_mp3_public = "public/media/diamantino/music.mp3"

cmd_norm = [
    "ffmpeg", "-y",
    "-i", raw_wav,
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur=90.0",
    "-ar", "48000",
    "-b:a", "320k",
    "-t", "90.0",
    out_mp3_asset
]
print("[*] Normalizando con FFmpeg (loudnorm I=-16, TP=-1.5, 320 kbps, 48 kHz)...")
res = subprocess.run(cmd_norm, capture_output=True, text=True)
if res.returncode != 0:
    print("[!] Error FFmpeg:", res.stderr)
else:
    import shutil
    shutil.copyfile(out_mp3_asset, out_mp3_media)
    shutil.copyfile(out_mp3_asset, out_mp3_public)
    sz = os.path.getsize(out_mp3_asset) / (1024 * 1024)
    print(f"[OK] BGM Original de 90s generado y normalizado con éxito: {sz:.2f} MB")
    print(f"     -> {out_mp3_asset}")
    print(f"     -> {out_mp3_media}")
    print(f"     -> {out_mp3_public}")
