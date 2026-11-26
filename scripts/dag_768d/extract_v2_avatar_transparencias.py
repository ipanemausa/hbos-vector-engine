#!/usr/bin/env python3
"""Extract 5 ultra-clean RGBA transparent poses from Guillermo's uploaded smiling keynote photos (0 SaaS Tax)."""

import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

UPLOAD_DIR = cfg.ARTIFACT_DIR / ".user_uploaded"
OUT_V2_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\avatar_v2_transparencias")
OUT_LIB_DIR = Path(r"G:\My Drive\Avatar Guillermo - transparencias\v2_sonrisa_natural")

SOURCES = [
    ("media_1795650014148_1021cd41.jpg", "guillermo_v2_01_bienvenida_sonrisa.png"),
    ("media_1795649955804_bc2c20b4.jpg", "guillermo_v2_02_senala_derecha.png"),
    ("media_1795649982860_ab1876da.jpg", "guillermo_v2_03_pensativo_menton.png"),
    ("media_1795649995543_c5b81150.jpg", "guillermo_v2_04_enfasis_tecnico.png"),
    ("media_1795649972611_5e2d2ae5.jpg", "guillermo_v2_05_saludo_cierre.png"),
]


def isolate_largest_foreground(rgba_img: Image.Image) -> Image.Image:
    """Keep strictly the largest connected foreground component (Guillermo), removing any stage audience remnants."""
    arr = np.array(rgba_img, dtype=np.uint8)
    alpha = arr[:, :, 3]
    binary = (alpha > 20).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if num_labels > 1:
        areas = stats[1:, cv2.CC_STAT_AREA]
        best_label = 1 + int(np.argmax(areas))
        keep_mask = (labels == best_label).astype(np.uint8)
        # Light 3px dilation around keep_mask preserves wispy hair/glasses edges belonging to Guillermo
        keep_dilated = cv2.dilate(keep_mask, np.ones((5, 5), np.uint8), iterations=1)
        arr[:, :, 3] = np.where(keep_dilated > 0, alpha, 0)
    # Trim transparent bounding padding cleanly with small margin
    out_im = Image.fromarray(arr)
    bbox = out_im.getbbox()
    if bbox:
        pad = 16
        crop_box = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(out_im.width, bbox[2] + pad),
            min(out_im.height, bbox[3] + pad),
        )
        out_im = out_im.crop(crop_box)
    return out_im


def main() -> None:
    print("=== EXTRACCION LOCAL RGBA REMBG: 5 POSES SONRISA NATURAL ===", flush=True)
    OUT_V2_DIR.mkdir(parents=True, exist_ok=True)
    OUT_LIB_DIR.mkdir(parents=True, exist_ok=True)

    session = new_session("u2net")
    report = []

    for src_name, dst_name in SOURCES:
        src_p = UPLOAD_DIR / src_name
        if not src_p.exists():
            raise FileNotFoundError(f"Falta imagen subida: {src_p}")
        im_in = Image.open(src_p).convert("RGB")
        try:
            cut = remove(
                im_in,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=15,
                alpha_matting_erode_size=8,
            )
        except Exception as exc:
            print(f"[WARN] alpha_matting fallback en {src_name}: {exc}", flush=True)
            cut = remove(im_in, session=session)

        clean_rgba = isolate_largest_foreground(cut)
        p_v2 = OUT_V2_DIR / dst_name
        p_lib = OUT_LIB_DIR / dst_name
        p_art = cfg.ARTIFACT_DIR / dst_name

        clean_rgba.save(p_v2, "PNG")
        shutil.copy2(str(p_v2), str(p_lib))
        shutil.copy2(str(p_v2), str(p_art))

        c_arr = np.array(clean_rgba)
        corners = [int(c_arr[0, 0, 3]), int(c_arr[0, -1, 3]), int(c_arr[-1, 0, 3]), int(c_arr[-1, -1, 3])]
        rec = {
            "name": dst_name,
            "source": str(src_p),
            "v2_path": str(p_v2),
            "library_path": str(p_lib),
            "size": [clean_rgba.width, clean_rgba.height],
            "bytes": p_v2.stat().st_size,
            "clean_corners": all(c == 0 for c in corners),
        }
        report.append(rec)
        print(f"[OK] {dst_name}: {clean_rgba.width}x{clean_rgba.height} ({p_v2.stat().st_size} B, corners={corners})", flush=True)

    manifest_p = OUT_V2_DIR / "avatar_v2_manifest.json"
    manifest_p.write_text(json.dumps({"count": len(report), "poses": report}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[PASS] 5/5 transparencias RGBA listas en {OUT_V2_DIR} y {OUT_LIB_DIR}", flush=True)


if __name__ == "__main__":
    main()
