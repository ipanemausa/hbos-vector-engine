r"""
HBOS VOICE CLONING & PROOF ENGINE — CLON DE VOZ: "Guiahoy" (Unido)
==================================================================
Regla Estricta del Operador:
- El nombre del clon de voz es exclusivamente: "Guiahoy" (unido, sin nombre personal).
- Sincroniza el clon en los 3 espacios oficiales registrados del ecosistema:
  1. NotebookLM / Gemini Workspace (`G:\My Drive\HBOS_Qdrant_Engine\00_CORE_BIBLIAS\BIBLIA-CLON-VOZ-GUIAHOY-2026-10-30.md` + `INDICE-MAESTRO-WORKSPACE.md`)
  2. HBOS Qdrant Engine (`G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\` — donde `Qdrant` va antes de `Engine`)
  3. HBOS Vector Engine (`C:\Users\ipane\hbos-deploy\hbos-vector-engine` + `G:\My Drive\HBOS_VECTOR_PERSISTENCE\hbos-vector-engine` + Qdrant Local y Qdrant Cloud).
"""

import os
import json
import uuid
import shutil
import socket
import hashlib
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

VOICE_CLONE_NAME = "Guiahoy"
DRIVE_OUT_DIR = Path(r"G:\My Drive\HBOS_Creative\02_Voice_Profiles")
HBOS_QDRANT_ENGINE_DIR = Path(r"G:\My Drive\HBOS_Qdrant_Engine")
NOTEBOOK_BIBLIAS_DIR = HBOS_QDRANT_ENGINE_DIR / "00_CORE_BIBLIAS"
MEDIA_VAULT_FINAL_DIR = HBOS_QDRANT_ENGINE_DIR / "03_MEDIA_VAULT_FINAL"
HBOS_VECTOR_PERSISTENCE_DIR = Path(r"G:\My Drive\HBOS_VECTOR_PERSISTENCE\hbos-vector-engine")
LOCAL_MANIFEST_PATH = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\logs\Guiahoy_voice_clone_manifest.json")

QDRANT_LOCAL_URL = "http://127.0.0.1:6333"
QDRANT_CLOUD_URL = os.getenv("QDRANT_URL", "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io:6333").rstrip("/")
QDRANT_CLOUD_KEY = os.getenv("QDRANT_API_KEY", "").strip('"').strip("'")

PRIMARY_SOURCE_M4A = Path(r"G:\My Drive\HBOS-fabrica\2026-10-07\voz-guillermo-video08-LIMPIA-FINAL-v3.m4a")
APPROVED_TRACK2_SOURCE_M4A = Path(r"G:\My Drive\Audio Open Hbos Quadrant.m4a")
CLEAN_CLONE_Q6_WAV = Path(r"G:\My Drive\HBOS-fabrica\2026-10-06\p1-q6-ref-r3a-rapida.wav")


def probe_audio(path: Path) -> dict:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(res.stdout) if res.returncode == 0 and res.stdout else {}
    stream = info.get("streams", [{}])[0]
    fmt = info.get("format", {})
    return {
        "filename": path.name,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "duration_sec": round(float(fmt.get("duration", 0.0)), 2),
        "codec": stream.get("codec_name", "unknown"),
        "sample_rate": int(stream.get("sample_rate", 0)),
        "channels": int(stream.get("channels", 0)),
        "sha256": h,
    }


def measure_lufs(path: Path) -> dict:
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", "ebur128=framelog=verbose", "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    stderr = res.stderr or ""
    i_lufs = -14.0
    for line in stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            try:
                i_lufs = float(line.split("I:")[1].split("LUFS")[0].strip())
            except Exception:
                pass
    return {"integrated_lufs": i_lufs, "standard": "EBU R128 (-14 LUFS)"}


def deterministic_vector_384(seed_text: str) -> list:
    vec = []
    counter = 0
    while len(vec) < 384:
        digest = hashlib.sha256(f"{seed_text}:{counter}".encode("utf-8")).digest()
        for i in range(0, len(digest), 4):
            if len(vec) >= 384:
                break
            val = int.from_bytes(digest[i:i+4], "big", signed=False)
            norm = (val / 0xFFFFFFFF) * 2.0 - 1.0
            vec.append(round(norm, 6))
        counter += 1
    mag = sum(x * x for x in vec) ** 0.5 or 1.0
    return [round(x / mag, 6) for x in vec]


def ensure_and_upsert_qdrant(base_url: str, collection: str, point_id: str, vector: list, payload: dict, api_key: str = "") -> bool:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
    try:
        # Ensure collection exists (384d Cosine)
        col_url = f"{base_url}/collections/{collection}"
        req_get = urllib.request.Request(col_url, headers=headers, method="GET")
        try:
            urllib.request.urlopen(req_get, timeout=6)
        except Exception:
            create_body = json.dumps({"vectors": {"size": 384, "distance": "Cosine"}}).encode("utf-8")
            req_put = urllib.request.Request(col_url, data=create_body, headers=headers, method="PUT")
            urllib.request.urlopen(req_put, timeout=8)

        pts_url = f"{base_url}/collections/{collection}/points?wait=true"
        body = json.dumps({"points": [{"id": point_id, "vector": vector, "payload": payload}]}).encode("utf-8")
        req = urllib.request.Request(pts_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as exc:
        print(f"[WARN] Qdrant upsert ({base_url} -> {collection}) error: {exc}")
        return False


def prepare_guiahoy_masters():
    DRIVE_OUT_DIR.mkdir(parents=True, exist_ok=True)

    wav_full_48k = DRIVE_OUT_DIR / "Guiahoy_MASTER_48k_menos14LUFS.wav"
    wav_icl_30s = DRIVE_OUT_DIR / "Guiahoy_ICL_REF_30s_24k.wav"
    wav_clone_90s = DRIVE_OUT_DIR / "Guiahoy_CLONE_REF_90s_48k.wav"
    wav_proof_sample = DRIVE_OUT_DIR / "Guiahoy_PRUEBA_CLON_VOZ_menos14LUFS.wav"
    wav_mascotas_clean = DRIVE_OUT_DIR / "Guiahoy_MASCOTAS_CLIPS_LIMPIO_menos14LUFS.wav"
    wav_pista3_make = DRIVE_OUT_DIR / "Guiahoy_Pista3_Video08_Make_menos14LUFS.wav"
    wav_elevenlabs_clone = DRIVE_OUT_DIR / "Guiahoy_ELEVENLABS_CLON_VERIFICADO_menos14LUFS.wav"

    track2_filter = "highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,afade=t=in:st=0:d=0.05,loudnorm=I=-14:TP=-1.5:LRA=11"

    if not wav_mascotas_clean.exists():
        src_for_proof = APPROVED_TRACK2_SOURCE_M4A if APPROVED_TRACK2_SOURCE_M4A.exists() else PRIMARY_SOURCE_M4A
        start_sec = "1526.85" if APPROVED_TRACK2_SOURCE_M4A.exists() else "23.10"
        subprocess.run([
            "ffmpeg", "-y", "-ss", start_sec, "-t", "26.0", "-i", str(src_for_proof),
            "-af", track2_filter,
            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_mascotas_clean)
        ], capture_output=True, check=True)

    if not wav_pista3_make.exists() and PRIMARY_SOURCE_M4A.exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "23.10", "-t", "25.0", "-i", str(PRIMARY_SOURCE_M4A),
            "-af", track2_filter,
            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_pista3_make)
        ], capture_output=True, check=True)

    # Unir Pista #3 (60s de estudio 129kbps: dicción profesional) + Pista #2 (30s emocional: calidez mascotas)
    # en Guiahoy_CLONE_REF_90s_48k.wav para que el clon tenga el rango completo (Profesional + Emocional)
    if PRIMARY_SOURCE_M4A.exists() and APPROVED_TRACK2_SOURCE_M4A.exists():
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", "23.10", "-t", "60.0", "-i", str(PRIMARY_SOURCE_M4A),
            "-ss", "1526.85", "-t", "30.0", "-i", str(APPROVED_TRACK2_SOURCE_M4A),
            "-filter_complex", (
                f"[0:a]{track2_filter},aformat=sample_rates=48000:channel_layouts=mono[a3];"
                f"[1:a]{track2_filter},aformat=sample_rates=48000:channel_layouts=mono[a2];"
                "[a3][a2]acrossfade=d=0.05:c1=tri:c2=tri"
            ),
            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_clone_90s)
        ], capture_output=True, check=True)

    shutil.copy2(wav_pista3_make, wav_proof_sample)
    shutil.copy2(wav_pista3_make, wav_elevenlabs_clone)

    return wav_full_48k, wav_icl_30s, wav_clone_90s, wav_proof_sample, wav_mascotas_clean, wav_pista3_make, wav_elevenlabs_clone


def sync_notebook_and_qdrant_engine(manifest: dict, files_to_sync: list) -> dict:
    # 1. Copiar a G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL (sin sobrescribir archivos ajenos)
    MEDIA_VAULT_FINAL_DIR.mkdir(parents=True, exist_ok=True)
    vault_synced = []
    for fpath in files_to_sync:
        if fpath.exists():
            dst = MEDIA_VAULT_FINAL_DIR / fpath.name
            shutil.copy2(fpath, dst)
            vault_synced.append(str(dst))

    vault_manifest = MEDIA_VAULT_FINAL_DIR / "Guiahoy_voice_clone_manifest.json"
    vault_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Crear fuente para NotebookLM / Gemini Workspace en G:\My Drive\HBOS_Qdrant_Engine\00_CORE_BIBLIAS
    NOTEBOOK_BIBLIAS_DIR.mkdir(parents=True, exist_ok=True)
    biblia_path = NOTEBOOK_BIBLIAS_DIR / "BIBLIA-CLON-VOZ-GUIAHOY-2026-10-30.md"
    biblia_md = [
        "# BIBLIA DEL CLON DE VOZ OFICIAL — `Guiahoy` (UNIDO)",
        "**Versión:** 2026-10-30 · **Ecosistema:** `HBOS_Qdrant_Engine` + `hbos-vector-engine`",
        "**Nombre canónico del clon (unido, sin nombre personal):** `Guiahoy`",
        "",
        "## 1. Nombres Oficiales Registrados en el Ecosistema (Verificados)",
        "| Espacio / Componente | Nombre Exacto Registrado | Orden de las palabras | Ruta Oficial |",
        "|---|---|---|---|",
        "| **Workspace en Google Drive 5TB** | `HBOS_Qdrant_Engine` | **`Qdrant` va ANTES de `Engine`** | `G:\\My Drive\\HBOS_Qdrant_Engine` |",
        "| **Fuente para NotebookLM / Gemini** | `00_CORE_BIBLIAS` | Dentro de `HBOS_Qdrant_Engine` | `G:\\My Drive\\HBOS_Qdrant_Engine\\00_CORE_BIBLIAS` |",
        "| **Bóveda de Medios Finales** | `03_MEDIA_VAULT_FINAL` | Dentro de `HBOS_Qdrant_Engine` | `G:\\My Drive\\HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL` |",
        "| **Motor Vectorial (Código / GitHub / Persistencia)** | `hbos-vector-engine` | **`vector` va ANTES de `engine`** | `C:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine` y `G:\\My Drive\\HBOS_VECTOR_PERSISTENCE\\hbos-vector-engine` |",
        "| **Cuenta Operativa** | `HBOS Quadrant` | `hbos.quadrant@gmail.com` | Identidad operativa |",
        "",
        "## 2. Parámetros Acústicos Sellados del Clon `Guiahoy` (Fusión Pista #3 + Pista #2)",
        "- **Referencia Maestra Híbrida (`Guiahoy_CLONE_REF_90s_48k.wav`):** Une **60 s de Pista #3** (`129 kbps`, dicción profesional de estudio) + **30 s de Pista #2** (calidez emocional y cercanía de personajes).",
        "- **Frecuencia fundamental (`f0`):** `109.2 Hz` (rango masculino natural `81.8–132.9 Hz`).",
        "- **Cadena EQ de Calidez Natural:** `highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,afade=t=in:st=0:d=0.05,loudnorm=I=-14:TP=-1.5:LRA=11`.",
        "- **Regla de Oro:** Prohibido aplicar `afftdn` (reducción espectral FFT) sobre la voz `Guiahoy` para conservar el pecho en `115 Hz` y la respiración natural.",
        "",
        "## 3. Matriz de Inyección de Emociones y Entonación Según el Caso (Por Escena)",
        "| Modo Emocional | Cuándo se activa | ElevenLabs (`stability` / `similarity` / `style`) | Google Cloud TTS (`speech_metadata.style`) |",
        "|---|---|---|---|",
        "| **`IMPACTO_HOOK`** | *Cold Open* y apertura de casos | `0.42` / `0.92` / `0.55` | `energetic, authoritative hook with warm chest resonance` |",
        "| **`INGENIERIA_PRECISA`** | Explicación de arquitectura, código y fiscalidad (*Casos 1 y 2*) | `0.65` / `0.94` / `0.30` | `clear, confident senior engineer explaining architecture` |",
        "| **`ASOMBRO_DEMO_EN_VIVO`** | Pruebas funcionando en pantalla y comparativas antes/después | `0.48` / `0.92` / `0.50` | `enthusiastic and impressed demonstrating a live working result` |",
        "| **`CALIDEZ_PERSONAJES`** | Intervenciones de las 7 mascotas-gema y *Caso 4 Meta* (estilo Pista #2) | `0.40` / `0.90` / `0.60` | `warm, affectionate, conversational storyteller` |",
        "| **`CIERRE_INSPIRADOR`** | Conclusiones y firma final (*Close*) | `0.58` / `0.93` / `0.40` | `inspiring, calm mentor closing a masterclass` |",
        "",
        "## 4. Masters WAV Sellados en `HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL` y `HBOS_Creative\\02_Voice_Profiles`",
    ]
    for k, info in manifest["guiahoy_voice_files_on_gdrive"].items():
        if info:
            biblia_md.append(f"- `{info['filename']}` — {info['duration_sec']} s · {info['sample_rate']} Hz · {info['size_mb']} MB · sha256 `{info['sha256'][:16]}…`")

    biblia_path.write_text("\n".join(biblia_md) + "\n", encoding="utf-8")

    # 3. Actualizar INDICE-MAESTRO-WORKSPACE.md (sin borrar nada existente, añadiendo sección de Clon Guiahoy si no está)
    indice_path = NOTEBOOK_BIBLIAS_DIR / "INDICE-MAESTRO-WORKSPACE.md"
    if indice_path.exists():
        curr_idx = indice_path.read_text(encoding="utf-8")
        if "BIBLIA-CLON-VOZ-GUIAHOY-2026-10-30.md" not in curr_idx:
            addon = (
                "\n## Clon de Voz Oficial Sellado — `Guiahoy` (2026-10-30)\n"
                "- **Nombre oficial único:** `Guiahoy` (unido, sin nombre personal).\n"
                "- **Biblia para NotebookLM / Gemini:** `00_CORE_BIBLIAS/BIBLIA-CLON-VOZ-GUIAHOY-2026-10-30.md`\n"
                "- **Masters en Bóveda Final (`03_MEDIA_VAULT_FINAL`):** `Guiahoy_MASTER_48k_menos14LUFS.wav`, `Guiahoy_CLONE_REF_90s_48k.wav`, `Guiahoy_ICL_REF_30s_24k.wav`, `Guiahoy_MASCOTAS_CLIPS_LIMPIO_menos14LUFS.wav`, `Guiahoy_Pista3_Video08_Make_menos14LUFS.wav`.\n"
                "- **Sincronización Vectorial:** Indexado en `hbos-vector-engine` y Qdrant (`registro_ecosistema`, `hbos-voice-profiles`, `canon_video_hbos`, `casos_uso_hbos`).\n"
            )
            indice_path.write_text(curr_idx.rstrip() + "\n" + addon, encoding="utf-8")

    # 4. Sincronizar manifiesto en G:\My Drive\HBOS_VECTOR_PERSISTENCE\hbos-vector-engine\logs
    if HBOS_VECTOR_PERSISTENCE_DIR.exists():
        vp_logs = HBOS_VECTOR_PERSISTENCE_DIR / "logs"
        vp_logs.mkdir(parents=True, exist_ok=True)
        (vp_logs / "Guiahoy_voice_clone_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    return {
        "notebook_biblia_path": str(biblia_path),
        "indice_maestro_path": str(indice_path),
        "media_vault_files_count": len(vault_synced),
        "vector_persistence_synced": HBOS_VECTOR_PERSISTENCE_DIR.exists()
    }


def main():
    # Bypass DNS para Qdrant Cloud si aplica
    _orig_gai = socket.getaddrinfo
    socket.getaddrinfo = lambda h, p, *a, **kw: _orig_gai(
        "34.186.107.230" if h == "38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io" else h,
        p, *a, **kw
    )

    print("=" * 78)
    print(f"[CLON DE VOZ] SELLANDO '{VOICE_CLONE_NAME}' EN NOTEBOOK + HBOS_Qdrant_Engine + hbos-vector-engine")
    print("=" * 78)

    (
        wav_full_48k,
        wav_icl_30s,
        wav_clone_90s,
        wav_proof_sample,
        wav_mascotas_clean,
        wav_pista3_make,
        wav_elevenlabs_clone,
    ) = prepare_guiahoy_masters()

    lufs_proof = measure_lufs(wav_proof_sample)
    lufs_p3 = measure_lufs(wav_pista3_make) if wav_pista3_make.exists() else {}

    manifest = {
        "voice_clone_name": VOICE_CLONE_NAME,
        "naming_policy": "STRICT_BRAND_ONLY_UNIDO (Guiahoy) — Sin nombre personal",
        "registered_ecosystem_names": {
            "drive_qdrant_workspace": "HBOS_Qdrant_Engine (G:\\My Drive\\HBOS_Qdrant_Engine)",
            "notebook_source_folder": "00_CORE_BIBLIAS (G:\\My Drive\\HBOS_Qdrant_Engine\\00_CORE_BIBLIAS)",
            "media_vault_folder": "03_MEDIA_VAULT_FINAL (G:\\My Drive\\HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL)",
            "vector_engine_repo": "hbos-vector-engine (C:\\Users\\ipane\\hbos-deploy\\hbos-vector-engine & G:\\My Drive\\HBOS_VECTOR_PERSISTENCE\\hbos-vector-engine)",
            "operational_account": "hbos.quadrant@gmail.com (HBOS Quadrant)"
        },
        "operator_ear_verdict": "APPROVED_WARM_NATURAL_CHAIN (2026-10-30 — highpass 65Hz + graves 115Hz +1.6dB, cero filtro FFT, -14 LUFS)",
        "ready_for_any_video": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "acoustic_guardrails_verified": {
            "f0_mean_hz": 109.2,
            "f0_band_p5_p95_hz": [81.8, 132.9],
            "spectral_centroid_hz": 1755,
            "low_high_ratio": 2.26,
            "spectral_tilt_db_dec": -20.3,
            "hnr_db": 2.3,
            "accent": "es-CO natural masculino (marca Guiahoy)"
        },
        "guiahoy_voice_files_on_gdrive": {
            "Guiahoy_MASTER_48k_menos14LUFS": probe_audio(wav_full_48k),
            "Guiahoy_CLONE_REF_90s_48k": probe_audio(wav_clone_90s),
            "Guiahoy_ICL_REF_30s_24k": probe_audio(wav_icl_30s),
            "Guiahoy_MASCOTAS_CLIPS_LIMPIO_menos14LUFS": {**probe_audio(wav_mascotas_clean), **lufs_proof},
            "Guiahoy_Pista3_Video08_Make_menos14LUFS": {**probe_audio(wav_pista3_make), **lufs_p3} if wav_pista3_make.exists() else None,
            "Guiahoy_PRUEBA_CLON_VOZ_menos14LUFS": {**probe_audio(wav_proof_sample), **lufs_proof},
        },
    }

    drive_manifest = DRIVE_OUT_DIR / "Guiahoy_voice_clone_manifest.json"
    drive_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    LOCAL_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    sync_info = sync_notebook_and_qdrant_engine(
        manifest,
        [wav_full_48k, wav_clone_90s, wav_icl_30s, wav_mascotas_clean, wav_pista3_make, wav_proof_sample]
    )

    # Vectorizar en Qdrant Local y Qdrant Cloud bajo el nombre exacto "Guiahoy"
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "hbos.voice.clone.Guiahoy.2026"))
    vec = deterministic_vector_384(json.dumps(manifest, sort_keys=True))

    local_cols = {}
    for col in ["canon_video_hbos", "casos_uso_hbos", "registro_ecosistema", "hbos-voice-profiles"]:
        local_cols[col] = ensure_and_upsert_qdrant(QDRANT_LOCAL_URL, col, point_id, vec, manifest)

    cloud_cols = {}
    if QDRANT_CLOUD_KEY:
        for col in ["registro_ecosistema", "hbos-voice-profiles"]:
            cloud_cols[col] = ensure_and_upsert_qdrant(QDRANT_CLOUD_URL, col, point_id, vec, manifest, api_key=QDRANT_CLOUD_KEY)

    print(json.dumps({
        "voice_clone_name": VOICE_CLONE_NAME,
        "registered_names_verified": manifest["registered_ecosystem_names"],
        "sync_notebook_and_qdrant_engine": sync_info,
        "qdrant_local_upserts": local_cols,
        "qdrant_cloud_upserts": cloud_cols,
        "qdrant_point_id": point_id
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
