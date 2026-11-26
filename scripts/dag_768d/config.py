"""Shared configuration and utilities for the HBOS DAG 768D video pipeline."""

import hashlib
import json
import urllib.request
from pathlib import Path

AUDIO_MASTER = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy_voxcpm\equipo_agentes_ia_master.wav")
AUDIO_BACKUP = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy\equipo_agentes_ia_guiahoy.wav")
TIEMPOS_SRC = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy_voxcpm\tiempos.json")
FONDOS_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\fondos_16x9")
AVATAR_TRANSP_DIR = Path(r"G:\My Drive\Avatar Guillermo - transparencias")
AVATAR_CLIP_LIB = Path(r"G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library")

OUT_ROOT = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_build")
BUILD_DIR = OUT_ROOT / "build"
AVATAR_ALPHA_DIR = BUILD_DIR / "avatar_alpha"
CONTROL_CLIPS_DIR = BUILD_DIR / "control_clips"
FINAL_DIR = OUT_ROOT / "final"
FINAL_MP4 = FINAL_DIR / "EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4"
VAULT_MP4 = Path(r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4")

LOCAL_TEMP = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\temp_dag_768d")
ARTIFACT_DIR = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83")

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "hbos_equipo_agentes_768"
QDRANT_CANON_COLLECTION = "canon_video_hbos_r768"

TARGET_W = 1920
TARGET_H = 1080
TARGET_FPS = 60

# 20 clean RGBA poses covering the 10 script blocks and complementary gestures
SELECTED_POSES = [
    "avatar-pose-t-arms-open-narrower.png",
    "avatar-pose-t-calm-both.png",
    "avatar-pose-t-chin-stroke-L.png",
    "avatar-pose-t-arms-open-palms-up.png",
    "avatar-pose-t-chin-stroke-R.png",
    "avatar-pose-t-arms-open-wider.png",
    "avatar-pose-t-arms-open-palms-front.png",
    "avatar-pose-t-both-thumbs-up.png",
    "avatar-pose-t-beckon-R.png",
    "avatar-pose-t-arms-relaxed.png",
    "avatar-pose-t-arms-crossed.png",
    "avatar-pose-t-arms-open-palms-down.png",
    "avatar-pose-t-beckon-L.png",
    "avatar-pose-t-count-two-R.png",
    "avatar-pose-t-count-three-R.png",
    "avatar-pose-t-point-up-R.png",
    "avatar-pose-t-point-left-L.png",
    "avatar-pose-t-point-right-R.png",
    "avatar-pose-t-explain-R.png",
    "avatar-pose-t-wave-R.png",
]


def ensure_dirs() -> None:
    """Create all persistent build/final and local temporary directories."""
    for d in [BUILD_DIR, AVATAR_ALPHA_DIR, CONTROL_CLIPS_DIR, FINAL_DIR, LOCAL_TEMP, VAULT_MP4.parent]:
        d.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def qdrant_http(endpoint: str, method: str = "GET", data: dict | None = None, timeout: int = 15) -> dict:
    """Perform JSON HTTP request against Qdrant REST API."""
    url = f"{QDRANT_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
