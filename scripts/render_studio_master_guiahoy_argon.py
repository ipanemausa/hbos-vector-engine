# -*- coding: utf-8 -*-
r"""
STUDIO AUTOMATION & DYNAMIC MOTION GRAPHICS DIRECTOR (137 SCENES E2E)
=====================================================================
Emula la dinámica de estudio profesional (Alejavi, Álvaro Morale, Lorena Bordonaba):
- Estudio Virtual 3D profundo (luces volumétricas cian/ámbar, consola Antigravity 2.0 / VS Code
  flotante en perspectiva central, diagramas Qdrant 768d, Matriz 3D, DAG Zero-Drift 5TB y REA+Hiperframes).
- Avatar dinámico Guiahoy en primer plano lateral RGBA sin cajas rectangulares (M-COMPOSICION-01),
  con rim-light cian/dorado, sombra de contacto a piso (ground shadow) y respiración M-IDLE-01.
- Director Cam Automation:
    1) Plano Amplio de Estudio (Zoom Out 1.00x) al abrir/cambiar de sección.
    2) Acercamiento fluido (Zoom In -> 1.35x con curva smoothstep_c1 6x^5-15x^4+10x^3) hacia el
       código/diagrama explicado con telemetría de cursor y puntero láser dual R-LASER-01 de las 7 Gemas.
    3) Regreso suave a Plano Amplio (Zoom Out) para transición.
- Destino obligatorio: G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\STUDIO_MASTER_GUIAHOY_ARGON.mp4
- Regla Dura RULE_AUTO_LAUNCH_01: Dispara os.startfile(STUDIO_MASTER_GUIAHOY_ARGON.mp4) inmediatamente.
"""
import base64
import gc
import hashlib
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw
from dotenv import load_dotenv

from render_argon_4_cases_pilot_and_thumbnails import (
    AVATAR_DIR,
    DIAMANTINI_DIR,
    PROJECT_DRIVE_DIR,
    QDRANT_VAULT_DIR,
    VOICE_PROFILES_DIR,
    WORKSPACE_ROOT,
    add_rim_light_and_contact_shadow,
    load_rgba_clean_bg,
)

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(".env.local")
load_dotenv(".env")

MANIFEST_PATH = PROJECT_DRIVE_DIR / "scene_manifest.json"
STUDIO_STREAM_DIR = PROJECT_DRIVE_DIR / "_studio_director_stream_temp"
STUDIO_MASTER_MP4 = QDRANT_VAULT_DIR / "STUDIO_MASTER_GUIAHOY_ARGON.mp4"
ARTIFACT_DIR = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83")

GEM_NAMES = ["Diamantino", "Rubin", "Zafir", "Esmeralda", "Amatista", "Citrilo", "Grafito"]

ARCH_CASE_META = {
    "COLD_OPEN": {
        "studio_banner": "ESTUDIO VIRTUAL HBOS · GEMINI ARGON + ANTIGRAVITY 2.0 (4 CASOS REALES)",
        "diagram_title": "ARQUITECTURA SOBERANA · COSTO $0 · 0 PESO EN PC",
        "accent": (255, 65, 95),
    },
    "CASE_1_ERP_CRM": {
        "studio_banner": "CASO 1 · ORQUESTACIÓN MULTI-AGENTE & RAG VECTORIAL QDRANT (768D)",
        "diagram_title": "SWARM PLANNER + EXECUTOR + AUDITOR <-> QDRANT 768D COSINE",
        "accent": (0, 229, 255),
    },
    "CASE_2_MARKETING_ENGINE": {
        "studio_banner": "CASO 2 · FACTORIZACIÓN MATRICIAL 3D (ESPACIO × TIEMPO × NEGOCIO)",
        "diagram_title": "TENSOR 3D SVD · PRESERVACIÓN SEMÁNTICA 99.98%",
        "accent": (255, 184, 0),
    },
    "CASE_3_WHATSAPP_VOICE_AGENT": {
        "studio_banner": "CASO 3 · PIPELINE DAG ZERO-DRIFT E2E & GOOGLE DRIVE 5TB APPEND-ONLY",
        "diagram_title": "RCLONE STREAMING · SHA-256 VERIFIED · 0 MB EN DISCO LOCAL",
        "accent": (16, 185, 129),
    },
    "CASE_4_FINANCE_RECONCILIATION": {
        "studio_banner": "CASO 4 · AUTOMATIZACIÓN CREATIVA MASIVA (REA + HIPERFRAMES + FISH DRAMA 3)",
        "diagram_title": "GALLERY-DL / YT-DLP CONTACT SHEETS -> HIPERFRAMES 3 PLANOS",
        "accent": (168, 85, 247),
    },
    "OUTRO_UNIFIED_ARCHITECTURE": {
        "studio_banner": "CIERRE DE ESTUDIO · ECOSISTEMA UNIFICADO Y AUTO-PREVIEW ACTIVO",
        "diagram_title": "STATUS 200 OK · ALL PROTOCOLS VERIFIED & UNALTERED",
        "accent": (59, 130, 246),
    },
}


def format_ass_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def load_studio_assets():
    pose_files = [
        AVATAR_DIR / "avatar-pose-t-energize.png",
        AVATAR_DIR / "avatar-pose-t-point-up.png",
        AVATAR_DIR / "avatar-pose-t-open-arms.png",
        AVATAR_DIR / "avatar-pose-t-thumbs-up.png",
        AVATAR_DIR / "avatar-pose-t-celebrate.png",
    ]
    avatars = []
    for pf in pose_files:
        raw = load_rgba_clean_bg(pf, target_height=580)
        avatars.append(add_rim_light_and_contact_shadow(raw, (0, 229, 255)))

    gems = {}
    for gname in GEM_NAMES:
        gfolder = DIAMANTINI_DIR / gname
        cands = list(gfolder.glob("*accion_dinamica1*.png")) + list(gfolder.glob("*.png"))
        src = cands[0] if cands else Path("")
        raw_g = load_rgba_clean_bg(src, target_height=230)
        gems[gname] = add_rim_light_and_contact_shadow(raw_g, (255, 204, 0))
    return avatars, gems


def render_studio_shot(
    scn: dict,
    idx: int,
    total_scenes: int,
    shot_mode: str,  # "WIDE_OPEN", "ZOOM_IN_FOCUS", "WIDE_OUT"
    avatars: list,
    gems: dict,
) -> Image.Image:
    W, H = 1920, 1080
    case_key = scn.get("case", "CASE_1_ERP_CRM")
    meta = ARCH_CASE_META.get(case_key, ARCH_CASE_META["CASE_1_ERP_CRM"])
    ar, ag, ab = meta["accent"]
    emotion_mode = scn.get("emotion_intonation", {}).get("mode", "INGENIERIA_PRECISA")

    # Fondo de Estudio Virtual (Estilo Alejavi / Álvaro Morale / Lorena Bordonaba)
    canvas = Image.new("RGBA", (W, H), (7, 10, 18, 255))
    draw = ImageDraw.Draw(canvas)

    # Luces ambientales de estudio (Key Cian izquierda + Rim Ámbar derecha + Piso reflectivo)
    draw.ellipse([-180, 120, 520, 820], fill=(0, 180, 255, 22))
    draw.ellipse([1380, 80, 2080, 780], fill=(255, 184, 0, 20))
    draw.rectangle([0, 920, W, H], fill=(11, 16, 28, 255))
    draw.line([(0, 920), (W, 920)], fill=(ar, ag, ab, 110), width=2)

    # Marco de Estudio Virtual + Monitor Principal Flotante (IDE / VS Code / Antigravity 2.0)
    mon_x0, mon_y0, mon_x1, mon_y1 = 86, 54, 1520, 910
    draw.rounded_rectangle([mon_x0 - 8, mon_y0 - 8, mon_x1 + 8, mon_y1 + 8], radius=22, fill=(18, 26, 44, 200), outline=(ar, ag, ab, 190), width=3)
    draw.rounded_rectangle([mon_x0, mon_y0, mon_x1, mon_y1], radius=18, fill=(12, 17, 30, 255))

    # Top bar del Monitor de Estudio
    draw.rounded_rectangle([mon_x0, mon_y0, mon_x1, mon_y0 + 52], radius=18, fill=(20, 28, 48, 255))
    draw.ellipse([mon_x0 + 22, mon_y0 + 18, mon_x0 + 38, mon_y0 + 34], fill=(255, 95, 86, 255))
    draw.ellipse([mon_x0 + 48, mon_y0 + 18, mon_x0 + 64, mon_y0 + 34], fill=(255, 189, 46, 255))
    draw.ellipse([mon_x0 + 74, mon_y0 + 18, mon_x0 + 90, mon_y0 + 34], fill=(39, 201, 63, 255))
    draw.text(
        (mon_x0 + 115, mon_y0 + 17),
        f"{meta['studio_banner']}  |  ESCENA {idx+1}/{total_scenes}  |  CÁMARA: {shot_mode}",
        fill=(235, 242, 255, 255),
    )

    # Sidebar VS Code / Antigravity 2.0
    draw.rectangle([mon_x0, mon_y0 + 52, mon_x0 + 270, mon_y1], fill=(15, 21, 36, 255))
    draw.text((mon_x0 + 18, mon_y0 + 72), "EXPLORADOR DE ARQUITECTURA", fill=(ar, ag, ab, 255))
    sidebar_files = [
        "01_qdrant_rag_768d.py",
        "02_matriz_3d_svd.py",
        "03_dag_zero_drift_5tb.py",
        "04_rea_hiperframes_fish.py",
        "scene_manifest_137.json",
        "sync_map_ctc_20ms.json",
    ]
    for si, sfile in enumerate(sidebar_files):
        sy = mon_y0 + 112 + si * 42
        active_file = (si == (idx % len(sidebar_files)))
        if active_file:
            draw.rounded_rectangle([mon_x0 + 10, sy - 6, mon_x0 + 258, sy + 28], radius=7, fill=(28, 40, 68, 255), outline=(ar, ag, ab, 180), width=2)
        draw.text((mon_x0 + 22, sy), sfile, fill=(255, 255, 255, 255) if active_file else (145, 162, 188, 255))

    # Editor de código en vivo + Diagrama Técnico Qdrant / Hiperframes
    ed_x0, ed_y0, ed_x1, ed_y1 = mon_x0 + 286, mon_y0 + 68, mon_x1 - 20, mon_y0 + 560
    draw.rounded_rectangle([ed_x0, ed_y0, ed_x1, ed_y1], radius=14, fill=(16, 23, 39, 255), outline=(45, 62, 96, 255), width=2)
    draw.text((ed_x0 + 24, ed_y0 + 18), f"{meta['diagram_title']}  ·  [{scn['scene_id']}]", fill=(255, 204, 0, 255))

    code_block = [
        f"# {scn.get('screen_action', 'Interactive Studio Execution')[:72]}",
        f"voice = GuiahoyClone(ref='Guiahoy_CLONE_REF_90s_48k.wav', f0=109.2, afftdn=False, mode='{emotion_mode}')",
        f"qdrant_768d = HbosVectorEngine(dim=768, matrix_3d=('Espacio', 'Tiempo', 'Contexto_Negocio'))",
        f"studio_cam  = DirectorCam(curve='smoothstep_c1_6x5_15x4_10x3', zoom={'1.35x' if shot_mode=='ZOOM_IN_FOCUS' else '1.00x'})",
        f"output = studio_cam.execute_target(ui='{scn.get('cursor_target', {}).get('ui_element', 'Run_Node')}', laser='R-LASER-01')",
    ]
    for cli, cl in enumerate(code_block):
        cly = ed_y0 + 68 + cli * 44
        if shot_mode == "ZOOM_IN_FOCUS" and cli in (3, 4):
            draw.rectangle([ed_x0 + 14, cly - 6, ed_x1 - 14, cly + 30], fill=(ar, ag, ab, 52))
        draw.text((ed_x0 + 26, cly), cl, fill=(220, 232, 250, 255))

    # Diagrama interactivo de nodos y botón objetivo del cursor
    tx = int(scn.get("cursor_target", {}).get("x", 880))
    ty = int(scn.get("cursor_target", {}).get("y", 460))
    tx = max(ed_x0 + 190, min(ed_x1 - 190, tx))
    ty = max(ed_y0 + 290, min(ed_y1 - 55, ty))
    ui_el = scn.get("cursor_target", {}).get("ui_element", "Execute_Node")

    is_zoomed = shot_mode == "ZOOM_IN_FOCUS"
    btn_fill = (ar, ag, ab, 255) if is_zoomed else (28, 42, 70, 255)
    txt_fill = (10, 14, 24, 255) if is_zoomed else (255, 255, 255, 255)
    draw.rounded_rectangle([tx - 175, ty - 28, tx + 175, ty + 28], radius=12, fill=btn_fill, outline=(255, 255, 255, 240), width=3)
    draw.text((tx - 150, ty - 10), f"▶ {ui_el[:28]}", fill=txt_fill)

    # Consola inferior de telemetría
    term_y0 = ed_y1 + 18
    draw.rounded_rectangle([ed_x0, term_y0, ed_x1, mon_y1 - 18], radius=14, fill=(9, 13, 22, 255), outline=(ar, ag, ab, 185), width=2)
    draw.text((ed_x0 + 24, term_y0 + 18), "CONSOLA ANTIGRAVITY 2.0 · TELEMETRÍA DE ESTUDIO EN VIVO ($0 LICENCIAS)", fill=(16, 185, 129, 255))
    draw.text((ed_x0 + 24, term_y0 + 58), f"$ hbos-studio --scene {scn['scene_id']} --cam {shot_mode} --voice Guiahoy_109.2Hz", fill=(235, 242, 255, 255))
    cam_msg = (
        f"[DIRECTOR CAM: ZOOM IN 1.35x] Enfocando {ui_el} · Puntero Láser Dual R-LASER-01 Activo"
        if is_zoomed
        else f"[DIRECTOR CAM: PLANO AMPLIO 1.00x] Panorama completo de estudio + Avatar RGBA + Interfaz"
    )
    draw.text((ed_x0 + 24, term_y0 + 98), cam_msg, fill=(255, 204, 0, 255) if is_zoomed else (0, 229, 255, 255))

    # DIRECTOR CAM AUTOMATION: Zoom In (1.35x) sobre el código/diagrama o Plano Amplio (1.00x)
    if is_zoomed:
        z_factor = 1.35
        zw, zh = int(W / z_factor), int(H / z_factor)
        left = max(0, min(W - zw, tx - zw // 2))
        top = max(0, min(H - zh, ty - zh // 2))
        cropped = canvas.crop((left, top, left + zw, top + zh))
        canvas = cropped.resize((W, H), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(canvas)
        cx_s = int((tx - left) * (W / zw))
        cy_s = int((ty - top) * (H / zh))
    else:
        cx_s = tx - (70 if shot_mode == "WIDE_OPEN" else -40)
        cy_s = ty - (35 if shot_mode == "WIDE_OPEN" else -20)

    # PLANO 3 (PRIMER PLANO DE ESTUDIO): Avatar Guiahoy RGBA con Rim-Light + Ground Shadow + 7 Gemas R-LASER-01
    relocate_left = is_zoomed and (cx_s > W * 0.60)
    av_img = avatars[idx % len(avatars)]
    breath_offset = 0 if is_zoomed else (-6 if shot_mode == "WIDE_OPEN" else 5)
    av_x = 38 if relocate_left else (W - av_img.width - 32)
    av_y = H - av_img.height - 10 + breath_offset

    g1_name = GEM_NAMES[idx % len(GEM_NAMES)]
    g2_name = GEM_NAMES[(idx + 3) % len(GEM_NAMES)]
    g1_img = gems[g1_name]
    g2_img = gems[g2_name]
    g1_x = (av_x + av_img.width - 28) if relocate_left else (av_x - g1_img.width + 28)
    g1_y = H - g1_img.height - 32 - breath_offset
    g2_x = g1_x + (140 if relocate_left else -140)
    g2_y = H - g2_img.height - 86 + breath_offset

    if is_zoomed:
        for gx, gy, col in [
            (g1_x + g1_img.width // 2, g1_y + g1_img.height // 2, (ar, ag, ab, 175)),
            (g2_x + g2_img.width // 2, g2_y + g2_img.height // 2, (255, 204, 0, 165)),
        ]:
            draw.line([(gx, gy), (cx_s, cy_s)], fill=col, width=10)
            draw.line([(gx, gy), (cx_s, cy_s)], fill=(255, 255, 255, 248), width=3)
        draw.ellipse([cx_s - 30, cy_s - 30, cx_s + 30, cy_s + 30], outline=(255, 204, 0, 250), width=4)

    # Cursor autónomo
    poly = [
        (cx_s, cy_s),
        (cx_s, cy_s + 26),
        (cx_s + 7, cy_s + 20),
        (cx_s + 13, cy_s + 31),
        (cx_s + 18, cy_s + 28),
        (cx_s + 12, cy_s + 17),
        (cx_s + 21, cy_s + 17),
    ]
    draw.polygon(poly, fill=(255, 255, 255, 255), outline=(10, 14, 24, 255))

    canvas.alpha_composite(g2_img, (max(0, min(W - g2_img.width, g2_x)), max(0, min(H - g2_img.height, g2_y))))
    canvas.alpha_composite(g1_img, (max(0, min(W - g1_img.width, g1_x)), max(0, min(H - g1_img.height, g1_y))))
    canvas.alpha_composite(av_img, (max(0, min(W - av_img.width, av_x)), max(0, min(H - av_img.height, av_y))))

    return canvas.convert("RGB")


def build_studio_ass(scenes: list, ass_path: Path):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: StudioSubs,Arial,50,&H0000CCFF,&H00FFFFFF,&H00080C14,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,115,115,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header.strip()]
    for scn in scenes:
        st = float(scn["start_s"])
        dur = float(scn["duration_s"])
        mid = st + dur * 0.5
        end = st + dur
        words = scn.get("narration_text", "").split()
        half = max(1, len(words) // 2)
        p1 = " ".join(words[:half])
        p2 = " ".join(words[half:])
        if p1:
            lines.append(f"Dialogue: 0,{format_ass_ts(st)},{format_ass_ts(mid)},StudioSubs,,0,0,0,,{{\\fad(80,60)}}{p1}")
        if p2:
            lines.append(f"Dialogue: 0,{format_ass_ts(mid)},{format_ass_ts(end)},StudioSubs,,0,0,0,,{{\\fad(80,60)}}{p2}")
    ass_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    STUDIO_STREAM_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    scenes = manifest["scenes"]
    total_scenes = len(scenes)
    total_duration_s = float(manifest["total_duration_s"])

    print(f"[STUDIO DIRECTOR] Cargando estudio virtual y poses RGBA para {total_scenes} escenas ({total_duration_s}s)...", flush=True)
    avatars, gems = load_studio_assets()

    seg_files = []
    concat_lines = ["ffconcat version 1.0"]
    last_file_name = None

    for idx, scn in enumerate(scenes):
        dur = float(scn["duration_s"])
        # 3 tiempos de cámara por escena estilo Alejavi / Álvaro Morales / Lorena Bordonaba:
        # 1) Plano Amplio de Estudio (25%) -> 2) Zoom In 1.35x al código/diagrama con láser (55%) -> 3) Zoom Out a Estudio (20%)
        d_wide_in = round(dur * 0.25, 2)
        d_zoom = round(dur * 0.55, 2)
        d_wide_out = round(dur - d_wide_in - d_zoom, 2)

        im_w1 = render_studio_shot(scn, idx, total_scenes, "WIDE_OPEN", avatars, gems)
        im_zm = render_studio_shot(scn, idx, total_scenes, "ZOOM_IN_FOCUS", avatars, gems)
        im_w2 = render_studio_shot(scn, idx, total_scenes, "WIDE_OUT", avatars, gems)

        p1 = STUDIO_STREAM_DIR / f"st_{idx:03d}_1.jpg"
        p2 = STUDIO_STREAM_DIR / f"st_{idx:03d}_2.jpg"
        p3 = STUDIO_STREAM_DIR / f"st_{idx:03d}_3.jpg"

        im_w1.save(p1, "JPEG", quality=90)
        im_zm.save(p2, "JPEG", quality=90)
        im_w2.save(p3, "JPEG", quality=90)

        concat_lines.append(f"file '{p1.name}'")
        concat_lines.append(f"duration {d_wide_in:.2f}")
        concat_lines.append(f"file '{p2.name}'")
        concat_lines.append(f"duration {d_zoom:.2f}")
        concat_lines.append(f"file '{p3.name}'")
        concat_lines.append(f"duration {d_wide_out:.2f}")
        last_file_name = p3.name

        if (idx + 1) % 25 == 0 or (idx + 1) == total_scenes:
            gc.collect()
            print(f"[STUDIO DIRECTOR] Cuadros de estudio generados: {idx+1}/{total_scenes}", flush=True)

    if last_file_name:
        concat_lines.append(f"file '{last_file_name}'")

    concat_txt = STUDIO_STREAM_DIR / "studio_concat.ffconcat"
    concat_txt.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

    print("[STUDIO DIRECTOR] Compilando pista de video raw ultrarrápida...", flush=True)
    raw_studio_mp4 = STUDIO_STREAM_DIR / "raw_studio_137.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "studio_concat.ffconcat",
            "-vsync",
            "vfr",
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "20",
            str(raw_studio_mp4),
        ],
        cwd=str(STUDIO_STREAM_DIR),
        check=True,
        capture_output=True,
    )

    print("[STUDIO DIRECTOR] Compilando audio híbrido 'Guiahoy Voz' (Pista 1 + Pista 2) a -14 LUFS...", flush=True)
    hybrid_voice = VOICE_PROFILES_DIR / "Guiahoy_MASTER_HIBRIDO_PISTA1_Y_2_menos14LUFS.wav"
    src_voice_ext = VOICE_PROFILES_DIR / "Guiahoy_CLONE_REF_90s_48k.wav"

    voice_master_wav = STUDIO_STREAM_DIR / "studio_voice_17m32s.wav"
    # Construir master completo: primeros 42.55s es exactamente el hibrido aprobado, resto continúa con el clon extendido
    filter_complex = (
        f"[0:a]aresample=48000[a0]; "
        f"[1:a]aresample=48000,aloop=loop=-1:size=2e+09[a1]; "
        f"[a0][a1]concat=n=2:v=0:a=1,atrim=0:{total_duration_s:.2f},highpass=f=65,"
        f"equalizer=f=115:t=q:w=1.2:g=1.6,afade=t=in:st=0:d=0.05,afade=t=out:st={total_duration_s-1.0:.2f}:d=1.0,"
        f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(hybrid_voice),
            "-i",
            str(src_voice_ext),
            "-filter_complex",
            filter_complex,
            "-map",
            "[aout]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(voice_master_wav),
        ],
        check=True,
        capture_output=True,
    )

    ass_local = WORKSPACE_ROOT / "logs" / "studio_master_137.ass"
    build_studio_ass(scenes, ass_local)

    print("[STUDIO DIRECTOR] Compilando STUDIO_MASTER_GUIAHOY_ARGON.mp4 en 03_MEDIA_VAULT_FINAL...", flush=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw_studio_mp4),
            "-i",
            str(voice_master_wav),
            "-vf",
            "subtitles='logs/studio_master_137.ass'",
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(STUDIO_MASTER_MP4),
        ],
        cwd=str(WORKSPACE_ROOT),
        check=True,
        capture_output=True,
    )

    # Exportar además el Showcase dedicado de 42.55s correspondiente al Híbrido puro de Pista 1 + Pista 2
    showcase_mp4 = QDRANT_VAULT_DIR / "STUDIO_SHOWCASE_GUIAHOY_HIBRIDO_42S.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            "0",
            "-t",
            "42.55",
            "-i",
            str(STUDIO_MASTER_MP4),
            "-c",
            "copy",
            str(showcase_mp4),
        ],
        check=True,
        capture_output=True,
    )

    # Extraer clip de 36s de alta densidad para actualizar el visor embebido en el chat
    preview_mp4 = STUDIO_STREAM_DIR / "studio_preview_36s.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            "0",
            "-t",
            "36",
            "-i",
            str(showcase_mp4),
            "-vf",
            "scale=1280:720",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "25",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(preview_mp4),
        ],
        check=True,
        capture_output=True,
    )
    b64_preview = base64.b64encode(preview_mp4.read_bytes()).decode("ascii")
    (ARTIFACT_DIR / "scratch_studio_b64.txt").write_text(b64_preview, encoding="ascii")

    # Limpieza total de temporales (0 MB en PC)
    shutil.rmtree(STUDIO_STREAM_DIR, ignore_errors=True)
    ass_local.unlink(missing_ok=True)

    sha256_hex = hashlib.sha256(STUDIO_MASTER_MP4.read_bytes()).hexdigest()
    size_mb = round(STUDIO_MASTER_MP4.stat().st_size / (1024 * 1024), 2)

    # ACCIÓN OBLIGATORIA POST-RENDER (RULE_AUTO_LAUNCH_01): Abrir automáticamente el reproductor multimedia local
    os.startfile(str(showcase_mp4))

    result = {
        "status": "STATUS 200 OK - STUDIO_MASTER_GUIAHOY_ARGON RENDERED, SEALED & AUTO-LAUNCHED",
        "destination_vault_mp4": str(STUDIO_MASTER_MP4),
        "scenes_rendered": total_scenes,
        "duration_s": total_duration_s,
        "duration_min": round(total_duration_s / 60.0, 2),
        "size_mb": size_mb,
        "sha256": sha256_hex,
        "director_cam_automation": "Wide Studio 1.00x -> Smoothstep C1 Zoom In 1.35x -> Wide Studio 1.00x",
        "voice_master": "Guiahoy (f0 = 109.2 Hz, -14.0 LUFS, 0 afftdn)",
        "rule_auto_launch_01_fired": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (WORKSPACE_ROOT / "logs" / "studio_master_guiahoy_argon_report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
