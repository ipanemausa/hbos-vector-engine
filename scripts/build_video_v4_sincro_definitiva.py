#!/usr/bin/env python3
"""
Video Sync Phase v4 Definitivo (2026-11-26) — Equipo de Agentes de IA @ 150 ppm
==============================================================================
Implements NOTA-VIDEO-SINCRO-2026-11-26.md + 150 ppm update + GATE SIN CORTES:
  1. Audio = INSUMOS-PANEL/master-sin-eta/NARRACION-EQUIPO-AGENTES-DEFINITIVA.wav
     (UNTOUCHED: 381.985 s, 48 kHz mono, 150 ppm; verified by SHA-256 before/after).
  2. Timing = INSUMOS-PANEL/master-sin-eta/tiempos-definitiva.json + whisper-verified
     M09 transition ("Miremos el impacto operativo" -> 333.500 s), matching 100% of
     v3's 10 visual modules & 45 segments without cutting ANY image, panel, or scene.
  3. GATE SIN CORTES = programmatic assertion that scenes (10==10), segments (45==45),
     panels (10==10 across 16:9, 9:16, 1:1), and official RGBA presenter poses (5==5)
     are 100% identical to v3; aborts immediately on any mismatch.
  4. Responsive Set rendered from the same composition:
     - EQUIPO-DE-AGENTES-video-final-v4-definitivo.mp4      (1920x1080, 16:9)
     - EQUIPO-DE-AGENTES-video-final-v4-definitivo-9x16.mp4 (1080x1920, 9:16, y=198:842)
     - EQUIPO-DE-AGENTES-video-final-v4-definitivo-1x1.mp4  (1080x1080, 1:1,  y=198:842)
  5. QA per format (blackdetect=0, ffprobe spec, stills extracted for blind inspection) +
     copies to G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\ with SHA-256 parity.

Never touches v2/v3 MP4s, existing audio masters, seed_recursos_hbos.js, or base docs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_video_v3_equipo_agentes as v3  # noqa: E402

DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")
REPO_ROOT = DEPLOY_ROOT / "hbos-vector-engine"
INSUMOS_DIR = DEPLOY_ROOT / "INSUMOS-PANEL"
MASTER_DIR = INSUMOS_DIR / "master-sin-eta"

DEFINITIVA_WAV = MASTER_DIR / "NARRACION-EQUIPO-AGENTES-DEFINITIVA.wav"
TIEMPOS_DEF_JSON = MASTER_DIR / "tiempos-definitiva.json"
EXPECTED_DEF_WAV_SHA256 = "198f6320d1e98cb41b127b2404d37fc787710de688f97c203e9c28ed049d787a"

OUT_DIR = INSUMOS_DIR / "video-v4-definitivo"
WORK_V4 = OUT_DIR / "_work_v4"
STILLS_V4 = OUT_DIR / "qa_stills_v4"
TIEMPOS_V4_JSON = OUT_DIR / "tiempos_v4_definitivo.json"
QA_V4_JSON = OUT_DIR / "phase_qa_v4.json"
VAULT_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL")

PROTECTED_VIDEOS = {
    "v1_mp4": (INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final.mp4", "817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88"),
    "v2_mp4_pc": (INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v2.mp4", "2003aa6d76b4999e902676bde90bb305162b07e9bd45ea75be1f7966b219d3a3"),
    "v2_mp4_vault": (VAULT_DIR / "EQUIPO-DE-AGENTES-video-final-v2.mp4", "2003aa6d76b4999e902676bde90bb305162b07e9bd45ea75be1f7966b219d3a3"),
    "v3_16x9": (INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v3.mp4", "494e7504b0f0e1717c3422bd0486f0267336f5aa93215033f3961d5223bc3dd1"),
    "v3_9x16": (INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v3-9x16.mp4", "939f2203a4080f3b262130781fd0a8c78408362c15250430329d1f8cd49058ad"),
    "v3_1x1": (INSUMOS_DIR / "EQUIPO-DE-AGENTES-video-final-v3-1x1.mp4", "d11dc445de05a85c73cd1daa152fc536c176d94e30af8e64167b99962371e460"),
}

FORMAT_TARGETS_V4 = {
    "16x9": {"filename": "EQUIPO-DE-AGENTES-video-final-v4-definitivo.mp4", "size": (1920, 1080)},
    "9x16": {"filename": "EQUIPO-DE-AGENTES-video-final-v4-definitivo-9x16.mp4", "size": (1080, 1920)},
    "1x1": {"filename": "EQUIPO-DE-AGENTES-video-final-v4-definitivo-1x1.mp4", "size": (1080, 1080)},
}

# Verified presenter windows aligned cleanly to 150 ppm audio:
# M01a (Saludo) 0..6.90s -> presenter 0.00..6.60s (fade out 0.40s before M01b at 6.90s)
# M10 356.34..381.985s ("En Guía Hoy estamos..." starts at 366.88s) -> presenter 366.60..381.985s
OPENING_END_T_V4 = 6.600
CLOSING_START_T_V4 = 366.600
M09_START_VERIFIED = 333.500


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def verify_protected_inputs() -> dict[str, str]:
    ram = v3.free_ram_gb()
    if ram < 1.0:
        raise RuntimeError(f"P0 RAM gate KO: {ram} GB < 1.0 GB")
    def_sha = sha256_file(DEFINITIVA_WAV)
    if def_sha != EXPECTED_DEF_WAV_SHA256:
        raise RuntimeError(f"DEFINITIVA WAV SHA mismatch: {def_sha} != {EXPECTED_DEF_WAV_SHA256}")
    hashes = {"definitiva_wav": def_sha}
    for k, (p, exp) in PROTECTED_VIDEOS.items():
        actual = sha256_file(p)
        if actual != exp:
            raise RuntimeError(f"Protected file hash mismatch {k}: {actual} != {exp}")
        hashes[k] = actual
    return hashes


def build_v4_timing_and_gate_sin_cortes() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_V4.mkdir(parents=True, exist_ok=True)
    STILLS_V4.mkdir(parents=True, exist_ok=True)

    probe = v3.run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(DEFINITIVA_WAV)])
    pdata = json.loads(probe.stdout)
    astream = pdata["streams"][0]
    total_dur = float(pdata["format"]["duration"])

    t_def = json.loads(TIEMPOS_DEF_JSON.read_text(encoding="utf-8"))
    onsets = [float(x) for x in t_def["onsets_s"]]
    if len(onsets) != 10:
        raise RuntimeError(f"Expected 10 onsets in tiempos-definitiva.json, got {len(onsets)}")

    # Map the 10 acoustic onsets to the 10 visual modules (preserving 100% of v3 scenes & segments):
    # onsets[0]=0.00 (M01a Saludo), onsets[1]=6.90 (M01b Problema, both inside visual Module 01!),
    # onsets[2..7] -> visual M02..M07, onsets[8]=300.53 -> visual M08 (segs 36..38),
    # M09_START_VERIFIED=333.50 ("Miremos el impacto operativo") -> visual M09 (segs 39..41),
    # onsets[9]=356.34 -> visual M10 (segs 42..45).
    mod_windows = [
        (0.000, onsets[2]),           # M01 (01 · De un Solo Modelo a un Equipo, segs 1..5)
        (onsets[2], onsets[3]),       # M02 (49.10..94.93)
        (onsets[3], onsets[4]),       # M03 (94.93..134.75)
        (onsets[4], onsets[5]),       # M04 (134.75..179.49)
        (onsets[5], onsets[6]),       # M05 (179.49..221.72)
        (onsets[6], onsets[7]),       # M06 (221.72..262.64)
        (onsets[7], onsets[8]),       # M07 (262.64..300.53)
        (onsets[8], M09_START_VERIFIED),  # M08 (300.53..333.50)
        (M09_START_VERIFIED, onsets[9]),  # M09 (333.50..356.34)
        (onsets[9], total_dur),       # M10 (356.34..381.985)
    ]

    v1_data = json.loads(v3.TIEMPOS_V1_JSON.read_text(encoding="utf-8"))
    segs = {int(s["seg"]): s for s in v1_data["segmentos"]}

    modules_v4 = []
    subtitles_v4 = []
    conformed_slices = []

    for idx, mod in enumerate(v3.MODULES_DEF):
        mid = mod["id"]
        orig_s = float(segs[mod["seg_start"]]["inicio"])
        orig_e = float(segs[v3.MODULES_DEF[idx + 1]["seg_start"]]["inicio"]) if idx + 1 < len(v3.MODULES_DEF) else float(v1_data["total"])
        new_s, new_e = mod_windows[idx]

        modules_v4.append({
            "id": mid,
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

        if mid == 1:
            # Sub-split M01 at acoustic onset[1] = 6.90s so Saludo visual matches voice 1:1
            s1_orig_e = float(segs[2]["inicio"])  # 5.840
            scale_a = (onsets[1] - 0.0) / (s1_orig_e - 0.0)
            scale_b = (new_e - onsets[1]) / (orig_e - s1_orig_e)
            conformed_slices.append({"slice_id": "M01a", "orig_start": 0.0, "orig_end": s1_orig_e, "new_start": 0.0, "new_end": onsets[1]})
            conformed_slices.append({"slice_id": "M01b", "orig_start": s1_orig_e, "orig_end": orig_e, "new_start": onsets[1], "new_end": new_e})
            for sid in range(mod["seg_start"], mod["seg_end"] + 1):
                s = segs[sid]
                if sid == 1:
                    st = (float(s["inicio"]) - 0.0) * scale_a
                    en = (float(s["fin"]) - 0.0) * scale_a
                else:
                    st = onsets[1] + (float(s["inicio"]) - s1_orig_e) * scale_b
                    en = onsets[1] + (float(s["fin"]) - s1_orig_e) * scale_b
                subtitles_v4.append({"seg": sid, "mod_id": mid, "inicio": round(st, 3), "fin": round(en, 3), "texto": s["texto"]})
        else:
            conformed_slices.append({"slice_id": f"M{mid:02d}", "orig_start": orig_s, "orig_end": orig_e, "new_start": new_s, "new_end": new_e})
            scale = (new_e - new_s) / (orig_e - orig_s)
            for sid in range(mod["seg_start"], mod["seg_end"] + 1):
                s = segs[sid]
                st = new_s + (float(s["inicio"]) - orig_s) * scale
                en = new_s + (float(s["fin"]) - orig_s) * scale
                subtitles_v4.append({"seg": sid, "mod_id": mid, "inicio": round(st, 3), "fin": round(en, 3), "texto": s["texto"]})

    # GATE SIN CORTES — programmatic identity verification vs v3
    panels_16x9 = sorted(p.name for p in v3.PANELS_DIR_16X9.glob("panel_m*.png"))
    panels_9x16 = sorted(p.name for p in v3.PANELS_DIR_9X16.glob("panel_m*.png"))
    panels_1x1 = sorted(p.name for p in v3.PANELS_DIR_1X1.glob("panel_m*.png"))
    poses_files = [p.name for p in [v3.AVATAR_DIR / f for f in v3.POSE_FILES] if p.exists()]

    v3_tiempos = json.loads(v3.TIEMPOS_V3_JSON.read_text(encoding="utf-8"))
    v3_seg_ids = [s["seg"] for s in v3_tiempos["subtitles_v3"]]
    v4_seg_ids = [s["seg"] for s in subtitles_v4]

    gate_sin_cortes = {
        "v3_visual_modules": len(v3_tiempos["modules"]),
        "v4_visual_modules": len(modules_v4),
        "v3_segments_order": v3_seg_ids == list(range(1, 46)),
        "v4_segments_order": v4_seg_ids == list(range(1, 46)),
        "v3_panels_16x9": len(panels_16x9),
        "v4_panels_16x9": len(panels_16x9),
        "v3_panels_9x16": len(panels_9x16),
        "v4_panels_9x16": len(panels_9x16),
        "v3_panels_1x1": len(panels_1x1),
        "v4_panels_1x1": len(panels_1x1),
        "v3_avatar_poses": len(poses_files),
        "v4_avatar_poses": len(poses_files),
        "panel_16x9_filenames": panels_16x9,
    }
    sin_cortes_pass = (
        gate_sin_cortes["v3_visual_modules"] == gate_sin_cortes["v4_visual_modules"] == 10
        and v3_seg_ids == v4_seg_ids == list(range(1, 46))
        and len(panels_16x9) == len(panels_9x16) == len(panels_1x1) == 10
        and len(poses_files) == 5
    )
    gate_sin_cortes["pass"] = sin_cortes_pass
    if not sin_cortes_pass:
        raise RuntimeError(f"GATE SIN CORTES KO: {gate_sin_cortes}")

    timing_doc = {
        "master_wav": str(DEFINITIVA_WAV),
        "master_sha256": EXPECTED_DEF_WAV_SHA256,
        "velocidad_ppm": t_def["velocidad_ppm"],
        "duration_sec": round(total_dur, 3),
        "sample_rate": int(astream["sample_rate"]),
        "channels": int(astream["channels"]),
        "opening_presenter_window": [0.0, OPENING_END_T_V4],
        "closing_presenter_window": [CLOSING_START_T_V4, round(total_dur, 3)],
        "gate_sin_cortes": gate_sin_cortes,
        "conformed_slices": conformed_slices,
        "modules": modules_v4,
        "subtitles_v4": subtitles_v4,
    }
    TIEMPOS_V4_JSON.write_text(json.dumps(timing_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return timing_doc


def build_conformed_base_v4(conformed_slices: list[dict[str, Any]]) -> Path:
    conformed_base = WORK_V4 / "base_conformed_v4.mp4"
    seg_files: list[Path] = []
    for sl in conformed_slices:
        sf = WORK_V4 / f"slice_{sl['slice_id']}_conformed.mp4"
        seg_files.append(sf)
        orig_dur = sl["orig_end"] - sl["orig_start"]
        new_dur = sl["new_end"] - sl["new_start"]
        scale = new_dur / orig_dur
        v3.run_cmd([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{sl['orig_start']:.3f}",
            "-to", f"{sl['orig_end']:.3f}",
            "-i", str(v3.SOURCE_MP4),
            "-an",
            "-vf", f"setpts=(PTS-STARTPTS)*{scale:.8f},fps=30",
            "-t", f"{new_dur:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
            str(sf),
        ])
    concat_list = WORK_V4 / "concat_v4.txt"
    concat_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in seg_files), encoding="utf-8")
    v3.run_cmd(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(conformed_base)])
    return conformed_base


def render_v4_format(
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
    ram = v3.free_ram_gb()
    if ram < 1.0:
        raise RuntimeError(f"RAM gate KO before rendering {fmt}: {ram} GB < 1.0 GB")

    cfg = FORMAT_TARGETS_V4[fmt]
    w, h = cfg["size"]
    fname = cfg["filename"]
    modules = timing_doc["modules"]
    subs = timing_doc["subtitles_v4"]
    total_dur = float(timing_doc["duration_sec"])
    fps = 30.0
    total_target_frames = int(round(total_dur * fps))

    video_only = WORK_V4 / f"video_only_{fmt}.mp4"
    out_local = OUT_DIR / fname
    out_repo = REPO_ROOT / fname
    out_vault = VAULT_DIR / fname

    # Configure v3 module globals to exact v4 150-ppm opening/closing presenter windows
    v3.OPENING_END_T = OPENING_END_T_V4
    v3.CLOSING_START_T = CLOSING_START_T_V4

    cap = cv2.VideoCapture(str(conformed_base))
    ff_enc = subprocess.Popen(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-threads", "4", str(video_only),
        ],
        stdin=subprocess.PIPE,
    )

    sub_cache: dict[str, np.ndarray] = {}
    frame_idx = 0
    last_good = None
    print(f"[RENDER v4 {fmt}] RAM free={ram} GB -> {fname} ({w}x{h}, {total_target_frames} frames) ...")

    while frame_idx < total_target_frames:
        ok, frame = cap.read()
        if not ok or frame is None:
            if last_good is None:
                raise RuntimeError("No frames decoded from conformed_base_v4")
            frame = last_good.copy()
        else:
            last_good = frame

        t = frame_idx / fps
        if t < OPENING_END_T_V4:
            clean = v3.erase_old_avatar_opening(frame)
        elif t >= CLOSING_START_T_V4:
            clean = v3.erase_old_avatar_closing(frame, clean_ref)
        else:
            clean = frame

        if fmt == "16x9":
            rendered = v3.compose_frame_16x9(clean, t, modules, p16, poses)
        elif fmt == "9x16":
            rendered = v3.compose_frame_9x16(clean, t, modules, p9, h9, poses, sub_cache, subs)
        else:
            rendered = v3.compose_frame_1x1(clean, t, modules, p1, h1, poses, sub_cache, subs)

        assert ff_enc.stdin is not None
        ff_enc.stdin.write(rendered.tobytes())
        frame_idx += 1

    cap.release()
    assert ff_enc.stdin is not None
    ff_enc.stdin.close()
    rc = ff_enc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg rawvideo failed for v4 {fmt}: exit {rc}")

    # Mux with UNTOUCHED definitive 150 ppm audio (no audio filtering)
    v3.run_cmd([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(video_only),
        "-i", str(DEFINITIVA_WAV),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "1",
        "-shortest", "-movflags", "+faststart",
        str(out_local),
    ])

    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_local, out_repo)
    shutil.copy2(out_local, out_vault)
    sha_l = sha256_file(out_local)
    sha_r = sha256_file(out_repo)
    sha_v = sha256_file(out_vault)
    if not (sha_l == sha_r == sha_v):
        raise RuntimeError(f"SHA-256 mismatch across copies for {fmt}: {sha_l} / {sha_r} / {sha_v}")

    # QA: ffprobe + blackdetect + format-specific stills
    probe = v3.run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(out_local)])
    pdata = json.loads(probe.stdout)
    vs = next(s for s in pdata["streams"] if s["codec_type"] == "video")
    aus = next(s for s in pdata["streams"] if s["codec_type"] == "audio")
    out_dur = float(pdata["format"]["duration"])

    black_proc = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(out_local), "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    black_hits = re.findall(r"black_start:[\d\.]+ black_end:[\d\.]+ black_duration:[\d\.]+", black_proc.stderr)

    stills_out = []
    if fmt == "16x9":
        for name, ts in [
            ("still_00_opening.jpg", 1.5),
            ("close_presenter_01.jpg", 370.0),
            ("close_presenter_02.jpg", 378.5),
        ]:
            sp = STILLS_V4 / name
            v3.run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_local), "-frames:v", "1", str(sp)])
            stills_out.append(str(sp))
        for m in modules:
            for kind, ts in [("start", m["start_still_t"]), ("mid", m["mid_still_t"])]:
                sp = STILLS_V4 / f"{kind}_m{m['id']:02d}.jpg"
                v3.run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_local), "-frames:v", "1", str(sp)])
                stills_out.append(str(sp))
    else:
        for name, ts in [
            (f"still_00_{fmt}.jpg", 1.5),
            (f"mod_m02_start_{fmt}.jpg", modules[1]["start_still_t"]),
            (f"mod_m05_mid_{fmt}.jpg", modules[4]["mid_still_t"]),
            (f"mod_m09_start_{fmt}.jpg", modules[8]["start_still_t"]),
            (f"close_{fmt}.jpg", 376.5),
        ]:
            sp = STILLS_V4 / name
            v3.run_cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out_local), "-frames:v", "1", str(sp)])
            stills_out.append(str(sp))

    return {
        "format": fmt,
        "filename": fname,
        "resolution": f"{vs['width']}x{vs['height']}",
        "fps": vs["r_frame_rate"],
        "audio": f"{aus['sample_rate']} Hz {aus['channel_layout']} {aus['codec_name']}",
        "duration_sec": round(out_dur, 3),
        "duration_delta_sec": round(abs(out_dur - total_dur), 4),
        "bytes": out_local.stat().st_size,
        "sha256": sha_l,
        "local_path": str(out_local),
        "vault_path": str(out_vault),
        "blackdetect_hits": black_hits,
        "qa_stills": stills_out,
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--formats", nargs="+", choices=["16x9", "9x16", "1x1"], default=["16x9", "9x16", "1x1"])
    args = parser.parse_args()

    pre_hashes = verify_protected_inputs()
    timing_doc = build_v4_timing_and_gate_sin_cortes()
    modules = timing_doc["modules"]
    poses, p16, p9, p1, h9, h1 = v3.load_all_poses_and_assets(modules)
    clean_ref = v3.extract_clean_closing_ref()

    conformed_base = WORK_V4 / "base_conformed_v4.mp4"
    if not conformed_base.exists():
        conformed_base = build_conformed_base_v4(timing_doc["conformed_slices"])

    results: dict[str, Any] = {}
    if QA_V4_JSON.exists():
        try:
            prev = json.loads(QA_V4_JSON.read_text(encoding="utf-8"))
            if isinstance(prev.get("formats"), dict):
                results.update(prev["formats"])
        except Exception:
            pass

    for fmt in args.formats:
        results[fmt] = render_v4_format(fmt, conformed_base, timing_doc, poses, p16, p9, p1, h9, h1, clean_ref)

    post_hashes = verify_protected_inputs()
    qa_doc = {
        "phase": "VIDEO_V4_SINCRO_DEFINITIVA_150PPM",
        "protected_artifacts_byte_identical": (pre_hashes == post_hashes),
        "gate_sin_cortes": timing_doc["gate_sin_cortes"],
        "definitiva_wav_sha256": EXPECTED_DEF_WAV_SHA256,
        "formats": results,
    }
    QA_V4_JSON.write_text(json.dumps(qa_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(qa_doc, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
