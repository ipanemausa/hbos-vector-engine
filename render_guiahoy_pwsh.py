import json
import os
import subprocess
import urllib.request
from pathlib import Path

DRIVE_ROOT = Path(r"G:\My Drive")
AVATAR_DIR = DRIVE_ROOT / "Avatar Guillermo - transparencias"
BG_DIR = DRIVE_ROOT / "Guiahoy_Produccion" / "2026-11-25" / "fondos_16x9"
VOICE_WAV = DRIVE_ROOT / "HBOS_Qdrant_Engine" / "03_MEDIA_VAULT_FINAL" / "Guiahoy_MASTER_48k_menos14LUFS.wav"
OUT_DIR = DRIVE_ROOT / "Guiahoy_Produccion" / "2026-11-25"
OUT_MP4 = OUT_DIR / "guiahoy_clase01_mit_ensamblado.mp4"
OUT_SRT = OUT_DIR / "guiahoy_clase01_mit_ensamblado.srt"

BLOCKS = [
    ("bg_01.jpg", "avatar-pose-t-arms-open-narrower.png", 55, "Bloque 01: Apertura - La IA sin misterio"),
    ("bg_02.jpg", "avatar-pose-t-calm-both.png", 75, "Bloque 02: Caso 1 - El perceptron y los pesos"),
    ("bg_03.jpg", "avatar-pose-t-chin-stroke-L.png", 65, "Bloque 03: Umbral de decision y cambio de criterio"),
    ("bg_04.jpg", "avatar-pose-t-arms-open-palms-up.png", 90, "Bloque 04: Caso 2 - Funcion de perdida y descenso de gradiente"),
    ("bg_05.jpg", "avatar-pose-t-chin-stroke-R.png", 70, "Bloque 05: Caso 3 - Valoracion de una joya y capas ocultas"),
    ("bg_06.jpg", "avatar-pose-t-arms-open-wider.png", 70, "Bloque 06: Retropropagacion hacia atras por la red"),
    ("bg_07.jpg", "avatar-pose-t-calm-both.png", 60, "Bloque 07: Reparto proporcional 50 / 30 / 20 y segundo pase"),
    ("bg_08.jpg", "avatar-pose-t-arms-open-palms-front.png", 50, "Bloque 08: El ciclo completo del aprendizaje profundo"),
    ("bg_09.jpg", "avatar-pose-t-both-thumbs-up.png", 35, "Bloque 09: Tres reglas operables para tus proyectos"),
    ("bg_10.jpg", "avatar-pose-t-beckon-R.png", 30, "Bloque 10: Cierre Guia Hoy y adelanto Clase 2"),
]

def get_audio_duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(res.stdout.strip())

def fmt_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    if not VOICE_WAV.exists():
        raise FileNotFoundError(f"No existe el audio: {VOICE_WAV}")

    total_audio_sec = get_audio_duration(VOICE_WAV)
    base_total = sum(b[2] for b in BLOCKS)
    scale_factor = total_audio_sec / base_total
    print(f"Duracion real de voz Guiahoy: {total_audio_sec:.2f}s (factor escala: {scale_factor:.4f})")

    temp_dir = OUT_DIR / "_segments_pwsh"
    temp_dir.mkdir(parents=True, exist_ok=True)
    segment_files = []
    srt_lines = []
    cursor = 0.0

    for idx, (bg_name, pose_name, nominal_dur, label) in enumerate(BLOCKS, start=1):
        bg_path = BG_DIR / bg_name
        pose_path = AVATAR_DIR / pose_name
        if not bg_path.exists():
            raise FileNotFoundError(f"Falta fondo: {bg_path}")
        if not pose_path.exists():
            raise FileNotFoundError(f"Falta pose avatar: {pose_path}")

        dur = round(nominal_dur * scale_factor, 3)
        if idx == len(BLOCKS):
            dur = max(1.0, round(total_audio_sec - cursor, 3))

        seg_mp4 = temp_dir / f"seg_{idx:02d}.mp4"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-t", f"{dur:.3f}", "-i", str(bg_path),
            "-loop", "1", "-t", f"{dur:.3f}", "-i", str(pose_path),
            "-filter_complex",
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1[bg];"
            "[1:v]scale=-1:780,format=rgba[av];"
            "[bg][av]overlay=W-w-40:H-h:format=auto[vout]",
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30",
            str(seg_mp4),
        ]
        print(f"[{idx:02d}/10] Renderizando {bg_name} + {pose_name} ({dur:.2f}s)...")
        subprocess.run(cmd, check=True)
        segment_files.append(seg_mp4)

        srt_lines.append(f"{idx}\n{fmt_srt_time(cursor)} --> {fmt_srt_time(cursor + dur)}\n{label}\n")
        cursor += dur

    concat_txt = temp_dir / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in segment_files), encoding="utf-8")

    merged_v = temp_dir / "merged_visual.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(merged_v)
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(merged_v),
        "-i", str(VOICE_WAV),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest",
        str(OUT_MP4),
    ], check=True)

    OUT_SRT.write_text("\n".join(srt_lines), encoding="utf-8")
    manifest = {
        "output_mp4": str(OUT_MP4),
        "output_srt": str(OUT_SRT),
        "voice_source": str(VOICE_WAV),
        "duration_sec": total_audio_sec,
        "blocks": len(BLOCKS),
    }
    (OUT_DIR / "render_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        urllib.request.urlopen("http://localhost:6333/collections", timeout=2)
        print("Qdrant activo verificado en localhost:6333.")
    except Exception:
        pass

    print(f"\nLISTO. Video final generado en:\n{OUT_MP4}")
    if os.name == "nt":
        os.startfile(str(OUT_MP4))

if __name__ == "__main__":
    main()
