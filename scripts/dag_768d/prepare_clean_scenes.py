#!/usr/bin/env python3
"""Normalize the 10 generated textless 3D scenes into exact 1920x1080 bg_01..10.jpg files."""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)


def auto_trim_letterbox(arr_bgr: np.ndarray) -> np.ndarray:
    """Trim uniform black top/bottom letterbox bars if present."""
    gray = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2GRAY)
    row_means = gray.mean(axis=1)
    h = len(row_means)
    top = 0
    while top < h // 4 and row_means[top] < 10.0:
        top += 1
    bot = h
    while bot > (3 * h) // 4 and row_means[bot - 1] < 10.0:
        bot -= 1
    if top > 10 or (h - bot) > 10:
        return arr_bgr[top:bot, :]
    return arr_bgr


def center_crop_resize_1080p(src: Path, dst: Path, smooth_right_zone: bool = False) -> dict:
    arr = cv2.imread(str(src))
    orig_h, orig_w = arr.shape[:2]
    arr = auto_trim_letterbox(arr)
    im = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
    w, h = im.size
    target_ratio = 16.0 / 9.0
    cur_ratio = w / h
    if cur_ratio > target_ratio + 0.001:
        new_w = int(round(h * target_ratio))
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    elif cur_ratio < target_ratio - 0.001:
        new_h = int(round(w / target_ratio))
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))
    im_1080 = im.resize((cfg.TARGET_W, cfg.TARGET_H), Image.Resampling.LANCZOS)

    if smooth_right_zone:
        # Replace unintended background silhouette in presenter zone with clean mirrored dark studio backdrop + soft bokeh
        out_bgr = cv2.cvtColor(np.array(im_1080, dtype=np.uint8), cv2.COLOR_RGB2BGR)
        h_o, w_o = out_bgr.shape[:2]
        # Sample clean right-edge dark architectural column strip [0.87w..0.98w] and stretch/blur across [0.64w..0.88w]
        clean_strip = cv2.resize(out_bgr[:, int(0.87 * w_o):int(0.98 * w_o)], (int(0.25 * w_o), h_o), interpolation=cv2.INTER_CUBIC)
        clean_strip = cv2.GaussianBlur(clean_strip, (51, 51), 18)
        patch = out_bgr.copy()
        patch[:, int(0.64 * w_o):int(0.64 * w_o) + clean_strip.shape[1]] = clean_strip
        x_coords = np.linspace(0.0, 1.0, w_o, dtype=np.float32)
        m_left = np.clip((x_coords - 0.62) / 0.06, 0.0, 1.0)
        m_right = np.clip((0.92 - x_coords) / 0.06, 0.0, 1.0)
        blend_x = np.minimum(m_left, m_right)[None, :, None]
        out_bgr = np.clip(out_bgr * (1.0 - blend_x) + patch * blend_x, 0, 255).astype(np.uint8)
        im_1080 = Image.fromarray(cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB))

    im_1080.save(dst, "JPEG", quality=94)
    return {"src": str(src), "dst": str(dst), "orig_size": [orig_w, orig_h], "final_size": [1920, 1080], "bytes": dst.stat().st_size}


def find_scene_source(i: int, clean_dir: Path) -> Path | None:
    patterns = [f"raw_bg_{i:02d}*.*", f"escena_{i:02d}*.*"]
    for search_dir in [clean_dir, cfg.ARTIFACT_DIR]:
        if not search_dir.exists():
            continue
        matches = []
        for pat in patterns:
            matches.extend(p for p in search_dir.glob(pat) if p.is_file() and p.stat().st_size > 0 and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        if matches:
            matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return matches[0]
    return None


def main() -> None:
    clean_dir = cfg.BUILD_DIR / "escenas_3d_clean"
    clean_dir.mkdir(parents=True, exist_ok=True)
    results = []
    missing = []

    for i in range(1, 11):
        found = find_scene_source(i, clean_dir)
        if not found:
            missing.append(f"raw_bg_{i:02d}*")
            continue
        dst = clean_dir / f"bg_{i:02d}.jpg"
        info = center_crop_resize_1080p(found, dst, smooth_right_zone=(i in (8, 9, 10)))
        results.append(info)
        print(f"[OK] bg_{i:02d}.jpg <- {found.name} ({info['orig_size']} -> 1920x1080, {info['bytes']} B)", flush=True)

    if missing:
        print("FAIL-FAST: Faltan escenas generadas:", missing, flush=True)
        sys.exit(1)

    manifest = {"clean_scenes_dir": str(clean_dir), "count": len(results), "scenes": results}
    (clean_dir / "scenes_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[PASS] 10/10 escenas 3D limpias 1920x1080 listas en {clean_dir}", flush=True)


if __name__ == "__main__":
    main()
