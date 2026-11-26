"""
Phase 3 — Panel Choreography for Equipo de Agentes de IA (v2).
Source: C:\\Users\\ipane\\hbos-deploy\\INSUMOS-PANEL\\EQUIPO-DE-AGENTES-video-final.mp4
Boundaries: C:\\Users\\ipane\\hbos-deploy\\INSUMOS-PANEL\\tiempos.json

Rules enforced:
- PRE-DEBUG: RAM >= 1.0 GB + input SHA-256 verification.
- Panel appears at the START of each of the 10 modules (~3.0s) with current module
  highlighted and others dimmed, then exits with a 0.5s alpha crossfade over the
  live video (never fade to black, never hard cut).
- Rest of each module: animated neon images + narration ONLY (no panel).
- DO NOT TOUCH: narration audio (-c:a copy, 407.656s, 48kHz mono), images/animation,
  1920x1080 @ 30fps, avatar opening/closing.
- POST-DEBUG: 10 start stills + 10 mid-module stills + blackdetect + ffprobe QA
  + Drive Vault SHA-256 boundary verification.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")
REPO_ROOT = DEPLOY_ROOT / "hbos-vector-engine"
INSUMOS_DIR = DEPLOY_ROOT / "INSUMOS-PANEL"
SOURCE_MP4 = INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final.mp4"
TIEMPOS_JSON = INSUMOS_DIR / "tiempos.json"

EXPECTED_VIDEO_SHA256 = "817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88"
EXPECTED_TIEMPOS_SHA256 = "7893c247eae689e132c421e448db5383e1c43473e7533c0698811ffbfd91699c"

OUT_INSUMOS = INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v2.mp4"
OUT_REPO = REPO_ROOT / "EQUIPO-DE-AGENTES-video-final-v2.mp4"
OUT_VAULT = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\EQUIPO-DE-AGENTES-video-final-v2.mp4")

WORK_DIR = INSUMOS_DIR / "_work_panel_v2"
PANELS_DIR = WORK_DIR / "panels"
STILLS_DIR = INSUMOS_DIR / "qa_stills_v2"
QA_JSON = WORK_DIR / "phase3_qa_report.json"

# Exact 10 module start/end boundaries derived from tiempos.json segments
# Verified against the source video's own module headers.
MODULES = [
    {"id": 1, "seg_start": 1, "seg_end": 5, "label": "01 · De un Solo Modelo a un Equipo"},
    {"id": 2, "seg_start": 6, "seg_end": 11, "label": "02 · Agente Coordinador"},
    {"id": 3, "seg_start": 12, "seg_end": 16, "label": "03 · Agente Investigador"},
    {"id": 4, "seg_start": 17, "seg_end": 21, "label": "04 · Agente Ejecutor"},
    {"id": 5, "seg_start": 22, "seg_end": 26, "label": "05 · Agente Auditor"},
    {"id": 6, "seg_start": 27, "seg_end": 30, "label": "06 · Handoffs Estructurados"},
    {"id": 7, "seg_start": 31, "seg_end": 35, "label": "07 · Humano en el Bucle"},
    {"id": 8, "seg_start": 36, "seg_end": 38, "label": "08 · Empresas Antioquia y Colombia"},
    {"id": 9, "seg_start": 39, "seg_end": 41, "label": "09 · Impacto Operativo"},
    {"id": 10, "seg_start": 42, "seg_end": 45, "label": "10 · Hoja de Ruta y Cierre"},
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def free_ram_gb() -> float:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return round(stat.ullAvailPhys / (1024**3), 2)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
        if bold
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size=size)
    return ImageFont.load_default()


def compute_module_windows(tiempos_path: Path) -> list[dict[str, Any]]:
    data = json.loads(tiempos_path.read_text(encoding="utf-8"))
    segs = {s["seg"]: s for s in data["segmentos"]}
    total = float(data["total"])
    out: list[dict[str, Any]] = []
    for idx, mod in enumerate(MODULES):
        start_t = float(segs[mod["seg_start"]]["inicio"])
        if idx + 1 < len(MODULES):
            next_start = float(segs[MODULES[idx + 1]["seg_start"]]["inicio"])
        else:
            next_start = total
        end_t = next_start
        mid_t = round((start_t + end_t) / 2.0, 3)
        out.append({
            "id": mod["id"],
            "label": mod["label"],
            "start": round(start_t, 3),
            "end": round(end_t, 3),
            "duration": round(end_t - start_t, 3),
            "start_still_t": round(start_t + 1.50, 3),
            "mid_still_t": mid_t,
        })
    return out


def render_panel_png(active_id: int, out_path: Path) -> None:
    """Render 1920x1080 transparent overlay with left-side 10-module roadmap panel."""
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Panel box placed cleanly below module title banner (y>=206) and above bottom subtitles (y<=876),
    # on left side (x=48..548) completely clear of right-side Guillermo avatar.
    px0, py0, px1, py1 = 48, 206, 548, 876
    draw.rounded_rectangle([px0, py0, px1, py1], radius=16, fill=(10, 16, 32, 226), outline=(45, 212, 191, 215), width=2)

    # Header strip inside panel
    draw.rounded_rectangle([px0 + 2, py0 + 2, px1 - 2, py0 + 60], radius=14, fill=(15, 23, 42, 245))
    draw.line([(px0 + 18, py0 + 62), (px1 - 18, py0 + 62)], fill=(245, 183, 0, 220), width=2)

    f_hdr = load_font(20, bold=True)
    f_badge = load_font(16, bold=True)
    f_row_act = load_font(19, bold=True)
    f_row_dim = load_font(17, bold=False)

    draw.text((px0 + 20, py0 + 19), "RUTA DE LA CLASE", font=f_hdr, fill=(245, 183, 0, 255))
    badge_txt = f"MÓDULO {active_id:02d}/10"
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = bb[2] - bb[0]
    bh = bb[3] - bb[1]
    pad_x, pad_y = 14, 7
    bx1 = px1 - 16
    bx0 = bx1 - bw - 2 * pad_x
    by0 = py0 + 14
    by1 = by0 + bh + 2 * pad_y
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=9, fill=(245, 183, 0, 245))
    draw.text((bx0 + pad_x - bb[0], by0 + pad_y - bb[1]), badge_txt, font=f_badge, fill=(11, 16, 32, 255))

    row_top = py0 + 74
    row_h = 58
    for m in MODULES:
        mid = m["id"]
        y0 = row_top + (mid - 1) * row_h
        y1 = y0 + 50
        cy = (y0 + y1) // 2
        if mid == active_id:
            # Active module: full brightness + gold-amber border + glowing vector play arrow
            draw.rounded_rectangle(
                [px0 + 14, y0, px1 - 14, y1],
                radius=10,
                fill=(30, 58, 110, 248),
                outline=(245, 183, 0, 255),
                width=2,
            )
            draw.rounded_rectangle([px0 + 16, y0 + 8, px0 + 23, y1 - 8], radius=3, fill=(245, 183, 0, 255))
            draw.polygon([(px0 + 34, cy - 6), (px0 + 34, cy + 6), (px0 + 45, cy)], fill=(245, 183, 0, 255))
            draw.text((px0 + 56, y0 + 13), m["label"], font=f_row_act, fill=(255, 255, 255, 255))
        elif mid < active_id:
            # Completed modules: dimmed with crisp vector checkmark
            draw.rounded_rectangle(
                [px0 + 14, y0, px1 - 14, y1],
                radius=10,
                fill=(15, 23, 42, 130),
                outline=(51, 65, 85, 115),
                width=1,
            )
            draw.line([(px0 + 33, cy), (px0 + 38, cy + 5), (px0 + 46, cy - 5)], fill=(45, 212, 191, 210), width=2)
            draw.text((px0 + 56, y0 + 14), m["label"], font=f_row_dim, fill=(148, 163, 184, 195))
        else:
            # Upcoming modules: dimmed with subtle circle dot
            draw.rounded_rectangle(
                [px0 + 14, y0, px1 - 14, y1],
                radius=10,
                fill=(15, 23, 42, 108),
                outline=(51, 65, 85, 95),
                width=1,
            )
            draw.ellipse([px0 + 36, cy - 3, px0 + 42, cy + 3], fill=(100, 116, 139, 175))
            draw.text((px0 + 56, y0 + 14), m["label"], font=f_row_dim, fill=(115, 130, 152, 180))

    img.save(out_path, "PNG")


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\nSTDERR:\n{proc.stderr[-2000:]}")
    return proc


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # PRE-DEBUG: RAM gate + Input Hash gate
    ram_free = free_ram_gb()
    if ram_free < 1.0:
        raise RuntimeError(f"F6 RAM gate KO: {ram_free} GB < 1.0 GB")
    v_sha = sha256_file(SOURCE_MP4)
    t_sha = sha256_file(TIEMPOS_JSON)
    if v_sha != EXPECTED_VIDEO_SHA256:
        raise RuntimeError(f"Input video SHA-256 mismatch: {v_sha}")
    if t_sha != EXPECTED_TIEMPOS_SHA256:
        raise RuntimeError(f"Input tiempos.json SHA-256 mismatch: {t_sha}")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    STILLS_DIR.mkdir(parents=True, exist_ok=True)

    windows = compute_module_windows(TIEMPOS_JSON)

    # Render 10 panel PNGs
    panel_paths: list[Path] = []
    for w in windows:
        p = PANELS_DIR / f"panel_m{w['id']:02d}.png"
        render_panel_png(w["id"], p)
        panel_paths.append(p)

    # Build FFmpeg single-pass filter_complex:
    # - Input 0: source MP4 (video + clean audio copied untouched)
    # - Inputs 1..10: panel_m01.png .. panel_m10.png looped for 3.55s at 30fps
    # Module 1 (t=0.0): immediately visible 0.00->3.00, 0.50s alpha crossfade OUT 3.00->3.50
    # Modules 2..10 (t=t_k): 0.25s alpha fade IN t_k->t_k+0.25, hold, 0.50s alpha crossfade OUT t_k+3.00->t_k+3.50
    cmd: list[str] = ["ffmpeg", "-y", "-i", str(SOURCE_MP4)]
    for p in panel_paths:
        cmd.extend(["-framerate", "30", "-loop", "1", "-t", "3.55", "-i", str(p)])

    filter_parts: list[str] = ["[0:v]setpts=PTS-STARTPTS[base]"]
    prev_lbl = "base"
    for idx, w in enumerate(windows):
        in_idx = idx + 1
        t_start = w["start"]
        t_end = round(t_start + 3.55, 3)
        p_lbl = f"p{in_idx}"
        out_lbl = f"v{in_idx}" if idx + 1 < len(windows) else "vout"
        if w["id"] == 1:
            # Start immediately visible at t=0.000, fade alpha out over 0.50s starting at 3.00s
            filter_parts.append(
                f"[{in_idx}:v]fps=30,format=rgba,fade=t=out:st=3.00:d=0.50:alpha=1,setpts=PTS+{t_start:.3f}/TB[{p_lbl}]"
            )
        else:
            filter_parts.append(
                f"[{in_idx}:v]fps=30,format=rgba,fade=t=in:st=0.00:d=0.25:alpha=1,fade=t=out:st=3.00:d=0.50:alpha=1,setpts=PTS+{t_start:.3f}/TB[{p_lbl}]"
            )
        filter_parts.append(
            f"[{prev_lbl}][{p_lbl}]overlay=0:0:enable='between(t,{t_start:.3f},{t_end:.3f})':eof_action=pass[{out_lbl}]"
        )
        prev_lbl = out_lbl

    filter_complex = ";".join(filter_parts)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "copy",
        "-movflags", "+faststart",
        "-threads", "4",
        str(OUT_INSUMOS),
    ])

    print(f"[PRE-DEBUG OK] RAM free={ram_free} GB | Rendering {OUT_INSUMOS} ...")
    run_cmd(cmd)

    # Copy to repo (gitignored *.mp4) and Google Drive Vault (F10 hash-verified)
    OUT_VAULT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_INSUMOS, OUT_REPO)
    shutil.copy2(OUT_INSUMOS, OUT_VAULT)

    sha_insumos = sha256_file(OUT_INSUMOS)
    sha_repo = sha256_file(OUT_REPO)
    sha_vault = sha256_file(OUT_VAULT)
    if not (sha_insumos == sha_repo == sha_vault):
        raise RuntimeError(f"Boundary SHA-256 mismatch: {sha_insumos} / {sha_repo} / {sha_vault}")

    # POST-DEBUG QA: ffprobe + blackdetect + 20 stills + M1->M2 & M9->M10 transition strips
    probe = run_cmd([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(OUT_INSUMOS)
    ])
    pdata = json.loads(probe.stdout)
    vstream = next(s for s in pdata["streams"] if s["codec_type"] == "video")
    astream = next(s for s in pdata["streams"] if s["codec_type"] == "audio")
    dur = float(pdata["format"]["duration"])

    black_proc = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(OUT_INSUMOS), "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    black_hits = re.findall(r"black_start:[\d\.]+ black_end:[\d\.]+ black_duration:[\d\.]+", black_proc.stderr)

    # Export 10 start stills + 10 mid stills
    start_stills: list[str] = []
    mid_stills: list[str] = []
    for w in windows:
        sp = STILLS_DIR / f"start_m{w['id']:02d}.jpg"
        mp = STILLS_DIR / f"mid_m{w['id']:02d}.jpg"
        run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{w['start_still_t']:.3f}", "-i", str(OUT_INSUMOS), "-frames:v", "1", str(sp)])
        run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{w['mid_still_t']:.3f}", "-i", str(OUT_INSUMOS), "-frames:v", "1", str(mp)])
        start_stills.append(str(sp))
        mid_stills.append(str(mp))

    # Export transition filmstrips for M1->M2 (around 49.168s and 52.168s) & M9->M10 (around 381.808s and 384.808s)
    transition_frames = [
        ("tr_m1_m2_pre_48.8.jpg", 48.8),
        ("tr_m1_m2_in_49.6.jpg", 49.6),
        ("tr_m1_m2_hold_51.0.jpg", 51.0),
        ("tr_m1_m2_fadeout_52.4.jpg", 52.4),
        ("tr_m1_m2_gone_53.0.jpg", 53.0),
        ("tr_m9_m10_pre_381.3.jpg", 381.3),
        ("tr_m9_m10_in_382.2.jpg", 382.2),
        ("tr_m9_m10_hold_383.5.jpg", 383.5),
        ("tr_m9_m10_fadeout_385.0.jpg", 385.0),
        ("tr_m9_m10_gone_385.6.jpg", 385.6),
    ]
    for fname, tpos in transition_frames:
        run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{tpos:.3f}", "-i", str(OUT_INSUMOS), "-frames:v", "1", str(STILLS_DIR / fname)])

    qa_report = {
        "ram_pre_render_gb": ram_free,
        "duration_sec": round(dur, 3),
        "resolution": f"{vstream['width']}x{vstream['height']}",
        "fps": vstream["r_frame_rate"],
        "audio": f"{astream['sample_rate']} Hz {astream['channel_layout']} {astream['codec_name']}",
        "sha256": sha_insumos,
        "bytes": OUT_INSUMOS.stat().st_size,
        "blackdetect_hits": black_hits,
        "modules": windows,
        "stills_dir": str(STILLS_DIR),
        "start_stills_count": len(start_stills),
        "mid_stills_count": len(mid_stills),
        "qa_summary": {
            "duration_delta_sec": round(abs(dur - 407.656), 4),
            "black_intervals": len(black_hits),
            "boundary_sha256_match": True,
        },
    }
    QA_JSON.write_text(json.dumps(qa_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(qa_report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
