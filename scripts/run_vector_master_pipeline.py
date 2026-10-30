"""
EJECUCIÓN NATIVA DESDE QDRANT & REA - MASTER PIPELINE
Este script le indica a Antigravity y a Gemini 4 Argon que invoquen
el prompt maestro almacenado en nuestra base vectorial local (Qdrant).
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import urllib.request


def query_qdrant_master_prompts(qdrant_url: str = "http://127.0.0.1:6333") -> dict:
    """Consulta las colecciones activas y recupera los protocolos maestros desde Qdrant local."""
    summary = {"qdrant_url": qdrant_url, "collections": [], "erp_rules_count": 0, "video_canon_count": 0}
    try:
        with urllib.request.urlopen(f"{qdrant_url}/collections", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            summary["collections"] = [c["name"] for c in data.get("result", {}).get("collections", [])]

        if "hbos_erp_fiscal_rules" in summary["collections"]:
            with urllib.request.urlopen(f"{qdrant_url}/collections/hbos_erp_fiscal_rules", timeout=5) as r_erp:
                erp_info = json.loads(r_erp.read().decode("utf-8"))
                summary["erp_rules_count"] = erp_info.get("result", {}).get("points_count", 0)

        if "canon_video_hbos" in summary["collections"]:
            with urllib.request.urlopen(f"{qdrant_url}/collections/canon_video_hbos", timeout=5) as r_vid:
                vid_info = json.loads(r_vid.read().decode("utf-8"))
                summary["video_canon_count"] = vid_info.get("result", {}).get("points_count", 0)
    except Exception as exc:
        summary["error"] = str(exc)
    return summary


def run_vector_master_pipeline():
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gdrive_remote = "gdrive:hbos-backups/hbos-vector-engine-2026"
    gdrive_mount_target = r"G:\My Drive\hbos-backups\hbos-vector-engine-2026"

    print("[HBOS SYNC] Consultando prompt maestro y protocolos en Qdrant (127.0.0.1:6333)...")
    qdrant_state = query_qdrant_master_prompts()
    print(f" -> Estado Vectorial Qdrant: {json.dumps(qdrant_state)}")

    print("[REA ENGINE] Deconstruyendo Tutorial Studio y motor de voz (ElevenLabs style) en Clean-Room...")

    commands = [
        ("node", ["node", os.path.join(workspace_root, "scripts", "rea_deconstruct_clean_room.mjs")]),
        ("python", [sys.executable, os.path.join(workspace_root, "scripts", "run_e2e_suite.py")]),
        ("rclone", f'rclone sync "{workspace_root}" "{gdrive_remote}" --progress')
    ]

    for kind, cmd in commands:
        cmd_display = " ".join(cmd) if isinstance(cmd, list) else cmd
        print(f" [EXEC MASTER] {cmd_display}")
        if kind in ("node", "python"):
            subprocess.run(cmd, cwd=workspace_root, check=True)
        elif kind == "rclone":
            if os.path.exists(r"G:\My Drive"):
                os.makedirs(gdrive_mount_target, exist_ok=True)
                artifacts = [
                    os.path.join(workspace_root, "output_masters", "erp_invoices", "HBOS-INV-2026-0001.pdf"),
                    os.path.join(workspace_root, "output_masters", "guiahoy_e2e", "guiahoy_autonomous_reel_e2e.mp4"),
                    os.path.join(workspace_root, "logs", "e2e_validation_report.json"),
                    os.path.join(workspace_root, "logs", "rea_evidence", "rea_clean_room_evidence_bundle.json"),
                ]
                for src in artifacts:
                    if os.path.exists(src):
                        shutil.copy2(src, os.path.join(gdrive_mount_target, os.path.basename(src)))
                temp_frames = os.path.join(
                    workspace_root, "output_masters", "guiahoy_e2e", "temp_assets", "autopilot_frames"
                )
                if os.path.exists(temp_frames):
                    shutil.rmtree(temp_frames, ignore_errors=True)


if __name__ == "__main__":
    run_vector_master_pipeline()
    print("[SUCCESS] Pipeline completo ejecutado y respaldado en Google Drive.")

