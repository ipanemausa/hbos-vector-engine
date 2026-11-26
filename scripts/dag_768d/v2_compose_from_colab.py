"""Compose v2 full-body avatar output from Google Colab chroma-key video (or --dry-run).

Applies HSV chroma keying + green spill suppression onto Guillermo's full body,
grounds him with a realistic floor shadow over the unobstructed 1920x1080 3D scene,
adds subtle volumetric light particles, thin lower-third subtitle, and clean 48kHz audio.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np

KIT_DIR = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\colab_3d_kit"
)
OUT_DIR = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\colab_3d_out"
)
BG_DEFAULT = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_build\build\escenas_3d_clean\bg_01.jpg"
)
AUDIO_48K = KIT_DIR / "piloto_10s_48k.wav"
ARTIFACT_DIR = Path(
    r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83"
)

CANVAS_W = 1920
CANVAS_H = 1080


def extract_chroma_alpha_and_despill(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Key out #00B140 green screen cleanly and remove edge green spill without eating black/blue."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0].astype(np.float32)  # OpenCV hue range [0..179]
    s = hsv[:, :, 1].astype(np.float32)
    v = hsv[:, :, 2].astype(np.float32)

    # Studio #00B140 sits near H=71 (OpenCV scale). Target [38..92] with high saturation.
    green_band = (h >= 38) & (h <= 92) & (s >= 65) & (v >= 55)
    # Distance in hue & green-dominance for soft feathering
    b_ch = bgr[:, :, 0].astype(np.float32)
    g_ch = bgr[:, :, 1].astype(np.float32)
    r_ch = bgr[:, :, 2].astype(np.float32)
    green_excess = g_ch - np.maximum(r_ch, b_ch)

    bg_score = np.where(
        green_band & (green_excess > 18.0),
        np.clip((green_excess - 18.0) / 42.0, 0.0, 1.0),
        0.0,
    )
    alpha = 1.0 - bg_score

    # Clean tiny isolated noise and gently feather silhouette 1.2px
    mask_u8 = (alpha * 255).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_u8 = cv2.morphologyEx(mask_u8, cv2.MORPH_OPEN, kernel)
    alpha_soft = cv2.GaussianBlur(mask_u8.astype(np.float32) / 255.0, (3, 3), 0.7)

    # Despill ONLY on semi-transparent boundary / green-dominant fringe pixels
    fringe = (alpha_soft < 0.98) | ((h >= 40) & (h <= 90) & (green_excess > 8.0))
    despilled = bgr.astype(np.float32).copy()
    max_rb = np.maximum(r_ch, b_ch)
    despilled[:, :, 1] = np.where(fringe, np.minimum(g_ch, max_rb + 2.0), g_ch)
    return np.clip(despilled, 0, 255).astype(np.uint8), np.clip(alpha_soft, 0.0, 1.0)


def draw_floor_shadow(
    bg: np.ndarray, center_x: int, foot_y: int, width_px: int
) -> np.ndarray:
    """Cast a soft elliptical contact shadow under Guillermo's shoes for 3D grounding."""
    shadow_layer = np.zeros((CANVAS_H, CANVAS_W), dtype=np.float32)
    cv2.ellipse(
        shadow_layer,
        (center_x, min(CANVAS_H - 6, foot_y - 4)),
        (max(40, int(width_px * 0.42)), 14),
        0,
        0,
        360,
        0.52,
        -1,
    )
    shadow_layer = cv2.GaussianBlur(shadow_layer, (35, 19), 0)
    out = bg.astype(np.float32) * (1.0 - shadow_layer[..., None])
    return np.clip(out, 0, 255).astype(np.uint8)


def add_subtle_3d_particles(frame: np.ndarray, t_sec: float) -> np.ndarray:
    """Add sparse ambient cyber particles matching Guía Hoy cyan/amber palette without clutter."""
    out = frame.copy()
    for i in range(14):
        px = int(((i * 157 + t_sec * (18 + (i % 4) * 5)) % CANVAS_W))
        py = int(((i * 97 + np.sin(t_sec * 0.8 + i) * 45 + 140) % (CANVAS_H - 120)))
        color = (245, 210, 60) if i % 3 else (70, 195, 255)
        radius = 2 if i % 2 == 0 else 3
        cv2.circle(out, (px, py), radius, color, -1, cv2.LINE_AA)
    return out


def draw_thin_lower_third(frame: np.ndarray, text: str) -> np.ndarray:
    """Overlay a slim lower-third subtitle pill keeping ~90% of the 3D scene open."""
    overlay = frame.copy()
    bar_y1, bar_y2 = CANVAS_H - 66, CANVAS_H - 18
    cv2.rectangle(overlay, (360, bar_y1), (CANVAS_W - 60, bar_y2), (14, 18, 30), -1)
    out = cv2.addWeighted(overlay, 0.72, frame, 0.28, 0)
    cv2.putText(
        out,
        text,
        (385, CANVAS_H - 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (240, 248, 255),
        2,
        cv2.LINE_AA,
    )
    return out


def compose_full_body_frame(
    bg_1080: np.ndarray,
    full_pose_chroma: np.ndarray,
    animated_upper_chroma: np.ndarray | None,
    t_sec: float,
    subtitle: str,
    side: str = "left",
) -> np.ndarray:
    """Composite animated upper-body + grounded full-body stance cleanly onto 1080p 3D scene."""
    full_bgr, full_alpha = extract_chroma_alpha_and_despill(full_pose_chroma)

    # Tight vertical/horizontal crop of full body from chroma canvas
    ys, xs = np.where(full_alpha > 0.15)
    y_min, y_max = int(ys.min()), int(ys.max()) + 1
    x_min, x_max = int(xs.min()), int(xs.max()) + 1

    body_bgr = full_bgr[y_min:y_max, x_min:x_max].copy()
    body_alpha = full_alpha[y_min:y_max, x_min:x_max].copy()

    # If Colab returned animated upper body (head/shoulders/lips/arms), fuse upper region seamlessly
    if animated_upper_chroma is not None:
        anim_bgr, anim_alpha = extract_chroma_alpha_and_despill(animated_upper_chroma)
        ays, axs = np.where(anim_alpha > 0.15)
        if len(ays) > 0 and len(axs) > 0:
            # Align animated upper crop to the exact top 52% of the standing pose
            anim_crop_bgr = anim_bgr[ays.min() : ays.max() + 1, axs.min() : axs.max() + 1]
            anim_crop_a = anim_alpha[ays.min() : ays.max() + 1, axs.min() : axs.max() + 1]
            target_h = max(64, int(body_bgr.shape[0] * 0.52))
            target_w = body_bgr.shape[1]
            scale = min(target_w / anim_crop_bgr.shape[1], target_h / anim_crop_bgr.shape[0])
            rw = max(2, int(round(anim_crop_bgr.shape[1] * scale)))
            rh = max(2, int(round(anim_crop_bgr.shape[0] * scale)))
            rs_bgr = cv2.resize(anim_crop_bgr, (rw, rh), interpolation=cv2.INTER_LANCZOS4)
            rs_a = cv2.resize(anim_crop_a, (rw, rh), interpolation=cv2.INTER_LANCZOS4)
            dx = max(0, (target_w - rw) // 2)
            # Soft feather bottom seam over torso (last 18% of animated crop) so waist blends naturally
            seam_h = max(8, int(rh * 0.18))
            grad = np.ones((rh, rw), dtype=np.float32)
            grad[-seam_h:, :] = np.linspace(1.0, 0.0, seam_h)[:, None]
            mix_w = (rs_a * grad)[..., None]
            roi_bgr = body_bgr[:rh, dx : dx + rw].astype(np.float32)
            body_bgr[:rh, dx : dx + rw] = np.clip(
                rs_bgr.astype(np.float32) * mix_w + roi_bgr * (1.0 - mix_w), 0, 255
            ).astype(np.uint8)
            body_alpha[:rh, dx : dx + rw] = np.maximum(
                body_alpha[:rh, dx : dx + rw] * (1.0 - grad), rs_a * grad
            ) + body_alpha[:rh, dx : dx + rw] * (1.0 - grad) * (1.0 - rs_a * grad)

    # Place Guillermo full-body at ~76% frame height on left (leaving ~90% of 3D art unobstructed)
    target_body_h = 820
    scale = target_body_h / body_bgr.shape[0]
    out_w = max(2, int(round(body_bgr.shape[1] * scale)))
    out_h = target_body_h

    # Subtle human breathing / weight-shift micro-motion (1.2px vertical, 0px distortion)
    breath_dy = int(round(np.sin(t_sec * 1.9) * 1.5))
    foot_y = CANVAS_H - 22 + breath_dy
    y0 = max(12, foot_y - out_h)
    x0 = 46 if side == "left" else (CANVAS_W - out_w - 46)

    rs_body = cv2.resize(body_bgr, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
    rs_alpha = cv2.resize(body_alpha, (out_w, out_h), interpolation=cv2.INTER_LINEAR)[..., None]

    scene = add_subtle_3d_particles(bg_1080, t_sec)
    scene = draw_floor_shadow(scene, x0 + out_w // 2, foot_y, out_w)

    roi = scene[y0 : y0 + out_h, x0 : x0 + out_w].astype(np.float32)
    comp = np.clip(rs_body.astype(np.float32) * rs_alpha + roi * (1.0 - rs_alpha), 0, 255)
    scene[y0 : y0 + out_h, x0 : x0 + out_w] = comp.astype(np.uint8)
    return draw_thin_lower_third(scene, subtitle)


def run_dry_run() -> None:
    """Verify full-body chroma despill and grounding locally with zero GPU usage."""
    full_pose_path = KIT_DIR / "chroma_full_01.png"
    upper_pose_path = KIT_DIR / "chroma_upper_01.png"
    bg = cv2.imread(str(BG_DEFAULT))
    full_pose = cv2.imread(str(full_pose_path))
    upper_pose = cv2.imread(str(upper_pose_path))
    if bg is None or full_pose is None or upper_pose is None:
        raise FileNotFoundError("Run prepare_v2_colab_kit.py before --dry-run")

    frame = compose_full_body_frame(
        bg_1080=bg,
        full_pose_chroma=full_pose,
        animated_upper_chroma=upper_pose,
        t_sec=1.5,
        subtitle="Guillermo Alonso Hoyos - Rionegro, Antioquia (QA v2 Cuerpo Entero)",
    )
    qa_path = KIT_DIR / "qa_v2_despill_cuerpo_entero.png"
    cv2.imwrite(str(qa_path), frame)
    if ARTIFACT_DIR.exists():
        shutil.copy2(qa_path, ARTIFACT_DIR / qa_path.name)
    print(f"PASS: dry-run QA frame saved to {qa_path}")


def run_video_compose(colab_video: Path, out_video: Path, pose_id: str) -> None:
    """Composite a Colab chroma-key animated avatar MP4 onto full-body 1080p 3D scene + 48kHz audio."""
    bg = cv2.imread(str(BG_DEFAULT))
    full_pose = cv2.imread(str(KIT_DIR / f"chroma_full_{pose_id}.png"))
    if bg is None or full_pose is None:
        raise FileNotFoundError("Missing background or chroma full pose in kit")

    cap = cv2.VideoCapture(str(colab_video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        raise RuntimeError(f"Empty video from Colab: {colab_video}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_mp4 = OUT_DIR / (out_video.stem + "_silent.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(raw_mp4), fourcc, fps, (CANVAS_W, CANVAS_H))

    idx = 0
    while True:
        ok, anim_frame = cap.read()
        if not ok:
            break
        t_sec = idx / fps
        comp = compose_full_body_frame(
            bg_1080=bg,
            full_pose_chroma=full_pose,
            animated_upper_chroma=anim_frame,
            t_sec=t_sec,
            subtitle="Soy Guillermo Alonso Hoyos - Equipo de Agentes de IA",
        )
        writer.write(comp)
        idx += 1
    cap.release()
    writer.release()

    duration = idx / fps
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(raw_mp4),
        "-t",
        f"{duration:.3f}",
        "-i",
        str(AUDIO_48K),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(out_video),
    ]
    subprocess.run(cmd, check=True)
    raw_mp4.unlink(missing_ok=True)
    print(f"PASS: final v2 pilot video saved to {out_video}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--colab-video", type=Path)
    parser.add_argument(
        "--out-video",
        type=Path,
        default=OUT_DIR / "piloto_v2_humano_colab_final.mp4",
    )
    parser.add_argument("--pose-id", default="01")
    args = parser.parse_args()

    if args.dry_run:
        run_dry_run()
        return
    if not args.colab_video or not args.colab_video.exists():
        raise FileNotFoundError(f"Specify existing --colab-video MP4: {args.colab_video}")
    run_video_compose(args.colab_video, args.out_video, args.pose_id)


if __name__ == "__main__":
    main()
