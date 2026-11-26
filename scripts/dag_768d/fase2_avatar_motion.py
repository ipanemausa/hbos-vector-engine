#!/usr/bin/env python3
"""FASE 2 — Avatar Alpha Normalization, 60fps Vocal Envelope, and Humanized Motion Verification."""

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

AVATAR_CANVAS_W = 680
AVATAR_CANVAS_H = 960


def normalize_avatar_pose(src_path: Path, dst_path: Path) -> dict:
    """Normalize a transparent full-body RGBA pose onto a uniform 680x960 canvas with soft edge & rim glow."""
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im, dtype=np.uint8)
    # Uniform proportional scale preserving aspect ratio inside 680x960
    scale = min((AVATAR_CANVAS_W - 20) / im.width, (AVATAR_CANVAS_H - 12) / im.height)
    new_w = max(1, int(round(im.width * scale)))
    new_h = max(1, int(round(im.height * scale)))
    resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Gentle anti-aliased edge smoothing on alpha channel only (suppresses harsh cutouts)
    r, g, b, a = resized.split()
    a_blur = a.filter(ImageFilter.GaussianBlur(radius=0.6))
    a_np = np.minimum(np.array(a, dtype=np.uint8), np.array(a_blur, dtype=np.uint8) + 8)
    # Keep solid interior intact
    a_orig = np.array(a, dtype=np.uint8)
    a_clean = np.where(a_orig > 240, a_orig, a_np).astype(np.uint8)
    resized = Image.merge("RGBA", (r, g, b, Image.fromarray(a_clean, mode="L")))

    canvas = Image.new("RGBA", (AVATAR_CANVAS_W, AVATAR_CANVAS_H), (0, 0, 0, 0))
    paste_x = (AVATAR_CANVAS_W - new_w) // 2
    paste_y = AVATAR_CANVAS_H - new_h
    canvas.paste(resized, (paste_x, paste_y), resized)
    canvas.save(dst_path, "PNG")

    c_arr = np.array(canvas)
    corners = [int(c_arr[0, 0, 3]), int(c_arr[0, -1, 3]), int(c_arr[-1, 0, 3]), int(c_arr[-1, -1, 3])]
    bbox = canvas.getbbox()
    return {
        "name": dst_path.name,
        "path": str(dst_path),
        "size_bytes": dst_path.stat().st_size,
        "canvas": [AVATAR_CANVAS_W, AVATAR_CANVAS_H],
        "corner_alpha": corners,
        "bbox": list(bbox) if bbox else None,
        "clean_corners": all(c == 0 for c in corners),
    }


def compute_vocal_envelope_60fps(wav_path: Path, total_frames: int) -> np.ndarray:
    """Compute normalized [rms_energy, syllabic_activity] per 60fps frame directly from the WAV."""
    samples, sr = sf.read(str(wav_path), dtype="float32")
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    samples_per_frame = sr / cfg.TARGET_FPS
    win_half = int(sr * 0.025)

    rms = np.zeros(total_frames, dtype=np.float32)
    n_tot = len(samples)
    for f in range(total_frames):
        center = int(round((f + 0.5) * samples_per_frame))
        lo = max(0, center - win_half)
        hi = min(n_tot, center + win_half)
        if hi > lo:
            seg = samples[lo:hi]
            rms[f] = float(np.sqrt(np.mean(seg * seg)))

    p95 = float(np.percentile(rms, 95)) or 1.0
    norm_rms = np.clip(rms / p95, 0.0, 1.0)
    # Smooth envelope (fast attack, gentle release)
    smooth = np.zeros_like(norm_rms)
    cur = 0.0
    for i, val in enumerate(norm_rms):
        alpha = 0.35 if val > cur else 0.14
        cur = cur + alpha * (val - cur)
        smooth[i] = cur

    # Syllabic oscillation gated by active speech (>0.08)
    syllabic = np.zeros_like(smooth)
    for i in range(total_frames):
        if smooth[i] > 0.08:
            t = i / cfg.TARGET_FPS
            syllabic[i] = smooth[i] * (0.55 + 0.45 * math.sin(2.0 * math.pi * 4.3 * t + 0.7 * math.sin(1.9 * t)))
    return np.stack([smooth, np.clip(syllabic, 0.0, 1.0)], axis=1).astype(np.float32)


def render_avatar_frame(
    pose_bgr: np.ndarray,
    pose_alpha: np.ndarray,
    t_sec: float,
    speech_rms: float,
    speech_syl: float,
    bg_bgr: np.ndarray,
    dest_x: int,
    dest_y: int,
) -> np.ndarray:
    """Composite a continuously animated humanized avatar onto bg_bgr at (dest_x, dest_y)."""
    h, w = pose_bgr.shape[:2]
    # Continuous breathing + weight sway + speech-synced head/upper-body cadence
    breath = 1.0 + 0.0085 * math.sin(2.0 * math.pi * 0.26 * t_sec) + 0.0055 * speech_syl
    sway_x = 5.5 * math.sin(2.0 * math.pi * 0.21 * t_sec) + 1.8 * speech_rms * math.sin(2.0 * math.pi * 1.1 * t_sec)
    sway_y = 3.2 * math.cos(2.0 * math.pi * 0.42 * t_sec) - 3.5 * speech_syl
    angle_deg = 0.85 * math.sin(2.0 * math.pi * 0.19 * t_sec) + 0.65 * speech_rms * math.sin(2.0 * math.pi * 1.45 * t_sec)

    # Anchor pivot near waist/feet bottom center so grounding stays realistic
    cx, cy = w * 0.5, h * 0.88
    mat = cv2.getRotationMatrix2D((cx, cy), angle_deg, breath)
    mat[0, 2] += sway_x
    mat[1, 2] += sway_y

    warped_bgr = cv2.warpAffine(pose_bgr, mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    warped_a = cv2.warpAffine(pose_alpha, mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0)

    # Subtle speaking mouth/chin vertical micro-motion on upper-head region (top 22% of canvas height)
    if speech_syl > 0.05:
        head_y_end = int(h * 0.26)
        jaw_shift = 1.8 * speech_syl
        # Subtle warm studio rim/key response during active speech
        warped_bgr[:head_y_end] = np.clip(warped_bgr[:head_y_end] * (1.0 + 0.03 * speech_syl), 0, 255)
        if jaw_shift > 0.2:
            jaw_slice_y0 = int(h * 0.13)
            jaw_slice_y1 = int(h * 0.20)
            m_jaw = np.float32([[1, 0, 0], [0, 1, jaw_shift]])
            warped_bgr[jaw_slice_y0:jaw_slice_y1] = cv2.warpAffine(
                warped_bgr[jaw_slice_y0:jaw_slice_y1], m_jaw, (w, jaw_slice_y1 - jaw_slice_y0),
                flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
            )

    # Clip to target ROI on bg_bgr
    bg_h, bg_w = bg_bgr.shape[:2]
    x0 = max(0, dest_x)
    y0 = max(0, dest_y)
    x1 = min(bg_w, dest_x + w)
    y1 = min(bg_h, dest_y + h)
    sx0, sy0 = x0 - dest_x, y0 - dest_y
    sx1, sy1 = sx0 + (x1 - x0), sy0 + (y1 - y0)

    roi = bg_bgr[y0:y1, x0:x1].astype(np.float32)
    fg = warped_bgr[sy0:sy1, sx0:sx1].astype(np.float32)
    alpha = warped_a[sy0:sy1, sx0:sx1, None]

    # Soft contact shadow offset slightly right/down
    shadow_a = cv2.GaussianBlur(warped_a[sy0:sy1, sx0:sx1], (25, 25), 9) * 0.42
    roi = roi * (1.0 - shadow_a[:, :, None])
    out_roi = fg * alpha + roi * (1.0 - alpha)
    bg_bgr[y0:y1, x0:x1] = np.clip(out_roi, 0, 255).astype(np.uint8)
    return bg_bgr


def load_pose_arrays(rgba_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load RGBA PNG into float/uint8 BGR + float32 alpha [0..1]."""
    im = Image.open(rgba_path).convert("RGBA")
    arr = np.array(im, dtype=np.uint8)
    bgr = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR).astype(np.float32)
    alpha = (arr[:, :, 3].astype(np.float32) / 255.0)
    return bgr, alpha


def main() -> None:
    print("=== FASE 2: CANAL ALFA + ANIMACION HUMANIZADA AVATAR ===", flush=True)
    df0 = json.loads((cfg.BUILD_DIR / "debug_fase0.json").read_text(encoding="utf-8"))
    df1 = json.loads((cfg.BUILD_DIR / "debug_fase1.json").read_text(encoding="utf-8"))
    if df1.get("gate_1_to_2") != "PASS":
        print("FAIL-FAST: Gate 1->2 no esta en PASS", flush=True)
        sys.exit(1)

    total_frames = int(df1["total_frames"])

    # L2.1 Normalize 20 RGBA poses
    poses_report = []
    failures = []
    for pinfo in df0["files"]["avatar_poses"]:
        src = Path(pinfo["path"])
        dst = cfg.AVATAR_ALPHA_DIR / src.name
        info = normalize_avatar_pose(src, dst)
        if not info["clean_corners"] or info["size_bytes"] == 0 or not info["bbox"]:
            failures.append(f"Alpha invalido en {src.name}: {info}")
        poses_report.append(info)
    print(f"[L2.1] {len(poses_report)} poses RGBA normalizadas en {cfg.AVATAR_ALPHA_DIR}", flush=True)

    # L2.2 Vocal envelope 60fps
    env = compute_vocal_envelope_60fps(cfg.AUDIO_MASTER, total_frames)
    env_local = cfg.LOCAL_TEMP / "voice_envelope_60fps.npy"
    env_drive = cfg.BUILD_DIR / "voice_envelope_60fps.npy"
    np.save(str(env_local), env)
    shutil.copy2(str(env_local), str(env_drive))
    print(f"[L2.2] Envolvente vocal 60fps calculada: shape={env.shape} | mean_rms={env[:,0].mean():.3f}", flush=True)

    # Render 5s 60fps avatar motion verification clip
    check_mp4 = cfg.BUILD_DIR / "avatar_motion_check.mp4"
    pose_a_bgr, pose_a_alpha = load_pose_arrays(cfg.AVATAR_ALPHA_DIR / poses_report[0]["name"])
    pose_b_bgr, pose_b_alpha = load_pose_arrays(cfg.AVATAR_ALPHA_DIR / poses_report[1]["name"])

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", "720x1080", "-pix_fmt", "bgr24", "-r", "60", "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        str(check_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base_canvas = np.full((1080, 720, 3), (26, 20, 14), dtype=np.uint8)

    n_test_frames = 300  # 5.0s @ 60fps
    for fi in range(n_test_frames):
        t = fi / 60.0
        # Smooth cross-dissolve across pose transition [135..165]
        if fi < 135:
            bgr, alp = pose_a_bgr, pose_a_alpha
        elif fi < 165:
            blend = (fi - 135) / 30.0
            bgr = pose_a_bgr * (1.0 - blend) + pose_b_bgr * blend
            alp = pose_a_alpha * (1.0 - blend) + pose_b_alpha * blend
        else:
            bgr, alp = pose_b_bgr, pose_b_alpha
        frame = base_canvas.copy()
        frame = render_avatar_frame(bgr, alp, t, float(env[fi, 0]), float(env[fi, 1]), frame, 20, 120)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0 or not check_mp4.exists() or check_mp4.stat().st_size == 0:
        failures.append("Error generando avatar_motion_check.mp4")

    # Gate 2->3 continuity check on avatar_motion_check.mp4 every 0.25s (15 frames)
    cap = cv2.VideoCapture(str(check_mp4))
    prev_f = None
    motion_deltas = []
    frozen_windows = 0
    idx = 0
    while True:
        ok, frm = cap.read()
        if not ok:
            break
        if idx % 15 == 0:
            if prev_f is not None:
                diff = float(np.mean(np.abs(frm.astype(np.float32) - prev_f.astype(np.float32))))
                motion_deltas.append(round(diff, 4))
                if diff < 0.02:
                    frozen_windows += 1
            prev_f = frm
        idx += 1
    cap.release()

    if frozen_windows > 0 or len(motion_deltas) < 15:
        failures.append(f"Congelamiento detectado en avatar_motion_check.mp4: frozen_windows={frozen_windows}, deltas={motion_deltas}")

    gate_pass = len(failures) == 0
    debug_f2 = {
        "phase": "FASE_2",
        "gate_2_to_3": "PASS" if gate_pass else "FAIL",
        "failures": failures,
        "poses_normalized_count": len(poses_report),
        "poses": poses_report,
        "voice_envelope_shape": list(env.shape),
        "motion_check_clip": str(check_mp4),
        "motion_deltas_025s": motion_deltas,
        "frozen_windows_detected": frozen_windows,
        "min_motion_delta": min(motion_deltas) if motion_deltas else 0.0,
        "mean_motion_delta": round(float(np.mean(motion_deltas)), 4) if motion_deltas else 0.0,
    }
    df2_path = cfg.BUILD_DIR / "debug_fase2.json"
    df2_path.write_text(json.dumps(debug_f2, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[GATE 2->3] Status={debug_f2['gate_2_to_3']} | Frozen={frozen_windows} | MinDelta={debug_f2['min_motion_delta']} | MeanDelta={debug_f2['mean_motion_delta']}", flush=True)

    if not gate_pass:
        print("FAIL-FAST ABORT:", failures, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
