"""
Multi-format build script for Equipo de Agentes de IA v3 (2026-11-26).
Produces 3 deliverables from the same repaired audio master & timeline:
  1. EQUIPO-DE-AGENTES-video-final-v3.mp4       (1920x1080, 16:9)
  2. EQUIPO-DE-AGENTES-video-final-v3-9x16.mp4  (1080x1920, 9:16 vertical)
  3. EQUIPO-DE-AGENTES-video-final-v3-1x1.mp4   (1080x1080, 1:1 square)

Fixes applied (and nothing else changed):
1. Audio = INSUMOS-PANEL/NARRACION-EQUIPO-AGENTES-REPARADA.wav (untouched, 404.146s,
   48 kHz mono, -14.1 LUFS) + 10 module start times recomputed from master.
2. Presenter = ONLY INSUMOS-PANEL/avatar-transparente/ (5 official RGBA PNG poses).
3. Presenter framing = full body head-to-sneakers with top & bottom margins, ~70% of v2,
   ABOVE every header/title band, face uncovered & lit, NO mouth effect, gentle motion.

Stages:
  --stage p1     : P0 preflight + P1 audio/joins + tiempos_v3.json + 6 gate stills (16:9, 9:16, 1:1)
  --stage render : P2 render (all 3 or selected --formats) + P3 QA stills/ffprobe/blackdetect
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")
REPO_ROOT = DEPLOY_ROOT / "hbos-vector-engine"
INSUMOS_DIR = DEPLOY_ROOT / "INSUMOS-PANEL"

SOURCE_MP4 = INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final.mp4"
V2_MP4_PC = INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v2.mp4"
V2_MP4_VAULT = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\EQUIPO-DE-AGENTES-video-final-v2.mp4")
REPAIRED_WAV = INSUMOS_DIR / "NARRACION-EQUIPO-AGENTES-REPARADA.wav"
TIEMPOS_V1_JSON = INSUMOS_DIR / "tiempos.json"
AVATAR_DIR = INSUMOS_DIR / "avatar-transparente"
PANELS_DIR_16X9 = INSUMOS_DIR / "_work_panel_v2" / "panels"

WORK_V3 = INSUMOS_DIR / "_work_panel_v3"
PANELS_DIR_9X16 = WORK_V3 / "panels_9x16"
PANELS_DIR_1X1 = WORK_V3 / "panels_1x1"
STILLS_V3 = INSUMOS_DIR / "qa_stills_v3"
P0_JSON = WORK_V3 / "p0_preflight_v3.json"
TIEMPOS_V3_JSON = WORK_V3 / "tiempos_v3.json"
QA_V3_JSON = WORK_V3 / "phase3_qa_v3.json"

VAULT_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL")

FORMAT_TARGETS = {
    "16x9": {
        "filename": "EQUIPO-DE-AGENTES-video-final-v3.mp4",
        "size": (1920, 1080),
    },
    "9x16": {
        "filename": "EQUIPO-DE-AGENTES-video-final-v3-9x16.mp4",
        "size": (1080, 1920),
    },
    "1x1": {
        "filename": "EQUIPO-DE-AGENTES-video-final-v3-1x1.mp4",
        "size": (1080, 1080),
    },
}

EXPECTED_HASHES = {
    "source_v1_mp4": "817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88",
    "v2_mp4_pc": "2003aa6d76b4999e902676bde90bb305162b07e9bd45ea75be1f7966b219d3a3",
    "v2_mp4_vault": "2003aa6d76b4999e902676bde90bb305162b07e9bd45ea75be1f7966b219d3a3",
    "repaired_wav": "f533117e16e8579ac30c833b2f17f2cf5f77008e82dcb86a0be239e1a4ba86ac",
    "tiempos_v1_json": "7893c247eae689e132c421e448db5383e1c43473e7533c0698811ffbfd91699c",
}

POSE_FILES = [
    "guillermo_oficial_01_bienvenida.png",
    "guillermo_oficial_02_senala_derecha.png",
    "guillermo_oficial_03_pensativo_menton.png",
    "guillermo_oficial_04_enfasis_tecnico.png",
    "guillermo_oficial_05_saludo_cierre.png",
]

MODULES_DEF = [
    {"id": 1, "seg_start": 1, "seg_end": 5, "label": "01 · De un Solo Modelo a un Equipo", "banner": "EQUIPO DE AGENTES DE IA"},
    {"id": 2, "seg_start": 6, "seg_end": 11, "label": "02 · Agente Coordinador", "banner": "AGENTE COORDINADOR · DIRECTOR DE ORQUESTA"},
    {"id": 3, "seg_start": 12, "seg_end": 16, "label": "03 · Agente Investigador", "banner": "AGENTE INVESTIGADOR · EVIDENCIA PURA"},
    {"id": 4, "seg_start": 17, "seg_end": 21, "label": "04 · Agente Ejecutor", "banner": "AGENTE EJECUTOR · EL ARTESANO TÉCNICO"},
    {"id": 5, "seg_start": 22, "seg_end": 26, "label": "05 · Agente Auditor", "banner": "AGENTE AUDITOR · CONTROL DE CALIDAD"},
    {"id": 6, "seg_start": 27, "seg_end": 30, "label": "06 · Handoffs Estructurados", "banner": "HANDOFFS ESTRUCTURADOS · PRODUCCIÓN"},
    {"id": 7, "seg_start": 31, "seg_end": 35, "label": "07 · Humano en el Bucle", "banner": "HUMANO EN EL BUCLE · EL LÍDER APRUEBA"},
    {"id": 8, "seg_start": 36, "seg_end": 38, "label": "08 · Empresas Antioquia y Colombia", "banner": "EMPRESAS DE ANTIOQUIA Y COLOMBIA"},
    {"id": 9, "seg_start": 39, "seg_end": 41, "label": "09 · Impacto Operativo", "banner": "IMPACTO OPERATIVO · DE SEMANA A MINUTOS"},
    {"id": 10, "seg_start": 42, "seg_end": 45, "label": "10 · Hoja de Ruta y Cierre", "banner": "GUÍA HOY · HASTA LA PRÓXIMA LECCIÓN"},
]

NEW_MODULE_STARTS = [0.000, 50.270, 99.030, 144.840, 191.620, 238.140, 278.260, 321.030, 353.290, 378.520]
OPENING_END_T = 6.000
CLOSING_START_T = 387.680


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


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\nSTDERR:\n{proc.stderr[-2500:]}")
    return proc


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


def verify_p0() -> dict[str, Any]:
    WORK_V3.mkdir(parents=True, exist_ok=True)
    PANELS_DIR_9X16.mkdir(parents=True, exist_ok=True)
    PANELS_DIR_1X1.mkdir(parents=True, exist_ok=True)
    STILLS_V3.mkdir(parents=True, exist_ok=True)

    ram = free_ram_gb()
    if ram < 1.0:
        raise RuntimeError(f"P0 RAM gate KO: {ram} GB < 1.0 GB")

    actual_hashes = {
        "source_v1_mp4": sha256_file(SOURCE_MP4),
        "v2_mp4_pc": sha256_file(V2_MP4_PC),
        "v2_mp4_vault": sha256_file(V2_MP4_VAULT),
        "repaired_wav": sha256_file(REPAIRED_WAV),
        "tiempos_v1_json": sha256_file(TIEMPOS_V1_JSON),
    }
    for key, exp in EXPECTED_HASHES.items():
        if actual_hashes[key] != exp:
            raise RuntimeError(f"P0 hash mismatch for {key}: {actual_hashes[key]} != {exp}")

    png_checks = []
    for name in POSE_FILES:
        p = AVATAR_DIR / name
        im = Image.open(p)
        arr = np.array(im)
        amin, amax = int(arr[:, :, 3].min()), int(arr[:, :, 3].max())
        if im.mode != "RGBA" or amin != 0 or amax != 255:
            raise RuntimeError(f"Pose {name} alpha check failed: mode={im.mode}, min={amin}, max={amax}")
        png_checks.append({"file": name, "size": list(im.size), "alpha_min": amin, "alpha_max": amax, "sha256": sha256_file(p)})

    git_stat = subprocess.check_output(["git", "-C", str(REPO_ROOT), "status", "-s"], text=True, encoding="utf-8", errors="replace").splitlines()
    p0_report = {
        "phase": "P0_PREFLIGHT_V3",
        "gate": "OK",
        "ram_free_gb": ram,
        "protected_and_input_hashes": actual_hashes,
        "avatar_poses": png_checks,
        "pending_git_lines": len(git_stat),
    }
    P0_JSON.write_text(json.dumps(p0_report, indent=2, ensure_ascii=False), encoding="utf-8")
    return p0_report


def measure_audio_and_joins() -> dict[str, Any]:
    probe = run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(REPAIRED_WAV)])
    pdata = json.loads(probe.stdout)
    astream = pdata["streams"][0]
    dur = float(pdata["format"]["duration"])

    lufs_proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(REPAIRED_WAV), "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    integrated_lufs = None
    for line in lufs_proc.stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            try:
                integrated_lufs = float(line.split("I:")[1].split("LUFS")[0].strip())
            except Exception:
                pass

    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(REPAIRED_WAV), "-ac", "1", "-ar", "48000", "-f", "f32le", "-"])
    y = np.frombuffer(raw, dtype=np.float32)
    hop = 480
    n_frames = len(y) // hop
    rms = np.sqrt(np.mean(y[: n_frames * hop].reshape(n_frames, hop) ** 2, axis=1) + 1e-12)
    db = 20.0 * np.log10(rms)

    join_targets = [
        ("J1 (M01->M02)", 49.55, 50.30),
        ("J2 (M02->M03)", 98.45, 99.10),
        ("J3 (M03->M04)", 144.20, 144.90),
        ("J4 (M04->M05)", 190.70, 191.65),
        ("J5 (M05->M06)", 237.55, 238.20),
        ("J6 (M06->M07)", 277.70, 278.32),
        ("J7 (M07->M08)", 320.28, 321.05),
        ("J8 (M08->M09)", 352.40, 353.35),
        ("J9 (M09->M10)", 377.95, 378.58),
    ]
    joins_measured = []
    for name, lo_t, hi_t in join_targets:
        i0, i1 = int(lo_t * 100), int(hi_t * 100)
        seg_db = db[i0:i1]
        quiet_mask = seg_db < -38.0
        pause_ms = int(np.sum(quiet_mask) * 10)
        mean_db = round(float(np.mean(seg_db[quiet_mask])) if np.any(quiet_mask) else float(np.mean(seg_db)), 1)
        joins_measured.append({"join": name, "window_sec": [lo_t, hi_t], "pause_ms_lt_38dbfs": pause_ms, "floor_dbfs": mean_db})

    v1_data = json.loads(TIEMPOS_V1_JSON.read_text(encoding="utf-8"))
    segs = {s["seg"]: s for s in v1_data["segmentos"]}
    modules = []
    subtitles_v3 = []
    for idx, mod in enumerate(MODULES_DEF):
        orig_s = float(segs[mod["seg_start"]]["inicio"])
        orig_e = float(segs[MODULES_DEF[idx + 1]["seg_start"]]["inicio"]) if idx + 1 < len(MODULES_DEF) else float(v1_data["total"])
        new_s = NEW_MODULE_STARTS[idx]
        new_e = NEW_MODULE_STARTS[idx + 1] if idx + 1 < len(NEW_MODULE_STARTS) else dur
        scale = (new_e - new_s) / (orig_e - orig_s)
        modules.append({
            "id": mod["id"],
            "label": mod["label"],
            "banner": mod["banner"],
            "orig_start": round(orig_s, 3),
            "orig_end": round(orig_e, 3),
            "orig_dur": round(orig_e - orig_s, 3),
            "new_start": round(new_s, 3),
            "new_end": round(new_e, 3),
            "new_dur": round(new_e - new_s, 3),
            "start_still_t": round(new_s + 1.50, 3),
            "mid_still_t": round((new_s + new_e) / 2.0, 3),
        })
        for sid in range(mod["seg_start"], mod["seg_end"] + 1):
            s = segs[sid]
            st_v3 = new_s + (float(s["inicio"]) - orig_s) * scale
            en_v3 = new_s + (float(s["fin"]) - orig_s) * scale
            subtitles_v3.append({
                "seg": sid,
                "mod_id": mod["id"],
                "inicio": round(st_v3, 3),
                "fin": round(en_v3, 3),
                "texto": s["texto"],
            })

    timing_doc = {
        "master_wav": str(REPAIRED_WAV),
        "master_sha256": sha256_file(REPAIRED_WAV),
        "duration_sec": round(dur, 3),
        "sample_rate": int(astream["sample_rate"]),
        "channels": int(astream["channels"]),
        "integrated_lufs": integrated_lufs,
        "opening_presenter_window": [0.0, OPENING_END_T],
        "closing_presenter_window": [CLOSING_START_T, round(dur, 3)],
        "joins_measured": joins_measured,
        "modules": modules,
        "subtitles_v3": subtitles_v3,
    }
    TIEMPOS_V3_JSON.write_text(json.dumps(timing_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return json.loads(TIEMPOS_V3_JSON.read_text(encoding="utf-8"))


def erase_old_avatar_opening(frame_bgr: np.ndarray) -> np.ndarray:
    """
    Surgically remove baked-in old avatar on opening scene (x~1515..1805, y~155..1030)
    without rectangular glow seams or touching title text, lamp, monitors, or subtitles.
    """
    out = frame_bgr.copy()

    # 1. Banner strip (y=128..204, x=1555..1765): smooth horizontal blend of clean dark banner
    by0, by1, bx0, bx1 = 128, 204, 1555, 1765
    lcol = np.mean(frame_bgr[by0:by1, bx0 - 15 : bx0, :].astype(np.float32), axis=1, keepdims=True)
    rcol = np.mean(frame_bgr[by0:by1, bx1 : bx1 + 15, :].astype(np.float32), axis=1, keepdims=True)
    bt = np.linspace(0.0, 1.0, bx1 - bx0, dtype=np.float32)[None, :, None]
    bpatch = lcol * (1.0 - bt) + rcol * bt
    bw = np.ones((1, bx1 - bx0, 1), dtype=np.float32)
    bw[:, :16, :] = np.linspace(0.0, 1.0, 16)[None, :, None]
    bw[:, -16:, :] = np.linspace(1.0, 0.0, 16)[None, :, None]
    out[by0:by1, bx0:bx1] = np.clip(bpatch * bw + out[by0:by1, bx0:bx1].astype(np.float32) * (1.0 - bw), 0, 255).astype(np.uint8)

    # 2. Upper wall & diagonal ceiling trim (y=202..638, x=1475..1828):
    # Mirror symmetric clean left wall (x=92..445)
    y0, y1, x0, x1 = 202, 638, 1475, 1828
    src = frame_bgr[y0:y1, 1920 - x1 : 1920 - x0][:, ::-1].astype(np.float32)
    dst = out[y0:y1, x0:x1].astype(np.float32)
    alpha = np.ones((1, x1 - x0, 1), dtype=np.float32)
    alpha[:, :18, :] = np.linspace(0.0, 1.0, 18)[None, :, None]
    alpha[:, -18:, :] = np.linspace(1.0, 0.0, 18)[None, :, None]
    valpha = np.ones((y1 - y0, 1, 1), dtype=np.float32)
    valpha[:10, :, :] = np.linspace(0.0, 1.0, 10)[:, None, None]
    w = alpha * valpha
    out[y0:y1, x0:x1] = np.clip(src * w + dst * (1.0 - w), 0, 255).astype(np.uint8)

    # 3. Hand & legs behind lower-right wall (y=585..922):
    # Replace narrow old-hand overhang (x=1512..1560, y=585..705) with clean neighboring wall,
    # then blend clean right wall slats (x=1825..1895) smoothly across x=1565..1825.
    hy0, hy1, hx0, hx1 = 585, 705, 1512, 1565
    h_src = out[hy0:hy1, 1495:1512].mean(axis=1, keepdims=True)
    h_patch = np.repeat(h_src, hx1 - hx0, axis=1)
    hw = np.ones((hy1 - hy0, hx1 - hx0, 1), dtype=np.float32)
    hw[:, :10, :] *= np.linspace(0.0, 1.0, 10)[None, :, None]
    hw[:12, :, :] *= np.linspace(0.0, 1.0, 12)[:, None, None]
    hw[-12:, :, :] *= np.linspace(1.0, 0.0, 12)[:, None, None]
    out[hy0:hy1, hx0:hx1] = np.clip(h_patch * hw + out[hy0:hy1, hx0:hx1].astype(np.float32) * (1.0 - hw), 0, 255).astype(np.uint8)

    ly0, ly1, lx0, lx1 = 635, 922, 1565, 1825
    clean_slat = frame_bgr[ly0:ly1, 1825:1895, :].astype(np.float32)
    rep = np.tile(clean_slat, (1, 4, 1))[:, : lx1 - lx0, :]
    lw = np.ones((ly1 - ly0, lx1 - lx0, 1), dtype=np.float32)
    lw[:, :55, :] *= np.linspace(0.0, 1.0, 55)[None, :, None]
    lw[:, -18:, :] *= np.linspace(1.0, 0.0, 18)[None, :, None]
    lw[:55, :, :] *= np.linspace(0.0, 1.0, 55)[:, None, None]
    out[ly0:ly1, lx0:lx1] = np.clip(rep * lw + out[ly0:ly1, lx0:lx1].astype(np.float32) * (1.0 - lw), 0, 255).astype(np.uint8)

    # 4. Shoes/ankles on far-right subtitle scrim (keep "mesa de" ending at x~1592 completely untouched)
    for sy0, sy1, sx0, sx1 in [(922, 975, 1598, 1835), (975, 1075, 1525, 1835)]:
        rref = np.median(frame_bgr[sy0:sy1, 1840:1895, :].astype(np.float32), axis=1, keepdims=True)
        lref = np.median(frame_bgr[sy0:sy1, sx0 - 10 : sx0, :].astype(np.float32), axis=1, keepdims=True)
        st = np.linspace(0.0, 1.0, sx1 - sx0, dtype=np.float32)[None, :, None]
        spatch = lref * (1.0 - st) + rref * st
        sw = np.ones((sy1 - sy0, sx1 - sx0, 1), dtype=np.float32)
        sw[:, :18, :] *= np.linspace(0.0, 1.0, 18)[None, :, None]
        sw[:, -18:, :] *= np.linspace(1.0, 0.0, 18)[None, :, None]
        out[sy0:sy1, sx0:sx1] = np.clip(spatch * sw + out[sy0:sy1, sx0:sx1].astype(np.float32) * (1.0 - sw), 0, 255).astype(np.uint8)
    return out


def extract_clean_closing_ref() -> np.ndarray:
    cap = cv2.VideoCapture(str(SOURCE_MP4))
    cap.set(cv2.CAP_PROP_POS_MSEC, 390500.0)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("Failed reading clean closing reference frame at t=390.5s")
    return frame


def erase_old_avatar_closing(frame_bgr: np.ndarray, clean_ref: np.ndarray) -> np.ndarray:
    out = frame_bgr.copy()
    y0, y1, x0, x1 = 130, 865, 1465, 1900
    src = clean_ref[y0:y1, x0:x1].astype(np.float32)
    dst = out[y0:y1, x0:x1].astype(np.float32)
    w = np.ones((y1 - y0, x1 - x0, 1), dtype=np.float32)
    w[:, :40, :] = np.linspace(0.0, 1.0, 40)[None, :, None]
    w[:16, :, :] *= np.linspace(0.0, 1.0, 16)[:, None, None]
    out[y0:y1, x0:x1] = np.clip(src * w + dst * (1.0 - w), 0, 255).astype(np.uint8)

    sy0, sy1, sx0, sx1 = 865, 1055, 1568, 1875
    src_low = clean_ref[sy0:sy1, sx0:sx1].astype(np.float32)
    ratio = (np.mean(frame_bgr[sy0:sy1, 1875:1910, :].astype(np.float32), axis=1, keepdims=True) + 1.0) / (
        np.mean(clean_ref[sy0:sy1, 1875:1910, :].astype(np.float32), axis=1, keepdims=True) + 1.0
    )
    ratio = np.clip(ratio, 0.30, 1.0)
    src_low_scrimmed = src_low * ratio
    sw = np.ones((sy1 - sy0, sx1 - sx0, 1), dtype=np.float32)
    sw[:, :22, :] *= np.linspace(0.0, 1.0, 22)[None, :, None]
    sw[:, -20:, :] *= np.linspace(1.0, 0.0, 20)[None, :, None]
    out[sy0:sy1, sx0:sx1] = np.clip(src_low_scrimmed * sw + out[sy0:sy1, sx0:sx1].astype(np.float32) * (1.0 - sw), 0, 255).astype(np.uint8)
    return out


def load_pose_scaled(pose_name: str, target_h: int) -> np.ndarray:
    im = Image.open(AVATAR_DIR / pose_name).convert("RGBA")
    w, h = im.size
    new_w = max(1, int(round(w * (target_h / h))))
    resized = im.resize((new_w, target_h), Image.Resampling.LANCZOS)
    return cv2.cvtColor(np.array(resized), cv2.COLOR_RGBA2BGRA)


def composite_presenter(frame_bgr: np.ndarray, pose_bgra: np.ndarray, cx: int, y_top: int, t_local: float, opacity: float = 1.0) -> np.ndarray:
    if opacity <= 0.0:
        return frame_bgr
    ph, pw = pose_bgra.shape[:2]
    dx = 1.6 * math.sin(2.0 * math.pi * 0.22 * t_local)
    dy = 2.0 * math.sin(2.0 * math.pi * 0.35 * t_local)
    M = np.float32([[1.0, 0.0, dx], [0.0, 1.0, dy]])
    moved = cv2.warpAffine(pose_bgra, M, (pw, ph), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    x0, y0 = cx - pw // 2, y_top
    x1, y1 = x0 + pw, y0 + ph
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(frame_bgr.shape[1], x1), min(frame_bgr.shape[0], y1)
    if fx0 >= fx1 or fy0 >= fy1:
        return frame_bgr

    px0, py0 = fx0 - x0, fy0 - y0
    px1, py1 = px0 + (fx1 - fx0), py0 + (fy1 - fy0)
    roi_fg = moved[py0:py1, px0:px1, :3].astype(np.float32)
    alpha = (moved[py0:py1, px0:px1, 3:4].astype(np.float32) / 255.0) * opacity
    roi_bg = frame_bgr[fy0:fy1, fx0:fx1].astype(np.float32)

    out = frame_bgr.copy()
    out[fy0:fy1, fx0:fx1] = np.clip(roi_fg * alpha + roi_bg * (1.0 - alpha), 0, 255).astype(np.uint8)
    return out


def alpha_blend_bgra(frame_bgr: np.ndarray, overlay_bgra: np.ndarray, opacity: float) -> np.ndarray:
    if opacity <= 0.0:
        return frame_bgr
    alpha = (overlay_bgra[:, :, 3:4].astype(np.float32) / 255.0) * opacity
    fg = overlay_bgra[:, :, :3].astype(np.float32)
    bg = frame_bgr.astype(np.float32)
    return np.clip(fg * alpha + bg * (1.0 - alpha), 0, 255).astype(np.uint8)


def render_format_panel_png(active_id: int, out_path: Path, box_w: int, box_h: int) -> None:
    """Render compact transparent panel card sized for 9:16 or 1:1 legibility."""
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, box_w - 1, box_h - 1], radius=16, fill=(10, 16, 32, 232), outline=(45, 212, 191, 225), width=2)
    hdr_h = int(box_h * 0.105)
    draw.rounded_rectangle([2, 2, box_w - 3, hdr_h], radius=14, fill=(15, 23, 42, 248))
    draw.line([(14, hdr_h + 2), (box_w - 14, hdr_h + 2)], fill=(245, 183, 0, 230), width=2)

    f_hdr = load_font(max(16, int(box_w * 0.042)), bold=True)
    f_badge = load_font(max(14, int(box_w * 0.034)), bold=True)
    f_act = load_font(max(15, int(box_w * 0.037)), bold=True)
    f_dim = load_font(max(14, int(box_w * 0.033)), bold=False)

    draw.text((16, int(hdr_h * 0.28)), "RUTA DE LA CLASE", font=f_hdr, fill=(245, 183, 0, 255))
    btxt = f"MÓD. {active_id:02d}/10"
    bb = draw.textbbox((0, 0), btxt, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx1 = box_w - 14
    bx0 = bx1 - bw - 20
    by0 = int((hdr_h - bh - 10) // 2)
    by1 = by0 + bh + 10
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(245, 183, 0, 245))
    draw.text((bx0 + 10 - bb[0], by0 + 5 - bb[1]), btxt, font=f_badge, fill=(11, 16, 32, 255))

    row_top = hdr_h + 10
    avail_h = box_h - row_top - 10
    row_h = avail_h / 10.0
    for m in MODULES_DEF:
        mid = m["id"]
        y0 = int(round(row_top + (mid - 1) * row_h))
        y1 = int(round(y0 + row_h - 6))
        cy = (y0 + y1) // 2
        if mid == active_id:
            draw.rounded_rectangle([12, y0, box_w - 12, y1], radius=9, fill=(30, 58, 110, 248), outline=(245, 183, 0, 255), width=2)
            draw.rounded_rectangle([14, y0 + 6, 20, y1 - 6], radius=2, fill=(245, 183, 0, 255))
            draw.polygon([(28, cy - 5), (28, cy + 5), (38, cy)], fill=(245, 183, 0, 255))
            draw.text((46, y0 + max(5, (y1 - y0 - 20) // 2)), m["label"], font=f_act, fill=(255, 255, 255, 255))
        elif mid < active_id:
            draw.rounded_rectangle([12, y0, box_w - 12, y1], radius=9, fill=(15, 23, 42, 140), outline=(51, 65, 85, 120), width=1)
            draw.line([(27, cy), (32, cy + 4), (39, cy - 4)], fill=(45, 212, 191, 215), width=2)
            draw.text((46, y0 + max(5, (y1 - y0 - 18) // 2)), m["label"], font=f_dim, fill=(148, 163, 184, 200))
        else:
            draw.rounded_rectangle([12, y0, box_w - 12, y1], radius=9, fill=(15, 23, 42, 115), outline=(51, 65, 85, 95), width=1)
            draw.ellipse([30, cy - 3, 35, cy + 2], fill=(100, 116, 139, 180))
            draw.text((46, y0 + max(5, (y1 - y0 - 18) // 2)), m["label"], font=f_dim, fill=(120, 136, 158, 185))
    img.save(out_path, "PNG")


def ensure_multiformat_panels() -> None:
    for m in MODULES_DEF:
        mid = m["id"]
        render_format_panel_png(mid, PANELS_DIR_9X16 / f"panel_m{mid:02d}.png", box_w=524, box_h=570)
        render_format_panel_png(mid, PANELS_DIR_1X1 / f"panel_m{mid:02d}.png", box_w=444, box_h=690)


def active_module_at(t: float, modules: list[dict[str, Any]]) -> dict[str, Any]:
    for m in modules:
        if m["new_start"] <= t < m["new_end"]:
            return m
    return modules[-1]


def active_subtitle_at(t: float, subs: list[dict[str, Any]]) -> str:
    for s in subs:
        if s["inicio"] <= t <= s["fin"]:
            return s["texto"]
    return ""


def panel_opacity_for(t: float, modules: list[dict[str, Any]]) -> tuple[int | None, float]:
    for m in modules:
        ts = m["new_start"]
        if ts <= t <= ts + 3.55:
            dt = t - ts
            if m["id"] == 1:
                op = 1.0 if dt <= 3.0 else max(0.0, 1.0 - (dt - 3.0) / 0.50)
            else:
                if dt < 0.25:
                    op = dt / 0.25
                elif dt <= 3.00:
                    op = 1.0
                else:
                    op = max(0.0, 1.0 - (dt - 3.00) / 0.50)
            return m["id"], op
    return None, 0.0


def build_header_cache_pil(fmt: str, banner_text: str) -> np.ndarray:
    """Pre-render crisp header + brand bar for 9:16 (1080x208) or 1:1 (1080x140) as BGRA."""
    if fmt == "9x16":
        w, h = 1080, 208
        im = Image.new("RGBA", (w, h), (9, 14, 26, 245))
        d = ImageDraw.Draw(im)
        f_brand = load_font(34, bold=True)
        f_tag = load_font(22, bold=False)
        f_mod = load_font(30, bold=True)
        d.text((34, 28), "GUÍA HOY", font=f_brand, fill=(245, 183, 0, 255))
        d.text((665, 36), "Avanza e Inventa con IA", font=f_tag, fill=(203, 213, 225, 255))
        d.line([(0, 102), (w, 102)], fill=(245, 183, 0, 255), width=3)
        d.rectangle([0, 105, w, h], fill=(15, 23, 42, 235))
        d.text((34, 130), banner_text, font=f_mod, fill=(255, 255, 255, 255))
        d.rectangle([34, 178, 128, 185], fill=(220, 38, 38, 255))
    else:
        w, h = 1080, 140
        im = Image.new("RGBA", (w, h), (9, 14, 26, 245))
        d = ImageDraw.Draw(im)
        f_brand = load_font(28, bold=True)
        f_tag = load_font(19, bold=False)
        f_mod = load_font(25, bold=True)
        d.text((28, 18), "GUÍA HOY", font=f_brand, fill=(245, 183, 0, 255))
        d.text((620, 24), "Avanza e Inventa con IA · CERO COSTO", font=f_tag, fill=(203, 213, 225, 255))
        d.line([(0, 68), (w, 68)], fill=(245, 183, 0, 255), width=3)
        d.rectangle([0, 71, w, h], fill=(15, 23, 42, 235))
        d.text((28, 86), banner_text, font=f_mod, fill=(255, 255, 255, 255))
        d.rectangle([28, 122, 106, 127], fill=(220, 38, 38, 255))
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def render_subtitle_box(text: str, box_w: int, box_h: int, font_size: int, wrap_chars: int) -> np.ndarray:
    im = Image.new("RGBA", (box_w, box_h), (8, 12, 24, 222))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, box_w - 1, box_h - 1], radius=16, fill=(8, 12, 24, 228), outline=(45, 212, 191, 110), width=2)
    if text:
        f = load_font(font_size, bold=True)
        lines = textwrap.wrap(text, width=wrap_chars)[:4]
        line_h = int(font_size * 1.28)
        total_h = len(lines) * line_h
        y = max(12, (box_h - total_h) // 2)
        for line in lines:
            bb = d.textbbox((0, 0), line, font=f)
            lw = bb[2] - bb[0]
            x = max(18, (box_w - lw) // 2 - bb[0])
            d.text((x + 2, y + 2), line, font=f, fill=(0, 0, 0, 220))
            d.text((x, y), line, font=f, fill=(255, 255, 255, 255))
            y += line_h
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def paste_bgra_rect(canvas_bgr: np.ndarray, overlay_bgra: np.ndarray, x0: int, y0: int, opacity: float = 1.0) -> np.ndarray:
    if opacity <= 0.0:
        return canvas_bgr
    oh, ow = overlay_bgra.shape[:2]
    roi_bg = canvas_bgr[y0 : y0 + oh, x0 : x0 + ow].astype(np.float32)
    roi_fg = overlay_bgra[:, :, :3].astype(np.float32)
    a = (overlay_bgra[:, :, 3:4].astype(np.float32) / 255.0) * opacity
    canvas_bgr[y0 : y0 + oh, x0 : x0 + ow] = np.clip(roi_fg * a + roi_bg * (1.0 - a), 0, 255).astype(np.uint8)
    return canvas_bgr


def compose_frame_16x9(
    clean_frame: np.ndarray,
    t: float,
    modules: list[dict[str, Any]],
    panels: dict[int, np.ndarray],
    poses: dict[str, np.ndarray],
) -> np.ndarray:
    out = clean_frame.copy()
    pid, pop = panel_opacity_for(t, modules)
    if pid is not None and pop > 0.0:
        out = alpha_blend_bgra(out, panels[pid], pop)

    if t < OPENING_END_T:
        fade_out = 1.0 if t <= OPENING_END_T - 0.40 else max(0.0, (OPENING_END_T - t) / 0.40)
        if t < 3.0:
            out = composite_presenter(out, poses["open1_16x9"], cx=1655, y_top=246, t_local=t, opacity=fade_out)
        elif t < 3.4:
            mix = (t - 3.0) / 0.4
            out = composite_presenter(out, poses["open1_16x9"], cx=1655, y_top=246, t_local=t, opacity=(1.0 - mix) * fade_out)
            out = composite_presenter(out, poses["open2_16x9"], cx=1655, y_top=246, t_local=t, opacity=mix * fade_out)
        else:
            out = composite_presenter(out, poses["open2_16x9"], cx=1655, y_top=246, t_local=t, opacity=fade_out)
    elif t >= CLOSING_START_T:
        dt_c = t - CLOSING_START_T
        fade_in = min(1.0, dt_c / 0.45)
        out = composite_presenter(out, poses["close_16x9"], cx=1670, y_top=222, t_local=dt_c, opacity=fade_in)
    return out


def compose_frame_9x16(
    clean_frame: np.ndarray,
    t: float,
    modules: list[dict[str, Any]],
    panels_9x16: dict[int, np.ndarray],
    headers_9x16: dict[int, np.ndarray],
    poses: dict[str, np.ndarray],
    sub_cache: dict[str, np.ndarray],
    subs_v3: list[dict[str, Any]],
) -> np.ndarray:
    mod = active_module_at(t, modules)
    # 1. Ambient blurred background 1080x1920 from clean scene region (y=198..842, above 4-line 16:9 subtitles)
    scene_clean = clean_frame[198:842, 200:1720]  # 1520x644 clean artwork
    amb_small = cv2.resize(scene_clean, (135, 240), interpolation=cv2.INTER_AREA)
    amb_small = cv2.GaussianBlur(amb_small, (9, 9), 0)
    amb = cv2.resize(amb_small, (1080, 1920), interpolation=cv2.INTER_LINEAR)
    canvas = (amb.astype(np.float32) * 0.28).astype(np.uint8)

    # 2. Live hero visual viewport (y=278..858): 1200x644 clean center crop -> 1080x580 (zero subtitle bleed)
    hero_src = clean_frame[198:842, 360:1560]
    hero = cv2.resize(hero_src, (1080, 580), interpolation=cv2.INTER_LANCZOS4)
    hy0 = 278
    canvas[hy0 : hy0 + 580, 0:1080] = hero
    cv2.line(canvas, (0, hy0), (1080, hy0), (45, 212, 191), 2)
    cv2.line(canvas, (0, hy0 + 580), (1080, hy0 + 580), (245, 183, 0), 2)

    # 3. Top header bar (ABOVE hero; presenter is below y=925 so never occluded!)
    paste_bgra_rect(canvas, headers_9x16[mod["id"]], 0, 0, 1.0)

    # 4. Panel in studio zone (y=945..1515): left on M1 (when opening presenter is on right), centered on M2..M10
    pid, pop = panel_opacity_for(t, modules)
    if pid is not None and pop > 0.0:
        px = 24 if pid == 1 else 278
        paste_bgra_rect(canvas, panels_9x16[pid], px, 945, pop)

    # 5. Official transparent presenter ABOVE all bands (full body head-to-sneakers with clear margins)
    if t < OPENING_END_T:
        fade_out = 1.0 if t <= OPENING_END_T - 0.40 else max(0.0, (OPENING_END_T - t) / 0.40)
        if t < 3.0:
            canvas = composite_presenter(canvas, poses["open1_9x16"], cx=815, y_top=942, t_local=t, opacity=fade_out)
        elif t < 3.4:
            mix = (t - 3.0) / 0.4
            canvas = composite_presenter(canvas, poses["open1_9x16"], cx=815, y_top=942, t_local=t, opacity=(1.0 - mix) * fade_out)
            canvas = composite_presenter(canvas, poses["open2_9x16"], cx=815, y_top=942, t_local=t, opacity=mix * fade_out)
        else:
            canvas = composite_presenter(canvas, poses["open2_9x16"], cx=815, y_top=942, t_local=t, opacity=fade_out)
    elif t >= CLOSING_START_T:
        dt_c = t - CLOSING_START_T
        fade_in = min(1.0, dt_c / 0.45)
        canvas = composite_presenter(canvas, poses["close_9x16"], cx=540, y_top=922, t_local=dt_c, opacity=fade_in)

    # 6. Dedicated phone-legible subtitle card (y=1558..1862)
    stxt = active_subtitle_at(t, subs_v3)
    skey = f"9x16:{stxt}"
    if skey not in sub_cache:
        sub_cache[skey] = render_subtitle_box(stxt, box_w=1016, box_h=300, font_size=36, wrap_chars=38)
    if stxt:
        paste_bgra_rect(canvas, sub_cache[skey], 32, 1558, 1.0)
    return canvas


def compose_frame_1x1(
    clean_frame: np.ndarray,
    t: float,
    modules: list[dict[str, Any]],
    panels_1x1: dict[int, np.ndarray],
    headers_1x1: dict[int, np.ndarray],
    poses: dict[str, np.ndarray],
    sub_cache: dict[str, np.ndarray],
    subs_v3: list[dict[str, Any]],
) -> np.ndarray:
    mod = active_module_at(t, modules)
    # 1. Clean artwork background for 1:1 (y=198..842, above 4-line 16:9 subtitles)
    scene_clean = clean_frame[198:842, 270:1530]  # 1260x644 clean artwork
    amb_small = cv2.resize(scene_clean, (135, 135), interpolation=cv2.INTER_AREA)
    amb_small = cv2.GaussianBlur(amb_small, (7, 7), 0)
    amb = cv2.resize(amb_small, (1080, 1080), interpolation=cv2.INTER_LINEAR)
    canvas = (amb.astype(np.float32) * 0.30).astype(np.uint8)

    hero = cv2.resize(scene_clean, (1080, 552), interpolation=cv2.INTER_LANCZOS4)
    canvas[237 : 237 + 552, 0:1080] = hero

    # 2. Top header bar (y=0..140)
    paste_bgra_rect(canvas, headers_1x1[mod["id"]], 0, 0, 1.0)

    # 3. 1:1 Module roadmap panel on left (x=22..466, y=158..848)
    pid, pop = panel_opacity_for(t, modules)
    if pid is not None and pop > 0.0:
        paste_bgra_rect(canvas, panels_1x1[pid], 22, 158, pop)

    # 4. Official transparent presenter ABOVE all bands (right side cx=845, y=232..807)
    if t < OPENING_END_T:
        fade_out = 1.0 if t <= OPENING_END_T - 0.40 else max(0.0, (OPENING_END_T - t) / 0.40)
        if t < 3.0:
            canvas = composite_presenter(canvas, poses["open1_1x1"], cx=845, y_top=232, t_local=t, opacity=fade_out)
        elif t < 3.4:
            mix = (t - 3.0) / 0.4
            canvas = composite_presenter(canvas, poses["open1_1x1"], cx=845, y_top=232, t_local=t, opacity=(1.0 - mix) * fade_out)
            canvas = composite_presenter(canvas, poses["open2_1x1"], cx=845, y_top=232, t_local=t, opacity=mix * fade_out)
        else:
            canvas = composite_presenter(canvas, poses["open2_1x1"], cx=845, y_top=232, t_local=t, opacity=fade_out)
    elif t >= CLOSING_START_T:
        dt_c = t - CLOSING_START_T
        fade_in = min(1.0, dt_c / 0.45)
        canvas = composite_presenter(canvas, poses["close_1x1"], cx=850, y_top=210, t_local=dt_c, opacity=fade_in)

    # 5. Dedicated feed-legible subtitle bar (y=888..1064)
    stxt = active_subtitle_at(t, subs_v3)
    skey = f"1x1:{stxt}"
    if skey not in sub_cache:
        sub_cache[skey] = render_subtitle_box(stxt, box_w=1032, box_h=176, font_size=28, wrap_chars=48)
    if stxt:
        paste_bgra_rect(canvas, sub_cache[skey], 24, 888, 1.0)
    return canvas


def load_all_poses_and_assets(modules: list[dict[str, Any]]) -> tuple[dict[str, np.ndarray], dict[int, np.ndarray], dict[int, np.ndarray], dict[int, np.ndarray], dict[int, np.ndarray], dict[int, np.ndarray]]:
    ensure_multiformat_panels()
    poses = {
        "open1_16x9": load_pose_scaled("guillermo_oficial_01_bienvenida.png", 620),
        "open2_16x9": load_pose_scaled("guillermo_oficial_04_enfasis_tecnico.png", 620),
        "close_16x9": load_pose_scaled("guillermo_oficial_05_saludo_cierre.png", 640),
        "open1_9x16": load_pose_scaled("guillermo_oficial_01_bienvenida.png", 560),
        "open2_9x16": load_pose_scaled("guillermo_oficial_04_enfasis_tecnico.png", 560),
        "close_9x16": load_pose_scaled("guillermo_oficial_05_saludo_cierre.png", 590),
        "open1_1x1": load_pose_scaled("guillermo_oficial_01_bienvenida.png", 575),
        "open2_1x1": load_pose_scaled("guillermo_oficial_04_enfasis_tecnico.png", 575),
        "close_1x1": load_pose_scaled("guillermo_oficial_05_saludo_cierre.png", 600),
    }
    p16 = {m["id"]: cv2.imread(str(PANELS_DIR_16X9 / f"panel_m{m['id']:02d}.png"), cv2.IMREAD_UNCHANGED) for m in modules}
    p9 = {m["id"]: cv2.imread(str(PANELS_DIR_9X16 / f"panel_m{m['id']:02d}.png"), cv2.IMREAD_UNCHANGED) for m in modules}
    p1 = {m["id"]: cv2.imread(str(PANELS_DIR_1X1 / f"panel_m{m['id']:02d}.png"), cv2.IMREAD_UNCHANGED) for m in modules}
    h9 = {m["id"]: build_header_cache_pil("9x16", m["banner"]) for m in modules}
    h1 = {m["id"]: build_header_cache_pil("1x1", m["banner"]) for m in modules}
    return poses, p16, p9, p1, h9, h1


def stage_p1() -> None:
    p0 = verify_p0()
    timing_doc = measure_audio_and_joins()
    modules = timing_doc["modules"]
    subs_v3 = timing_doc["subtitles_v3"]
    poses, p16, p9, p1, h9, h1 = load_all_poses_and_assets(modules)
    clean_ref = extract_clean_closing_ref()
    sub_cache: dict[str, np.ndarray] = {}

    cap = cv2.VideoCapture(str(SOURCE_MP4))
    cap.set(cv2.CAP_PROP_POS_MSEC, 1500.0)
    ok_open, f_open = cap.read()
    cap.set(cv2.CAP_PROP_POS_MSEC, 401500.0)  # orig timestamp inside closing window
    ok_close, f_close = cap.read()
    cap.release()
    if not ok_open or not ok_close:
        raise RuntimeError("Failed reading sample frames from source MP4")

    open_clean = erase_old_avatar_opening(f_open)
    close_clean = erase_old_avatar_closing(f_close, clean_ref)

    t_open = 1.50
    t_close = 398.50
    gates = {
        "still_00_opening_gate.jpg": compose_frame_16x9(open_clean, t_open, modules, p16, poses),
        "still_closing_gate.jpg": compose_frame_16x9(close_clean, t_close, modules, p16, poses),
        "still_00_9x16_gate.jpg": compose_frame_9x16(open_clean, t_open, modules, p9, h9, poses, sub_cache, subs_v3),
        "still_close_9x16_gate.jpg": compose_frame_9x16(close_clean, t_close, modules, p9, h9, poses, sub_cache, subs_v3),
        "still_00_1x1_gate.jpg": compose_frame_1x1(open_clean, t_open, modules, p1, h1, poses, sub_cache, subs_v3),
        "still_close_1x1_gate.jpg": compose_frame_1x1(close_clean, t_close, modules, p1, h1, poses, sub_cache, subs_v3),
    }
    saved = {}
    for name, img in gates.items():
        p = STILLS_V3 / name
        cv2.imwrite(str(p), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved[name] = str(p)

    print(json.dumps({
        "p0_gate": p0["gate"],
        "p1_gate": "READY_FOR_6_STILL_VISUAL_CHECK",
        "master_duration_sec": timing_doc["duration_sec"],
        "integrated_lufs": timing_doc["integrated_lufs"],
        "gate_stills": saved,
    }, indent=2, ensure_ascii=False))


def build_conformed_base(modules: list[dict[str, Any]]) -> Path:
    conformed_base = WORK_V3 / "base_conformed_v3.mp4"
    seg_files: list[Path] = []
    for m in modules:
        mid = m["id"]
        sf = WORK_V3 / f"mod_{mid:02d}_conformed.mp4"
        seg_files.append(sf)
        scale = m["new_dur"] / m["orig_dur"]
        run_cmd([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{m['orig_start']:.3f}",
            "-to", f"{m['orig_end']:.3f}",
            "-i", str(SOURCE_MP4),
            "-an",
            "-vf", f"setpts=(PTS-STARTPTS)*{scale:.8f},fps=30",
            "-t", f"{m['new_dur']:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
            str(sf),
        ])
    concat_list = WORK_V3 / "concat_v3.txt"
    concat_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in seg_files), encoding="utf-8")
    run_cmd(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(conformed_base)])
    return conformed_base


def render_single_format(
    fmt: str,
    conformed_base: Path,
    timing_doc: dict[str, Any],
    poses: dict[str, np.ndarray],
    p16: dict[int, np.ndarray],
    p9: dict[int, np.ndarray],
    p1: dict[int, np.ndarray],
    h9: dict[int, np.ndarray],
    h1: dict[int, np.ndarray],
    clean_ref: np.ndarray,
) -> dict[str, Any]:
    ram = free_ram_gb()
    if ram < 1.0:
        raise RuntimeError(f"RAM gate KO before rendering {fmt}: {ram} GB < 1.0 GB")

    cfg = FORMAT_TARGETS[fmt]
    w, h = cfg["size"]
    fname = cfg["filename"]
    modules = timing_doc["modules"]
    subs_v3 = timing_doc["subtitles_v3"]
    total_dur = float(timing_doc["duration_sec"])
    fps = 30.0
    total_target_frames = int(round(total_dur * fps))

    video_only = WORK_V3 / f"video_only_{fmt}.mp4"
    out_insumos = INSUMOS_DIR / fname
    out_repo = REPO_ROOT / fname
    out_vault = VAULT_DIR / fname

    cap = cv2.VideoCapture(str(conformed_base))
    ff_enc = subprocess.Popen(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-threads", "4", str(video_only),
        ],
        stdin=subprocess.PIPE,
    )

    sub_cache: dict[str, np.ndarray] = {}
    frame_idx = 0
    last_good = None
    print(f"[RENDER {fmt}] RAM free={ram} GB -> {fname} ({w}x{h}) ...")

    while frame_idx < total_target_frames:
        ok, frame = cap.read()
        if not ok or frame is None:
            if last_good is None:
                raise RuntimeError("No frames decoded from conformed_base")
            frame = last_good.copy()
        else:
            last_good = frame

        t = frame_idx / fps
        if t < OPENING_END_T:
            clean = erase_old_avatar_opening(frame)
        elif t >= CLOSING_START_T:
            clean = erase_old_avatar_closing(frame, clean_ref)
        else:
            clean = frame

        if fmt == "16x9":
            rendered = compose_frame_16x9(clean, t, modules, p16, poses)
        elif fmt == "9x16":
            rendered = compose_frame_9x16(clean, t, modules, p9, h9, poses, sub_cache, subs_v3)
        else:
            rendered = compose_frame_1x1(clean, t, modules, p1, h1, poses, sub_cache, subs_v3)

        assert ff_enc.stdin is not None
        ff_enc.stdin.write(rendered.tobytes())
        frame_idx += 1

    cap.release()
    assert ff_enc.stdin is not None
    ff_enc.stdin.close()
    rc = ff_enc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg rawvideo failed for {fmt}: exit {rc}")

    run_cmd([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(video_only),
        "-i", str(REPAIRED_WAV),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "1",
        "-shortest", "-movflags", "+faststart",
        str(out_insumos),
    ])

    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_insumos, out_repo)
    shutil.copy2(out_insumos, out_vault)
    sha_i = sha256_file(out_insumos)
    sha_r = sha256_file(out_repo)
    sha_v = sha256_file(out_vault)
    if not (sha_i == sha_r == sha_v):
        raise RuntimeError(f"Boundary SHA-256 mismatch for {fmt}: {sha_i}/{sha_r}/{sha_v}")

    # QA: ffprobe + blackdetect + format-specific stills
    probe = run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(out_insumos)])
    pdata = json.loads(probe.stdout)
    vs = next(s for s in pdata["streams"] if s["codec_type"] == "video")
    aus = next(s for s in pdata["streams"] if s["codec_type"] == "audio")
    out_dur = float(pdata["format"]["duration"])

    black_proc = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(out_insumos), "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    black_hits = re.findall(r"black_start:[\d\.]+ black_end:[\d\.]+ black_duration:[\d\.]+", black_proc.stderr)

    stills_out = []
    if fmt == "16x9":
        for name, ts in [
            ("still_00_opening.jpg", 1.5),
            ("close_presenter_01.jpg", 392.0),
            ("close_presenter_02.jpg", 400.5),
            ("join_j1.jpg", 50.8),
            ("join_j4.jpg", 192.2),
            ("join_j7.jpg", 321.5),
        ]:
            sp = STILLS_V3 / name
            run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_insumos), "-frames:v", "1", str(sp)])
            stills_out.append(str(sp))
        for m in modules:
            for kind, ts in [("start", m["start_still_t"]), ("mid", m["mid_still_t"])]:
                sp = STILLS_V3 / f"{kind}_m{m['id']:02d}.jpg"
                run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_insumos), "-frames:v", "1", str(sp)])
                stills_out.append(str(sp))
    else:
        for name, ts in [
            (f"still_00_{fmt}.jpg", 1.5),
            (f"mod_m02_start_{fmt}.jpg", modules[1]["start_still_t"]),
            (f"mod_m05_mid_{fmt}.jpg", modules[4]["mid_still_t"]),
            (f"mod_m09_start_{fmt}.jpg", modules[8]["start_still_t"]),
            (f"close_{fmt}.jpg", 398.5),
        ]:
            sp = STILLS_V3 / name
            run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_insumos), "-frames:v", "1", str(sp)])
            stills_out.append(str(sp))

    return {
        "format": fmt,
        "filename": fname,
        "resolution": f"{vs['width']}x{vs['height']}",
        "fps": vs["r_frame_rate"],
        "audio": f"{aus['sample_rate']} Hz {aus['channel_layout']} {aus['codec_name']}",
        "duration_sec": round(out_dur, 3),
        "duration_delta_sec": round(abs(out_dur - total_dur), 4),
        "bytes": out_insumos.stat().st_size,
        "sha256": sha_i,
        "vault_path": str(out_vault),
        "insumos_path": str(out_insumos),
        "blackdetect_hits": black_hits,
        "qa_stills": stills_out,
    }


def stage_render(formats: list[str]) -> None:
    p0 = verify_p0()
    timing_doc = json.loads(TIEMPOS_V3_JSON.read_text(encoding="utf-8")) if TIEMPOS_V3_JSON.exists() else measure_audio_and_joins()
    modules = timing_doc["modules"]
    poses, p16, p9, p1, h9, h1 = load_all_poses_and_assets(modules)
    clean_ref = extract_clean_closing_ref()

    conformed_base = WORK_V3 / "base_conformed_v3.mp4"
    if not conformed_base.exists():
        conformed_base = build_conformed_base(modules)

    results: dict[str, Any] = {}
    if QA_V3_JSON.exists():
        try:
            prev_qa = json.loads(QA_V3_JSON.read_text(encoding="utf-8"))
            if isinstance(prev_qa.get("formats"), dict):
                results.update(prev_qa["formats"])
        except Exception:
            pass
    for fmt in formats:
        results[fmt] = render_single_format(fmt, conformed_base, timing_doc, poses, p16, p9, p1, h9, h1, clean_ref)

    protected_ok = (
        sha256_file(V2_MP4_PC) == EXPECTED_HASHES["v2_mp4_pc"]
        and sha256_file(V2_MP4_VAULT) == EXPECTED_HASHES["v2_mp4_vault"]
        and sha256_file(SOURCE_MP4) == EXPECTED_HASHES["source_v1_mp4"]
        and sha256_file(REPAIRED_WAV) == EXPECTED_HASHES["repaired_wav"]
    )
    qa_doc = {
        "phase": "P2_P3_MULTIFORMAT_V3",
        "ram_pre_render_gb": p0["ram_free_gb"],
        "protected_artifacts_byte_identical": protected_ok,
        "formats": results,
    }
    QA_V3_JSON.write_text(json.dumps(qa_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(qa_doc, indent=2, ensure_ascii=False))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["p1", "render"], required=True)
    parser.add_argument("--formats", nargs="+", choices=["16x9", "9x16", "1x1"], default=["16x9", "9x16", "1x1"])
    args = parser.parse_args()
    if args.stage == "p1":
        stage_p1()
    else:
        stage_render(args.formats)


if __name__ == "__main__":
    main()
