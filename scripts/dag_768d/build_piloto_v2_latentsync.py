#!/usr/bin/env python3
"""Piloto v2 (8s, carril aislado): Escena 3D neón a pantalla completa + Lip-Sync Wav2Lip real."""

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import cv2
import numpy as np
from gradio_client import Client, handle_file
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

PILOT_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto")
POSE_ORIG = PILOT_DIR / "avatar_v2_transparencias" / "guillermo_v2_01_bienvenida_sonrisa.png"
BG_CLEAN = cfg.BUILD_DIR / "escenas_3d_clean" / "bg_01.jpg"

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
if not Path(FONT_BOLD).exists():
    FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def make_waist_up_avatar_720p() -> tuple[np.ndarray, np.ndarray]:
    """Crop unaltered canonical PNG waist-up (top 62%) and resize cleanly inside 500x670."""
    im = Image.open(POSE_ORIG).convert("RGBA")
    crop_h = int(round(im.height * 0.62))
    bbox = im.crop((0, 0, im.width, crop_h)).getbbox()
    if bbox:
        x0 = max(0, bbox[0] - 24)
        x1 = min(im.width, bbox[2] + 24)
        y0 = max(0, bbox[1] - 12)
        im_crop = im.crop((x0, y0, x1, crop_h))
    else:
        im_crop = im.crop((0, 0, im.width, crop_h))

    target_h = 670
    scale = target_h / im_crop.height
    target_w = int(round(im_crop.width * scale))
    if target_w > 500:
        scale = 500 / im_crop.width
        target_w = 500
        target_h = int(round(im_crop.height * scale))
    im_res = im_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (500, 670), (0, 0, 0, 0))
    canvas.paste(im_res, ((500 - target_w) // 2, 670 - target_h), im_res)
    arr = np.array(canvas, dtype=np.uint8)
    return cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR), arr[:, :, 3]


def build_clean_overlay_1080p() -> Path:
    """Minimal top-left studio pill + thin lower-third subtitle only (~90% neon 3D scene open!)."""
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_pill = ImageFont.truetype(FONT_BOLD, 20)
    f_sub = ImageFont.truetype(FONT_BOLD, 28)

    draw.rounded_rectangle((44, 34, 490, 82), radius=12, fill=(8, 14, 28, 210), outline=(56, 189, 248, 160), width=1)
    draw.text((66, 46), "GUÍA HOY · RIONEGRO, ANTIOQUIA", font=f_pill, fill=(245, 158, 11, 255))

    draw.rounded_rectangle((44, 945, 1180, 1045), radius=14, fill=(8, 13, 25, 215), outline=(56, 189, 248, 150), width=1)
    draw.rounded_rectangle((56, 960, 64, 1030), radius=4, fill=(56, 189, 248, 255))
    lines = textwrap.wrap(
        "Soy Guillermo Alonso Hoyos. Les hablo desde mi mesa de trabajo en Rionegro, Antioquia.",
        width=68,
    )[:2]
    y = 958 if len(lines) == 2 else 978
    for ln in lines:
        draw.text((84, y), ln, font=f_sub, fill=(244, 248, 255, 255))
        y += 38

    ov_path = cfg.LOCAL_TEMP / "piloto_v2" / "minimal_overlay.png"
    img.save(ov_path, "PNG")
    return ov_path


def main() -> None:
    print("=== PILOTO V2 (8s): ESCENA 3D DESPEJADA + WAV2LIP REAL ===", flush=True)
    PILOT_DIR.mkdir(parents=True, exist_ok=True)
    local_work = cfg.LOCAL_TEMP / "piloto_v2"
    local_work.mkdir(parents=True, exist_ok=True)

    # 1. Exact 8.0s audio slice
    audio_8s = local_work / "piloto_audio_8s.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "0", "-t", "8.0", "-i", str(cfg.AUDIO_MASTER),
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(audio_8s)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # 2. Razor-sharp 1280x720 base frame (full neon 3D bg + unaltered Guillermo waist-up on right third)
    base_frame_png = local_work / "piloto_base_frame.png"
    bg_720 = cv2.resize(cv2.imread(str(BG_CLEAN)), (1280, 720), interpolation=cv2.INTER_LANCZOS4)
    av_bgr, av_alp = make_waist_up_avatar_720p()
    av_h, av_w = av_bgr.shape[:2]
    av_x0, av_y0 = 755, 50
    roi = bg_720[av_y0:av_y0 + av_h, av_x0:av_x0 + av_w]

    sh_mat = np.float32([[1.0, 0.0, 8.0], [0.0, 1.0, 4.0]])
    sh_a = cv2.warpAffine(av_alp, sh_mat, (av_w, av_h), flags=cv2.INTER_NEAREST)
    _, sh_mask = cv2.threshold(sh_a, 80, 255, cv2.THRESH_BINARY)
    cv2.copyTo(cv2.convertScaleAbs(roi, alpha=0.70, beta=0), sh_mask, roi)

    edge_mask = cv2.inRange(av_alp, 35, 190)
    cv2.copyTo(cv2.addWeighted(av_bgr, 0.55, roi, 0.45, 0), edge_mask, roi)
    _, solid_mask = cv2.threshold(av_alp, 190, 255, cv2.THRESH_BINARY)
    cv2.copyTo(av_bgr, solid_mask, roi)
    cv2.imwrite(str(base_frame_png), bg_720)
    print(f"[1/4] Base frame 720p y audio 8s listos. Llamando pragnakalp/Wav2lip-ZeroGPU...", flush=True)

    # 3. Call pragnakalp/Wav2lip-ZeroGPU (/run_infrence)
    try:
        client = Client("pragnakalp/Wav2lip-ZeroGPU")
        res = client.predict(
            input_image=handle_file(str(base_frame_png)),
            input_audio=handle_file(str(audio_8s)),
            api_name="/run_infrence",
        )
        vid_path = res.get("video") if isinstance(res, dict) else res
        if not vid_path or not os.path.exists(str(vid_path)):
            raise RuntimeError(f"Retorno inesperado de Wav2Lip: {res}")
    except Exception as exc:
        err_report = {"status": "BLOCKED", "engine": "pragnakalp/Wav2lip-ZeroGPU", "cause": str(exc)}
        (PILOT_DIR / "piloto_status.json").write_text(json.dumps(err_report, indent=2, ensure_ascii=False), encoding="utf-8")
        print("BLOCKED:", err_report, flush=True)
        sys.exit(2)

    print(f"[2/4] Wav2Lip completado: {vid_path}", flush=True)
    raw_w2l = local_work / "wav2lip_raw.mp4"
    shutil.copy2(str(vid_path), str(raw_w2l))

    # 4. Smooth subtle zoom + minimal unobstructed lower-third & top-left badge -> 1920x1080 @ 60fps
    ov_png = build_clean_overlay_1080p()
    final_piloto = PILOT_DIR / "piloto_v2_sonrisa_8s.mp4"
    local_final = local_work / "piloto_v2_sonrisa_8s.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_w2l),
        "-i", str(ov_png),
        "-i", str(audio_8s),
        "-filter_complex",
        "[0:v]scale=2016:1134:flags=lanczos,crop=1920:1080:'(iw-1920)*0.5*(1-t/8.0)':'(ih-1080)*0.5',fps=60[base];[base][1:v]overlay=0:0[outv]",
        "-map", "[outv]", "-map", "2:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
        str(local_final),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy2(str(local_final), str(final_piloto))

    for qn, ts in [("qa_v2_sonrisa_t02.png", "2.0"), ("qa_v2_sonrisa_t05.png", "5.5")]:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", ts, "-i", str(final_piloto), "-frames:v", "1", str(PILOT_DIR / qn)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", str(final_piloto)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(pr.stdout)
    (PILOT_DIR / "piloto_status.json").write_text(json.dumps({
        "status": "PASS",
        "engine": "pragnakalp/Wav2lip-ZeroGPU",
        "piloto_mp4": str(final_piloto),
        "size_bytes": final_piloto.stat().st_size,
        "streams": info["streams"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[4/4] PILOTO V2 LISTO: {final_piloto} ({final_piloto.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
