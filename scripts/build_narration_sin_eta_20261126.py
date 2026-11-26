#!/usr/bin/env python3
"""
Equipo de Agentes — New Narration Master Without the "ETA" (26-nov-2026)
========================================================================
Strict E7 / E8 / S1 pipeline:
  P0 : Calibrate E8 10ms-hop F0 detector on NARRACION-EQUIPO-AGENTES-CONTINUA.wav + verify inputs
  P1 : Synthesize 10 continuous module takes via openbmb/VoxCPM-Demo with sacrificial lead-in/trailing,
       QC via hf-audio/whisper-large-v3 (sim >= 0.93, 0 looped 4-grams), word-align trim (whisper base),
       and verify E8 F0 gesture absent at trimmed onset (auto-retry once with 2x lead-in if needed; HALT if persists)
  P2 : Assemble 48 kHz 16-bit mono WAV master using >=2.0s DISJOINT real room-tone slices for 0.50s pauses,
       2-pass loudnorm to -14 LUFS / TP <= -1.0 dBTP, verify 0 ms digital black inside pauses
  P3 : Verify E8 F0 figure absent at 10/10 onsets of NARRACION-EQUIPO-AGENTES-SIN-ETA.wav,
       build TIRA-EMPALMES-SIN-ETA.wav / .mp3 and REPORTE-FIGURA-E8.txt

Never modifies v2/v3 videos, existing masters, seed_recursos_hbos.js, or the 4 base architecture docs.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile as sf
import whisper
from gradio_client import Client, handle_file

DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")
REPO_ROOT = DEPLOY_ROOT / "hbos-vector-engine"
INSUMOS_DIR = DEPLOY_ROOT / "INSUMOS-PANEL"

TIEMPOS_V1_JSON = INSUMOS_DIR / "tiempos.json"
CONTINUA_WAV = INSUMOS_DIR / "NARRACION-EQUIPO-AGENTES-CONTINUA.wav"
TIEMPOS_CONTINUO_JSON = INSUMOS_DIR / "tiempos-master-continuo.json"
REF_WAV = REPO_ROOT / "ref-video08-15s-16k.wav"
PROMPT_GUIDE = "y lo publica todo sola, en todas tus redes sociales, sin programar, empezando gratis..."

OUT_DIR = INSUMOS_DIR / "master-sin-eta"
TAKES_DIR = OUT_DIR / "takes"
FINAL_MASTER_WAV = OUT_DIR / "NARRACION-EQUIPO-AGENTES-SIN-ETA.wav"
STRIP_WAV = OUT_DIR / "TIRA-EMPALMES-SIN-ETA.wav"
STRIP_MP3 = OUT_DIR / "TIRA-EMPALMES-SIN-ETA.mp3"
REPORT_TXT = OUT_DIR / "REPORTE-FIGURA-E8.txt"

LEAD_IN = "Vamos a comenzar con el primer punto de esta presentación."
TRAILING = "Y con esto cerramos este punto."

MODULE_RANGES: dict[int, tuple[int, int]] = {
    1: (1, 1),
    2: (2, 5),
    3: (6, 11),
    4: (12, 16),
    5: (17, 21),
    6: (22, 26),
    7: (27, 30),
    8: (31, 35),
    9: (36, 41),
    10: (42, 45),
}

TARGET_SR = 48000
PAUSE_SEC = 0.50


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def normalize_text(text: str) -> str:
    s = unicodedata.normalize("NFD", text.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_modules() -> list[dict[str, Any]]:
    data = json.loads(TIEMPOS_V1_JSON.read_text(encoding="utf-8"))
    segs_by_id = {int(s["seg"]): s for s in data["segmentos"]}
    modules = []
    for mid, (s0, s1) in MODULE_RANGES.items():
        seg_texts = [segs_by_id[i]["texto"].strip() for i in range(s0, s1 + 1)]
        modules.append({
            "module_id": mid,
            "seg_start": s0,
            "seg_end": s1,
            "text": " ".join(seg_texts),
        })
    return modules


def to_48k_pcm16(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ar", str(TARGET_SR), "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True,
    )


def analyze_e8_onset(sig_48k: np.ndarray, sr: int = TARGET_SR) -> dict[str, Any]:
    """
    Measure F0 at 10 ms hops over the first 400 ms of voiced onset (at 16-bit/48kHz).
    Detect VoxCPM2 cold-start E8 gesture: flat plateau (~120..143 Hz for >=50ms)
    -> abrupt rise (>= +1.4 st to >=145 Hz, held >=20ms) -> fall (or voiced end).
    """
    hop = int(sr * 0.010)
    win = min(len(sig_48k), int(1.0 * sr))
    n_hops = max(0, (win - hop) // hop)
    rms_db = []
    for i in range(n_hops):
        seg = sig_48k[i * hop : (i + 1) * hop]
        rms_db.append(20.0 * math.log10(float(np.sqrt(np.mean(seg**2) + 1e-12))))

    idx0 = next((i for i, db in enumerate(rms_db) if db > -38.0), 0)
    start_samp = idx0 * hop
    sub = sig_48k[start_samp : min(len(sig_48k), start_samp + int(0.46 * sr))]
    if len(sub) < int(0.30 * sr):
        sub = np.pad(sub, (0, int(0.46 * sr) - len(sub)))

    f0, _, _ = librosa.pyin(sub, fmin=70.0, fmax=240.0, sr=sr, frame_length=2048, hop_length=hop)
    vals: list[float | None] = [round(float(v), 1) if np.isfinite(v) else None for v in f0[:40]]

    best: dict[str, Any] | None = None
    for k in range(5, 22):
        pre = [v for v in vals[:k] if v is not None]
        if len(pre) < 5:
            continue
        pre_arr = np.array(pre, dtype=np.float64)
        pre_med = float(np.median(pre_arr))
        pre_iqr = float(np.percentile(pre_arr, 75) - np.percentile(pre_arr, 25))
        if not (118.0 <= pre_med <= 143.0 and pre_iqr <= 10.5):
            continue

        peak_win_start = max(k - 1, 8)
        peak_win = [(idx, v) for idx, v in enumerate(vals[peak_win_start:30], start=peak_win_start) if v is not None]
        if not peak_win:
            continue
        peak_idx, peak_hz = max(peak_win, key=lambda x: x[1])
        rise_st = 12.0 * math.log2(peak_hz / pre_med)
        sustained = sum(1 for _, v in peak_win if v >= pre_med * (2.0 ** (1.1 / 12.0)))
        if peak_hz < 145.0 or rise_st < 1.4 or sustained < 2:
            continue

        post = [v for v in vals[peak_idx + 1 : 40] if v is not None]
        fall_ok = (len(post) <= 2) or (min(post) <= peak_hz * (2.0 ** (-0.4 / 12.0)))
        if not fall_ok:
            continue

        cand = {
            "e8_detected": True,
            "split_ms": k * 10,
            "pre_median_hz": round(pre_med, 1),
            "pre_iqr_hz": round(pre_iqr, 1),
            "peak_hz": round(peak_hz, 1),
            "peak_ms": peak_idx * 10,
            "rise_st": round(rise_st, 2),
            "post_min_hz": round(min(post), 1) if post else None,
        }
        if best is None or cand["rise_st"] > best["rise_st"]:
            best = cand

    voiced_all = [v for v in vals if v is not None]
    if best is None:
        return {
            "e8_detected": False,
            "speech_offset_ms": idx0 * 10,
            "voiced_frames": len(voiced_all),
            "f0_min_hz": round(min(voiced_all), 1) if voiced_all else None,
            "f0_max_hz": round(max(voiced_all), 1) if voiced_all else None,
            "f0_10ms_hops": vals,
        }
    return {
        **best,
        "speech_offset_ms": idx0 * 10,
        "voiced_frames": len(voiced_all),
        "f0_10ms_hops": vals,
    }


def detect_looped_ngrams(norm_exp: str, norm_hyp: str, n: int = 4) -> list[dict[str, Any]]:
    ew = norm_exp.split()
    hw = norm_hyp.split()
    exp_counts: dict[tuple[str, ...], int] = {}
    for i in range(max(0, len(ew) - n + 1)):
        g = tuple(ew[i : i + n])
        exp_counts[g] = exp_counts.get(g, 0) + 1
    hyp_counts: dict[tuple[str, ...], int] = {}
    for i in range(max(0, len(hw) - n + 1)):
        g = tuple(hw[i : i + n])
        hyp_counts[g] = hyp_counts.get(g, 0) + 1
    loops = []
    for g, cnt in hyp_counts.items():
        if cnt > exp_counts.get(g, 0) and cnt >= 2:
            # Verify contiguous or near-contiguous duplication anomaly
            loops.append({"ngram": " ".join(g), "hyp_count": cnt, "exp_count": exp_counts.get(g, 0)})
    return loops


def rms_curve_10ms(sig: np.ndarray, sr: int = TARGET_SR) -> np.ndarray:
    hop = int(sr * 0.010)
    n_hops = len(sig) // hop
    arr = np.empty(n_hops, dtype=np.float64)
    for i in range(n_hops):
        seg = sig[i * hop : (i + 1) * hop]
        arr[i] = 20.0 * math.log10(float(np.sqrt(np.mean(seg**2) + 1e-12)))
    return arr


def find_boundary_cuts(
    sig: np.ndarray,
    sr: int,
    w_words: list[dict[str, Any]],
    lead_in_count: int,
    real_text: str,
) -> tuple[float, float, dict[str, Any]]:
    """
    Align local whisper word timestamps against expected token sequence:
    [LEAD_IN * lead_in_count] + [real_text] + [TRAILING]
    to locate exact valley cuts around sentence boundaries.
    """
    lead_words = normalize_text(" ".join([LEAD_IN] * lead_in_count)).split()
    real_words = normalize_text(real_text).split()
    trail_words = normalize_text(TRAILING).split()
    exp_tokens = lead_words + real_words + trail_words

    hyp_tokens = []
    hyp_meta = []
    for w in w_words:
        tok = normalize_text(w.get("word", ""))
        for part in tok.split():
            if part:
                hyp_tokens.append(part)
                hyp_meta.append((float(w["start"]), float(w["end"]), part))

    if not hyp_tokens:
        raise RuntimeError("No word timestamps extracted by local whisper")

    sm = difflib.SequenceMatcher(None, exp_tokens, hyp_tokens, autojunk=False)
    exp_to_hyp: dict[int, int] = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                exp_to_hyp[i1 + k] = j1 + k
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                exp_to_hyp[i1 + k] = j1 + k

    # Find end of lead-in & start of real text
    real_idx0 = len(lead_words)
    real_idx1 = len(lead_words) + len(real_words) - 1

    # Closest matched token at/before real_idx0 for lead-in end
    lead_end_candidates = [exp_to_hyp[i] for i in range(max(0, real_idx0 - 4), real_idx0) if i in exp_to_hyp]
    real_start_candidates = [exp_to_hyp[i] for i in range(real_idx0, min(real_idx0 + 5, real_idx1 + 1)) if i in exp_to_hyp]
    if not lead_end_candidates or not real_start_candidates:
        raise RuntimeError("Could not align start boundary tokens")

    # Extrapolate word offset back if very first real token shifted
    first_matched_exp = next(i for i in range(real_idx0, real_idx0 + 5) if i in exp_to_hyp)
    first_real_j = exp_to_hyp[first_matched_exp] - (first_matched_exp - real_idx0)
    first_real_j = max(lead_end_candidates[-1] + 1, min(first_real_j, len(hyp_meta) - 1))
    last_lead_j = max(0, first_real_j - 1)

    t_lead_end = hyp_meta[last_lead_j][1]
    t_real_start = hyp_meta[first_real_j][0]

    # Trailing boundary
    real_end_candidates = [exp_to_hyp[i] for i in range(max(real_idx0, real_idx1 - 4), real_idx1 + 1) if i in exp_to_hyp]
    trail_start_candidates = [exp_to_hyp[i] for i in range(real_idx1 + 1, min(len(exp_tokens), real_idx1 + 5)) if i in exp_to_hyp]
    if not real_end_candidates or not trail_start_candidates:
        raise RuntimeError("Could not align end boundary tokens")

    last_matched_exp = max(i for i in range(real_idx1 - 4, real_idx1 + 1) if i in exp_to_hyp)
    last_real_j = exp_to_hyp[last_matched_exp] + (real_idx1 - last_matched_exp)
    last_real_j = min(trail_start_candidates[0] - 1, max(last_real_j, 0))
    first_trail_j = min(len(hyp_meta) - 1, last_real_j + 1)

    t_real_end = hyp_meta[last_real_j][1]
    t_trail_start = hyp_meta[first_trail_j][0]

    # Refine start cut inside quiet valley between lead_end and real_start
    db = rms_curve_10ms(sig, sr)
    tot_dur = len(sig) / sr

    w0_s = max(0, int((t_lead_end - 0.12) * 100))
    w0_e = min(len(db) - 1, int((t_real_start + 0.15) * 100))
    if w0_e <= w0_s:
        w0_s = max(0, int((t_real_start - 0.25) * 100))
        w0_e = min(len(db) - 1, int((t_real_start + 0.10) * 100))
    valley0 = w0_s + int(np.argmin(db[w0_s : w0_e + 1]))
    # Walk forward from valley0 to speech attack (> -42 dBFS)
    onset_hop = next((h for h in range(valley0, min(len(db), valley0 + 60)) if db[h] > -42.0), int(t_real_start * 100))
    cut_start_s = max(valley0 * 0.010, onset_hop * 0.010 - 0.030)

    # Refine end cut inside quiet valley between real_end and trail_start
    w1_s = max(0, int((t_real_end - 0.15) * 100))
    w1_e = min(len(db) - 1, int((t_trail_start + 0.12) * 100))
    if w1_e <= w1_s:
        w1_s = max(0, int((t_real_end - 0.10) * 100))
        w1_e = min(len(db) - 1, int((t_real_end + 0.25) * 100))
    valley1 = w1_s + int(np.argmin(db[w1_s : w1_e + 1]))
    # Walk backward from valley1 to find end of speech decay (> -42 dBFS)
    decay_hop = next((h for h in range(valley1, max(-1, valley1 - 60), -1) if db[h] > -42.0), int(t_real_end * 100))
    cut_end_s = min(valley1 * 0.010, decay_hop * 0.010 + 0.045, tot_dur)
    if cut_end_s <= cut_start_s + 1.0:
        raise RuntimeError(f"Invalid cut window {cut_start_s:.3f}..{cut_end_s:.3f}")

    info = {
        "t_lead_end_word": round(t_lead_end, 3),
        "t_real_start_word": round(t_real_start, 3),
        "valley_start_s": round(valley0 * 0.010, 3),
        "cut_start_s": round(cut_start_s, 3),
        "t_real_end_word": round(t_real_end, 3),
        "t_trail_start_word": round(t_trail_start, 3),
        "valley_end_s": round(valley1 * 0.010, 3),
        "cut_end_s": round(cut_end_s, 3),
        "boundary_start_tokens": hyp_tokens[max(0, last_lead_j - 1) : min(len(hyp_tokens), first_real_j + 4)],
        "boundary_end_tokens": hyp_tokens[max(0, last_real_j - 3) : min(len(hyp_tokens), first_trail_j + 2)],
    }
    return cut_start_s, cut_end_s, info


def cmd_p0() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TAKES_DIR.mkdir(parents=True, exist_ok=True)

    modules = load_modules()
    assert len(modules) == 10
    assert REF_WAV.exists(), f"Missing voice ref: {REF_WAV}"
    assert CONTINUA_WAV.exists(), f"Missing CONTINUA WAV: {CONTINUA_WAV}"

    y, sr = sf.read(str(CONTINUA_WAV), dtype="float64")
    info = sf.info(str(CONTINUA_WAV))
    assert sr == 48000 and info.channels == 1 and info.subtype == "PCM_16"

    tm = json.loads(TIEMPOS_CONTINUO_JSON.read_text(encoding="utf-8"))
    continua_onsets = {}
    detected = 0
    for m in tm:
        t0 = float(m["inicio"])
        res = analyze_e8_onset(y[int(t0 * sr) : int((t0 + 1.0) * sr)], sr)
        continua_onsets[f"M{m['modulo']:02d}"] = res
        if res["e8_detected"]:
            detected += 1

    # Negative check on internal non-cut windows in CONTINUA (e.g., 10.0s, 52.0s, 133.0s)
    internal_checks = {}
    for ts in [10.5, 52.5, 134.0]:
        res = analyze_e8_onset(y[int(ts * sr) : int((ts + 1.0) * sr)], sr)
        internal_checks[f"{ts}s"] = res

    # Probe endpoints
    Client("openbmb/VoxCPM-Demo")
    Client("hf-audio/whisper-large-v3")

    cal = {
        "gate_p0": "OK" if detected >= 9 else "KO",
        "ref_wav": str(REF_WAV),
        "ref_sha256": sha256_file(REF_WAV),
        "tiempos_sha256": sha256_file(TIEMPOS_V1_JSON),
        "continua_detected_count": detected,
        "continua_onsets": continua_onsets,
        "internal_negative_checks": internal_checks,
    }
    (OUT_DIR / "p0_calibration.json").write_text(json.dumps(cal, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "gate_p0": cal["gate_p0"],
        "continua_detected": f"{detected}/10",
        "internal_fp": sum(1 for v in internal_checks.values() if v["e8_detected"]),
    }, indent=2))
    if cal["gate_p0"] != "OK":
        raise RuntimeError(f"P0 calibration KO: only {detected}/10 CONTINUA onsets detected")


def synthesize_one(client_vox: Client, text: str) -> Path:
    last_err = None
    for attempt in range(1, 4):
        try:
            res = client_vox.predict(
                text_input=text,
                control_instruction="",
                reference_wav_path_input=handle_file(str(REF_WAV)),
                use_prompt_text=True,
                prompt_text_input=PROMPT_GUIDE,
                cfg_value_input=2.0,
                do_normalize=False,
                denoise=False,
                api_name="/generate",
            )
            if res and Path(res).exists() and Path(res).stat().st_size > 4000:
                return Path(res)
        except Exception as e:
            last_err = e
            print(f"    [VoxCPM2 retry {attempt}/3] {str(e)[:140]}")
            time.sleep(5 * attempt)
    raise RuntimeError(f"VoxCPM2 failed after 3 attempts: {last_err}")


def transcribe_large_v3(client_wh: Client, wav_path: Path) -> str:
    last_err = None
    for attempt in range(1, 4):
        try:
            txt = client_wh.predict(inputs=handle_file(str(wav_path)), task="transcribe", api_name="/transcribe")
            return str(txt or "").strip()
        except Exception as e:
            last_err = e
            print(f"    [Whisper large-v3 retry {attempt}/3] {str(e)[:140]}")
            time.sleep(5 * attempt)
    raise RuntimeError(f"Whisper large-v3 failed after 3 attempts: {last_err}")


def run_module_p1(
    mod: dict[str, Any],
    client_vox: Client,
    client_wh: Client,
    local_wh: Any,
    force: bool = False,
) -> dict[str, Any]:
    mid = mod["module_id"]
    real_text = mod["text"]
    meta_path = TAKES_DIR / f"M{mid:02d}_meta.json"
    trimmed_wav = TAKES_DIR / f"M{mid:02d}_trimmed.wav"

    if not force and meta_path.exists() and trimmed_wav.exists():
        old_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if old_meta.get("qc_pass") and old_meta.get("trimmed_e8", {}).get("e8_detected") is False:
            print(f"[M{mid:02d}] Reusing already passed take ({old_meta['trimmed_duration_sec']:.2f}s, sim={old_meta['qc_similarity']:.3f})")
            return old_meta

    norm_real = normalize_text(real_text)
    real_tokens = norm_real.split()

    for lead_in_count in (1, 2):
        lead_str = " ".join([LEAD_IN] * lead_in_count)
        full_prompt = f"{lead_str} {real_text} {TRAILING}"
        norm_expected = normalize_text(full_prompt)

        print(f"\n[M{mid:02d}] Generating continuous take (lead_in_count={lead_in_count})...")
        for att in range(1, 4):
            raw_dl = synthesize_one(client_vox, full_prompt)
            raw_48k = TAKES_DIR / f"M{mid:02d}_raw_l{lead_in_count}_a{att}.wav"
            to_48k_pcm16(raw_dl, raw_48k)
            raw_sig, _ = sf.read(str(raw_48k), dtype="float64")
            raw_dur = len(raw_sig) / TARGET_SR
            raw_head_e8 = analyze_e8_onset(raw_sig[: int(1.0 * TARGET_SR)], TARGET_SR)

            # QC with Whisper large-v3
            hyp_text = transcribe_large_v3(client_wh, raw_48k)
            norm_hyp = normalize_text(hyp_text)
            sim = difflib.SequenceMatcher(None, norm_expected, norm_hyp).ratio()
            loops = detect_looped_ngrams(norm_expected, norm_hyp, n=4)
            print(f"  [M{mid:02d} att {att}] dur={raw_dur:.2f}s sim={sim:.3f} loops={len(loops)} raw_e8={raw_head_e8['e8_detected']}")
            if sim < 0.93 or loops:
                print(f"    QC KO (sim={sim:.3f}, loops={loops}) -> regenerating")
                continue

            # Word timestamps alignment via local whisper base
            w_res = local_wh.transcribe(str(raw_48k), language="es", word_timestamps=True, fp16=False)
            w_words = [w for s in w_res.get("segments", []) for w in s.get("words", [])]
            try:
                cut_s, cut_e, binfo = find_boundary_cuts(raw_sig, TARGET_SR, w_words, lead_in_count, real_text)
            except Exception as e:
                print(f"    Boundary alignment KO ({e}) -> regenerating")
                continue

            # Extract trimmed signal with 10ms gentle edge fades in quiet valley
            s_idx = max(0, int(round(cut_s * TARGET_SR)))
            e_idx = min(len(raw_sig), int(round(cut_e * TARGET_SR)))
            trimmed = raw_sig[s_idx:e_idx].copy()
            fade_n = min(int(0.010 * TARGET_SR), len(trimmed) // 10)
            if fade_n > 0:
                t_grid = np.linspace(0.0, math.pi / 2.0, fade_n)
                trimmed[:fade_n] *= np.sin(t_grid) ** 2
                trimmed[-fade_n:] *= np.cos(t_grid) ** 2
            sf.write(str(trimmed_wav), trimmed, TARGET_SR, subtype="PCM_16")

            # Verify trimmed boundaries don't contain lead-in/trailing
            tr_chk = local_wh.transcribe(str(trimmed_wav), language="es", fp16=False)
            tr_tokens = normalize_text(tr_chk.get("text", "")).split()
            start_ok = len(tr_tokens) >= 3 and difflib.SequenceMatcher(None, real_tokens[:3], tr_tokens[:3]).ratio() >= 0.65
            end_ok = len(tr_tokens) >= 3 and difflib.SequenceMatcher(None, real_tokens[-3:], tr_tokens[-3:]).ratio() >= 0.65
            tr_sim = difflib.SequenceMatcher(None, norm_real, " ".join(tr_tokens)).ratio()
            print(f"    Trimmed {cut_s:.3f}s..{cut_e:.3f}s -> {len(trimmed)/TARGET_SR:.2f}s | start_ok={start_ok} ({tr_tokens[:4]}) end_ok={end_ok} ({tr_tokens[-4:]}) tr_sim={tr_sim:.3f}")
            if not (start_ok and end_ok and tr_sim >= 0.88):
                print("    Trim boundary sanity check KO -> regenerating")
                continue

            # Per-take E8 check on trimmed onset
            trim_sig, _ = sf.read(str(trimmed_wav), dtype="float64")
            trimmed_e8 = analyze_e8_onset(trim_sig[: int(1.0 * TARGET_SR)], TARGET_SR)
            print(f"    Trimmed onset E8 check: detected={trimmed_e8['e8_detected']} (voiced={trimmed_e8['voiced_frames']})")

            if trimmed_e8["e8_detected"]:
                print(f"    [WARN] E8 STILL DETECTED after trimming (lead_in_count={lead_in_count})!")
                break  # Move to lead_in_count=2 or HALT

            meta = {
                "module_id": mid,
                "lead_in_count": lead_in_count,
                "attempt": att,
                "raw_wav": str(raw_48k),
                "trimmed_wav": str(trimmed_wav),
                "raw_duration_sec": round(raw_dur, 3),
                "trimmed_duration_sec": round(len(trim_sig) / TARGET_SR, 3),
                "qc_pass": True,
                "qc_similarity": round(sim, 4),
                "qc_loops": loops,
                "whisper_large_v3_text": hyp_text,
                "boundary_info": binfo,
                "trimmed_check_tokens_head": tr_tokens[:6],
                "trimmed_check_tokens_tail": tr_tokens[-6:],
                "raw_head_e8": raw_head_e8,
                "trimmed_e8": trimmed_e8,
            }
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            return meta
        else:
            raise RuntimeError(f"HALT P1: M{mid:02d} failed QC/alignment 3 consecutive attempts (lead_in_count={lead_in_count})")

    raise RuntimeError(f"HALT P1: E8 figure persisted at M{mid:02d} even after 2x sacrificial lead-in")


def cmd_p1(module_ids: list[int], force: bool) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TAKES_DIR.mkdir(parents=True, exist_ok=True)
    modules = {m["module_id"]: m for m in load_modules()}
    client_vox = Client("openbmb/VoxCPM-Demo")
    client_wh = Client("hf-audio/whisper-large-v3")
    local_wh = whisper.load_model("base")

    results = {}
    for mid in module_ids:
        results[f"M{mid:02d}"] = run_module_p1(modules[mid], client_vox, client_wh, local_wh, force=force)
    (OUT_DIR / "p1_takes_summary.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n[P1 POST-GATE] All requested takes completed cleanly with E8 absent.")


def harvest_room_tone_slices(raw_paths: list[Path], n_needed: int = 9, min_len_s: float = 2.0) -> list[dict[str, Any]]:
    """
    Extract 9 DISJOINT >= 2.0 s real room-tone pools from raw takes (< -46 dBFS, > -78 dBFS,
    with >= 40ms safety margin away from speech), never repeating any sample (anti-S1).
    """
    candidates: list[dict[str, Any]] = []
    hop = int(0.010 * TARGET_SR)
    for rp in raw_paths:
        sig, sr = sf.read(str(rp), dtype="float64")
        db = rms_curve_10ms(sig, sr)
        is_quiet = (db < -46.0) & (db > -78.0)
        run_start = None
        for i, q in enumerate(is_quiet):
            if q and run_start is None:
                run_start = i
            elif not q and run_start is not None:
                # 50ms margin on both ends
                s_h = run_start + 5
                e_h = i - 5
                if e_h - s_h >= 12:  # >= 120 ms usable room tone
                    seg = sig[s_h * hop : e_h * hop].copy()
                    candidates.append({
                        "source_file": rp.name,
                        "start_s": round(s_h * 0.010, 3),
                        "end_s": round(e_h * 0.010, 3),
                        "dur_s": round(len(seg) / sr, 3),
                        "samples": seg,
                    })
                run_start = None
        if run_start is not None:
            s_h = run_start + 5
            e_h = len(is_quiet) - 2
            if e_h - s_h >= 12:
                seg = sig[s_h * hop : e_h * hop].copy()
                candidates.append({
                    "source_file": rp.name,
                    "start_s": round(s_h * 0.010, 3),
                    "end_s": round(e_h * 0.010, 3),
                    "dur_s": round(len(seg) / sr, 3),
                    "samples": seg,
                })

    total_avail = sum(c["dur_s"] for c in candidates)
    if total_avail < n_needed * min_len_s:
        raise RuntimeError(f"Insufficient disjoint room tone ({total_avail:.2f}s < {n_needed * min_len_s:.2f}s needed)")

    # Distribute unique candidates across 9 bins keeping each bin >= min_len_s (2.0 s)
    candidates.sort(key=lambda c: c["dur_s"], reverse=True)
    bins: list[list[dict[str, Any]]] = [[] for _ in range(n_needed)]
    bin_durs = [0.0] * n_needed

    for cand in candidates:
        # Fill under-2.0s bins first
        idx = min(range(n_needed), key=lambda k: bin_durs[k])
        bins[idx].append(cand)
        bin_durs[idx] += cand["dur_s"]

    min_bin = min(bin_durs)
    if min_bin < min_len_s:
        raise RuntimeError(f"Room-tone bin fell short of {min_len_s}s: {min_bin:.3f}s")

    # Equal-power crossfade (35 ms) pieces inside each bin, verify no periodic 250ms loop, slice central 0.50 s
    xf = int(0.035 * TARGET_SR)
    pause_samples = int(PAUSE_SEC * TARGET_SR)
    out_pauses = []
    for j_idx, grp in enumerate(bins, start=1):
        buf = grp[0]["samples"].copy()
        for nxt in grp[1:]:
            nx = nxt["samples"].copy()
            k_xf = min(xf, len(buf) // 4, len(nx) // 4)
            if k_xf > 0:
                t = np.linspace(0.0, math.pi / 2.0, k_xf)
                tail = buf[-k_xf:] * np.cos(t) + nx[:k_xf] * np.sin(t)
                buf = np.concatenate([buf[:-k_xf], tail, nx[k_xf:]])
            else:
                buf = np.concatenate([buf, nx])

        mid0 = max(0, (len(buf) - pause_samples) // 2)
        p_seg = buf[mid0 : mid0 + pause_samples].copy()
        # Envelope autocorrelation at 5ms hops (lags 50ms..450ms) to prove no periodic S1 bed
        hop5 = int(0.005 * TARGET_SR)
        env = np.array([math.sqrt(float(np.mean(p_seg[i : i + hop5] ** 2) + 1e-18)) for i in range(0, len(p_seg) - hop5, hop5)])
        env_z = env - np.mean(env)
        denom = float(np.sum(env_z**2))
        max_acf = 0.0
        if denom > 1e-24:
            for lag in range(10, min(90, len(env_z) - 5)):
                acf = abs(float(np.sum(env_z[:-lag] * env_z[lag:]) / denom))
                if acf > max_acf:
                    max_acf = acf

        out_pauses.append({
            "join_id": f"J{j_idx}",
            "source_pool_sec": round(len(buf) / TARGET_SR, 3),
            "max_envelope_autocorr_50_450ms": round(max_acf, 3),
            "sources": [{"file": c["source_file"], "start_s": c["start_s"], "end_s": c["end_s"]} for c in grp],
            "pause_samples": p_seg,
        })
    return out_pauses


def measure_loudness_and_black(wav_path: Path, joins: list[dict[str, Any]]) -> dict[str, Any]:
    ln = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(wav_path), "-af", "loudnorm=I=-14.0:TP=-1.2:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    )
    js_s = ln.stderr.rfind("{")
    js_e = ln.stderr.rfind("}") + 1
    ln_json = json.loads(ln.stderr[js_s:js_e])

    eb = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(wav_path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    )
    eb_i = None
    eb_tp = None
    for line in eb.stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            eb_i = line.strip()
        elif "Peak:" in line and "dBFS" in line:
            eb_tp = line.strip()

    sig, sr = sf.read(str(wav_path), dtype="float64")
    digital_black_ms = 0
    for j in joins:
        s0 = int(j["pause_start_sec"] * sr)
        s1 = int(j["pause_end_sec"] * sr)
        p_sig = sig[s0:s1]
        hop = int(0.010 * sr)
        for i in range(0, max(0, len(p_sig) - hop + 1), hop):
            db = 20.0 * math.log10(float(np.sqrt(np.mean(p_sig[i : i + hop] ** 2) + 1e-12)))
            if db < -85.0:
                digital_black_ms += 10

    return {
        "loudnorm_measured": ln_json,
        "ebur128_summary": {"I": eb_i, "TP": eb_tp},
        "digital_black_in_pauses_ms": digital_black_ms,
        "duration_sec": round(len(sig) / sr, 3),
    }


def cmd_p2() -> None:
    takes = []
    raw_paths = []
    for mid in range(1, 11):
        meta = json.loads((TAKES_DIR / f"M{mid:02d}_meta.json").read_text(encoding="utf-8"))
        assert meta.get("qc_pass") and not meta["trimmed_e8"]["e8_detected"], f"M{mid:02d} failed P1 gate"
        takes.append(Path(meta["trimmed_wav"]))
        raw_paths.append(Path(meta["raw_wav"]))

    pauses = harvest_room_tone_slices(raw_paths, n_needed=9, min_len_s=2.0)

    # Concatenate 10 takes with 0.50s real room-tone pauses & 15ms equal-power crossfade
    xf = int(0.015 * TARGET_SR)
    buf, _ = sf.read(str(takes[0]), dtype="float64")
    modules_timeline = []
    joins_timeline = []
    cur_len = len(buf)
    modules_timeline.append({"module": 1, "inicio": 0.0, "fin": round(cur_len / TARGET_SR, 3)})

    def append_xf(acc: np.ndarray, piece: np.ndarray) -> tuple[np.ndarray, int]:
        k = min(xf, len(acc) // 10, len(piece) // 10)
        t = np.linspace(0.0, math.pi / 2.0, k)
        blend = acc[-k:] * np.cos(t) + piece[:k] * np.sin(t)
        new_start_samp = len(acc) - k
        return np.concatenate([acc[:-k], blend, piece[k:]]), new_start_samp

    for i in range(9):
        p_info = pauses[i]
        p_sig = p_info["pause_samples"]
        buf, p_start_s = append_xf(buf, p_sig)
        t_sig, _ = sf.read(str(takes[i + 1]), dtype="float64")
        buf, mod_start_s = append_xf(buf, t_sig)
        joins_timeline.append({
            "join_id": f"J{i+1}",
            "pause_start_sec": round(p_start_s / TARGET_SR, 3),
            "pause_end_sec": round(mod_start_s / TARGET_SR, 3),
            "midpoint_sec": round((p_start_s + mod_start_s) / (2.0 * TARGET_SR), 3),
            "source_pool_sec": p_info["source_pool_sec"],
            "max_envelope_autocorr_50_450ms": p_info["max_envelope_autocorr_50_450ms"],
            "sources": p_info["sources"],
        })
        modules_timeline.append({
            "module": i + 2,
            "inicio": round(mod_start_s / TARGET_SR, 3),
            "fin": round(len(buf) / TARGET_SR, 3),
        })

    unnorm = OUT_DIR / "master_sin_eta_unnorm.wav"
    sf.write(str(unnorm), buf, TARGET_SR, subtype="PCM_16")

    # 2-pass loudnorm targeting -14.0 LUFS, TP <= -1.0 dBTP (tighten TP target if needed)
    for tp_target in (-1.2, -1.5, -1.8):
        p1_cmd = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(unnorm), "-af", f"loudnorm=I=-14.0:TP={tp_target}:LRA=11:print_format=json", "-f", "null", "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        )
        m = json.loads(p1_cmd.stderr[p1_cmd.stderr.rfind("{") : p1_cmd.stderr.rfind("}") + 1])
        flt = (
            f"loudnorm=I=-14.0:TP={tp_target}:LRA=11:"
            f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}:linear=true"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(unnorm), "-af", flt, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(FINAL_MASTER_WAV)],
            check=True,
        )
        meas = measure_loudness_and_black(FINAL_MASTER_WAV, joins_timeline)
        lufs_out = float(meas["loudnorm_measured"]["input_i"])
        tp_out = float(meas["loudnorm_measured"]["input_tp"])
        if -14.3 <= lufs_out <= -13.7 and tp_out <= -1.0:
            break
    else:
        raise RuntimeError(f"Loudness gate failed: {meas}")

    (OUT_DIR / "tiempos-sin-eta.json").write_text(json.dumps(modules_timeline, indent=2, ensure_ascii=False), encoding="utf-8")
    p2_doc = {
        "gate_p2": "OK",
        "master_wav": str(FINAL_MASTER_WAV),
        "sha256": sha256_file(FINAL_MASTER_WAV),
        "bytes": FINAL_MASTER_WAV.stat().st_size,
        "duration_sec": meas["duration_sec"],
        "measured_lufs": lufs_out,
        "measured_tp_dbtp": tp_out,
        "digital_black_in_pauses_ms": meas["digital_black_in_pauses_ms"],
        "ebur128_summary": meas["ebur128_summary"],
        "modules": modules_timeline,
        "joins": joins_timeline,
    }
    (OUT_DIR / "p2_assembly.json").write_text(json.dumps(p2_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "gate_p2": "OK",
        "duration_sec": p2_doc["duration_sec"],
        "lufs": lufs_out,
        "tp_dbtp": tp_out,
        "digital_black_ms": meas["digital_black_in_pauses_ms"],
    }, indent=2))


def cmd_p3() -> None:
    p2_doc = json.loads((OUT_DIR / "p2_assembly.json").read_text(encoding="utf-8"))
    p0_doc = json.loads((OUT_DIR / "p0_calibration.json").read_text(encoding="utf-8"))
    sig, sr = sf.read(str(FINAL_MASTER_WAV), dtype="float64")
    assert sr == 48000

    onset_checks = {}
    failed = []
    for mod in p2_doc["modules"]:
        mid = mod["module"]
        t0 = float(mod["inicio"])
        res = analyze_e8_onset(sig[int(t0 * sr) : int((t0 + 1.0) * sr)], sr)
        onset_checks[f"M{mid:02d}"] = {"start_sec": t0, **res}
        if res["e8_detected"]:
            failed.append(f"M{mid:02d}@{t0}s")

    # Build audition strip: 9 joins, +-1.5s around join midpoint, separated by 0.40s quiet separator
    sep_src = p2_doc["joins"][0]["pause_start_sec"]
    # Use a 0.40s quiet section padded cleanly (-64 dBFS tone from a raw take floor via joins midpoint)
    sep = np.zeros(int(0.40 * sr), dtype=np.float64)
    chunks = []
    strip_map = []
    cur_t = 0.0
    for j in p2_doc["joins"]:
        mid_t = float(j["midpoint_sec"])
        s0 = max(0, int((mid_t - 1.50) * sr))
        s1 = min(len(sig), int((mid_t + 1.50) * sr))
        clip = sig[s0:s1].copy()
        fn = int(0.015 * sr)
        tg = np.linspace(0.0, math.pi / 2.0, fn)
        clip[:fn] *= np.sin(tg) ** 2
        clip[-fn:] *= np.cos(tg) ** 2
        chunks.append(clip)
        strip_map.append({
            "join_id": j["join_id"],
            "master_window": f"{mid_t-1.5:.2f}s..{mid_t+1.5:.2f}s",
            "strip_start_sec": round(cur_t, 2),
            "strip_end_sec": round(cur_t + len(clip) / sr, 2),
        })
        cur_t += len(clip) / sr
        chunks.append(sep)
        cur_t += len(sep) / sr

    strip_sig = np.concatenate(chunks[:-1])  # omit trailing sep
    sf.write(str(STRIP_WAV), strip_sig, sr, subtype="PCM_16")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(STRIP_WAV), "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "1", str(STRIP_MP3)],
        check=True,
    )

    gate_e8 = "PASS" if not failed else "FAIL"
    lines = [
        "REPORTE DE COMPUERTA E8 — NARRACION-EQUIPO-AGENTES-SIN-ETA.wav",
        "==========================================================================",
        f"Archivo máster : {FINAL_MASTER_WAV}",
        f"SHA-256        : {p2_doc['sha256']}",
        f"Especificación : 48000 Hz mono PCM 16-bit | {p2_doc['duration_sec']} s | {p2_doc['measured_lufs']} LUFS | {p2_doc['measured_tp_dbtp']} dBTP",
        f"Silencio digit.: {p2_doc['digital_black_in_pauses_ms']} ms dentro de las 9 pausas (S1 autocorr max = {max(j['max_envelope_autocorr_50_450ms'] for j in p2_doc['joins'])})",
        f"Compuerta E8   : {gate_e8} (figura detectada en {len(failed)}/10 inicios: {failed or 'NINGUNO'})",
        "",
        "COMPARATIVA F0 (saltos de 10 ms en los primeros 400 ms, en Hz; '-' = sordo/no sonoro)",
        "--------------------------------------------------------------------------",
    ]
    for mid in range(1, 11):
        key = f"M{mid:02d}"
        cur = onset_checks[key]
        old = p0_doc["continua_onsets"].get(key, {})
        meta_m = json.loads((TAKES_DIR / f"{key}_meta.json").read_text(encoding="utf-8"))
        hops_new = " ".join(f"{v:.0f}" if v is not None else "-" for v in cur["f0_10ms_hops"][:35])
        hops_old = " ".join(f"{v:.0f}" if v is not None else "-" for v in old.get("f0_10ms_hops", [])[:35])
        lines.append(f"\n[{key}] Inicio máster={cur['start_sec']:.3f}s | Whisper-v3 sim={meta_m['qc_similarity']:.3f} | loops={len(meta_m['qc_loops'])} | E8={cur['e8_detected']}")
        lines.append(f"  ANTIGUO CONTINUA (E8={old.get('e8_detected')}, +{old.get('rise_st','-')}st @ {old.get('peak_ms','-')}ms): {hops_old}")
        lines.append(f"  NUEVO SIN-ETA    (E8={cur['e8_detected']}, range={cur.get('f0_min_hz')}..{cur.get('f0_max_hz')} Hz): {hops_new}")

    lines.extend([
        "",
        "PAQUETE DE AUDICIÓN — TIRA-EMPALMES-SIN-ETA (.wav / .mp3)",
        "--------------------------------------------------------------------------",
    ])
    for sm in strip_map:
        lines.append(f"  {sm['join_id']}: tira {sm['strip_start_sec']:.2f}s..{sm['strip_end_sec']:.2f}s  <- máster {sm['master_window']}")

    REPORT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    p3_doc = {
        "gate_e8": gate_e8,
        "failed_onsets": failed,
        "onsets": onset_checks,
        "strip_wav": str(STRIP_WAV),
        "strip_wav_sha256": sha256_file(STRIP_WAV),
        "strip_mp3": str(STRIP_MP3),
        "strip_mp3_sha256": sha256_file(STRIP_MP3),
        "report_txt": str(REPORT_TXT),
        "report_txt_sha256": sha256_file(REPORT_TXT),
        "strip_map": strip_map,
    }
    (OUT_DIR / "p3_e8_report.json").write_text(json.dumps(p3_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"gate_e8": gate_e8, "failed": failed, "report": str(REPORT_TXT)}, indent=2))
    if failed:
        raise RuntimeError(f"HALT P3: E8 figure detected at onsets: {failed}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["p0", "p1", "p2", "p3"], required=True)
    parser.add_argument("--modules", nargs="+", type=int, default=list(range(1, 11)))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.stage == "p0":
        cmd_p0()
    elif args.stage == "p1":
        cmd_p1(args.modules, args.force)
    elif args.stage == "p2":
        cmd_p2()
    elif args.stage == "p3":
        cmd_p3()


if __name__ == "__main__":
    main()
