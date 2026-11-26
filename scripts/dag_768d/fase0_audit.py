#!/usr/bin/env python3
"""FASE 0 — Real pre-flight audit of binaries, packages, Qdrant, encoders, and verified files."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)


def test_encoder_1080p60(encoder: str) -> tuple[bool, float, str]:
    """Run a quick 0.2s 1080p@60fps encoding benchmark + frame count check."""
    test_mp4 = cfg.LOCAL_TEMP / f"_enc_test_{encoder}.mp4"
    if test_mp4.exists():
        test_mp4.unlink()
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"testsrc2=size={cfg.TARGET_W}x{cfg.TARGET_H}:rate={cfg.TARGET_FPS}:duration=0.5",
        "-c:v", encoder,
    ]
    if encoder == "libx264":
        cmd += ["-preset", "veryfast", "-crf", "20"]
    elif encoder == "h264_qsv":
        cmd += ["-preset", "faster", "-global_quality", "20"]
    cmd += ["-pix_fmt", "yuv420p", "-r", str(cfg.TARGET_FPS), "-video_track_timescale", "60000", str(test_mp4)]

    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    dt = round(time.time() - t0, 3)
    if r.returncode != 0 or not test_mp4.exists() or test_mp4.stat().st_size == 0:
        return False, dt, (r.stderr or "")[-300:]

    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_read_frames,r_frame_rate,duration",
         "-of", "json", str(test_mp4)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(pr.stdout)["streams"][0]
    frames = int(info.get("nb_read_frames", 0))
    ok = (frames == 30 and int(info.get("width", 0)) == cfg.TARGET_W and int(info.get("height", 0)) == cfg.TARGET_H)
    test_mp4.unlink(missing_ok=True)
    return ok, dt, f"frames={frames}/30 dur={info.get('duration')} fps={info.get('r_frame_rate')}"


def main() -> None:
    cfg.ensure_dirs()
    failures: list[str] = []

    print("=== FASE 0: AUDITORIA REAL DE FUENTES Y ENTORNO ===", flush=True)

    # L0.1 Binaries, packages, Qdrant, encoders
    binaries = {}
    for b in ["python", "ffmpeg", "ffprobe"]:
        r = subprocess.run([b, "--version" if b == "python" else "-version"], capture_output=True, text=True)
        if r.returncode != 0:
            failures.append(f"Binario faltante o con error: {b}")
        else:
            binaries[b] = (r.stdout or r.stderr).splitlines()[0].strip()

    pkg_status = {}
    for pkg in ["sentence_transformers", "cv2", "PIL", "numpy", "scipy", "soundfile", "qdrant_client"]:
        try:
            __import__(pkg)
            pkg_status[pkg] = "OK"
        except ImportError as exc:
            pkg_status[pkg] = f"MISSING: {exc}"
            failures.append(f"Paquete Python faltante: {pkg}")

    qdrant_collections = []
    try:
        qres = cfg.qdrant_http("/collections")
        qdrant_collections = [c["name"] for c in qres.get("result", {}).get("collections", [])]
    except Exception as exc:
        failures.append(f"Qdrant inaccesible en {cfg.QDRANT_URL}: {exc}")

    qsv_ok, qsv_dt, qsv_msg = test_encoder_1080p60("h264_qsv")
    x264_ok, x264_dt, x264_msg = test_encoder_1080p60("libx264")
    if qsv_ok:
        selected_encoder = "h264_qsv"
    elif x264_ok:
        selected_encoder = "libx264"
    else:
        selected_encoder = "NONE"
        failures.append("Ningun encoder H.264 1080p60 funcional (qsv y libx264 fallaron)")

    print(f"[L0.1] Qdrant colecciones={len(qdrant_collections)} | h264_qsv={qsv_ok} ({qsv_dt}s, {qsv_msg}) | libx264={x264_ok} ({x264_dt}s, {x264_msg}) -> elegido={selected_encoder}", flush=True)

    # L0.2 Physical file checks
    files_report = {"audio": {}, "backgrounds": [], "avatar_poses": [], "avatar_clips": []}

    for label, fp in [
        ("audio_master_wav", cfg.AUDIO_MASTER),
        ("audio_backup_wav", cfg.AUDIO_BACKUP),
        ("tiempos_json", cfg.TIEMPOS_SRC),
    ]:
        if not fp.exists() or fp.stat().st_size == 0:
            failures.append(f"Falta o esta vacio {label}: {fp}")
        else:
            files_report["audio"][label] = {"path": str(fp), "size_bytes": fp.stat().st_size}

    for i in range(1, 11):
        bg = cfg.FONDOS_DIR / f"bg_{i:02d}.jpg"
        if not bg.exists() or bg.stat().st_size == 0:
            failures.append(f"Falta fondo 16:9: {bg}")
            continue
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", str(bg)],
            capture_output=True, text=True, check=True,
        )
        w, h = [int(x) for x in pr.stdout.strip().split(",")]
        if (w, h) != (cfg.TARGET_W, cfg.TARGET_H):
            failures.append(f"Resolucion inesperada en {bg.name}: {w}x{h}")
        files_report["backgrounds"].append({"name": bg.name, "path": str(bg), "width": w, "height": h, "size_bytes": bg.stat().st_size})

    # Discover clean avatar RGBA poses and match SELECTED_POSES (or fallback to clean poses)
    all_clean_poses = sorted(
        f.name for f in cfg.AVATAR_TRANSP_DIR.glob("avatar-pose-t-*.png")
        if "acoplada" not in f.name and f.stat().st_size > 0
    )
    if len(all_clean_poses) < 20:
        failures.append(f"Se requieren >=20 poses RGBA limpias en {cfg.AVATAR_TRANSP_DIR}, encontradas: {len(all_clean_poses)}")

    chosen_poses = [p for p in cfg.SELECTED_POSES if (cfg.AVATAR_TRANSP_DIR / p).exists() and (cfg.AVATAR_TRANSP_DIR / p).stat().st_size > 0]
    for p in all_clean_poses:
        if len(chosen_poses) >= 20:
            break
        if p not in chosen_poses:
            chosen_poses.append(p)

    for pname in chosen_poses:
        fp = cfg.AVATAR_TRANSP_DIR / pname
        files_report["avatar_poses"].append({"name": pname, "path": str(fp), "size_bytes": fp.stat().st_size})

    manifest_clips = cfg.AVATAR_CLIP_LIB / "canonical_15_avatar_clips_manifest.json"
    if not manifest_clips.exists() or manifest_clips.stat().st_size == 0:
        failures.append(f"Falta manifiesto de clips: {manifest_clips}")
    avm_clips = sorted(cfg.AVATAR_CLIP_LIB.glob("AVM_*.mp4"))
    if len(avm_clips) < 15:
        failures.append(f"Se requieren 15 clips AVM_*.mp4 en {cfg.AVATAR_CLIP_LIB}, encontrados: {len(avm_clips)}")
    for ac in avm_clips:
        if ac.stat().st_size == 0:
            failures.append(f"Clip vacio: {ac}")
        files_report["avatar_clips"].append({"name": ac.name, "path": str(ac), "size_bytes": ac.stat().st_size})

    print(f"[L0.2] Fondos={len(files_report['backgrounds'])}/10 | Poses RGBA={len(files_report['avatar_poses'])} (disponibles={len(all_clean_poses)}) | Clips AVM={len(files_report['avatar_clips'])}/15", flush=True)

    # L0.3 Acoustic measurement on AUDIO_MASTER
    audio_metrics = {}
    if cfg.AUDIO_MASTER.exists():
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
             "-show_entries", "stream=codec_name,sample_rate,channels", "-of", "json", str(cfg.AUDIO_MASTER)],
            capture_output=True, text=True, check=True,
        )
        adata = json.loads(pr.stdout)
        dur = float(adata["format"]["duration"])
        st = adata["streams"][0]

        lr = subprocess.run(
            ["ffmpeg", "-i", str(cfg.AUDIO_MASTER), "-af", "loudnorm=I=-14.5:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
            capture_output=True, text=True, check=True,
        )
        s = lr.stderr
        ljson = json.loads(s[s.rfind("{"):s.rfind("}") + 1])
        audio_metrics = {
            "duration_sec": dur,
            "sample_rate": int(st["sample_rate"]),
            "channels": int(st["channels"]),
            "codec": st["codec_name"],
            "input_i_lufs": float(ljson["input_i"]),
            "input_tp_db": float(ljson["input_tp"]),
            "sha256": cfg.sha256_file(cfg.AUDIO_MASTER),
        }
        if dur <= 0:
            failures.append("Duracion de audio invalida <= 0")
        if audio_metrics["sample_rate"] != 48000 or audio_metrics["channels"] != 1:
            failures.append(f"Audio debe ser 48000Hz mono, encontrado: {audio_metrics}")
        print(f"[L0.3] Audio real: {dur:.3f}s | {audio_metrics['sample_rate']}Hz ch={audio_metrics['channels']} | LUFS={audio_metrics['input_i_lufs']} | TP={audio_metrics['input_tp_db']}", flush=True)

    gate_pass = len(failures) == 0
    debug_out = {
        "phase": "FASE_0",
        "gate_0_to_1": "PASS" if gate_pass else "FAIL",
        "failures": failures,
        "binaries": binaries,
        "python_packages": pkg_status,
        "qdrant_url": cfg.QDRANT_URL,
        "qdrant_existing_collections": qdrant_collections,
        "encoder_bench": {
            "selected": selected_encoder,
            "h264_qsv": {"ok": qsv_ok, "time_s": qsv_dt, "detail": qsv_msg},
            "libx264": {"ok": x264_ok, "time_s": x264_dt, "detail": x264_msg},
        },
        "audio_metrics": audio_metrics,
        "files": files_report,
        "total_clean_rgba_poses_available": len(all_clean_poses),
    }

    out_path = cfg.BUILD_DIR / "debug_fase0.json"
    out_path.write_text(json.dumps(debug_out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[GATE 0->1] Status={debug_out['gate_0_to_1']} | Guardado en {out_path}", flush=True)

    if not gate_pass:
        print("FAIL-FAST ABORT:", failures, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
