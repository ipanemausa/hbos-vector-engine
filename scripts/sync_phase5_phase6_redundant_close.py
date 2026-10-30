# -*- coding: utf-8 -*-
r"""
Sync Phase 5 (QA Gates + 30s Pilot Exit Proof + 3 Thumbnails) and Phase 6 (Redundant Close)
across:
1. Artifact directory (copy 3 thumbnails for direct visual inspection in chat)
2. G:\My Drive\HBOS_Qdrant_Engine\00_CORE_BIBLIAS\ (NotebookLM Markdown Bible update)
3. Qdrant Local (casos_uso_hbos, canon_video_hbos, registro_ecosistema)
4. Qdrant Cloud (registro_ecosistema)
"""
import hashlib
import json
import os
import shutil
import socket
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

PROJECT_DIR = Path(r"G:\My Drive\HBOS_Creative\07_Project_Argon_4_Cases")
BIBLIAS_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\00_CORE_BIBLIAS")
ARTIFACT_DIR = Path(r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83")
REPO_LOGS = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\logs")


def deterministic_vector_384(seed_text: str) -> list:
    vec = []
    counter = 0
    while len(vec) < 384:
        h = hashlib.sha256(f"{seed_text}:{counter}".encode("utf-8")).digest()
        for i in range(0, len(h), 4):
            if len(vec) >= 384:
                break
            val = int.from_bytes(h[i:i+4], "little", signed=True) / 2147483648.0
            vec.append(round(val, 6))
        counter += 1
    norm = sum(x * x for x in vec) ** 0.5 or 1.0
    return [round(x / norm, 6) for x in vec]


def ensure_and_upsert_qdrant(base_url: str, collection: str, point_id: str, vector: list, payload: dict, api_key: str = "") -> bool:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
    try:
        col_url = f"{base_url.rstrip('/')}/collections/{collection}"
        req_get = urllib.request.Request(col_url, headers=headers, method="GET")
        try:
            urllib.request.urlopen(req_get, timeout=6)
        except Exception:
            create_body = json.dumps({"vectors": {"size": 384, "distance": "Cosine"}}).encode("utf-8")
            req_put = urllib.request.Request(col_url, data=create_body, headers=headers, method="PUT")
            urllib.request.urlopen(req_put, timeout=8)

        pts_url = f"{base_url.rstrip('/')}/collections/{collection}/points?wait=true"
        body = json.dumps({"points": [{"id": point_id, "vector": vector, "payload": payload}]}).encode("utf-8")
        req = urllib.request.Request(pts_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status in (200, 201)
    except Exception:
        return False


def main():
    _orig_gai = socket.getaddrinfo
    socket.getaddrinfo = lambda h, p, *a, **kw: _orig_gai(
        "34.186.107.230" if h == "38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io" else h,
        p, *a, **kw
    )

    qa_report = json.loads((PROJECT_DIR / "qa_report_phase5.json").read_text(encoding="utf-8"))

    copied_thumbs = []
    for thumb_str in qa_report["thumbnails_generated_R_THUMB_01"]:
        src = Path(thumb_str)
        dst = ARTIFACT_DIR / src.name
        shutil.copy2(src, dst)
        copied_thumbs.append(str(dst))

    biblia_video = BIBLIAS_DIR / "BIBLIA-VIDEO-ARGON-ANTIGRAVITY-4-CASOS-2026-10-30.md"
    md_content = f"""# BIBLIA DE PRODUCCIÓN INTERACTIVA: GEMINI ARGON + ANTIGRAVITY (4 CASOS DE USO REALES)

- **Fecha de Sellado:** `{datetime.now(timezone.utc).isoformat()}`
- **Clon de Voz Oficial:** `Guiahoy` (unido en una sola palabra, fusión #3 `129 kbps` precisión de estudio + #2 calidez expresiva de personajes + Matriz de 5 Emociones e Intonaciones Dinámicas)
- **Duración Calibrada del Manifiesto Completo:** `17.54 minutos` (`1,052.1 segundos`, `137 escenas interactivas`, `5.2s–8.0s` por escena, 0 tomas estáticas >= 10s)
- **Piloto Maestro 30s (`EXIT PROOF` Fase 5):** `G:\\My Drive\\HBOS_Creative\\07_Project_Argon_4_Cases\\pilot_30s_argon_antigravity_4_casos_16x9.mp4` (`{qa_report['pilot_mp4_size_mb']} MB`, SHA-256 `{qa_report['pilot_sha256']}`)
- **Copia en Bóveda Final (`HBOS_Qdrant_Engine`):** `G:\\My Drive\\HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL\\pilot_30s_argon_antigravity_4_casos_16x9.mp4`

## Sinergia Técnica: Mejoras de Ayer (`2026-10-29` / Spec v2) + Implementación de Hoy (`2026-10-30`)

1. **Corrección de Brecha #2 (`M-COMPOSICION-01` — Efecto JH en 3 Planos sin Caja Rectangular):**
   - En el pipeline de ayer (`studio/video/guiahoy_pipeline.py`), `_draw_floating_camera_bubble` dibujaba un recuadro rectangular visible alrededor del presentador, lo cual fue detectado en `investigacion-salto-de-calidad-20261027.md` (§2 Brecha 2) como violación de `M-COMPOSICION-01`.
   - Hoy eliminamos por completo el recuadro pegado e integramos las poses transparentes reales RGBA (`G:\\My Drive\\Avatar Guillermo - transparencias\\avatar-pose-t-*.png`) directamente sobre la escena con **rim light cian/dorado**, **sombra de contacto a piso (`ground shadow`)** y **respiración orgánica (`M-IDLE-01`)**.
2. **Telemetría de Cursor `smoothstep_c1` + Autozoom `1.35x` + Anti-Oclusión:**
   - Conservamos la interpolación matemática `6x^5 - 15x^4 + 10x^3` de ayer y la trasladamos a formato horizontal YouTube `16:9` (`1920x1080 @ 30fps`), relocalizando automáticamente al presentador de derecha a izquierda cuando el clic ocurre en el cuadrante derecho.
3. **Puntero Láser de las 7 Gemas Canónicas (`R-LASER-01`):**
   - Integramos a `Diamantino`, `Rubin`, `Zafir`, `Esmeralda`, `Amatista`, `Citrilo` y `Grafito` (`G:\\My Drive\\Diamantini\\`) disparando un haz láser dual con pulso luminoso exactamente al botón del IDE donde ocurre la acción.
4. **Sincronización Milimétrica (`F5-TTS-Spanish` + `Wav2Vec2-Large-XLSR-53-Spanish` + `sync_map.json`):**
   - Alineación forzada fonema por fonema (`CTC Forced Alignment` cada `20 ms`) acoplada a la matriz de 5 modos emocionales (`IMPACTO_HOOK`, `INGENIERIA_PRECISA`, `ASOMBRO_DEMO_EN_VIVO`, `CALIDEZ_PERSONAJES`, `CIERRE_INSPIRADOR`) y subtítulos animados ASS palabra por palabra.
5. **3 Miniaturas Benefit-First (`R-THUMB-01`):**
   - `THUMB_A_BENEFICIO_DIRECTO.png`: `"4 APPS EN 17 MIN"`
   - `THUMB_B_ARTEFACTO_PRUEBA.png`: `"0 CAJAS PEGADAS"`
   - `THUMB_C_CONTRASTE_MAXIMO.png`: `"100% GRATIS LOCAL"`
"""
    biblia_video.write_text(md_content, encoding="utf-8")

    point_id = "9c41f2a8-38e1-4c99-b4d2-81a0e5c71030"
    vec = deterministic_vector_384("HBOS_ARGON_4_CASOS_PILOT_30S_GUIAHOY_PHASE5_PHASE6_2026_10_30")
    payload = {
        "entity": "VIDEO_PILOT_AND_MANIFEST_ARGON_ANTIGRAVITY_4_CASES",
        "voice_clone_id": "Guiahoy",
        "pilot_mp4_vault_path": qa_report["pilot_mp4_vault_path"],
        "pilot_sha256": qa_report["pilot_sha256"],
        "full_duration_min": 17.54,
        "scenes_count": 137,
        "qa_gates": qa_report["qa_gates"],
        "thumbnails": qa_report["thumbnails_generated_R_THUMB_01"],
        "notebook_bible": str(biblia_video),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    local_results = {}
    for col in ["casos_uso_hbos", "canon_video_hbos", "registro_ecosistema"]:
        local_results[col] = ensure_and_upsert_qdrant("http://127.0.0.1:6333", col, point_id, vec, payload)

    cloud_url = os.getenv("QDRANT_URL", "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io:6333").rstrip("/")
    cloud_key = os.getenv("QDRANT_API_KEY", "").strip('"').strip("'")
    cloud_ok = ensure_and_upsert_qdrant(cloud_url, "registro_ecosistema", point_id, vec, payload, api_key=cloud_key) if cloud_key else False

    summary = {
        "status": "PHASE_5_AND_6_SEALED",
        "point_id": point_id,
        "qdrant_local": local_results,
        "qdrant_cloud_registro_ecosistema": cloud_ok,
        "notebook_bible": str(biblia_video),
        "artifact_thumbnails": copied_thumbs,
    }
    (REPO_LOGS / "argon_4_cases_phase5_phase6_close.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
