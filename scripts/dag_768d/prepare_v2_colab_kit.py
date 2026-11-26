"""Prepare isolated Google Colab T4 input kit for v2 full-body humanized avatar.

Reads ONLY from validated v1 master audio and official transparent PNG poses,
writing isolated pilot WAVs (16kHz/48kHz) and chroma-key PNGs (#00B140) into:
G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\equipo_agentes_v2_piloto\\colab_3d_kit\\
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

MASTER_WAV = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy_voxcpm\equipo_agentes_ia_master.wav"
)
AVATAR_DIR = Path(r"G:\My Drive\AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS")
PILOT_ROOT = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto"
)
KIT_DIR = PILOT_ROOT / "colab_3d_kit"
OUT_DIR = PILOT_ROOT / "colab_3d_out"

# Studio chroma green in BGR (#00B140 -> R=0, G=177, B=64 -> BGR=(64, 177, 0))
CHROMA_BGR = np.array([64, 177, 0], dtype=np.uint8)

POSES = [
    ("01", "guillermo_oficial_01_bienvenida.png", "Bienvenida brazos abiertos"),
    ("02", "guillermo_oficial_02_senala_derecha.png", "Señala a la derecha"),
    ("03", "guillermo_oficial_03_pensativo_menton.png", "Pensativo mano al mentón"),
    ("04", "guillermo_oficial_04_enfasis_tecnico.png", "Énfasis técnico"),
    ("05", "guillermo_oficial_05_saludo_cierre.png", "Saludo cierre"),
]


def probe_media(path: Path) -> dict:
    """Return ffprobe stream/format metadata for audio or video verification."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def cut_audio(src: Path, dst: Path, duration: float, sample_rate: int) -> dict:
    """Slice mono PCM WAV cleanly from master narration without modifying source."""
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        "0",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(src),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-c:a",
        "pcm_s16le",
        str(dst),
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = probe_media(dst)
    stream = info["streams"][0]
    return {
        "file": dst.name,
        "path": str(dst),
        "duration_sec": round(float(info["format"]["duration"]), 4),
        "sample_rate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "bytes": dst.stat().st_size,
    }


def composite_on_chroma(
    rgba: np.ndarray,
    canvas_w: int,
    canvas_h: int,
    top_pad_ratio: float,
    bottom_pad_ratio: float,
    crop_top_fraction: float | None = None,
) -> np.ndarray:
    """Place an RGBA cutout cleanly onto #00B140 studio green preserving full-body x-alignment."""
    # First tighten to the full-body non-transparent bounding box so upper & full share exact width/center
    ys_all, xs_all = np.where(rgba[:, :, 3] > 16)
    if len(ys_all) == 0 or len(xs_all) == 0:
        raise ValueError("Source RGBA pose has empty alpha channel")
    src = rgba[ys_all.min() : ys_all.max() + 1, xs_all.min() : xs_all.max() + 1]
    if crop_top_fraction is not None:
        cut_h = max(64, int(src.shape[0] * crop_top_fraction))
        src = src[:cut_h, :, :]

    avail_h = int(canvas_h * (1.0 - top_pad_ratio - bottom_pad_ratio))
    avail_w = int(canvas_w * 0.86)
    scale = min(avail_w / src.shape[1], avail_h / src.shape[0])
    new_w = max(2, int(round(src.shape[1] * scale)))
    new_h = max(2, int(round(src.shape[0] * scale)))
    resized = cv2.resize(src, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    canvas = np.empty((canvas_h, canvas_w, 3), dtype=np.uint8)
    canvas[:, :] = CHROMA_BGR

    x0 = (canvas_w - new_w) // 2
    y0 = int(canvas_h * top_pad_ratio)
    if y0 + new_h > canvas_h:
        y0 = max(0, canvas_h - new_h)

    # Hard-alpha core + 1px clean ramp avoids dark/green edge halos
    alpha = resized[:, :, 3].astype(np.float32) / 255.0
    alpha = np.clip((alpha - 0.12) / 0.88, 0.0, 1.0)[..., None]
    fg = resized[:, :, :3].astype(np.float32)
    roi = canvas[y0 : y0 + new_h, x0 : x0 + new_w].astype(np.float32)
    blended = np.clip(fg * alpha + roi * (1.0 - alpha), 0, 255).astype(np.uint8)
    canvas[y0 : y0 + new_h, x0 : x0 + new_w] = blended
    return canvas


def main() -> None:
    if not MASTER_WAV.exists():
        raise FileNotFoundError(f"Master WAV missing: {MASTER_WAV}")
    KIT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    audio_meta = {
        "piloto_10s_16k": cut_audio(
            MASTER_WAV, KIT_DIR / "piloto_10s_16k.wav", 10.0, 16000
        ),
        "piloto_10s_48k": cut_audio(
            MASTER_WAV, KIT_DIR / "piloto_10s_48k.wav", 10.0, 48000
        ),
        "piloto_5s_16k": cut_audio(
            MASTER_WAV, KIT_DIR / "piloto_5s_16k.wav", 5.0, 16000
        ),
    }

    poses_meta = []
    for idx, fname, label in POSES:
        src_path = AVATAR_DIR / fname
        if not src_path.exists():
            raise FileNotFoundError(f"Official pose missing: {src_path}")
        rgba = cv2.imread(str(src_path), cv2.IMREAD_UNCHANGED)
        if rgba is None or rgba.ndim != 3 or rgba.shape[2] != 4:
            raise ValueError(f"Expected RGBA PNG: {src_path}")

        full_img = composite_on_chroma(
            rgba,
            canvas_w=768,
            canvas_h=1344,
            top_pad_ratio=0.06,
            bottom_pad_ratio=0.05,
            crop_top_fraction=None,
        )
        full_path = KIT_DIR / f"chroma_full_{idx}.png"
        cv2.imwrite(str(full_path), full_img)

        # Upper-body / waist-up crop gives maximum facial pixel density for Ditto & EchoMimicV2
        upper_img = composite_on_chroma(
            rgba,
            canvas_w=768,
            canvas_h=768,
            top_pad_ratio=0.10,
            bottom_pad_ratio=0.0,
            crop_top_fraction=0.52,
        )
        upper_path = KIT_DIR / f"chroma_upper_{idx}.png"
        cv2.imwrite(str(upper_path), upper_img)

        poses_meta.append(
            {
                "id": idx,
                "label": label,
                "source_png": str(src_path),
                "source_shape": list(rgba.shape),
                "chroma_full": str(full_path),
                "chroma_full_shape": list(full_img.shape),
                "chroma_upper": str(upper_path),
                "chroma_upper_shape": list(upper_img.shape),
            }
        )

    manifest = {
        "status": "READY",
        "chroma_hex": "#00B140",
        "kit_dir": str(KIT_DIR),
        "out_dir": str(OUT_DIR),
        "audio": audio_meta,
        "poses": poses_meta,
    }
    manifest_path = KIT_DIR / "kit_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"PASS: kit written to {manifest_path}")


if __name__ == "__main__":
    main()
