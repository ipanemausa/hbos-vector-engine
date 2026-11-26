#!/usr/bin/env python3
"""Seal official transparent smiling avatar pack in G:\\My Drive\\AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS, index in Qdrant, and auto-launch pilot."""

import json
import os
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

from PIL import Image
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

SRC_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\avatar_v2_transparencias")
OFFICIAL_DIR = Path(r"G:\My Drive\AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS")
PILOT_MP4 = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\piloto_v2_sonrisa_8s.mp4")

MAP_NAMES = [
    ("guillermo_v2_01_bienvenida_sonrisa.png", "guillermo_oficial_01_bienvenida.png"),
    ("guillermo_v2_02_senala_derecha.png", "guillermo_oficial_02_senala_derecha.png"),
    ("guillermo_v2_03_pensativo_menton.png", "guillermo_oficial_03_pensativo_menton.png"),
    ("guillermo_v2_04_enfasis_tecnico.png", "guillermo_oficial_04_enfasis_tecnico.png"),
    ("guillermo_v2_05_saludo_cierre.png", "guillermo_oficial_05_saludo_cierre.png"),
]


def main() -> None:
    print("=== SELLANDO AVATAR OFICIAL EN TRANSPARENCIA (G:\\My Drive) ===", flush=True)
    OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OFFICIAL_DIR / "AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS.zip"

    entries = []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src_name, dst_name in MAP_NAMES:
            src_p = SRC_DIR / src_name
            dst_p = OFFICIAL_DIR / dst_name
            if not src_p.exists():
                raise FileNotFoundError(f"Falta transparencia RGBA: {src_p}")
            shutil.copy2(str(src_p), str(dst_p))
            zf.write(str(dst_p), arcname=dst_name)
            with Image.open(dst_p) as im:
                entries.append({
                    "name": dst_name,
                    "path": str(dst_p),
                    "mode": im.mode,
                    "size": [im.width, im.height],
                    "bytes": dst_p.stat().st_size,
                    "sha256": cfg.sha256_file(dst_p),
                })

    zip_sha = cfg.sha256_file(zip_path)
    manifest = {
        "canonical_id": "AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS_V2",
        "status": "CANONICAL_APPROVED_AVATAR_V2",
        "owner": "Guillermo Alonso Hoyos (Guía Hoy)",
        "official_dir": str(OFFICIAL_DIR),
        "zip_archive": str(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": zip_sha,
        "pilot_video_verified": str(PILOT_MP4),
        "poses": entries,
    }
    manifest_path = OFFICIAL_DIR / "AVATAR_OFICIAL_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[1/3] Carpeta y ZIP sellados: {zip_path} ({zip_path.stat().st_size} B)", flush=True)

    # Index in Qdrant hbos_nodo_avatar_768d (768D)
    try:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", local_files_only=True)
    except Exception:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    desc = (
        f"AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS_V2 Guillermo Alonso Hoyos sonrisa natural RGBA PNG transparente "
        f"HB.OS SOVEREIGN AI ruta oficial {OFFICIAL_DIR} zip {zip_path}"
    )
    vec768 = [float(x) for x in model.encode([desc], normalize_embeddings=True, show_progress_bar=False)[0]]
    assert len(vec768) == 768
    pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"avatar_oficial_v2_{zip_sha}"))
    cfg.qdrant_http(
        "/collections/hbos_nodo_avatar_768d/points?wait=true",
        method="PUT",
        data={"points": [{"id": pid, "vector": vec768, "payload": manifest}]},
    )
    print(f"[2/3] Indexado en Qdrant hbos_nodo_avatar_768d (ID={pid})", flush=True)

    if PILOT_MP4.exists():
        try:
            os.startfile(str(PILOT_MP4))
            print(f"[3/3] RULE_AUTO_LAUNCH_01 lanzado: {PILOT_MP4}", flush=True)
        except Exception as exc:
            print(f"[WARN] os.startfile: {exc}", flush=True)


if __name__ == "__main__":
    main()
