import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')

DRIVE_BASE = Path(r"G:\My Drive\HBOS-Diamantino")
LOCAL_BASE = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine")
ARTIFACTS_DIR = Path(r"C:\Users\ipane\.gemini\antigravity-ide\brain\d81d4d69-f81d-4539-a5cd-9d522623d434")

# Configuración por episodio
THUMBNAIL_CONFIGS = {
    "Ep02": {
        "dir_name": "Ep02-Los7Chips",
        "ep_label": "EPISODIO 02",
        "title_lines": ["7 CHIPS", "DE NVIDIA"],
        "badge_text": "VERA RUBIN NVL72",
        "bg_path": DRIVE_BASE / "Ep02-Los7Chips" / "02_Storyboard" / "backgrounds" / "bg_tematico_1080p.png",
        "char_path": DRIVE_BASE / "Ep02-Los7Chips" / "02_Storyboard" / "diamantino_v1_keynote.png",
        "color_accent": (0, 240, 255),      # Cian eléctrico
        "badge_bg": (0, 180, 216),
        "badge_fg": (10, 15, 30)
    },
    "Ep03": {
        "dir_name": "Ep03-RedesFotonicasCuanticas",
        "ep_label": "EPISODIO 03",
        "title_lines": ["1.6 Tbps", "FOTÓNICOS"],
        "badge_text": "SPECTRUM-X & CPO",
        "bg_path": DRIVE_BASE / "Ep03-RedesFotonicasCuanticas" / "02_Storyboard" / "backgrounds" / "bg_tematico_1080p.png",
        "char_path": DRIVE_BASE / "Ep03-RedesFotonicasCuanticas" / "02_Storyboard" / "amatista_v1_articulado.png",
        "color_accent": (189, 0, 255),    # Violeta neón
        "badge_bg": (168, 85, 247),
        "badge_fg": (255, 255, 255)
    }
}

def get_font(size, bold=True):
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_gradient_mask(size, direction='horizontal', intensity=0.85):
    w, h = size
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    if direction == 'horizontal':
        for x in range(w):
            alpha = int(255 * intensity * (1.0 - (x / w)))
            draw.line([(x, 0), (x, h)], fill=alpha)
    else:
        for y in range(h):
            alpha = int(255 * intensity * (y / h))
            draw.line([(0, y), (w, y)], fill=alpha)
    return mask

def generate_thumb_16x9(cfg):
    target_w, target_h = 1280, 720
    bg = Image.open(cfg["bg_path"]).convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Gradiente oscuro lateral para asegurar legibilidad del texto en el lado izquierdo
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for x in range(int(target_w * 0.75)):
        ratio = 1.0 - (x / (target_w * 0.75))
        alpha = int(230 * (ratio ** 1.3))
        draw_ov.line([(x, 0), (x, target_h)], fill=(5, 8, 18, alpha))
    bg = Image.alpha_composite(bg, overlay)

    # Personaje en el lado derecho
    char_img = Image.open(cfg["char_path"]).convert("RGBA")
    char_h = int(target_h * 0.95)
    char_w = int(char_img.width * (char_h / char_img.height))
    char_img = char_img.resize((char_w, char_h), Image.Resampling.LANCZOS)
    
    pos_x = target_w - char_w + int(char_w * 0.1)
    pos_y = target_h - char_h
    bg.paste(char_img, (pos_x, pos_y), char_img)

    # Texto
    draw = ImageDraw.Draw(bg)
    font_ep = get_font(28)
    font_title = get_font(74)
    font_badge = get_font(24)

    # Badge Episodio
    ep_box = (60, 60, 240, 102)
    draw.rounded_rectangle(ep_box, radius=8, outline=cfg["color_accent"], width=2)
    draw.text((75, 68), cfg["ep_label"], font=font_ep, fill=cfg["color_accent"])

    # Titular Masivo
    cur_y = 125
    for line in cfg["title_lines"]:
        # Sombra
        draw.text((64, cur_y + 4), line, font=font_title, fill=(0, 0, 0, 240))
        draw.text((62, cur_y + 2), line, font=font_title, fill=(0, 0, 0, 200))
        # Texto blanco
        draw.text((60, cur_y), line, font=font_title, fill=(255, 255, 255))
        cur_y += 82

    # Micro Badge Técnico
    badge_w = 320
    badge_h = 44
    b_box = (60, cur_y + 20, 60 + badge_w, cur_y + 20 + badge_h)
    draw.rounded_rectangle(b_box, radius=10, fill=cfg["badge_bg"])
    draw.text((75, cur_y + 28), cfg["badge_text"], font=font_badge, fill=cfg["badge_fg"])

    return bg.convert("RGB")

def generate_thumb_9x16(cfg):
    target_w, target_h = 1080, 1920
    raw_bg = Image.open(cfg["bg_path"]).convert("RGBA")
    
    # Ajustar fondo a 9:16 haciendo crop central
    bg_w = int(raw_bg.height * (target_w / target_h))
    left = (raw_bg.width - bg_w) // 2
    bg = raw_bg.crop((left, 0, left + bg_w, raw_bg.height)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Overlay gradiente oscuro inferior y superior
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(target_h):
        # Oscurecer zona superior (texto) y zona inferior
        if y < 750:
            ratio = 1.0 - (y / 750)
            alpha = int(220 * (ratio ** 1.2))
            draw_ov.line([(0, y), (target_w, y)], fill=(5, 8, 18, alpha))
        elif y > 1400:
            ratio = (y - 1400) / (target_h - 1400)
            alpha = int(200 * ratio)
            draw_ov.line([(0, y), (target_w, y)], fill=(5, 8, 18, alpha))
    bg = Image.alpha_composite(bg, overlay)

    # Personaje centrado / plano medio
    char_img = Image.open(cfg["char_path"]).convert("RGBA")
    char_h = int(target_h * 0.62)
    char_w = int(char_img.width * (char_h / char_img.height))
    char_img = char_img.resize((char_w, char_h), Image.Resampling.LANCZOS)
    
    pos_x = (target_w - char_w) // 2
    pos_y = target_h - char_h + 80
    bg.paste(char_img, (pos_x, pos_y), char_img)

    # Texto en el tercio superior
    draw = ImageDraw.Draw(bg)
    font_ep = get_font(34)
    font_title = get_font(96)
    font_badge = get_font(30)

    # Badge Episodio
    ep_box = (80, 120, 320, 180)
    draw.rounded_rectangle(ep_box, radius=10, outline=cfg["color_accent"], width=3)
    draw.text((105, 132), cfg["ep_label"], font=font_ep, fill=cfg["color_accent"])

    # Titular Masivo
    cur_y = 220
    for line in cfg["title_lines"]:
        draw.text((84, cur_y + 4), line, font=font_title, fill=(0, 0, 0, 240))
        draw.text((80, cur_y), line, font=font_title, fill=(255, 255, 255))
        cur_y += 108

    # Micro Badge Técnico
    badge_w = 400
    badge_h = 56
    b_box = (80, cur_y + 25, 80 + badge_w, cur_y + 25 + badge_h)
    draw.rounded_rectangle(b_box, radius=12, fill=cfg["badge_bg"])
    draw.text((100, cur_y + 35), cfg["badge_text"], font=font_badge, fill=cfg["badge_fg"])

    return bg.convert("RGB")

def generate_thumb_1x1(cfg):
    target_w, target_h = 1080, 1080
    raw_bg = Image.open(cfg["bg_path"]).convert("RGBA")
    
    # Crop central cuadrado
    side = min(raw_bg.width, raw_bg.height)
    left = (raw_bg.width - side) // 2
    top = (raw_bg.height - side) // 2
    bg = raw_bg.crop((left, top, left + side, top + side)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Overlay lateral
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for x in range(int(target_w * 0.7)):
        ratio = 1.0 - (x / (target_w * 0.7))
        alpha = int(230 * (ratio ** 1.3))
        draw_ov.line([(x, 0), (x, target_h)], fill=(5, 8, 18, alpha))
    bg = Image.alpha_composite(bg, overlay)

    # Personaje lado derecho
    char_img = Image.open(cfg["char_path"]).convert("RGBA")
    char_h = int(target_h * 0.9)
    char_w = int(char_img.width * (char_h / char_img.height))
    char_img = char_img.resize((char_w, char_h), Image.Resampling.LANCZOS)
    
    pos_x = target_w - char_w + int(char_w * 0.12)
    pos_y = target_h - char_h
    bg.paste(char_img, (pos_x, pos_y), char_img)

    # Texto
    draw = ImageDraw.Draw(bg)
    font_ep = get_font(30)
    font_title = get_font(84)
    font_badge = get_font(26)

    # Badge Episodio
    ep_box = (60, 80, 270, 130)
    draw.rounded_rectangle(ep_box, radius=8, outline=cfg["color_accent"], width=2)
    draw.text((80, 90), cfg["ep_label"], font=font_ep, fill=cfg["color_accent"])

    # Titular Masivo
    cur_y = 160
    for line in cfg["title_lines"]:
        draw.text((64, cur_y + 4), line, font=font_title, fill=(0, 0, 0, 240))
        draw.text((60, cur_y), line, font=font_title, fill=(255, 255, 255))
        cur_y += 94

    # Micro Badge Técnico
    badge_w = 360
    badge_h = 50
    b_box = (60, cur_y + 25, 60 + badge_w, cur_y + 25 + badge_h)
    draw.rounded_rectangle(b_box, radius=10, fill=cfg["badge_bg"])
    draw.text((80, cur_y + 35), cfg["badge_text"], font=font_badge, fill=cfg["badge_fg"])

    return bg.convert("RGB")

def process_episode_thumbnails(ep_code):
    cfg = THUMBNAIL_CONFIGS.get(ep_code)
    if not cfg:
        raise ValueError(f"Episodio no configurado: {ep_code}")

    print(f"[*] Generando Thumbnails Profesionales para {ep_code} ({cfg['title_lines']})...")
    
    t_16x9 = generate_thumb_16x9(cfg)
    t_9x16 = generate_thumb_9x16(cfg)
    t_1x1  = generate_thumb_1x1(cfg)

    # Rutas destino
    dest_dirs = [
        DRIVE_BASE / cfg["dir_name"] / "06_Publicado" / "thumbnails",
        LOCAL_BASE / cfg["dir_name"] / "06_Publicado" / "thumbnails"
    ]
    for d in dest_dirs:
        d.mkdir(parents=True, exist_ok=True)

    prefix = ep_code.lower()
    files_saved = {}
    for d in dest_dirs:
        p_16x9 = d / f"{prefix}_thumb_16x9.png"
        p_9x16 = d / f"{prefix}_thumb_9x16.png"
        p_1x1  = d / f"{prefix}_thumb_1x1.png"
        
        t_16x9.save(p_16x9, format="PNG", optimize=True)
        t_9x16.save(p_9x16, format="PNG", optimize=True)
        t_1x1.save(p_1x1, format="PNG", optimize=True)
        
        files_saved[str(d)] = [p_16x9, p_9x16, p_1x1]

    # Copia a Artifacts directory para previsualización inmediata
    art_16x9 = ARTIFACTS_DIR / f"{prefix}_thumb_16x9.png"
    art_9x16 = ARTIFACTS_DIR / f"{prefix}_thumb_9x16.png"
    art_1x1  = ARTIFACTS_DIR / f"{prefix}_thumb_1x1.png"
    t_16x9.save(art_16x9, format="PNG")
    t_9x16.save(art_9x16, format="PNG")
    t_1x1.save(art_1x1, format="PNG")

    print(f"[OK] {ep_code} Thumbnails generados en 3 formatos:")
    for f in files_saved[str(dest_dirs[0])]:
        print(f"     - {f.name} ({f.stat().st_size:,} bytes)")

if __name__ == "__main__":
    for ep in ["Ep02", "Ep03"]:
        process_episode_thumbnails(ep)
