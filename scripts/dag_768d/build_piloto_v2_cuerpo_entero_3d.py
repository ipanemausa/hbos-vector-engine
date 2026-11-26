#!/usr/bin/env python3
"""Piloto v2 Cuerpo Entero 3D Humanizado Cinemático (8s, 1080p 60fps, 0 SaaS Tax)."""

import json
import math
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
POSE_FULL = Path(r"G:\My Drive\AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS\guillermo_oficial_01_bienvenida.png")
BG_CLEAN = cfg.BUILD_DIR / "escenas_3d_clean" / "bg_01.jpg"

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
if not Path(FONT_BOLD).exists():
    FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def prepare_fullbody_canvas(pose_path: Path) -> tuple[np.ndarray, np.ndarray, tuple[int, int, int, int]]:
    """Scale official RGBA pose cleanly to height ~950 inside 680x960 canvas preserving head-to-sneakers."""
    im = Image.open(pose_path).convert("RGBA")
    target_h = 945
    scale = min(650.0 / im.width, target_h / im.height)
    nw = max(1, int(round(im.width * scale)))
    nh = max(1, int(round(im.height * scale)))
    im_res = im.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (680, 960), (0, 0, 0, 0))
    px = (680 - nw) // 2
    py = 960 - nh - 4
    canvas.paste(im_res, (px, py), im_res)

    arr = np.array(canvas, dtype=np.uint8)
    bgr = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    alpha = arr[:, :, 3]

    # Detect exact face rectangle inside upper body
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray[:320, :], scaleFactor=1.1, minNeighbors=4, minSize=(45, 45))
    if len(faces) > 0:
        fx, fy, fw, fh = [int(v) for v in max(faces, key=lambda r: r[2] * r[3])]
    else:
        fx, fy, fw, fh = 285, 42, 110, 125
    print(f"[FACE DETECT] Pose 680x960 face box: x={fx}, y={fy}, w={fw}, h={fh}", flush=True)
    return bgr, alpha, (fx, fy, fw, fh)


def build_clean_hud_layers() -> tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]:
    """Pre-render minimal unobstructed lower-third + floating KPI badge (~88% 3D scene open)."""
    f_pill = ImageFont.truetype(FONT_BOLD, 19)
    f_kpi = ImageFont.truetype(FONT_BOLD, 21)
    f_sub = ImageFont.truetype(FONT_BOLD, 27)

    # Layer 1: Always-on sleek pill + thin lower-third subtitle
    im1 = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(im1)
    d1.rounded_rectangle((44, 34, 490, 82), radius=12, fill=(8, 14, 28, 205), outline=(56, 189, 248, 160), width=1)
    d1.text((66, 46), "GUÍA HOY · RIONEGRO, ANTIOQUIA", font=f_pill, fill=(245, 158, 11, 255))

    d1.rounded_rectangle((44, 945, 1170, 1045), radius=14, fill=(8, 13, 25, 215), outline=(56, 189, 248, 150), width=1)
    d1.rounded_rectangle((56, 960, 64, 1030), radius=4, fill=(56, 189, 248, 255))
    lines = textwrap.wrap(
        "Soy Guillermo Alonso Hoyos. Les hablo desde mi mesa de trabajo en Rionegro, Antioquia.",
        width=66,
    )[:2]
    y = 958 if len(lines) == 2 else 978
    for ln in lines:
        d1.text((84, y), ln, font=f_sub, fill=(244, 248, 255, 255))
        y += 38

    a1 = np.array(im1, dtype=np.uint8)
    l1 = (cv2.cvtColor(a1[:, :, :3], cv2.COLOR_RGB2BGR), ((a1[:, :, 3] > 64).astype(np.uint8) * 255))

    # Layer 2: Brief floating micro-KPI badge (fades in 3.2s..7.6s without blocking 3D scenery)
    im2 = Image.new("RGBA", (420, 90), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(im2)
    d2.rounded_rectangle((0, 0, 420, 90), radius=14, fill=(10, 20, 38, 225), outline=(56, 189, 248, 190), width=2)
    d2.text((22, 16), "ARQUITECTURA MULTI-AGENTE", font=f_pill, fill=(56, 189, 248, 255))
    d2.text((22, 46), "EQUIPO IA · 0 SAAS TAX", font=f_kpi, fill=(245, 158, 11, 255))
    a2 = np.array(im2, dtype=np.uint8)
    l2 = (cv2.cvtColor(a2[:, :, :3], cv2.COLOR_RGB2BGR), ((a2[:, :, 3] > 64).astype(np.uint8) * 255))
    return l1, l2


def main() -> None:
    print("=== PILOTO V2 CUERPO ENTERO 3D HUMANIZADO (8s @ 60fps) ===", flush=True)
    PILOT_DIR.mkdir(parents=True, exist_ok=True)
    work = cfg.LOCAL_TEMP / "piloto_v2_ce"
    work.mkdir(parents=True, exist_ok=True)

    # 1. Exact 8.0s audio slice
    audio_8s = work / "audio_8s.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "0", "-t", "8.0", "-i", str(cfg.AUDIO_MASTER),
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(audio_8s)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # 2. Prepare unaltered full-body canvas & extract razor-sharp 512x512 portrait patch for Wav2Lip
    av_bgr, av_alp, (fx, fy, fw, fh) = prepare_fullbody_canvas(POSE_FULL)
    patch_half = max(int(fw * 1.45), 150)
    cx = fx + fw // 2
    cy = fy + int(fh * 0.50)
    px0 = max(0, cx - patch_half)
    py0 = max(0, cy - patch_half)
    px1 = min(680, cx + patch_half)
    py1 = min(960, cy + patch_half)
    pw, ph = px1 - px0, py1 - py0

    # Composite portrait patch over clean studio slate (#182232) so Wav2Lip tracks crisp contrast
    patch_bg = np.full((ph, pw, 3), (50, 34, 24), dtype=np.uint8)
    pa = (av_alp[py0:py1, px0:px1].astype(np.float32) / 255.0)[:, :, None]
    patch_clean = np.clip(av_bgr[py0:py1, px0:px1] * pa + patch_bg * (1.0 - pa), 0, 255).astype(np.uint8)
    head_512 = cv2.resize(patch_clean, (512, 512), interpolation=cv2.INTER_LANCZOS4)
    head_png = work / "head_patch_512.png"
    cv2.imwrite(str(head_png), head_png_img := head_512)

    print("[1/4] Parche facial 512x512 listo. Llamando pragnakalp/Wav2lip-ZeroGPU...", flush=True)
    try:
        client = Client("pragnakalp/Wav2lip-ZeroGPU")
        res = client.predict(
            input_image=handle_file(str(head_png)),
            input_audio=handle_file(str(audio_8s)),
            api_name="/run_infrence",
        )
        vid_path = res.get("video") if isinstance(res, dict) else res
        if not vid_path or not os.path.exists(str(vid_path)):
            raise RuntimeError(f"Retorno invalido Wav2Lip: {res}")
    except Exception as exc:
        err = {"status": "BLOCKED", "engine": "pragnakalp/Wav2lip-ZeroGPU", "cause": str(exc)}
        (PILOT_DIR / "piloto_ce_status.json").write_text(json.dumps(err, indent=2, ensure_ascii=False), encoding="utf-8")
        print("BLOCKED:", err, flush=True)
        sys.exit(2)

    print(f"[2/4] Wav2Lip completado: {vid_path}", flush=True)
    cap = cv2.VideoCapture(str(vid_path))
    w2l_frames = []
    while True:
        ok, frm = cap.read()
        if not ok:
            break
        w2l_frames.append(cv2.resize(frm, (pw, ph), interpolation=cv2.INTER_LANCZOS4))
    cap.release()
    if not w2l_frames:
        raise RuntimeError("Wav2Lip retorno 0 cuadros")

    # Smooth oval feather mask strictly over lower mouth/chin region (keeps eyes, glasses, nose tip untouched)
    mouth_mask = np.zeros((ph, pw), dtype=np.float32)
    mcx = int((fx + fw * 0.50) - px0)
    mcy = int((fy + fh * 0.77) - py0)
    mrx = max(14, int(fw * 0.25))
    mry = max(10, int(fh * 0.17))
    cv2.ellipse(mouth_mask, (mcx, mcy), (mrx, mry), 0, 0, 360, 1.0, -1)
    mouth_mask = cv2.GaussianBlur(mouth_mask, (21, 21), 7.0)
    # Never bleed outside silhouette alpha
    sil_norm = np.clip((av_alp[py0:py1, px0:px1].astype(np.float32) - 140.0) / 115.0, 0.0, 1.0)
    mouth_mask = (mouth_mask * sil_norm)[:, :, None]

    # Precompute 3D volumetric particles + studio rim halo + grounded floor ellipse shadow
    bg_up = cv2.resize(cv2.imread(str(BG_CLEAN)), (2208, 1242), interpolation=cv2.INTER_CUBIC)
    (base_bgr, base_mask), (kpi_bgr, kpi_mask) = build_clean_hud_layers()

    rng = np.random.default_rng(768)
    particles = [
        (rng.uniform(80, 1840), rng.uniform(80, 920), rng.uniform(1.8, 5.2),
         rng.uniform(18, 42), rng.uniform(0.3, 1.2), bool(i % 3 == 0))
        for i in range(28)
    ]

    # Volumetric cyan/amber halo centered behind Guillermo (x=1220..1900, y=95..1055)
    hy, hx = np.ogrid[:960, :680]
    dsq = ((hx - 340.0) / 270.0) ** 2 + ((hy - 410.0) / 390.0) ** 2
    h_exp = np.exp(-1.5 * dsq).astype(np.float32)
    halo_bgr = np.zeros((960, 680, 3), dtype=np.uint8)
    halo_bgr[:, :, 0] = np.clip(h_exp * 38.0, 0, 255).astype(np.uint8)
    halo_bgr[:, :, 1] = np.clip(h_exp * 26.0, 0, 255).astype(np.uint8)
    halo_bgr[:, :, 2] = np.clip(h_exp * 14.0, 0, 255).astype(np.uint8)

    local_final = work / "piloto_v2_cuerpo_entero_3d_8s.mp4"
    final_drive = PILOT_DIR / "piloto_v2_cuerpo_entero_3d_8s.mp4"
    temp_silent = work / "ce_silent_1080p60.mp4"

    proc = subprocess.Popen([
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", "1920x1080", "-pix_fmt", "bgr24", "-r", "60", "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        str(temp_silent),
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    av_x0, av_y0 = 1220, 98  # Full body grounded with feet around y=1054 inside 1920x1080
    sh_mat = np.float32([[1.0, 0.0, 12.0], [0.0, 1.0, 6.0]])
    n_frames = 480  # 8.0s @ 60fps

    print("[3/4] Renderizando 480 cuadros 1080p60 cuerpo entero + partículas 3D + sombra de piso...", flush=True)
    for fi in range(n_frames):
        t = fi / 60.0
        prog = fi / max(1, n_frames - 1)

        # Plane Z0: Smooth 2.5D dolly-in across unobstructed 3D neon scene
        zoom = 1.0 - 0.07 * prog
        inv_s = 1.0 / zoom
        m_cam = np.float32([
            [inv_s, 0.0, 960.0 - inv_s * (1104.0 + 18.0 * math.sin(math.pi * prog))],
            [0.0, inv_s, 540.0 - inv_s * (621.0 - 8.0 * prog)],
        ])
        frame = cv2.warpAffine(bg_up, m_cam, (1920, 1080), flags=cv2.INTER_LINEAR)

        # Plane Z1: Drifting 3D volumetric bokeh dust motes (cyan & warm amber)
        part_layer = frame.copy()
        for px_b, py_b, rad, speed_y, phase, is_amber in particles:
            px_i = int((px_b + 16.0 * math.sin(t * 0.9 + phase)) % 1920)
            py_i = int((py_b - t * speed_y) % 1080)
            col = (24, 155, 245) if is_amber else (248, 195, 68)
            cv2.circle(part_layer, (px_i, py_i), int(rad + 2), col, -1)
        frame = cv2.addWeighted(part_layer, 0.22, frame, 0.78, 0)

        # Plane Z2: Grounded full-body Guillermo with real Wav2Lip mouth patch spliced seamlessly
        widx = min(len(w2l_frames) - 1, int(round(t * 25.0)))
        cur_av = av_bgr.copy()
        orig_patch = cur_av[py0:py1, px0:px1].astype(np.float32)
        lip_patch = w2l_frames[widx].astype(np.float32)
        cur_av[py0:py1, px0:px1] = np.clip(lip_patch * mouth_mask + orig_patch * (1.0 - mouth_mask), 0, 255).astype(np.uint8)

        # Anchor pivot near ankles/shoes (y = 0.97 * 960) so shoes stay firmly planted on floor
        breath = 1.0 + 0.0055 * math.sin(2.0 * math.pi * 0.25 * t)
        ang = 0.45 * math.sin(2.0 * math.pi * 0.19 * t)
        sx = 2.5 * math.sin(2.0 * math.pi * 0.20 * t)
        mat = cv2.getRotationMatrix2D((340.0, 932.0), ang, breath)
        mat[0, 2] += sx

        wbgr = cv2.warpAffine(cur_av, mat, (680, 960), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        walp = cv2.warpAffine(av_alp, mat, (680, 960), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        # Grounded elliptical floor shadow beneath his white-soled sneakers
        fl_roi = frame[1025:1075, 1370:1750]
        fl_dark = cv2.convertScaleAbs(fl_roi, alpha=0.48, beta=0)
        fl_mask = np.zeros((50, 380), dtype=np.uint8)
        cv2.ellipse(fl_mask, (190, 26), (145, 14), 0, 0, 360, 255, -1)
        fl_mask = cv2.GaussianBlur(fl_mask, (31, 17), 9)
        _, fl_bin = cv2.threshold(fl_mask, 70, 255, cv2.THRESH_BINARY)
        cv2.copyTo(fl_dark, fl_bin, fl_roi)

        av_roi = frame[av_y0:av_y0 + 960, av_x0:av_x0 + 680]
        cv2.add(av_roi, halo_bgr, dst=av_roi)

        sh_a = cv2.warpAffine(walp, sh_mat, (680, 960), flags=cv2.INTER_NEAREST)
        _, sh_m = cv2.threshold(sh_a, 80, 255, cv2.THRESH_BINARY)
        cv2.copyTo(cv2.convertScaleAbs(av_roi, alpha=0.68, beta=0), sh_m, av_roi)

        edge_m = cv2.inRange(walp, 35, 190)
        cv2.copyTo(cv2.addWeighted(wbgr, 0.55, av_roi, 0.45, 0), edge_m, av_roi)
        _, solid_m = cv2.threshold(walp, 190, 255, cv2.THRESH_BINARY)
        cv2.copyTo(wbgr, solid_m, av_roi)

        # Plane Z3: Minimal broadcast HUD (unobstructed neon 3D studio)
        blended_hud = cv2.addWeighted(base_bgr, 0.86, frame, 0.14, 0)
        cv2.copyTo(blended_hud, base_mask, frame)

        # Brief floating micro-KPI badge [3.2s..7.6s]
        if 3.2 <= t <= 7.6:
            kr = frame[105:195, 44:464]
            kb = cv2.addWeighted(kpi_bgr, 0.88, kr, 0.12, 0)
            cv2.copyTo(kb, kpi_mask, kr)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    err_s = proc.stderr.read().decode("utf-8", errors="replace")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed: {err_s[-400:]}")

    subprocess.run([
        "ffmpeg", "-y", "-i", str(temp_silent), "-i", str(audio_8s),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", str(local_final),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy2(str(local_final), str(final_drive))

    for qn, ts in [("qa_ce_t02.png", "2.2"), ("qa_ce_t06.png", "6.0")]:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", ts, "-i", str(final_drive), "-frames:v", "1", str(PILOT_DIR / qn)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    print(f"[4/4] PILOTO CUERPO ENTERO 3D LISTO: {final_drive} ({final_drive.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
