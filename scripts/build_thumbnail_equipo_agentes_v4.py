#!/usr/bin/env python3
"""
House Thumbnail System — Equipo de Agentes de IA v4 (16:9, 9:16, 1:1 + phone check)
- Nano Banana text-free studio background
- Official transparent Guillermo on the right with subtle cyan rim-light & shadow
- Template typography ONLY (never baked inside AI art), max 4-5 high-contrast words,
  verified legible at 320x180 phone scale.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = Path(r"C:\Users\ipane\hbos-deploy\INSUMOS-PANEL\video-v4-definitivo")
VAULT_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL")
BG_SRC = Path(r"C:\Users\ipane\.gemini\antigravity\brain\e66a4ab7-69f7-48e5-a974-a2e850552fac\thumb_bg_nanobanana_1795726827625.jpg")
BG_PNG = OUT_DIR / "thumb_bg_nanobanana.png"
POSE_PATH = Path(r"C:\Users\ipane\hbos-deploy\INSUMOS-PANEL\avatar-transparente\guillermo_oficial_01_bienvenida.png")

RIM_CYAN = (0, 240, 255)
GOLD = (245, 183, 0)
EMERALD = (16, 185, 129)
CRIMSON = (220, 38, 38)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in (r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def presenter_half_body_with_rim(pose_path: Path, target_h: int) -> Image.Image:
    im = Image.open(pose_path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    # Waist-up high-impact crop (top 64% keeps head, hands, HB.OS shirt crisp for thumbnails)
    im = im.crop((0, 0, im.width, int(im.height * 0.64)))
    scale = target_h / max(1, im.height)
    im = im.resize((max(1, int(round(im.width * scale))), target_h), Image.Resampling.LANCZOS)

    pad = 22
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    alpha = im.getchannel("A")
    # Dark outer drop shadow
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 190), mask=alpha)
    sh_c = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_c.paste(sh, (pad - 6, pad + 6))
    sh_c = sh_c.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(sh_c)

    # Cyan rim-light glow
    dil = alpha.filter(ImageFilter.MaxFilter(9))
    rim = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rim.paste((*RIM_CYAN, 170), mask=dil)
    rim_c = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    rim_c.paste(rim, (pad, pad))
    rim_c = rim_c.filter(ImageFilter.GaussianBlur(5))
    canvas.alpha_composite(rim_c)

    canvas.paste(im, (pad, pad), im)
    return canvas


def draw_shadow_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int], stroke: int = 4) -> None:
    x, y = xy
    draw.text((x + stroke + 2, y + stroke + 3), text, font=font, fill=(4, 8, 18, 240))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(6, 10, 22, 255))


def draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont, bg_rgba: tuple[int, int, int, int], outline_rgba: tuple[int, int, int, int], pad_x: int = 24, pad_y: int = 12, radius: int = 16, stroke_text: int = 0) -> None:
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bx1 = x + tw + pad_x * 2
    by1 = y + th + pad_y * 2
    draw.rounded_rectangle([x, y, bx1, by1], radius=radius, fill=bg_rgba, outline=outline_rgba, width=3)
    tx, ty = x + pad_x - bb[0], y + pad_y - bb[1]
    if stroke_text > 0:
        draw_shadow_text(draw, (tx, ty), text, font, (255, 255, 255, 255), stroke=stroke_text)
    else:
        draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))


def make_thumb_16x9(bg: Image.Image) -> Image.Image:
    w, h = 1280, 720
    canvas = bg.copy().resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
    # Left gradient scrim so left typography pops at phone size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(int(w * 0.68)):
        a = int(205 * ((1.0 - x / (w * 0.68)) ** 1.25))
        od.line([(x, 0), (x, h)], fill=(6, 10, 22, a))
    canvas = Image.alpha_composite(canvas, ov)

    # Presenter strictly on the right (Guillermo a la derecha)
    guillermo = presenter_half_body_with_rim(POSE_PATH, target_h=670)
    gx = w - guillermo.width + 55
    gy = h - guillermo.height + 16
    canvas.alpha_composite(guillermo, (gx, gy))

    d = ImageDraw.Draw(canvas)
    f_pill = load_font(34)
    f_l1 = load_font(124)
    f_l2 = load_font(124)
    f_sub = load_font(54)

    draw_pill(d, 54, 48, "GUÍA HOY", f_pill, (*CRIMSON, 255), (*GOLD, 255), pad_x=24, pad_y=12, radius=14)
    draw_shadow_text(d, (54, 150), "EQUIPO DE", f_l1, (255, 255, 255, 255), stroke=5)
    draw_shadow_text(d, (54, 290), "AGENTES IA", f_l2, (*GOLD, 255), stroke=5)
    draw_pill(d, 54, 485, "5 EN 1 · GRATIS", f_sub, (*EMERALD, 255), (255, 255, 255, 240), pad_x=28, pad_y=16, radius=22, stroke_text=3)
    return canvas


def make_thumb_9x16(bg: Image.Image) -> Image.Image:
    w, h = 1080, 1920
    # Center-crop & darken slightly
    bw, bh = bg.size
    crop_w = int(bh * 9 / 16)
    cx = bw // 2
    base = bg.crop((max(0, cx - crop_w // 2), 0, min(bw, cx + crop_w // 2), bh)).resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (6, 10, 22, 110))
    canvas = Image.alpha_composite(base, ov)

    guillermo = presenter_half_body_with_rim(POSE_PATH, target_h=920)
    gx = w - guillermo.width + 65
    gy = h - guillermo.height + 24
    canvas.alpha_composite(guillermo, (gx, gy))

    d = ImageDraw.Draw(canvas)
    f_pill = load_font(44)
    f_l1 = load_font(154)
    f_l2 = load_font(154)
    f_sub = load_font(68)

    draw_pill(d, 64, 150, "GUÍA HOY", f_pill, (*CRIMSON, 255), (*GOLD, 255), pad_x=30, pad_y=14, radius=16)
    draw_shadow_text(d, (64, 300), "EQUIPO DE", f_l1, (255, 255, 255, 255), stroke=6)
    draw_shadow_text(d, (64, 480), "AGENTES IA", f_l2, (*GOLD, 255), stroke=6)
    draw_pill(d, 64, 710, "5 EN 1 · GRATIS", f_sub, (*EMERALD, 255), (255, 255, 255, 240), pad_x=36, pad_y=22, radius=24, stroke_text=4)
    return canvas


def make_thumb_1x1(bg: Image.Image) -> Image.Image:
    w, h = 1080, 1080
    bw, bh = bg.size
    crop_w = bh
    cx = bw // 2
    base = bg.crop((max(0, cx - crop_w // 2), 0, min(bw, cx + crop_w // 2), bh)).resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(int(w * 0.72)):
        a = int(195 * ((1.0 - x / (w * 0.72)) ** 1.25))
        od.line([(x, 0), (x, h)], fill=(6, 10, 22, a))
    canvas = Image.alpha_composite(base, ov)

    guillermo = presenter_half_body_with_rim(POSE_PATH, target_h=720)
    gx = w - guillermo.width + 95
    gy = h - guillermo.height + 20
    canvas.alpha_composite(guillermo, (gx, gy))

    d = ImageDraw.Draw(canvas)
    f_pill = load_font(38)
    f_l1 = load_font(112)
    f_l2 = load_font(112)
    f_sub = load_font(54)

    draw_pill(d, 50, 68, "GUÍA HOY", f_pill, (*CRIMSON, 255), (*GOLD, 255), pad_x=26, pad_y=12, radius=14)
    draw_shadow_text(d, (50, 195), "EQUIPO DE", f_l1, (255, 255, 255, 255), stroke=5)
    draw_shadow_text(d, (50, 330), "AGENTES IA", f_l2, (*GOLD, 255), stroke=5)
    draw_pill(d, 50, 520, "5 EN 1 · GRATIS", f_sub, (*EMERALD, 255), (255, 255, 255, 240), pad_x=30, pad_y=18, radius=22, stroke_text=3)
    return canvas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bg = Image.open(BG_SRC).convert("RGBA")
    bg.save(BG_PNG, "PNG")

    t16 = make_thumb_16x9(bg)
    t9 = make_thumb_9x16(bg)
    t1 = make_thumb_1x1(bg)
    t_phone = t16.resize((320, 180), Image.Resampling.LANCZOS)

    outputs = {
        "16x9": (OUT_DIR / "EQUIPO-DE-AGENTES-miniatura-v4-16x9.png", t16),
        "9x16": (OUT_DIR / "EQUIPO-DE-AGENTES-miniatura-v4-9x16.png", t9),
        "1x1": (OUT_DIR / "EQUIPO-DE-AGENTES-miniatura-v4-1x1.png", t1),
        "phone_320x180": (OUT_DIR / "thumb_phone_check_320x180.png", t_phone),
    }
    report = {}
    for k, (p, im) in outputs.items():
        im.save(p, "PNG")
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        report[k] = {"path": str(p), "size": list(im.size), "bytes": p.stat().st_size, "sha256": sha}
        if k in ("16x9", "9x16", "1x1"):
            vp = VAULT_DIR / p.name
            im.save(vp, "PNG")
            vsha = hashlib.sha256(vp.read_bytes()).hexdigest()
            assert sha == vsha, f"Vault SHA mismatch for {p.name}"
            report[k]["vault_path"] = str(vp)
    (OUT_DIR / "thumbnails_v4_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
