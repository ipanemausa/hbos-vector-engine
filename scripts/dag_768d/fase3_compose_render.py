#!/usr/bin/env python3
"""FASE 3 — Fast C++ OpenCV uint8 1080p 60fps Cinematic Composition, HUD Charts, Avatar & QA Clips."""

import json
import math
import subprocess
import sys
import textwrap
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

HUD_X0, HUD_Y0, HUD_W, HUD_H = 48, 34, 1130, 846
SUB_X0, SUB_Y0, SUB_W, SUB_H = 48, 902, 1130, 144
AV_X0, AV_Y0 = 1210, 120

FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
if not Path(FONT_BOLD).exists():
    FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
if not Path(FONT_REG).exists():
    FONT_REG = r"C:\Windows\Fonts\arial.ttf"

CYAN = (56, 189, 248, 255)
AMBER = (245, 158, 11, 255)
WHITE = (244, 248, 255, 255)
MUTED = (165, 180, 205, 255)
CARD_BG = (10, 16, 30, 220)
PANEL_BG = (16, 26, 48, 240)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_round_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], r: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def draw_diagram(draw: ImageDraw.ImageDraw, dtype: str, x0: int, y0: int, w: int, h: int, f_md, f_sm, f_lg):
    """Draw bespoke architectural diagram for each block inside (x0, y0, x0+w, y0+h)."""
    draw_round_rect(draw, (x0, y0, x0 + w, y0 + h), 14, (13, 21, 38, 240), outline=(56, 189, 248, 110), width=1)
    pad = 18
    ix0, iy0, iw, ih = x0 + pad, y0 + pad, w - 2 * pad, h - 2 * pad

    if dtype == "vs_bottleneck":
        bw = (iw - 70) // 2
        draw_round_rect(draw, (ix0, iy0, ix0 + bw, iy0 + ih), 12, (55, 28, 14, 230), outline=AMBER, width=2)
        draw.text((ix0 + 18, iy0 + 18), "ANTES · MODELO ÚNICO", font=f_sm, fill=AMBER)
        draw.text((ix0 + 18, iy0 + 52), "1 Chatbot = Todo", font=f_lg, fill=WHITE)
        draw.text((ix0 + 18, iy0 + 98), "Investiga + Redacta + Programa + Audita", font=f_sm, fill=MUTED)
        draw.text((ix0 + 18, iy0 + 132), "Resultado: Superficial / Confuso", font=f_md, fill=AMBER)

        ax = ix0 + bw + 14
        ay = iy0 + ih // 2
        draw.text((ax, ay - 16), ">>>", font=f_lg, fill=CYAN)

        rx = ix0 + bw + 70
        draw_round_rect(draw, (rx, iy0, rx + bw, iy0 + ih), 12, (12, 44, 66, 235), outline=CYAN, width=2)
        draw.text((rx + 18, iy0 + 18), "AHORA · ARQUITECTURA HBOS", font=f_sm, fill=CYAN)
        draw.text((rx + 18, iy0 + 52), "Equipo de Agentes IA", font=f_lg, fill=WHITE)
        draw.text((rx + 18, iy0 + 98), "Roles + Herramientas + Objetivos Claros", font=f_sm, fill=MUTED)
        draw.text((rx + 18, iy0 + 132), "Precisión Empresarial Multiplicada", font=f_md, fill=CYAN)

    elif dtype == "orchestrator_hub":
        hw = 430
        hx = ix0 + (iw - hw) // 2
        draw_round_rect(draw, (hx, iy0, hx + hw, iy0 + 62), 12, (16, 52, 78, 245), outline=CYAN, width=2)
        draw.text((hx + 28, iy0 + 16), "AGENTE COORDINADOR · ORQUESTA", font=f_md, fill=WHITE)
        roles = [("01 INVESTIGADOR", CYAN), ("02 EJECUTOR", CYAN), ("03 AUDITOR", AMBER), ("04 ENTREGA", CYAN)]
        cw = (iw - 36) // 4
        for idx, (rname, col) in enumerate(roles):
            cx = ix0 + idx * (cw + 12)
            cy = iy0 + 98
            draw.line([(ix0 + iw // 2, iy0 + 62), (cx + cw // 2, cy)], fill=(56, 189, 248, 180), width=2)
            draw_round_rect(draw, (cx, cy, cx + cw, iy0 + ih), 10, PANEL_BG, outline=col, width=2)
            draw.text((cx + 14, cy + 28), rname, font=f_md, fill=col)

    elif dtype == "data_mining":
        steps = [
            ("FUENTES REALES", "Docs · Bases · Portales", CYAN),
            ("FILTRO ESTRICTO", "Cero Opinión / Solo Datos", AMBER),
            ("EVIDENCIA PURA", "Citas + Contexto al Minuto", CYAN),
        ]
        sw = (iw - 60) // 3
        for idx, (t1, t2, col) in enumerate(steps):
            sx = ix0 + idx * (sw + 30)
            draw_round_rect(draw, (sx, iy0 + 14, sx + sw, iy0 + ih - 14), 12, PANEL_BG, outline=col, width=2)
            draw.text((sx + 18, iy0 + 38), t1, font=f_md, fill=col)
            draw.text((sx + 18, iy0 + 82), t2, font=f_sm, fill=WHITE)
            if idx < 2:
                draw.text((sx + sw + 7, iy0 + ih // 2 - 14), "->", font=f_md, fill=CYAN)

    elif dtype == "executor_forge":
        draw_round_rect(draw, (ix0, iy0 + 16, ix0 + 280, iy0 + ih - 16), 12, (48, 30, 12, 235), outline=AMBER, width=2)
        draw.text((ix0 + 18, iy0 + 44), "INSUMOS", font=f_sm, fill=AMBER)
        draw.text((ix0 + 18, iy0 + 78), "Evidencia + Pauta", font=f_md, fill=WHITE)
        draw.text((ix0 + 292, iy0 + ih // 2 - 14), "=>", font=f_lg, fill=CYAN)
        pillars = [("PROPUESTAS", "Redacción Comercial"), ("CÓDIGO", "Automatización"), ("DISEÑO", "Piezas Visuales")]
        pw = (iw - 340 - 24) // 3
        for idx, (p1, p2) in enumerate(pillars):
            px = ix0 + 340 + idx * (pw + 12)
            draw_round_rect(draw, (px, iy0 + 16, px + pw, iy0 + ih - 16), 12, (12, 44, 66, 235), outline=CYAN, width=2)
            draw.text((px + 16, iy0 + 42), p1, font=f_md, fill=CYAN)
            draw.text((px + 16, iy0 + 84), p2, font=f_sm, fill=WHITE)

    elif dtype == "auditor_gate":
        draw_round_rect(draw, (ix0, iy0 + 28, ix0 + 235, iy0 + ih - 28), 12, PANEL_BG, outline=CYAN, width=2)
        draw.text((ix0 + 48, iy0 + 52), "BORRADOR", font=f_md, fill=WHITE)
        draw.text((ix0 + 52, iy0 + 84), "EJECUTOR", font=f_md, fill=CYAN)
        draw.text((ix0 + 248, iy0 + 72), "->", font=f_md, fill=CYAN)
        draw_round_rect(draw, (ix0 + 292, iy0 + 18, ix0 + 628, iy0 + ih - 18), 12, (50, 32, 12, 240), outline=AMBER, width=2)
        draw.text((ix0 + 314, iy0 + 42), "AGENTE AUDITOR", font=f_md, fill=AMBER)
        draw.text((ix0 + 314, iy0 + 82), "Sumas · Lógica · Evidencia", font=f_sm, fill=WHITE)
        draw.text((ix0 + 640, iy0 + 72), "->", font=f_md, fill=CYAN)
        draw_round_rect(draw, (ix0 + 676, iy0 + 12, ix0 + iw, iy0 + 88), 10, (12, 54, 48, 240), outline=CYAN, width=2)
        draw.text((ix0 + 694, iy0 + 34), "PASS: CERO ALUCINACIÓN", font=f_md, fill=CYAN)
        draw_round_rect(draw, (ix0 + 676, iy0 + 100, ix0 + iw, iy0 + ih - 8), 10, (56, 22, 18, 235), outline=AMBER, width=2)
        draw.text((ix0 + 694, iy0 + 120), "RECHAZO -> REPORTE Y AJUSTE", font=f_sm, fill=AMBER)

    elif dtype == "handoff_pipeline":
        nodes = ["01 INPUT", "02 SCHEMA", "03 VALIDACIÓN", "04 AUTO-SIGUIENTE"]
        nw = (iw - 72) // 4
        for idx, nd in enumerate(nodes):
            nx = ix0 + idx * (nw + 24)
            col = AMBER if idx == 2 else CYAN
            draw_round_rect(draw, (nx, iy0 + 34, nx + nw, iy0 + ih - 34), 12, PANEL_BG, outline=col, width=2)
            draw.text((nx + 16, iy0 + 72), nd, font=f_md, fill=col)
            if idx < 3:
                draw.text((nx + nw + 3, iy0 + 70), ">", font=f_lg, fill=WHITE)

    elif dtype == "human_in_loop":
        draw.text((ix0, iy0 + 14), "DIVISIÓN ÓPTIMA DE TRABAJO (HUMAN-IN-THE-LOOP)", font=f_sm, fill=CYAN)
        bar_y0, bar_y1 = iy0 + 52, iy0 + 132
        split_x = ix0 + int(iw * 0.68)
        draw_round_rect(draw, (ix0, bar_y0, split_x - 8, bar_y1), 12, (12, 48, 72, 240), outline=CYAN, width=2)
        draw.text((ix0 + 20, bar_y0 + 22), "AGENTES IA · Busca · Clasifica · Redacta · Verifica", font=f_md, fill=WHITE)
        draw_round_rect(draw, (split_x, bar_y0, ix0 + iw, bar_y1), 12, (58, 36, 12, 245), outline=AMBER, width=2)
        draw.text((split_x + 18, bar_y0 + 22), "LÍDER · 1 CLIC FINAL", font=f_md, fill=AMBER)
        draw.text((ix0, iy0 + 148), "La IA amplifica el criterio humano, nunca lo reemplaza.", font=f_sm, fill=MUTED)

    elif dtype == "regional_kpis":
        tiles = [("< 10 SEG", "Respuesta Catálogo", CYAN), ("0 ERRORES", "Auditoría y Facturas", CYAN), ("100% PROPIA", "Infraestructura Segura", AMBER)]
        tw = (iw - 36) // 3
        for idx, (big, sub, col) in enumerate(tiles):
            tx = ix0 + idx * (tw + 18)
            draw_round_rect(draw, (tx, iy0 + 14, tx + tw, iy0 + ih - 14), 12, PANEL_BG, outline=col, width=2)
            draw.text((tx + 22, iy0 + 38), big, font=f_lg, fill=col)
            draw.text((tx + 22, iy0 + 96), sub, font=f_md, fill=WHITE)

    elif dtype == "impact_chart":
        draw.text((ix0, iy0 + 8), "COMPARATIVO DE TIEMPO DE CICLO OPERATIVO", font=f_sm, fill=MUTED)
        draw_round_rect(draw, (ix0, iy0 + 44, ix0 + iw - 230, iy0 + 94), 8, (180, 95, 18, 240), outline=AMBER, width=1)
        draw.text((ix0 + 18, iy0 + 56), "ANTES: 5 Especialistas · 1 Semana Completa", font=f_md, fill=WHITE)
        draw_round_rect(draw, (ix0, iy0 + 114, ix0 + 260, iy0 + 164), 8, (16, 130, 175, 245), outline=CYAN, width=2)
        draw.text((ix0 + 276, iy0 + 126), "HOY: Equipo de Agentes IA · Minutos", font=f_md, fill=CYAN)
        draw_round_rect(draw, (ix0 + iw - 210, iy0 + 34, ix0 + iw, iy0 + ih - 14), 12, (12, 48, 72, 245), outline=CYAN, width=2)
        draw.text((ix0 + iw - 190, iy0 + 58), "> 90%", font=f_lg, fill=CYAN)
        draw.text((ix0 + iw - 190, iy0 + 108), "REDUCCIÓN", font=f_sm, fill=WHITE)

    else:
        pillars = [("01 AUTONOMÍA", "Sistemas Organizados", CYAN), ("02 SOBERANÍA", "0 SaaS Tax · Control", CYAN), ("03 GUÍA HOY", "Mesa de Trabajo Activa", AMBER)]
        pw = (iw - 36) // 3
        for idx, (t1, t2, col) in enumerate(pillars):
            px = ix0 + idx * (pw + 18)
            draw_round_rect(draw, (px, iy0 + 18, px + pw, iy0 + ih - 18), 12, PANEL_BG, outline=col, width=2)
            draw.text((px + 20, iy0 + 42), t1, font=f_md, fill=col)
            draw.text((px + 20, iy0 + 88), t2, font=f_sm, fill=WHITE)


def build_block_hud_u8(block: dict) -> tuple[np.ndarray, np.ndarray]:
    """Pre-render block HUD card as uint8 (bgr_u8, mask_u8)."""
    img = Image.new("RGBA", (HUD_W, HUD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_badge = load_font(FONT_BOLD, 19)
    f_eyebrow = load_font(FONT_BOLD, 20)
    f_title = load_font(FONT_BOLD, 38)
    f_lg = load_font(FONT_BOLD, 32)
    f_md = load_font(FONT_BOLD, 22)
    f_sm = load_font(FONT_REG, 19)
    f_kpi_lbl = load_font(FONT_BOLD, 16)
    f_kpi_val = load_font(FONT_BOLD, 25)
    f_bul = load_font(FONT_REG, 22)

    draw_round_rect(draw, (0, 0, HUD_W, 56), 14, (8, 14, 28, 240), outline=(56, 189, 248, 140), width=1)
    draw.text((22, 16), "GUÍA HOY · RIONEGRO, ANTIOQUIA  |  HBOS 768D · 0 SAAS TAX", font=f_badge, fill=WHITE)
    bid_str = f"BLOQUE {block['block_id']:02d} / 10"
    draw_round_rect(draw, (HUD_W - 190, 8, HUD_W - 10, 48), 10, (56, 36, 10, 245), outline=AMBER, width=1)
    draw.text((HUD_W - 172, 16), bid_str, font=f_badge, fill=AMBER)

    draw_round_rect(draw, (0, 74, HUD_W, HUD_H), 20, CARD_BG, outline=(56, 189, 248, 150), width=2)
    hud = block["hud"]
    draw.text((34, 98), hud["eyebrow"], font=f_eyebrow, fill=CYAN)

    title_lines = textwrap.wrap(hud["headline"], width=46)[:2]
    ty = 130
    for line in title_lines:
        draw.text((34, ty), line, font=f_title, fill=WHITE)
        ty += 46

    draw_diagram(draw, hud["diagram_type"], 34, 232, HUD_W - 68, 218, f_md, f_sm, f_lg)

    kpis = hud["kpis"]
    kw = (HUD_W - 68 - 32) // 3
    for idx, kpi in enumerate(kpis):
        kx = 34 + idx * (kw + 16)
        ky = 472
        col = AMBER if kpi["tone"] == "amber" else CYAN
        draw_round_rect(draw, (kx, ky, kx + kw, ky + 104), 12, PANEL_BG, outline=col, width=2)
        draw.text((kx + 18, ky + 16), kpi["label"], font=f_kpi_lbl, fill=MUTED)
        draw.text((kx + 18, ky + 48), kpi["value"], font=f_kpi_val, fill=col)

    by = 602
    for btxt in hud["bullets"][:3]:
        draw.ellipse((38, by + 9, 50, by + 21), fill=CYAN)
        draw.text((64, by), btxt, font=f_bul, fill=WHITE)
        by += 52

    draw.text((34, HUD_H - 42), "HBOS 768D · QDRANT VERIFICADO", font=f_kpi_lbl, fill=MUTED)

    arr = np.array(img, dtype=np.uint8)
    bgr_u8 = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    mask_u8 = ((arr[:, :, 3] > 64).astype(np.uint8) * 255)
    return bgr_u8, mask_u8


def build_subtitle_u8(text: str) -> tuple[np.ndarray, np.ndarray]:
    """Pre-render lower-third subtitle banner as uint8 (bgr_u8, mask_u8)."""
    img = Image.new("RGBA", (SUB_W, SUB_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_round_rect(draw, (0, 0, SUB_W, SUB_H), 16, (8, 13, 25, 240), outline=(56, 189, 248, 140), width=1)
    draw_round_rect(draw, (12, 16, 20, SUB_H - 16), 4, CYAN)

    f_sub = load_font(FONT_BOLD, 25)
    lines = textwrap.wrap(text.strip(), width=78)[:3]
    line_h = 34
    total_h = len(lines) * line_h
    y = max(14, (SUB_H - total_h) // 2 - 2)
    for line in lines:
        draw.text((38, y), line, font=f_sub, fill=WHITE)
        y += line_h

    arr = np.array(img, dtype=np.uint8)
    bgr_u8 = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    mask_u8 = ((arr[:, :, 3] > 64).astype(np.uint8) * 255)
    return bgr_u8, mask_u8


def load_pose_u8(rgba_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load normalized RGBA pose directly as uint8 (bgr_u8, alpha_u8)."""
    im = Image.open(rgba_path).convert("RGBA")
    arr = np.array(im, dtype=np.uint8)
    bgr_u8 = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    alpha_u8 = arr[:, :, 3]
    return bgr_u8, alpha_u8


def render_block_worker(task: tuple[dict, str]) -> dict:
    """Render one complete 1080p 60fps block MP4 using pure C++ OpenCV uint8 ops."""
    block, out_mp4_str = task
    bid = block["block_id"]
    out_mp4 = Path(out_mp4_str)
    n_frames = int(block["num_frames"])
    b_start_frame = int(block["start_frame"])
    cam_mode = block["camera_mode"]

    t_start = time.time()
    env = np.load(str(cfg.LOCAL_TEMP / "voice_envelope_60fps.npy"))

    clean_bg_path = cfg.BUILD_DIR / "escenas_3d_clean" / block["bg_file"]
    bg_raw = cv2.imread(str(clean_bg_path))
    if bg_raw is None:
        raise FileNotFoundError(f"Escena limpia 3D no encontrada: {clean_bg_path}")
    up_w, up_h = 2208, 1242
    bg_up = cv2.resize(bg_raw, (up_w, up_h), interpolation=cv2.INTER_CUBIC)
    # Subtle executive dark slate balance so HUD & foreground avatar separate cleanly
    bg_up[:, :, 0] = cv2.convertScaleAbs(bg_up[:, :, 0], alpha=0.88, beta=0)
    bg_up[:, :, 1] = cv2.convertScaleAbs(bg_up[:, :, 1], alpha=0.85, beta=0)
    bg_up[:, :, 2] = cv2.convertScaleAbs(bg_up[:, :, 2], alpha=0.82, beta=0)

    # Precompute subtle cyan/amber volumetric rim halo behind right-third presenter zone (680x960)
    halo_y, halo_x = np.ogrid[:960, :680]
    dist_sq = ((halo_x - 340.0) / 280.0) ** 2 + ((halo_y - 420.0) / 380.0) ** 2
    halo_mask = np.exp(-1.4 * dist_sq).astype(np.float32)
    halo_bgr = np.zeros((960, 680, 3), dtype=np.uint8)
    halo_bgr[:, :, 0] = np.clip(halo_mask * 36.0, 0, 255).astype(np.uint8)  # subtle cyan rim blue
    halo_bgr[:, :, 1] = np.clip(halo_mask * 26.0, 0, 255).astype(np.uint8)
    halo_bgr[:, :, 2] = np.clip(halo_mask * 12.0, 0, 255).astype(np.uint8)

    hud_bgr_u8, hud_mask_u8 = build_block_hud_u8(block)

    beat_assets = []
    pose_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for bt in block["beats"]:
        sbgr, smask = build_subtitle_u8(bt["text"])
        pname = bt["avatar_pose"]
        if pname not in pose_cache:
            pose_cache[pname] = load_pose_u8(cfg.AVATAR_ALPHA_DIR / pname)
        beat_assets.append({
            "start_local": int(bt["start_frame"]) - b_start_frame,
            "end_local": int(bt["end_frame"]) - b_start_frame,
            "sub_bgr": sbgr,
            "sub_mask": smask,
            "pose": pname,
        })

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{cfg.TARGET_W}x{cfg.TARGET_H}", "-pix_fmt", "bgr24",
        "-r", str(cfg.TARGET_FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(cfg.TARGET_FPS),
        "-video_track_timescale", "60000", "-threads", "2",
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    cur_beat_idx = 0
    sh_mat = np.float32([[1.0, 0.0, 10.0], [0.0, 1.0, 6.0]])

    for lf in range(n_frames):
        gf = b_start_frame + lf
        t_sec = gf / cfg.TARGET_FPS
        prog = lf / max(1, n_frames - 1)
        rms = float(env[gf, 0]) if gf < len(env) else 0.0
        syl = float(env[gf, 1]) if gf < len(env) else 0.0

        # 1. Smooth 60fps 2.5D camera dynamics via C++ warpAffine
        if cam_mode == "dolly_in":
            zoom = 1.0 - 0.09 * prog
            dx = 18.0 * math.sin(math.pi * prog)
            dy = -10.0 * prog
        elif cam_mode == "dolly_out":
            zoom = 0.91 + 0.09 * prog
            dx = -18.0 * math.sin(math.pi * prog)
            dy = 8.0 * prog
        elif cam_mode == "parallax_right":
            zoom = 0.94 + 0.02 * math.sin(2.0 * math.pi * prog)
            dx = -55.0 + 110.0 * prog
            dy = 12.0 * math.sin(math.pi * prog)
        else:
            zoom = 0.95 - 0.02 * math.sin(2.0 * math.pi * prog)
            dx = 55.0 - 110.0 * prog
            dy = -12.0 * math.sin(math.pi * prog)

        inv_s = 1.0 / zoom
        m_cam = np.float32([
            [inv_s, 0.0, cfg.TARGET_W * 0.5 - inv_s * (up_w * 0.5 + dx)],
            [0.0, inv_s, cfg.TARGET_H * 0.5 - inv_s * (up_h * 0.5 + dy)],
        ])
        frame = cv2.warpAffine(bg_up, m_cam, (cfg.TARGET_W, cfg.TARGET_H), flags=cv2.INTER_LINEAR)

        # Gentle transition exposure swell on first/last 18 frames (never pure black -> 0 blackframes)
        if lf < 18:
            swell = 0.38 + 0.62 * (lf / 18.0)
            frame = cv2.convertScaleAbs(frame, alpha=swell, beta=0)
        elif lf > n_frames - 18:
            swell = 0.38 + 0.62 * ((n_frames - 1 - lf) / 18.0)
            frame = cv2.convertScaleAbs(frame, alpha=swell, beta=0)

        # 2. C++ uint8 HUD glassmorphic blend
        hud_roi = frame[HUD_Y0:HUD_Y0 + HUD_H, HUD_X0:HUD_X0 + HUD_W]
        hud_blended = cv2.addWeighted(hud_bgr_u8, 0.86, hud_roi, 0.14, 0)
        cv2.copyTo(hud_blended, hud_mask_u8, hud_roi)

        # Animated progress bar + voice-reactive equalizer (strictly separated from footer label)
        bar_x0, bar_y0 = HUD_X0 + 510, HUD_Y0 + HUD_H - 36
        bar_w = 575
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + bar_w, bar_y0 + 10), (30, 48, 78), -1)
        fill_w = max(4, int(bar_w * prog))
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + fill_w, bar_y0 + 10), (248, 189, 56), -1)
        for bi in range(12):
            bx = HUD_X0 + 350 + bi * 11
            bh = int(4 + 16 * max(0.1, rms * (0.6 + 0.4 * math.sin(t_sec * 11.0 + bi * 0.9))))
            col_eq = (11, 158, 245) if bi % 3 == 0 else (248, 189, 56)
            cv2.rectangle(frame, (bx, bar_y0 + 10 - bh), (bx + 7, bar_y0 + 10), col_eq, -1)

        # 3. Active beat determination & C++ uint8 subtitle blend
        while cur_beat_idx < len(beat_assets) - 1 and lf >= beat_assets[cur_beat_idx]["end_local"]:
            cur_beat_idx += 1
        cur_b = beat_assets[cur_beat_idx]

        sub_roi = frame[SUB_Y0:SUB_Y0 + SUB_H, SUB_X0:SUB_X0 + SUB_W]
        sub_blended = cv2.addWeighted(cur_b["sub_bgr"], 0.88, sub_roi, 0.12, 0)
        cv2.copyTo(sub_blended, cur_b["sub_mask"], sub_roi)

        # 4. Humanized continuous avatar motion + crisp 8-frame pose transition
        p_bgr, p_alp = pose_cache[cur_b["pose"]]
        frames_into_beat = lf - cur_b["start_local"]
        if cur_beat_idx > 0 and frames_into_beat < 8:
            prev_bgr, prev_alp = pose_cache[beat_assets[cur_beat_idx - 1]["pose"]]
            if prev_bgr is not p_bgr:
                w_mix = frames_into_beat / 8.0
                p_bgr = cv2.addWeighted(prev_bgr, 1.0 - w_mix, p_bgr, w_mix, 0)
                p_alp = cv2.addWeighted(prev_alp, 1.0 - w_mix, p_alp, w_mix, 0)

        av_h, av_w = p_bgr.shape[:2]
        breath = 1.0 + 0.0085 * math.sin(2.0 * math.pi * 0.26 * t_sec) + 0.0055 * syl
        sway_x = 5.5 * math.sin(2.0 * math.pi * 0.21 * t_sec) + 1.8 * rms * math.sin(2.0 * math.pi * 1.1 * t_sec)
        sway_y = 3.2 * math.cos(2.0 * math.pi * 0.42 * t_sec) - 3.5 * syl
        angle_deg = 0.85 * math.sin(2.0 * math.pi * 0.19 * t_sec) + 0.65 * rms * math.sin(2.0 * math.pi * 1.45 * t_sec)

        mat = cv2.getRotationMatrix2D((av_w * 0.5, av_h * 0.88), angle_deg, breath)
        mat[0, 2] += sway_x
        mat[1, 2] += sway_y

        wbgr = cv2.warpAffine(p_bgr, mat, (av_w, av_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        walp = cv2.warpAffine(p_alp, mat, (av_w, av_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        if syl > 0.05:
            head_y_end = int(av_h * 0.26)
            wbgr[:head_y_end] = cv2.convertScaleAbs(wbgr[:head_y_end], alpha=1.0 + 0.03 * syl, beta=0)
            jaw_shift = 1.8 * syl
            if jaw_shift > 0.2:
                jy0, jy1 = int(av_h * 0.13), int(av_h * 0.20)
                m_jaw = np.float32([[1, 0, 0], [0, 1, jaw_shift]])
                wbgr[jy0:jy1] = cv2.warpAffine(wbgr[jy0:jy1], m_jaw, (av_w, jy1 - jy0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        av_roi = frame[AV_Y0:AV_Y0 + av_h, AV_X0:AV_X0 + av_w]
        # Volumetric studio rim halo behind presenter
        cv2.add(av_roi, halo_bgr, dst=av_roi)
        # Contact shadow
        shifted_alp = cv2.warpAffine(walp, sh_mat, (av_w, av_h), flags=cv2.INTER_NEAREST)
        _, sh_mask = cv2.threshold(shifted_alp, 80, 255, cv2.THRESH_BINARY)
        sh_roi = cv2.convertScaleAbs(av_roi, alpha=0.68, beta=0)
        cv2.copyTo(sh_roi, sh_mask, av_roi)

        # Anti-aliased edge ring + crisp solid core
        edge_mask = cv2.inRange(walp, 35, 190)
        edge_blend = cv2.addWeighted(wbgr, 0.55, av_roi, 0.45, 0)
        cv2.copyTo(edge_blend, edge_mask, av_roi)

        _, solid_mask = cv2.threshold(walp, 190, 255, cv2.THRESH_BINARY)
        cv2.copyTo(wbgr, solid_mask, av_roi)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="replace")
    proc.wait()
    if proc.returncode != 0 or not out_mp4.exists() or out_mp4.stat().st_size == 0:
        raise RuntimeError(f"Error renderizando bloque {bid:02d}: {stderr_out[-400:]}")

    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames,duration", "-of", "json", str(out_mp4)],
        capture_output=True, text=True, check=True,
    )
    st = json.loads(pr.stdout)["streams"][0]
    read_frames = int(st["nb_read_frames"])
    if read_frames != n_frames:
        raise RuntimeError(f"Frame mismatch en bloque {bid:02d}: esperado={n_frames}, real={read_frames}")

    elapsed = round(time.time() - t_start, 2)
    print(f"[+] Bloque {bid:02d} OK: {read_frames} frames ({float(st['duration']):.3f}s) en {elapsed}s ({read_frames/max(0.1,elapsed):.1f} fps)", flush=True)
    return {"block_id": bid, "mp4": str(out_mp4), "frames": read_frames, "duration": float(st["duration"]), "render_sec": elapsed}


def generate_control_clips(concat_list: Path, audio_master: Path) -> list[dict]:
    """Extract 3 control clips (with synced audio) and 3 QA PNG frames for Gate 3->4 visual verification."""
    temp_silent = cfg.LOCAL_TEMP / "temp_full_silent.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c:v", "copy", str(temp_silent)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    specs = [
        ("ctrl_inicio_00_00_00_30.mp4", "qa_inicio.png", "0", "30", "15"),
        ("ctrl_mitad_03_10_03_40.mp4", "qa_mitad.png", "190", "30", "205"),
        ("ctrl_cierre_06_20_06_54.mp4", "qa_cierre.png", "380", "34.276", "396"),
    ]
    out_reports = []
    for mp4_name, png_name, ss, dur, qa_t in specs:
        mp4_p = cfg.CONTROL_CLIPS_DIR / mp4_name
        png_p = cfg.CONTROL_CLIPS_DIR / png_name
        subprocess.run([
            "ffmpeg", "-y", "-ss", ss, "-t", dur, "-i", str(temp_silent),
            "-ss", ss, "-t", dur, "-i", str(audio_master),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "superfast", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            str(mp4_p),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([
            "ffmpeg", "-y", "-ss", qa_t, "-i", str(temp_silent),
            "-frames:v", "1", str(png_p),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out_reports.append({
            "clip": str(mp4_p),
            "clip_bytes": mp4_p.stat().st_size,
            "qa_png": str(png_p),
            "qa_png_bytes": png_p.stat().st_size,
            "window": f"{ss}s+{dur}s",
        })
    return out_reports


def main() -> None:
    print("=== FASE 3: COMPOSICION CINEMATICA 1080p60 C++ UINT8 ===", flush=True)
    df2 = json.loads((cfg.BUILD_DIR / "debug_fase2.json").read_text(encoding="utf-8"))
    if df2.get("gate_2_to_3") != "PASS":
        print("FAIL-FAST: Gate 2->3 no esta en PASS", flush=True)
        sys.exit(1)

    timeline = json.loads((cfg.BUILD_DIR / "timeline_768.json").read_text(encoding="utf-8"))
    blocks = timeline["blocks"]

    tasks = [(b, str(cfg.LOCAL_TEMP / f"block_{b['block_id']:02d}.mp4")) for b in blocks]
    t0 = time.time()
    print(f"[L3] Renderizando {len(tasks)} bloques en paralelo (max_workers=3, 1920x1080 @ 60fps C++ uint8)...", flush=True)
    with ProcessPoolExecutor(max_workers=3) as ex:
        block_results = list(ex.map(render_block_worker, tasks))

    block_results.sort(key=lambda r: r["block_id"])
    concat_txt = cfg.LOCAL_TEMP / "blocks_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for br in block_results:
            f.write(f"file '{br['mp4'].replace(chr(92), '/')}'\n")

    ctrl_reports = generate_control_clips(concat_txt, cfg.AUDIO_MASTER)
    total_elapsed = round(time.time() - t0, 2)

    debug_f3 = {
        "phase": "FASE_3",
        "gate_3_to_4": "PASS",
        "total_render_sec": total_elapsed,
        "total_frames_rendered": sum(r["frames"] for r in block_results),
        "blocks": block_results,
        "control_clips": ctrl_reports,
        "concat_list": str(concat_txt),
    }
    df3_path = cfg.BUILD_DIR / "debug_fase3.json"
    df3_path.write_text(json.dumps(debug_f3, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[GATE 3->4] Status=PASS | Frames={debug_f3['total_frames_rendered']} | Tiempo total={total_elapsed}s", flush=True)


if __name__ == "__main__":
    main()
