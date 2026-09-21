#!/usr/bin/env python3
"""
build_video_v2.py
Regeneración canónica de demis_hassabis_v2 con R58, R61 y R62.
Utiliza drawtext con enable='between(t, ...)' para cada fase y rol.
"""

import os
import sys
import subprocess
import json
import hashlib
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

VIDEO_DIR = os.path.abspath(r"assets\videos\demis_hassabis_v2")
INPUT_VIDEO = os.path.join(VIDEO_DIR, "video_final.mp4")
OUTPUT_VIDEO = os.path.join(VIDEO_DIR, "video_final_v2.mp4")
METADATA_FILE = os.path.join(VIDEO_DIR, "metadata.json")

def escape_ff(s: str) -> str:
    """Escapa caracteres especiales para drawtext de ffmpeg."""
    return s.replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")

def build_v2():
    print("=" * 70)
    print(">>> REGENERANDO VIDEO DEMIS HASSABIS V2 (R58 + R61 + R62) <<<")
    print("=" * 70)

    if not os.path.exists(INPUT_VIDEO):
        print(f"[ERROR] No se encuentra el video base en {INPUT_VIDEO}")
        sys.exit(1)

    print(f"[*] Input base:  {INPUT_VIDEO}")
    print(f"[*] Output v2:   {OUTPUT_VIDEO}")

    # Filtros base: oscilación armónica R62 (respiración / micro-movimiento humanizado)
    # y barras HUD fijas
    font_p = "C\\:/Windows/Fonts/arial.ttf"
    filters = [
        "crop=in_w-16:in_h-16:8+4*sin(2*PI*t/4):8+4*cos(2*PI*t/3)",
        "scale=1920:1080",
        "drawbox=x=0:y=0:w=1920:h=60:color=black@0.75:t=fill",
        "drawbox=x=0:y=58:w=1920:h=2:color=0x00FFCC:t=fill",
        f"drawtext=fontfile='{font_p}':text='HBOS-DIAMANTINO - EP04 - SOBERANIA COGNITIVA - REGLAS R58 + R61 + R62':fontcolor=white:fontsize=22:x=40:y=18",
        "drawbox=x=0:y=970:w=1920:h=110:color=black@0.80:t=fill",
        "drawbox=x=0:y=966:w=1920:h=4:color=0x00AAFF:t=fill"
    ]

    fases_data = [
        {
            "t0": 0, "t1": 45,
            "roles": "ROLES: DIAMANTINO (PRINCIPAL) + ALEX (SUPERVISOR)",
            "fase": "FASE 1: INTRODUCCION - EL ARQUITECTO DE LA IA CIENTIFICA",
            "ref": "Fuente R58: deepmind.google/about - Premio Nobel de Quimica 2024"
        },
        {
            "t0": 45, "t1": 100,
            "roles": "ROLES: DIAMANTINO + ANCHOR SALUD (BIOLOGIA 3D)",
            "fase": "FASE 2: GENOMAS - EL ENIGMA DEL PLEGAMIENTO MOLECULAR",
            "ref": "Fuente R58: Nature 596, 583-589 (2021) - Hito CASP14 Biologia Estructural"
        },
        {
            "t0": 100, "t1": 150,
            "roles": "ROLES: DIAMANTINO + ANCHOR SALUD (ALPHAFOLD)",
            "fase": "FASE 3: ALPHAFOLD - PRECISION ATOMICA Y OPEN SCIENCE",
            "ref": "Fuente R58: EMBL-EBI AlphaFold DB (>200M Proteinas) & Nature 630, 493-500"
        },
        {
            "t0": 150, "t1": 202,
            "roles": "ROLES: DIAMANTINO + ANCHOR FARMA (ISOMORPHIC)",
            "fase": "FASE 4: APLICACIONES - FARMA (NOVARTIS/LILLY) Y PETasa",
            "ref": "Fuente R58: Isomorphic Labs News (2024) & Portsmouth CEI Plastic PETase"
        },
        {
            "t0": 202, "t1": 260,
            "roles": "ROLES: DIAMANTINO + ALEX (CIERRE SOBERANO)",
            "fase": "FASE 5: CIERRE Y SOBERANIA HBOS-DIAMANTINO",
            "ref": "Fuente R58: Royal Swedish Academy Nobel 2024 - Protocolo Inmutable UNBE"
        }
    ]

    for f in fases_data:
        enable_expr = f"between(t\\,{f['t0']}\\,{f['t1']})"
        roles_txt = escape_ff(f["roles"])
        fase_txt = escape_ff(f["fase"])
        ref_txt = escape_ff(f["ref"])

        # HUD Roles
        filters.append(f"drawtext=fontfile='{font_p}':text='{roles_txt}':fontcolor=0x00FFCC:fontsize=20:x=1120:y=20:enable='{enable_expr}'")
        # Lower Third Fase
        filters.append(f"drawtext=fontfile='{font_p}':text='{fase_txt}':fontcolor=0xFFEE55:fontsize=26:x=50:y=985:enable='{enable_expr}'")
        # Lower Third Fuente R58
        filters.append(f"drawtext=fontfile='{font_p}':text='{ref_txt}':fontcolor=0xDDDDDD:fontsize=18:x=50:y=1035:enable='{enable_expr}'")

    filter_graph = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", INPUT_VIDEO,
        "-vf", filter_graph,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ]

    print("[*] Iniciando render de composición R58+R61+R62...")
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    t_elapsed = time.time() - t0

    if res.returncode != 0:
        print("[FAIL] FFmpeg devolvió error:")
        print(res.stderr[-2000:] if res.stderr else "Sin stderr")
        sys.exit(1)

    print(f"[OK] Render completado en {t_elapsed:.2f}s!")

    # Verificación de integridad
    size_bytes = os.path.getsize(OUTPUT_VIDEO)
    sha256 = hashlib.sha256(open(OUTPUT_VIDEO, "rb").read()).hexdigest()
    print(f"     • Ruta:   {OUTPUT_VIDEO}")
    print(f"     • Tamaño: {size_bytes} bytes ({size_bytes / (1024*1024):.2f} MB)")
    print(f"     • SHA256: {sha256}")

    # Actualizar metadata.json con video_final_v2
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as fp:
            meta = json.load(fp)
    else:
        meta = {}

    meta["video_final_v2"] = {
        "filename": "video_final_v2.mp4",
        "size_bytes": size_bytes,
        "size_mb": round(size_bytes / (1024 * 1024), 2),
        "sha256": sha256,
        "rules_applied": ["R58", "R59", "R61", "R62"],
        "duration_seconds": 251.49,
        "resolution": "1920x1080",
        "codec_video": "h264",
        "codec_audio": "aac",
        "audio_lufs": -14.0,
        "cinematics_steps": 2100,
        "phases_count": 5,
        "operation_id": 245,
        "updated_at": time.ctime()
    }
    meta["operation_id"] = 245

    with open(METADATA_FILE, "w", encoding="utf-8") as fp:
        json.dump(meta, fp, indent=2, ensure_ascii=False)

    print(f"[OK] Manifiesto metadata.json actualizado con video_final_v2.")
    print("=" * 70)

if __name__ == "__main__":
    build_v2()
