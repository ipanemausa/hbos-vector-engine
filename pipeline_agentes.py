#!/usr/bin/env python3
# HBOS Equipo de Agentes de IA — pipeline verificable
# Python 3.11+ | Sin Docker | Sin servicios SaaS
# Fases: 0 preflight, 1 embeddings/Qdrant, 2 chroma, 3 composición, 4 auditoría.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FPS = 60
AUDIO_SECONDS = 414.276
VIDEO_FRAMES = 24857
VIDEO_SECONDS = VIDEO_FRAMES / FPS
EXPECTED_SCENES = 20
EXPECTED_POSES = 10
EXPECTED_EMBEDDING_DIM = 768

AUDIO_WAV = Path("audio/narracion-equipo-agentes.wav")
AUDIO_MP3 = Path("audio/narracion-equipo-agentes.mp3")
TIMINGS = Path("audio/tiempos.json")

SCENES_DIR = Path("escenas_3d")
POSES_DIR = Path("avatar_3d_magenta")

BUILD = Path("build")
FINAL = Path("final")
DEBUG_JSON = BUILD / "debug_fase0.json"
MANIFEST_JSON = BUILD / "manifest.json"

TEXT_COLLECTION = "hbos_guion_textual_768d"
VISUAL_COLLECTION = "hbos_activos_visuales_768d"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_cmd(args: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, check=False
    )

def executable(name: str) -> str | None:
    return shutil.which(name)

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def safe_extract_zip(zip_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for item in archive.infolist():
            name = item.filename.replace("\\", "/")
            target = (destination / name).resolve()
            if not target.is_relative_to(destination_resolved):
                raise RuntimeError(f"Ruta insegura dentro del ZIP: {item.filename}")
            unix_mode = (item.external_attr >> 16) & 0xFFFF
            if (unix_mode & 0o170000) == 0o120000:
                raise RuntimeError(f"Enlace simbólico no permitido: {item.filename}")
        archive.extractall(destination)

def locate_root(source: Path, workspace: Path) -> Path:
    if source.is_dir():
        return source.resolve()

    if not source.is_file() or source.suffix.lower() != ".zip":
        raise FileNotFoundError(f"No existe ZIP/carpeta de entrada: {source}")

    extracted = workspace / "input_extracted"
    if extracted.exists():
        shutil.rmtree(extracted)
    extracted.mkdir(parents=True)

    safe_extract_zip(source, extracted)

    if (extracted / "audio").is_dir():
        return extracted

    candidates = [p for p in extracted.iterdir() if p.is_dir()]
    matching = [p for p in candidates if (p / "audio").is_dir()]
    if len(matching) == 1:
        return matching[0]
    raise RuntimeError(
        "No se encontró una raíz inequívoca con la carpeta audio/ en el ZIP."
    )

def ffprobe_json(path: Path) -> dict[str, Any]:
    binary = executable("ffprobe")
    if not binary:
        raise RuntimeError("ffprobe no está instalado o no está en PATH.")
    result = run_cmd([
        binary, "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe falló.")
    return json.loads(result.stdout)

def media_duration(probe: dict[str, Any]) -> float | None:
    value = probe.get("format", {}).get("duration")
    if value is not None:
        return float(value)
    durations = [
        float(s["duration"]) for s in probe.get("streams", [])
        if s.get("duration") is not None
    ]
    return max(durations) if durations else None

def loudnorm_measure(path: Path) -> dict[str, Any]:
    binary = executable("ffmpeg")
    if not binary:
        return {"status": "NO_VERIFICABLE", "reason": "ffmpeg no disponible"}

    result = run_cmd([
        binary, "-hide_banner", "-nostats", "-i", str(path),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ], timeout=600)

    stderr = result.stderr
    start = stderr.rfind("{")
    end = stderr.rfind("}")
    if result.returncode != 0 or start < 0 or end < start:
        return {
            "status": "FAIL",
            "returncode": result.returncode,
            "stderr_tail": stderr[-2500:]
        }
    try:
        measured = json.loads(stderr[start:end + 1])
        return {"status": "MEASURED", "measurement": measured}
    except json.JSONDecodeError:
        return {"status": "NO_VERIFICABLE", "stderr_tail": stderr[-2500:]}

def image_inventory(folder: Path) -> list[dict[str, Any]]:
    from PIL import Image

    records = []
    if not folder.exists():
        return records

    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".jpg", ".jpeg", ".png", ".webp"
        }:
            continue
        record: dict[str, Any] = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        try:
            with Image.open(path) as im:
                record.update({
                    "width": im.width,
                    "height": im.height,
                    "mode": im.mode,
                    "format": im.format,
                    "valid_image": True,
                })
        except Exception as exc:
            record.update({"valid_image": False, "error": str(exc)})
        records.append(record)
    return records

def check_timing_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "FAIL", "reason": "No existe tiempos.json"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "FAIL", "reason": f"JSON inválido: {exc}"}

    strings: list[str] = []
    numeric_values: list[float] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
        elif isinstance(obj, str):
            if obj.strip():
                strings.append(obj.strip())
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            numeric_values.append(float(obj))

    walk(data)
    return {
        "status": "READABLE",
        "root_type": type(data).__name__,
        "text_strings_found": len(strings),
        "numeric_values_found": len(numeric_values),
        "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
        "note": (
            "La estructura se inventarió; la semántica temporal debe "
            "mapearse explícitamente antes de declarar cobertura sin huecos."
        )
    }

def phase0(source: Path, workspace: Path) -> tuple[Path, dict[str, Any]]:
    BUILD.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "pipeline": "HBOS Equipo de Agentes de IA",
        "timestamp_utc": utc_now(),
        "status": "INCONCLUSIVE",
        "environment": {
            "python": sys.version,
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
            "cpu_count": os.cpu_count(),
            "ffmpeg": executable("ffmpeg"),
            "ffprobe": executable("ffprobe"),
            "blender": executable("blender"),
            "disk_workspace": shutil.disk_usage(workspace)._asdict(),
        },
        "contract": {
            "audio_master_seconds": AUDIO_SECONDS,
            "video_fps": FPS,
            "video_frames": VIDEO_FRAMES,
            "video_seconds": VIDEO_SECONDS,
            "audio_video_duration_difference_seconds":
                round(AUDIO_SECONDS - VIDEO_SECONDS, 6),
            "audio_must_not_be_trimmed": True,
            "embedding_dimension": EXPECTED_EMBEDDING_DIM,
        },
        "checks": {},
        "files": [],
        "warnings": [],
        "errors": [],
    }

    try:
        root = locate_root(source, workspace)
        report["input_root"] = str(root)
    except Exception as exc:
        report["errors"].append(f"No se pudo localizar/examinar la entrada: {exc}")
        report["status"] = "FAIL"
        DEBUG_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return workspace, report

    required = [AUDIO_WAV, AUDIO_MP3, TIMINGS]
    missing = [str(p) for p in required if not (root / p).is_file()]
    report["checks"]["required_audio_files"] = {
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
    }

    wav = root / AUDIO_WAV
    mp3 = root / AUDIO_MP3
    timing = root / TIMINGS

    if wav.is_file():
        report["files"].append({
            "path": str(wav),
            "bytes": wav.stat().st_size,
            "sha256": sha256_file(wav),
        })
        try:
            probe = ffprobe_json(wav)
            audio_streams = [
                s for s in probe.get("streams", []) if s.get("codec_type") == "audio"
            ]
            duration = media_duration(probe)
            stream = audio_streams[0] if audio_streams else {}
            report["checks"]["wav"] = {
                "status": "PASS" if audio_streams and duration is not None else "FAIL",
                "duration_seconds": duration,
                "duration_matches_master_within_1ms":
                    duration is not None and abs(duration - AUDIO_SECONDS) <= 0.001,
                "codec": stream.get("codec_name"),
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "channel_layout": stream.get("channel_layout"),
                "bits_per_sample": stream.get("bits_per_sample"),
                "ffprobe": probe,
            }
            report["checks"]["wav_loudnorm"] = loudnorm_measure(wav)
        except Exception as exc:
            report["checks"]["wav"] = {"status": "FAIL", "reason": str(exc)}
    else:
        report["checks"]["wav"] = {"status": "FAIL", "reason": "WAV ausente"}

    if mp3.is_file():
        try:
            probe = ffprobe_json(mp3)
            report["checks"]["mp3"] = {
                "status": "PASS",
                "duration_seconds": media_duration(probe),
                "ffprobe": probe,
            }
            report["files"].append({
                "path": str(mp3),
                "bytes": mp3.stat().st_size,
                "sha256": sha256_file(mp3),
            })
        except Exception as exc:
            report["checks"]["mp3"] = {"status": "FAIL", "reason": str(exc)}
    else:
        report["checks"]["mp3"] = {"status": "FAIL", "reason": "MP3 ausente"}

    report["checks"]["timings"] = check_timing_json(timing)

    scenes = image_inventory(root / SCENES_DIR)
    poses = image_inventory(root / POSES_DIR)
    report["checks"]["scenes"] = {
        "status": "PASS" if len(scenes) == EXPECTED_SCENES
        and all(x.get("valid_image") for x in scenes) else "FAIL",
        "count": len(scenes),
        "expected": EXPECTED_SCENES,
        "images": scenes,
    }
    report["checks"]["poses"] = {
        "status": "PASS" if len(poses) == EXPECTED_POSES
        and all(x.get("valid_image") for x in poses) else "FAIL",
        "count": len(poses),
        "expected": EXPECTED_POSES,
        "images": poses,
    }

    report["checks"]["runtime_tools"] = {
        "python": sys.version.split()[0],
        "ffmpeg": executable("ffmpeg") or "NO ENCONTRADO",
        "ffprobe": executable("ffprobe") or "NO ENCONTRADO",
        "blender": executable("blender") or "NO ENCONTRADO",
    }

    statuses = []
    for key, value in report["checks"].items():
        if isinstance(value, dict) and "status" in value:
            statuses.append(value["status"])

    hard_fail = any(s == "FAIL" for s in statuses)
    unverifiable = any(s in {"NO_VERIFICABLE", "INCONCLUSIVE"} for s in statuses)
    if hard_fail:
        report["status"] = "FAIL"
    elif unverifiable:
        report["status"] = "INCONCLUSIVE"
    else:
        report["status"] = "PASS"

    DEBUG_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return root, report

def require_phase0_pass() -> dict[str, Any]:
    if not DEBUG_JSON.is_file():
        raise RuntimeError("No existe build/debug_fase0.json. Ejecuta Fase 0.")
    report = json.loads(DEBUG_JSON.read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise RuntimeError(
            f"Gate bloqueado: Fase 0 = {report.get('status')}. "
            "No se permite avanzar."
        )
    return report

def collect_text_chunks(root: Path) -> list[str]:
    candidates = [
        root / TIMINGS,
        root / "guion.txt",
        root / "audio/guion.txt",
        root / "guion.json",
    ]
    chunks: list[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.lower() in {
                    "text", "texto", "narration", "narracion", "script",
                    "guion", "sentence", "segment_text"
                } and isinstance(value, str) and value.strip():
                    chunks.append(value.strip())
                else:
                    walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for path in candidates:
        if not path.is_file():
            continue
        if path.suffix.lower() == ".txt":
            content = path.read_text(encoding="utf-8").strip()
            if content:
                chunks.extend([x.strip() for x in content.splitlines() if x.strip()])
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            walk(data)

    seen = set()
    result = []
    for item in chunks:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def phase1(root: Path, workspace: Path) -> None:
    require_phase0_pass()

    from sentence_transformers import SentenceTransformer
    from transformers import AutoProcessor, AutoModel
    from PIL import Image
    import torch
    from qdrant_client import QdrantClient, models

    device = "cuda" if torch.cuda.is_available() else "cpu"
    qdrant_path = workspace / "build/qdrant_local"
    qdrant_path.mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=str(qdrant_path))

    text_model_name = "intfloat/multilingual-e5-base"
    text_model = SentenceTransformer(text_model_name, device=device)
    text_chunks = collect_text_chunks(root)
    if not text_chunks:
        raise RuntimeError(
            "No se encontraron textos de guion en tiempos.json/guion.*. "
            "No se vectoriza el audio como si fuera texto."
        )

    text_inputs = ["passage: " + t for t in text_chunks]
    text_vectors = text_model.encode(
        text_inputs, normalize_embeddings=True, show_progress_bar=True
    )
    if int(text_vectors.shape[1]) != EXPECTED_EMBEDDING_DIM:
        raise RuntimeError(f"Dimensión textual inesperada: {text_vectors.shape}")

    visual_model_name = "google/siglip-base-patch16-224"
    processor = AutoProcessor.from_pretrained(visual_model_name)
    visual_model = AutoModel.from_pretrained(visual_model_name).to(device).eval()

    visual_paths = []
    for folder in [root / SCENES_DIR, root / POSES_DIR]:
        visual_paths.extend(sorted(
            p for p in folder.rglob("*")
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ))

    visual_vectors = []
    visual_records = []
    for path in visual_paths:
        with Image.open(path) as im:
            image = im.convert("RGB")
            inputs = processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                features = visual_model.get_image_features(**inputs)
                features = torch.nn.functional.normalize(features, p=2, dim=-1)
            vector = features[0].detach().cpu().numpy().astype("float32")
        if len(vector) != EXPECTED_EMBEDDING_DIM:
            raise RuntimeError(f"Dimensión visual inesperada en {path}: {len(vector)}")
        visual_vectors.append(vector.tolist())
        visual_records.append({
            "path": str(path.relative_to(root)),
            "asset_type": "scene" if SCENES_DIR in path.parents else "avatar_pose",
            "sha256": sha256_file(path),
        })

    for collection in [TEXT_COLLECTION, VISUAL_COLLECTION]:
        if client.collection_exists(collection):
            client.delete_collection(collection)

    client.create_collection(
        collection_name=TEXT_COLLECTION,
        vectors_config=models.VectorParams(
            size=EXPECTED_EMBEDDING_DIM, distance=models.Distance.COSINE
        )
    )
    client.create_collection(
        collection_name=VISUAL_COLLECTION,
        vectors_config=models.VectorParams(
            size=EXPECTED_EMBEDDING_DIM, distance=models.Distance.COSINE
        )
    )

    text_points = [
        models.PointStruct(
            id=i + 1,
            vector=text_vectors[i].tolist(),
            payload={"text": text_chunks[i], "modality": "text", "source": "script"}
        )
        for i in range(len(text_chunks))
    ]
    visual_points = [
        models.PointStruct(
            id=i + 1,
            vector=visual_vectors[i],
            payload={**visual_records[i], "modality": "visual"}
        )
        for i in range(len(visual_vectors))
    ]

    client.upsert(collection_name=TEXT_COLLECTION, points=text_points)
    client.upsert(collection_name=VISUAL_COLLECTION, points=visual_points)

    manifest = {
        "created_utc": utc_now(),
        "status": "CREATED_BY_EXECUTION",
        "device": device,
        "text_encoder": text_model_name,
        "visual_encoder": visual_model_name,
        "dimension": EXPECTED_EMBEDDING_DIM,
        "text_collection": TEXT_COLLECTION,
        "visual_collection": VISUAL_COLLECTION,
        "text_points": len(text_points),
        "visual_points": len(visual_points),
        "separation": "STRICT: text and visual embeddings stored separately",
        "qdrant_local_path": str(qdrant_path),
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    client.close()
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

def require_video(path: Path, description: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Falta {description}: {path}")
    probe = ffprobe_json(path)
    streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "video"]
    if not streams:
        raise RuntimeError(f"{path} no contiene un stream de video.")
    return probe

def phase2(root: Path, workspace: Path, motion_video: Path) -> Path:
    require_phase0_pass()
    require_video(motion_video, "video real de avatar animado sobre fondo magenta")
    output = BUILD / "avatar_alpha.mov"
    output.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = executable("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg no disponible.")

    cmd = [
        ffmpeg, "-y", "-i", str(motion_video),
        "-vf", "colorkey=0xFF00FF:0.12:0.08,format=yuva444p",
        "-c:v", "qtrle", "-an", str(output)
    ]
    result = run_cmd(cmd, timeout=3600)
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"Fase 2 falló: {result.stderr[-3000:]}")
    probe = ffprobe_json(output)
    video_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {}
    )
    if not video_stream:
        raise RuntimeError("El resultado de Fase 2 no tiene stream de video.")
    (BUILD / "fase2_report.json").write_text(json.dumps({
        "status": "CREATED_BY_EXECUTION",
        "input": str(motion_video),
        "output": str(output),
        "filter": "colorkey 0xFF00FF",
        "video_stream": video_stream,
        "note": "La calidad del alfa debe revisarse visualmente; ffprobe no certifica bordes limpios."
    }, indent=2, ensure_ascii=False))
    return output

def phase3(alpha_video: Path, background_video: Path) -> Path:
    require_phase0_pass()
    require_video(alpha_video, "video del avatar con alfa")
    require_video(background_video, "render animado de escenarios 3D")

    ffmpeg = executable("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg no disponible.")
    output = BUILD / "composicion_1080p60.mp4"

    cmd = [
        ffmpeg, "-y",
        "-i", str(background_video),
        "-i", str(alpha_video),
        "-filter_complex",
        (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,fps=60,setsar=1[bg];"
            "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            "fps=60,format=rgba[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,"
            "format=yuv420p[out]"
        ),
        "-map", "[out]", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-r", "60", "-pix_fmt", "yuv420p",
        str(output)
    ]
    result = run_cmd(cmd, timeout=7200)
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"Fase 3 falló: {result.stderr[-3000:]}")

    probe = ffprobe_json(output)
    stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {}
    )
    if stream.get("width") != 1920 or stream.get("height") != 1080:
        raise RuntimeError(f"Resolución final incorrecta: {stream}")
    (BUILD / "fase3_report.json").write_text(json.dumps({
        "status": "CREATED_BY_EXECUTION",
        "output": str(output),
        "video_stream": stream,
        "background_source": str(background_video),
        "avatar_source": str(alpha_video),
    }, indent=2, ensure_ascii=False))
    return output

def phase4(video_only: Path, root: Path) -> Path:
    require_phase0_pass()
    require_video(video_only, "composición 1080p60")
    wav = root / AUDIO_WAV
    if not wav.is_file():
        raise RuntimeError("No existe el WAV maestro; no se puede cerrar el master.")

    ffmpeg = executable("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg no disponible.")

    output = FINAL / "EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg, "-y",
        "-i", str(video_only),
        "-i", str(wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-frames:v", str(VIDEO_FRAMES),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k",
        "-t", f"{AUDIO_SECONDS:.3f}",
        "-movflags", "+faststart",
        str(output)
    ]
    result = run_cmd(cmd, timeout=7200)
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"Fase 4 falló: {result.stderr[-3000:]}")

    probe = ffprobe_json(output)
    video_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {}
    )
    audio_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), {}
    )
    video_duration = float(video_stream.get("duration", 0) or 0)
    audio_duration = float(audio_stream.get("duration", 0) or 0)
    frame_count = int(video_stream.get("nb_frames", 0) or 0)

    checks = {
        "resolution_1920x1080":
            video_stream.get("width") == 1920 and video_stream.get("height") == 1080,
        "video_fps_60":
            video_stream.get("r_frame_rate") == "60/1"
            or video_stream.get("avg_frame_rate") == "60/1",
        "video_frames_24857": frame_count == VIDEO_FRAMES,
        "audio_not_shortened_below_master":
            audio_duration >= AUDIO_SECONDS - 0.020,
        "audio_video_duration_difference_expected":
            abs(video_duration - VIDEO_SECONDS) <= 0.050,
    }
    final_status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "status": final_status,
        "created_utc": utc_now(),
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "video_duration_seconds": video_duration,
        "audio_duration_seconds": audio_duration,
        "expected_video_seconds": VIDEO_SECONDS,
        "expected_audio_seconds": AUDIO_SECONDS,
        "video_frames": frame_count,
        "checks": checks,
        "ffprobe": probe,
        "important": (
            "El video dura 407.650 s por 24.459 cuadros a 60 fps; "
            "el audio maestro se conserva en torno a 407.656 s. "
            "No son duraciones matemáticamente idénticas."
        )
    }
    (FINAL / "auditoria_final.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    if final_status != "PASS":
        raise RuntimeError(
            "Auditoría final FAIL. Consulta final/auditoria_final.json."
        )
    return output

def main() -> int:
    parser = argparse.ArgumentParser(
        description="HBOS — Pipeline verificable Equipo de Agentes de IA"
    )
    parser.add_argument(
        "--input", required=True,
        help="Ruta a equipo_agentes.zip o a la carpeta ya extraída."
    )
    parser.add_argument(
        "--workspace", default=".",
        help="Directorio de trabajo para build/, final/ y Qdrant local."
    )
    parser.add_argument(
        "--phase", choices=["0", "1", "2", "3", "4"], default="0"
    )
    parser.add_argument(
        "--motion-video",
        help="Video REAL del avatar animado sobre fondo #FF00FF, requerido en Fase 2."
    )
    parser.add_argument(
        "--background-video",
        help="Render REAL animado de escenarios 3D, requerido en Fase 3."
    )
    parser.add_argument(
        "--alpha-video",
        help="Video con alfa generado en Fase 2, requerido en Fase 3."
    )
    parser.add_argument(
        "--composite-video",
        help="Composición generada en Fase 3, requerida en Fase 4."
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    os.chdir(workspace)

    source = Path(args.input).resolve()

    try:
        if args.phase == "0":
            root, report = phase0(source, workspace)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            print(f"\nInforme: {DEBUG_JSON.resolve()}")
            return 0 if report["status"] == "PASS" else 2

        if source.is_dir():
            root = source
        else:
            extracted = workspace / "input_extracted"
            if not extracted.exists():
                raise RuntimeError("Ejecuta primero Fase 0 para extraer e inventariar el ZIP.")
            root = extracted
            if not (root / "audio").is_dir():
                candidates = [p for p in root.iterdir() if p.is_dir() and (p / "audio").is_dir()]
                if len(candidates) != 1:
                    raise RuntimeError("No se pudo resolver la carpeta raíz de los activos.")
                root = candidates[0]

        if args.phase == "1":
            phase1(root, workspace)
        elif args.phase == "2":
            if not args.motion_video:
                raise RuntimeError(
                    "Fase 2 exige --motion-video con animación real del avatar. "
                    "Las 10 poses JPG no prueban movimiento continuo."
                )
            print(f"Avatar alfa creado: {phase2(root, workspace, Path(args.motion_video))}")
        elif args.phase == "3":
            if not args.alpha_video or not args.background_video:
                raise RuntimeError(
                    "Fase 3 exige --alpha-video y --background-video. "
                    "El fondo debe ser un render 3D animado, no una imagen fija."
                )
            print(f"Composición creada: {phase3(Path(args.alpha_video), Path(args.background_video))}")
        elif args.phase == "4":
            if not args.composite_video:
                raise RuntimeError("Fase 4 exige --composite-video.")
            print(f"Master auditado: {phase4(Path(args.composite_video), root)}")
        return 0

    except Exception as exc:
        print(f"HBOS_PIPELINE_ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())


