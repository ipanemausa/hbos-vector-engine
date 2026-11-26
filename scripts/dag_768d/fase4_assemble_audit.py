#!/usr/bin/env python3
"""FASE 4 — Final H.264/AAC Assembly, Technical Audit Gate, Qdrant Indexing, and Auto-Launch."""

import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import cv2
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)


def run_ffmpeg_detect(mp4_path: Path, vf_or_af: str, is_audio: bool = False) -> str:
    """Run blackdetect or silencedetect and return stderr log."""
    flag = "-af" if is_audio else "-vf"
    drop = "-vn" if is_audio else "-an"
    cmd = ["ffmpeg", "-i", str(mp4_path), drop, flag, vf_or_af, "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return r.stderr


def check_frame_motion_across_video(mp4_path: Path, timeline: dict) -> dict:
    """Sample frames every 0.3s within every block and verify zero prolonged (>0.6s) freezes."""
    cap = cv2.VideoCapture(str(mp4_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
    step_frames = int(round(0.3 * fps))
    freezes = []
    block_stats = []

    for b in timeline["blocks"]:
        sf = int(b["start_frame"])
        ef = int(b["end_frame"])
        deltas = []
        prev = None
        for fidx in range(sf + 12, ef - 12, step_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
            ok, frm = cap.read()
            if not ok:
                continue
            small = cv2.resize(frm, (320, 180))
            if prev is not None:
                d = float(np.mean(np.abs(small.astype(np.float32) - prev.astype(np.float32))))
                deltas.append(d)
            prev = small
        consec_zero = 0
        for d in deltas:
            if d < 0.05:
                consec_zero += 1
                if consec_zero >= 2:  # >= 0.6s without motion
                    freezes.append({"block_id": b["block_id"], "delta": d})
            else:
                consec_zero = 0
        block_stats.append({
            "block_id": b["block_id"],
            "samples": len(deltas),
            "min_delta": round(min(deltas), 4) if deltas else 0.0,
            "mean_delta": round(float(np.mean(deltas)), 4) if deltas else 0.0,
        })
    cap.release()
    return {"freezes_over_06s": freezes, "block_stats": block_stats}


def main() -> None:
    print("=== FASE 4: ENSAMBLE FINAL, AUDITORIA TECNICA Y AUTO-LAUNCH ===", flush=True)
    df0 = json.loads((cfg.BUILD_DIR / "debug_fase0.json").read_text(encoding="utf-8"))
    df3 = json.loads((cfg.BUILD_DIR / "debug_fase3.json").read_text(encoding="utf-8"))
    timeline = json.loads((cfg.BUILD_DIR / "timeline_768.json").read_text(encoding="utf-8"))

    if df3.get("gate_3_to_4") != "PASS":
        print("FAIL-FAST: Gate 3->4 no esta en PASS", flush=True)
        sys.exit(1)

    master_audio_dur = float(df0["audio_metrics"]["duration_sec"])
    concat_txt = Path(df3["concat_list"])
    temp_silent = cfg.LOCAL_TEMP / "temp_full_silent_final.mp4"
    local_final = cfg.LOCAL_TEMP / cfg.FINAL_MP4.name

    print("[L4.1] Concatenando bloques y multiplexando audio master 48kHz (-14.87 LUFS)...", flush=True)
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c:v", "copy", str(temp_silent)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(temp_silent),
        "-i", str(cfg.AUDIO_MASTER),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        "-shortest",
        str(local_final),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    shutil.copy2(str(local_final), str(cfg.FINAL_MP4))
    shutil.copy2(str(local_final), str(cfg.VAULT_MP4))
    print(f"[L4.1] Copiado a Drive Final y Media Vault: {cfg.FINAL_MP4}", flush=True)

    # L4.2 Automated Audit directly on FINAL_MP4
    print("[L4.2] Ejecutando auditoria ffprobe / blackdetect / silencedetect / motion...", flush=True)
    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels",
         "-of", "json", str(cfg.FINAL_MP4)],
        capture_output=True, text=True, check=True,
    )
    pdata = json.loads(pr.stdout)
    vstream = next(s for s in pdata["streams"] if s["codec_type"] == "video")
    astream = next(s for s in pdata["streams"] if s["codec_type"] == "audio")

    vid_dur = float(vstream["duration"])
    aud_dur = float(astream["duration"])
    fmt_dur = float(pdata["format"]["duration"])
    fps_parts = [float(x) for x in vstream["r_frame_rate"].split("/")]
    fps_val = fps_parts[0] / (fps_parts[1] or 1.0)

    black_log = run_ffmpeg_detect(cfg.FINAL_MP4, "blackdetect=d=0.2:pix_th=0.05", is_audio=False)
    black_hits = re.findall(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)", black_log)

    sil_log = run_ffmpeg_detect(cfg.FINAL_MP4, "silencedetect=noise=-45dB:d=3.0", is_audio=True)
    sil_hits = re.findall(r"silence_duration:\s*([0-9.]+)", sil_log)

    motion_audit = check_frame_motion_across_video(cfg.FINAL_MP4, timeline)

    failures = []
    if int(vstream["width"]) != 1920 or int(vstream["height"]) != 1080:
        failures.append(f"Resolucion inesperada: {vstream['width']}x{vstream['height']}")
    if abs(fps_val - 60.0) > 0.1:
        failures.append(f"FPS inesperado: {fps_val}")
    if abs(vid_dur - master_audio_dur) > 0.05:
        failures.append(f"Desfase duracion video vs audio master: {vid_dur} vs {master_audio_dur}")
    if abs(aud_dur - master_audio_dur) > 0.05:
        failures.append(f"Desfase duracion audio vs audio master: {aud_dur} vs {master_audio_dur}")
    if black_hits:
        failures.append(f"Cuadros negros detectados: {black_hits}")
    if sil_hits:
        failures.append(f"Silencios rotos (>3s) detectados: {sil_hits}")
    if motion_audit["freezes_over_06s"]:
        failures.append(f"Congelamientos >0.6s detectados: {motion_audit['freezes_over_06s']}")

    sha = cfg.sha256_file(cfg.FINAL_MP4)
    size_mb = round(cfg.FINAL_MP4.stat().st_size / (1024 * 1024), 2)

    # Index closure record in Qdrant (both hbos_equipo_agentes_768 and canon_video_hbos_r768)
    try:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", local_files_only=True)
    except Exception:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    summary_txt = (
        f"Equipo de Agentes de IA Guillermo Alonso Hoyos Guia Hoy Rionegro Antioquia 1080p 60fps "
        f"Coordinador Investigador Ejecutor Auditor Handoffs Estructurados Humano en el Bucle "
        f"Antioquia Colombia 0 SaaS Tax SHA256 {sha}"
    )
    vec768 = [float(x) for x in model.encode([summary_txt], normalize_embeddings=True, show_progress_bar=False)[0]]
    assert len(vec768) == 768

    q_payload = {
        "kind": "final_master_video",
        "project": "Equipo de Agentes de IA",
        "date": "2026-11-25",
        "speaker": "Guillermo Alonso Hoyos (Guía Hoy)",
        "resolution": "1920x1080",
        "fps": 60,
        "video_duration_sec": vid_dur,
        "audio_duration_sec": aud_dur,
        "size_mb": size_mb,
        "sha256": sha,
        "final_drive_path": str(cfg.FINAL_MP4),
        "vault_path": str(cfg.VAULT_MP4),
        "gate_4": "PASS" if not failures else "FAIL",
    }
    pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"hbos_eq_ag_final_{sha}"))
    for coll in [cfg.QDRANT_COLLECTION, cfg.QDRANT_CANON_COLLECTION]:
        try:
            cfg.qdrant_http(
                f"/collections/{coll}/points?wait=true",
                method="PUT",
                data={"points": [{"id": pid, "vector": vec768, "payload": q_payload}]},
            )
            print(f"[QDRANT] Cierre indexado en {coll} (ID={pid})", flush=True)
        except Exception as exc:
            print(f"[WARN] Qdrant {coll}: {exc}", flush=True)

    report = {
        "phase": "FASE_4_CIERRE",
        "gate_4_final": "PASS" if not failures else "FAIL",
        "failures": failures,
        "final_mp4": str(cfg.FINAL_MP4),
        "vault_mp4": str(cfg.VAULT_MP4),
        "sha256": sha,
        "size_bytes": cfg.FINAL_MP4.stat().st_size,
        "size_mb": size_mb,
        "video_stream": {
            "codec": vstream["codec_name"],
            "width": int(vstream["width"]),
            "height": int(vstream["height"]),
            "fps": round(fps_val, 3),
            "nb_frames": int(vstream.get("nb_frames", 0)),
            "duration_sec": vid_dur,
        },
        "audio_stream": {
            "codec": astream["codec_name"],
            "sample_rate": int(astream["sample_rate"]),
            "channels": int(astream["channels"]),
            "duration_sec": aud_dur,
        },
        "master_audio_reference_sec": master_audio_dur,
        "av_sync_delta_sec": round(abs(vid_dur - aud_dur), 4),
        "master_sync_delta_sec": round(abs(vid_dur - master_audio_dur), 4),
        "blackdetect_segments": len(black_hits),
        "silencedetect_segments_over_3s": len(sil_hits),
        "motion_continuity": motion_audit,
        "format_duration_sec": fmt_dur,
    }

    rep_path = cfg.FINAL_DIR / "REPORTE_AUDITORIA_FINAL.json"
    rep_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[GATE 4] Status={report['gate_4_final']} | Video={vid_dur:.3f}s | Audio={aud_dur:.3f}s | Black={len(black_hits)} | Silence>3s={len(sil_hits)} | Freezes={len(motion_audit['freezes_over_06s'])}", flush=True)

    if failures:
        print("FAIL-FAST ABORT:", failures, flush=True)
        sys.exit(1)

    # Copy QA PNGs to artifact dir for interactive player
    for qname in ["qa_inicio.png", "qa_mitad.png", "qa_cierre.png"]:
        src_q = cfg.CONTROL_CLIPS_DIR / qname
        if src_q.exists():
            shutil.copy2(str(src_q), str(cfg.ARTIFACT_DIR / qname))

    # RULE_AUTO_LAUNCH_01
    try:
        os.startfile(str(cfg.FINAL_MP4))
        print(f"[RULE_AUTO_LAUNCH_01] Lanzado en Windows: {cfg.FINAL_MP4}", flush=True)
    except Exception as exc:
        print(f"[WARN] os.startfile: {exc}", flush=True)


if __name__ == "__main__":
    main()
