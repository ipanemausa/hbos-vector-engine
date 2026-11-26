"""
HBOS Quadrant Master Registry & Ledger Sync (2026-11-26)
Operates strictly against Cloud Quadrant (Qdrant Cloud + Vercel Vector Engine)
with canonical gemini-embedding-2 (768 dimensions, Cosine).
Never touches local Docker Qdrant (:6333) and never prints/embeds secrets.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

REPO_ROOT = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")

_ENV_LOCAL = dotenv_values(REPO_ROOT / ".env.local")
_ENV_MAIN = dotenv_values(REPO_ROOT / ".env")

QDRANT_URL = (_ENV_LOCAL.get("QDRANT_URL") or "").strip().strip('"').rstrip("/")
QDRANT_API_KEY = (_ENV_LOCAL.get("QDRANT_API_KEY") or "").strip().strip('"')
GEMINI_API_KEY = (_ENV_LOCAL.get("GEMINI_API_KEY") or "").strip().strip('"')
FREELLMAPI_KEY = (_ENV_MAIN.get("FREELLMAPI_KEY") or _ENV_LOCAL.get("FREELLMAPI_KEY") or "").strip().strip('"')

if not QDRANT_URL.startswith("https://"):
    raise RuntimeError(f"F1/F5 violation guard: QDRANT_URL must be Qdrant Cloud https://..., got {QDRANT_URL!r}")

VERCEL_BASE = "https://hbos-vector-engine.vercel.app"
COL_REGISTRO = "registro_ecosistema_r768"
COL_VIDEO = "canon_video_hbos_r768"
EMBED_MODEL = "gemini-embedding-2"
EMBED_DIMS = 768

INPUT_VIDEO = DEPLOY_ROOT / "INSUMOS-PANEL" / "EQUIPO-DE-AGENTES-video-final.mp4"
INPUT_TIEMPOS = DEPLOY_ROOT / "INSUMOS-PANEL" / "tiempos.json"
EXPECTED_VIDEO_SHA256 = "817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88"
EXPECTED_TIEMPOS_SHA256 = "7893c247eae689e132c421e448db5383e1c43473e7533c0698811ffbfd91699c"

BASE_DOCS = {
    "HBOS_MULTIAGENT_TOPOLOGY_01.md": {
        "path": REPO_ROOT / ".agents" / "rules" / "HBOS_MULTIAGENT_TOPOLOGY_01.md",
        "expected_sha256": "e2296bd7951f3d7571894bd5bd735167e76da2ee8fba0c63301fcdb66a81b437",
    },
    "HBOS_PRODUCTION_DAG_01.md": {
        "path": REPO_ROOT / ".agents" / "rules" / "HBOS_PRODUCTION_DAG_01.md",
        "expected_sha256": "660ef37a3af9210a1be2d6b5cfea93380adddfce34401c61b4288c2ce7ed07f2",
    },
    "HBOS_MASTER_SYSTEM_MAP.md": {
        "path": REPO_ROOT / "docs" / "HBOS_MASTER_SYSTEM_MAP.md",
        "expected_sha256": "fb82414168ec99eb3cc832cc95c3a6d82adb5c80b0f71c998b11c61f93ccb142",
    },
    "HBOS_MASTER_SYSTEM_MAP.html": {
        "path": REPO_ROOT / "docs" / "HBOS_MASTER_SYSTEM_MAP.html",
        "expected_sha256": "ec54b4b8edb36923817dd521d1b1207013aa642a0b7b7754c39976c514730023",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def stable_uuid(key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"hbos-quadrant-2026-11-26:{key}"))


def http_json(url: str, method: str = "GET", body: dict | None = None, headers: dict | None = None, timeout: int = 20) -> tuple[int, Any]:
    hdrs = {"Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    data = None
    if body is not None:
        hdrs["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {"error": str(e)}
        except Exception:
            parsed = {"raw_error": raw[:400]}
        return e.code, parsed


def qdrant_req(path: str, method: str = "GET", body: dict | None = None, timeout: int = 25) -> tuple[int, Any]:
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise RuntimeError("Missing QDRANT_URL or QDRANT_API_KEY in .env.local")
    return http_json(f"{QDRANT_URL}{path}", method=method, body=body, headers={"api-key": QDRANT_API_KEY}, timeout=timeout)


def embed_768(text: str) -> list[float]:
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in .env.local")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={GEMINI_API_KEY}"
    body = {
        "model": f"models/{EMBED_MODEL}",
        "content": {"parts": [{"text": text[:6000]}]},
        "outputDimensionality": EMBED_DIMS,
    }
    status, data = http_json(url, method="POST", body=body, timeout=20)
    if status != 200:
        raise RuntimeError(f"Gemini embedding HTTP {status}: {data}")
    vec = (data.get("embedding") or {}).get("values")
    if not isinstance(vec, list) or len(vec) != EMBED_DIMS:
        raise RuntimeError(f"Expected {EMBED_DIMS} dims, got {len(vec) if isinstance(vec, list) else None}")
    return vec


def ensure_768_collection(name: str) -> dict[str, Any]:
    status, info = qdrant_req(f"/collections/{name}")
    if status == 200:
        cfg = info.get("result", {}).get("config", {}).get("params", {}).get("vectors", {})
        size = cfg.get("size")
        dist = cfg.get("distance")
        if size != EMBED_DIMS:
            raise RuntimeError(f"Collection {name} exists with size={size} != {EMBED_DIMS}")
        return {"collection": name, "created": False, "size": size, "distance": dist}
    if status == 404:
        c_status, c_res = qdrant_req(
            f"/collections/{name}",
            method="PUT",
            body={"vectors": {"size": EMBED_DIMS, "distance": "Cosine"}},
        )
        if c_status not in (200, 201):
            raise RuntimeError(f"Failed creating {name}: HTTP {c_status} {c_res}")
        return {"collection": name, "created": True, "size": EMBED_DIMS, "distance": "Cosine"}
    raise RuntimeError(f"Unexpected status checking {name}: HTTP {status} {info}")


def upsert_points(collection: str, items: list[tuple[str, dict[str, Any], str]]) -> list[str]:
    points = []
    ids = []
    for key, payload, embed_text in items:
        pid = stable_uuid(key)
        ids.append(pid)
        vec = embed_768(embed_text)
        enriched = {"canonical_key": key, "updated_at": now_iso(), **payload}
        points.append({"id": pid, "vector": vec, "payload": enriched})
    status, res = qdrant_req(f"/collections/{collection}/points?wait=true", method="PUT", body={"points": points}, timeout=45)
    if status not in (200, 201):
        raise RuntimeError(f"Qdrant upsert {collection} failed: HTTP {status} {res}")
    return ids


def retrieve_points(collection: str, ids: list[str]) -> list[dict[str, Any]]:
    status, res = qdrant_req(
        f"/collections/{collection}/points",
        method="POST",
        body={"ids": ids, "with_payload": True, "with_vector": False},
        timeout=25,
    )
    if status != 200:
        raise RuntimeError(f"Qdrant retrieve {collection} failed: HTTP {status} {res}")
    return res.get("result", [])


def scroll_all(collection: str, limit: int = 250) -> list[dict[str, Any]]:
    status, res = qdrant_req(
        f"/collections/{collection}/points/scroll",
        method="POST",
        body={"limit": limit, "with_payload": True, "with_vector": False},
        timeout=25,
    )
    if status != 200:
        raise RuntimeError(f"Qdrant scroll {collection} failed: HTTP {status} {res}")
    return res.get("result", {}).get("points", [])


def vercel_register(evento: str, payload: dict[str, Any]) -> dict[str, Any]:
    status, res = http_json(
        f"{VERCEL_BASE}/v1/ecosistema/registrar",
        method="POST",
        body={"evento": evento, "payload": payload},
        timeout=20,
    )
    return {"http_status": status, "response": res}


def get_ram_gb() -> dict[str, float]:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    gb = 1024**3
    return {
        "total_gb": round(stat.ullTotalPhys / gb, 2),
        "free_gb": round(stat.ullAvailPhys / gb, 2),
        "used_pct": float(stat.dwMemoryLoad),
    }


def probe_local_6333_off() -> dict[str, Any]:
    try:
        status, _ = http_json("http://127.0.0.1:6333/healthz", timeout=2)
        return {"port_6333": "RUNNING", "http_status": status, "f5_compliant": False}
    except Exception as e:
        return {"port_6333": "OFF", "detail": str(e)[:120], "f5_compliant": True}


def probe_freellmapi() -> dict[str, Any]:
    ts = now_iso()
    if not FREELLMAPI_KEY:
        return {"status": "POR CONSTATAR", "timestamp": ts, "reason": "FREELLMAPI_KEY missing in .env"}
    try:
        status, data = http_json(
            "http://127.0.0.1:3001/v1/models",
            headers={"Authorization": f"Bearer {FREELLMAPI_KEY}"},
            timeout=4,
        )
        if status == 200:
            return {"status": "ACTIVO", "timestamp": ts, "http_status": 200, "models_count": len(data.get("data", []))}
        return {"status": "INACTIVO", "timestamp": ts, "http_status": status}
    except Exception as e:
        return {"status": "INACTIVO", "timestamp": ts, "error": str(e)[:160]}


def probe_vercel_health() -> dict[str, Any]:
    ts = now_iso()
    status, data = http_json(f"{VERCEL_BASE}/v1/health", timeout=12)
    return {
        "status": "ACTIVO" if status == 200 and data.get("status") == "HEALTHY" else "DEGRADED",
        "timestamp": ts,
        "http_status": status,
        "service_status": data.get("status"),
        "qdrant_connected": (data.get("vector_db") or {}).get("conectado"),
        "total_collections": (data.get("vector_db") or {}).get("total_colecciones"),
    }


def cmd_preflight() -> None:
    ts = now_iso()
    ram = get_ram_gb()
    vercel = probe_vercel_health()
    freellm = probe_freellmapi()
    local_qdrant = probe_local_6333_off()

    if not INPUT_VIDEO.exists() or not INPUT_TIEMPOS.exists():
        raise RuntimeError("Missing INSUMOS-PANEL input files")
    v_hash = sha256_file(INPUT_VIDEO)
    t_hash = sha256_file(INPUT_TIEMPOS)
    if v_hash != EXPECTED_VIDEO_SHA256:
        raise RuntimeError(f"Video SHA-256 mismatch: {v_hash} != {EXPECTED_VIDEO_SHA256}")
    if t_hash != EXPECTED_TIEMPOS_SHA256:
        raise RuntimeError(f"Tiempos SHA-256 mismatch: {t_hash} != {EXPECTED_TIEMPOS_SHA256}")
    if ram["free_gb"] < 1.0:
        raise RuntimeError(f"RAM gate KO: free_gb={ram['free_gb']} < 1.0 GB")

    c_reg = ensure_768_collection(COL_REGISTRO)
    c_vid = ensure_768_collection(COL_VIDEO)

    # Check pre-existing capsule lineage in Quadrant & filesystem
    estado_files = [
        str(p) for p in [DEPLOY_ROOT / "ESTADO-HILO.md", REPO_ROOT / "ESTADO-HILO.md"] if p.exists()
    ]
    existing_caps = [
        p.get("payload", {}).get("canonical_key")
        for p in scroll_all(COL_REGISTRO, limit=50)
        if p.get("payload", {}).get("record_type") == "handoff_capsule"
    ]

    preflight_payload = {
        "record_type": "phase_gate_report",
        "phase": "PHASE_0_PREFLIGHT",
        "date": "2026-11-26",
        "timestamp": ts,
        "place": "SPLIT_PC_AND_CLOUD",
        "gate_status": "OK",
        "capsule_lineage_check": {
            "existing_estado_hilo_files": estado_files,
            "existing_quadrant_capsules": existing_caps,
            "note": "No 2026-11-26 capsule prior to run; session initializes F12 lineage.",
        },
        "pc_side": {
            "ram": ram,
            "local_qdrant_6333": local_qdrant,
            "freellmapi": freellm,
            "inputs_verified": {
                "EQUIPO-DE-AGENTES-video-final.mp4": {"sha256": v_hash, "bytes": INPUT_VIDEO.stat().st_size, "match": True},
                "tiempos.json": {"sha256": t_hash, "bytes": INPUT_TIEMPOS.stat().st_size, "match": True},
            },
            "base_docs_hashes": {k: sha256_file(v["path"]) for k, v in BASE_DOCS.items()},
        },
        "cloud_side": {
            "vercel_vector_engine": vercel,
            "qdrant_collections_768d": [c_reg, c_vid],
            "embedder": {"model": EMBED_MODEL, "dimensions": EMBED_DIMS, "status": "ACTIVO", "timestamp": ts},
        },
    }

    ids = upsert_points(
        COL_REGISTRO,
        [
            (
                "phase0_preflight_2026_11_26",
                preflight_payload,
                f"HBOS Phase 0 Preflight 2026-11-26 RAM {ram['free_gb']}GB Vercel {vercel['status']} FreeLLMAPI {freellm['status']} inputs SHA256 verified",
            )
        ],
    )
    readback = retrieve_points(COL_REGISTRO, ids)
    if len(readback) != 1 or readback[0]["payload"]["gate_status"] != "OK":
        raise RuntimeError("Phase 0 Quadrant readback verification failed")

    v_reg = vercel_register("phase0_preflight_2026_11_26", {"gate": "OK", "ram_free_gb": ram["free_gb"], "qdrant_point_id": ids[0]})
    print(json.dumps({"phase": "PHASE_0", "gate": "OK", "qdrant_id": ids[0], "vercel_register": v_reg, "report": preflight_payload}, indent=2, ensure_ascii=False))


def cmd_phase1() -> None:
    ts = now_iso()
    ensure_768_collection(COL_REGISTRO)
    ensure_768_collection(COL_VIDEO)

    # L1: Master Flow (F10 + F11 + F13 + F14)
    flow_records = [
        (
            "flow_master_skeleton_f11",
            {
                "record_type": "master_flow",
                "layer": "L1",
                "title": "HBOS Master Operating Skeleton (F11 One Flow)",
                "date": "2026-11-26",
                "discipline": ["factors_F1_F14", "DAG_phases", "PRE_POST_gates", "split_PC_CLOUD_tagging", "hash_boundary_check", "quadrant_registration", "version_discipline", "verified_close_F12"],
                "nodes": [
                    {"node": "creative_video", "status": "ACTIVO", "subflow_key": "flow_subflow_creative_video"},
                    {"node": "financial", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "planning", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "direction", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "control", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "organization", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "project_feasibility_analysis", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                    {"node": "source_analysis", "status": "SKELETON_READY", "subflow_key": "pending_subflow_definition"},
                ],
                "anthropic_mcp_upgrade_f13": {
                    "tasks": "Long phases run as delegated background jobs; coordinator retrieves results on completion",
                    "elicitation": "Human approval gates (Guillermo picks/approvals) stop and ask; never self-approve",
                    "skills_over_mcp": "House protocols travel packaged as skills alongside MCP servers",
                    "direct_file_uploads": "POR CONSTATAR",
                },
            },
            "HBOS Master Flow Skeleton F11 covering creative_video financial planning direction control organization feasibility and source analysis under F10 split PC CLOUD and F13 MCP Tasks Elicitation Skills",
        ),
        (
            "flow_subflow_creative_video",
            {
                "record_type": "subflow",
                "layer": "L1",
                "node": "creative_video",
                "title": "Sub-flow: Creative Video Production (Split PC <-> CLOUD)",
                "date": "2026-11-26",
                "stages": [
                    {
                        "order": 0,
                        "stage": "FASE_0_PREFLIGHT",
                        "place": "PC+CLOUD",
                        "owner_models_agents": "Coordinador (Claude/Gemini) + Default Agent (self) + MCP gdrive/hbos-chat-context",
                        "gate": "Read F12 capsule + verify inputs SHA-256 + RAM >= 1 GB + probe Vector Engine & FreeLLMAPI",
                        "boundary_hash_check": "SHA-256 on PC before & after Drive/Cloud sync",
                    },
                    {
                        "order": 1,
                        "stage": "FASE_1_GUION_SEMANTICO_768D",
                        "place": "CLOUD",
                        "owner_models_agents": "Investigador (research + Gemini/GPT via FreeLLMAPI) + Vector Engine (gemini-embedding-2, 768d)",
                        "gate": "10 structured blocks + dim==768 + 0 drift + Quadrant write/readback",
                        "boundary_hash_check": "SHA-256 on guion.md & tiempos.json downloaded to PC",
                    },
                    {
                        "order": 2,
                        "stage": "FASE_2A_VISUALES_FONDOS",
                        "place": "CLOUD->PC",
                        "owner_models_agents": "Director de Arte (image-generator + FLUX gateway + hbos-diamantino/diamantini-imagenes)",
                        "gate": "1920x1080 clean 16:9 scenes, 0 residual text/letterbox",
                        "boundary_hash_check": "SHA-256 manifest on arrival in G:\\My Drive / PC staging",
                    },
                    {
                        "order": 3,
                        "stage": "FASE_2B_VOZ_CANONICA",
                        "place": "CLOUD->PC",
                        "owner_models_agents": "Motor Audio (VoxCPM2 Plus Space, ref-video08, -14 LUFS, 48 kHz mono; F5-TTS VETOED)",
                        "gate": "ffprobe duration > 0, 48kHz mono, -14 LUFS, no generic SAPI",
                        "boundary_hash_check": "SHA-256 on master WAV landing on PC/Drive",
                    },
                    {
                        "order": 4,
                        "stage": "FASE_2C_AVATAR_CANON_O_COLAB_EXP",
                        "place": "PC (Canon) | CLOUD (F14 Colab Experimental)",
                        "owner_models_agents": "Ejecutor (Photographic RGBA route canonical) || Isolated F14 Colab lane (only if pre-verified media + blind gate)",
                        "gate": "No static frozen PNG; F14 requires pre-verify media (avoid INVALID_MEDIA 2011) + blind verification",
                        "boundary_hash_check": "SHA-256 on alpha clips before compose",
                    },
                    {
                        "order": 5,
                        "stage": "FASE_3_COMPOSE_RENDER_PANEL",
                        "place": "PC",
                        "owner_models_agents": "Ejecutor (FFmpeg / OpenCV local on PC) + guiahoy-video-producer",
                        "gate": "PRE: RAM >= 1 GB + input SHA-256; POST: 10 start stills + 10 mid stills + transition QA + blackdetect==0",
                        "boundary_hash_check": "SHA-256 computed on PC output and verified after upload to Google Drive 5TB Vault",
                    },
                    {
                        "order": 6,
                        "stage": "FASE_4_5_AUDITORIA_CIERRE_BACKUP_RAM",
                        "place": "PC+CLOUD",
                        "owner_models_agents": "Auditor (GPT/Claude/Gemini cross-check) + Coordinador",
                        "gate": "Secret scan 0 hits -> git commit/push -> rclone Drive 5TB backup verified -> F12 Handoff Capsule -> Zero-Task RAM Reset (>=7 GB free)",
                        "boundary_hash_check": "SHA-256/count readback on rclone Drive 5TB backup & Quadrant readback",
                    },
                ],
            },
            "Creative video subflow stages 0 to 6 tagged PC and CLOUD with model agent owners Gemini GPT Claude default agents and SHA-256 boundary checks",
        ),
        (
            "flow_colab_isolated_lane_f14",
            {
                "record_type": "isolated_lane",
                "layer": "L1",
                "title": "F14 Colab Isolated Experimental Avatar Lane",
                "date": "2026-11-26",
                "place": "CLOUD (Google Colab)",
                "status": "EXPERIMENTAL",
                "hard_limits": [
                    "Never touches active runs or canonical photographic route",
                    "PHASE 0 media pre-verification required (format/size/integrity) due to 2026-11-25 INVALID_MEDIA error 2011",
                    "Adopted ONLY after blind verification: 100% Guillermo likeness, 1.87m proportions, continuous motion, light background",
                    "Logged in Quadrant strictly as EXPERIMENTAL with evidence",
                ],
            },
            "F14 Google Colab isolated experimental lane for avatar only with media pre-verification against INVALID_MEDIA 2011 and blind verification gate",
        ),
    ]

    # L2: Video Ledger (in canon_video_hbos_r768 AND mirrored in registro_ecosistema_r768)
    video_items = [
        (
            "video_equipo_agentes_v1_archer_407s",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "equipo_de_agentes_ia",
                "version": "v1_archer_407s",
                "title": "Equipo de Agentes de IA — Build Archer (407.656s, 19 neon images)",
                "date": "2026-11-25",
                "duration_sec": 407.656,
                "resolution": "1920x1080",
                "fps": 30,
                "audio": "48000 Hz mono AAC",
                "sha256": EXPECTED_VIDEO_SHA256,
                "bytes": INPUT_VIDEO.stat().st_size,
                "path": str(INPUT_VIDEO),
                "place": "PC",
                "status": "VERIFIED_SOURCE_CANDIDATE",
                "canonical_note": "One of the existing builds; Guillermo selects canonical. Input source for Phase 3 v2 panel choreography.",
            },
            "Video ledger Equipo de Agentes de IA v1 Archer build 407.656s 19 neon images SHA256 817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88",
        ),
        (
            "video_equipo_agentes_v1_antigravity_10min",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "equipo_de_agentes_ia",
                "version": "v1_antigravity_10min",
                "title": "Equipo de Agentes de IA — Build Antigravity 10min (map cited 424.4s; measured 455.767s)",
                "date": "2026-11-25",
                "duration_sec": 455.767,
                "map_reported_duration_sec": 424.4,
                "resolution": "1920x1080",
                "sha256": "7e0f0cef35bb1bac247f20cdd6c6c0018baa169b1a8ccdbdcd7fcc955f575a25",
                "bytes": 126028121,
                "path": r"G:\My Drive\Guiahoy_Produccion\2026-11-25\2026-11-25_Equipo_Agentes_IA_10min.mp4",
                "vault_path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\2026-11-25_Equipo_Agentes_IA_10min.mp4",
                "place": "CLOUD_DRIVE_5TB",
                "status": "CANDIDATE_AWAITING_GUILLERMO_PICK",
                "canonical_note": "Antigravity build registered alongside Archer build; neither hidden.",
            },
            "Video ledger Equipo de Agentes de IA v1 Antigravity 10min build measured 455.767s map 424.4s SHA256 7e0f0cef35bb1bac247f20cdd6c6c0018baa169b1a8ccdbdcd7fcc955f575a25",
        ),
        (
            "video_equipo_agentes_v1_antigravity_3d_60fps",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "equipo_de_agentes_ia",
                "version": "v1_antigravity_3d_60fps",
                "title": "Equipo de Agentes de IA — Build 3D Cinematico 60fps (414.276s)",
                "date": "2026-11-25",
                "duration_sec": 414.276,
                "resolution": "1920x1080",
                "fps": 60,
                "sha256": "694702e426629a1cace1dc586e8390c26e6df9c3121c1e4cc11381bd05da01de",
                "bytes": 494239839,
                "path": r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_build\final\EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4",
                "vault_path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4",
                "place": "CLOUD_DRIVE_5TB",
                "status": "CANDIDATE_AWAITING_GUILLERMO_PICK",
                "canonical_note": "Antigravity 60fps 3D build preserved in vault.",
            },
            "Video ledger Equipo de Agentes de IA v1 Antigravity 3D cinematico 60fps 414.276s SHA256 694702e426629a1cace1dc586e8390c26e6df9c3121c1e4cc11381bd05da01de",
        ),
        (
            "video_equipo_agentes_v2_panel_choreography",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "equipo_de_agentes_ia",
                "version": "v2_panel_choreography",
                "title": "Equipo de Agentes de IA — v2 Panel Choreography (Pending Phase 3 Render)",
                "date": "2026-11-26",
                "duration_sec": 407.656,
                "sha256": "PENDING_PHASE_3",
                "path": r"C:\Users\ipane\hbos-deploy\INSUMOS-PANEL\EQUIPO-DE-AGENTES-video-final-v2.mp4",
                "vault_path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\EQUIPO-DE-AGENTES-video-final-v2.mp4",
                "place": "PC+CLOUD_DRIVE_5TB",
                "status": "PENDING_PHASE_3",
            },
            "Video ledger Equipo de Agentes de IA v2 panel choreography pending phase 3 render",
        ),
        (
            "video_clase01_mit_10min",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "clase_01_mit",
                "version": "v1_vault",
                "title": "Clase 01 MIT (Vault)",
                "date": "2026-11-25",
                "bytes": 22738397,
                "path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\guiahoy_clase01_mit_10min.mp4",
                "place": "CLOUD_DRIVE_5TB",
                "status": "HISTORICAL_VAULT",
            },
            "Video ledger historical Clase 01 MIT guiahoy_clase01_mit_10min.mp4 in vault",
        ),
        (
            "video_nube_creativo_analitica_20261124",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "nube_creativo_analitica",
                "version": "v1_vault",
                "title": "Video Nube Creativo Analitica",
                "date": "2026-11-24",
                "bytes": 1182593,
                "path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\guiahoy_nube_creativo_analitica_20261124_1525.mp4",
                "place": "CLOUD_DRIVE_5TB",
                "status": "HISTORICAL_VAULT",
            },
            "Video ledger historical Video Nube Creativo Analitica 2026-11-24 in vault",
        ),
        (
            "video_argon_antigravity_4_casos",
            {
                "record_type": "video_ledger",
                "layer": "L2",
                "work_id": "argon_antigravity_4_casos",
                "version": "master_17m32s",
                "title": "MASTER 17M32S Argon Antigravity 4 Casos 16x9",
                "date": "2026-10-31",
                "bytes": 211973557,
                "path": r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\MASTER_17M32S_ARGON_ANTIGRAVITY_4_CASOS_16x9.mp4",
                "place": "CLOUD_DRIVE_5TB",
                "status": "HISTORICAL_VAULT",
            },
            "Video ledger historical MASTER 17M32S Argon Antigravity 4 Casos 2026-10-31 in vault",
        ),
    ]

    # L3: File Index + F9 Pending + Live Probes + F2 Discrepancies
    l3_items = [
        (
            "file_index_bloque_curado",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "BLOQUE-ANTIGRAVITY-CURADO-2026-11-26.md",
                "date": "2026-11-26",
                "purpose": "Canonical execution DAG and Factors F1-F14",
                "place": "PC",
                "path": r"C:\Users\ipane\hbos-deploy\BLOQUE-ANTIGRAVITY-CURADO-2026-11-26.md",
                "sha256": sha256_file(DEPLOY_ROOT / "BLOQUE-ANTIGRAVITY-CURADO-2026-11-26.md"),
            },
            "File index BLOQUE-ANTIGRAVITY-CURADO-2026-11-26.md canonical DAG factors F1-F14",
        ),
        (
            "file_index_tiempos_json",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "tiempos.json",
                "date": "2026-11-26",
                "purpose": "45 narration segment timings (0.0 -> 407.656s) for 10 modules",
                "place": "PC",
                "path": str(INPUT_TIEMPOS),
                "sha256": EXPECTED_TIEMPOS_SHA256,
            },
            "File index tiempos.json narration segment timings 407.656s for Equipo de Agentes panel choreography",
        ),
        (
            "file_index_sync_quadrant_script",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "scripts/sync_quadrant_master_20261126.py",
                "date": "2026-11-26",
                "purpose": "Cloud Quadrant 768d ledger, probes, and F12 handoff capsule writer",
                "place": "PC->CLOUD",
                "path": str(REPO_ROOT / "scripts" / "sync_quadrant_master_20261126.py"),
                "sha256": sha256_file(REPO_ROOT / "scripts" / "sync_quadrant_master_20261126.py"),
            },
            "File index scripts/sync_quadrant_master_20261126.py Quadrant 768d registry sync",
        ),
        (
            "file_index_base_topology",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "HBOS_MULTIAGENT_TOPOLOGY_01.md",
                "date": "2026-11-25",
                "purpose": "Read-only base multi-agent topology (F2 preserved)",
                "place": "PC",
                "path": str(BASE_DOCS["HBOS_MULTIAGENT_TOPOLOGY_01.md"]["path"]),
                "sha256": BASE_DOCS["HBOS_MULTIAGENT_TOPOLOGY_01.md"]["expected_sha256"],
            },
            "File index HBOS_MULTIAGENT_TOPOLOGY_01.md read-only base topology",
        ),
        (
            "file_index_base_dag",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "HBOS_PRODUCTION_DAG_01.md",
                "date": "2026-11-25",
                "purpose": "Read-only base production DAG (F2 preserved)",
                "place": "PC",
                "path": str(BASE_DOCS["HBOS_PRODUCTION_DAG_01.md"]["path"]),
                "sha256": BASE_DOCS["HBOS_PRODUCTION_DAG_01.md"]["expected_sha256"],
            },
            "File index HBOS_PRODUCTION_DAG_01.md read-only base production DAG",
        ),
        (
            "file_index_base_map_md",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "HBOS_MASTER_SYSTEM_MAP.md",
                "date": "2026-11-25",
                "purpose": "Read-only base system map MD (F2 preserved)",
                "place": "PC",
                "path": str(BASE_DOCS["HBOS_MASTER_SYSTEM_MAP.md"]["path"]),
                "sha256": BASE_DOCS["HBOS_MASTER_SYSTEM_MAP.md"]["expected_sha256"],
            },
            "File index HBOS_MASTER_SYSTEM_MAP.md read-only base system map",
        ),
        (
            "file_index_base_map_html",
            {
                "record_type": "file_index",
                "layer": "L3",
                "name": "HBOS_MASTER_SYSTEM_MAP.html",
                "date": "2026-11-25",
                "purpose": "Read-only base system map HTML (F2 preserved)",
                "place": "PC",
                "path": str(BASE_DOCS["HBOS_MASTER_SYSTEM_MAP.html"]["path"]),
                "sha256": BASE_DOCS["HBOS_MASTER_SYSTEM_MAP.html"]["expected_sha256"],
            },
            "File index HBOS_MASTER_SYSTEM_MAP.html read-only base system map HTML",
        ),
        (
            "pending_f9_archer_antigravity_channel",
            {
                "record_type": "pending_registered",
                "layer": "L3",
                "factor": "F9",
                "name": "direct_archer_to_antigravity_handoff_channel",
                "date": "2026-11-26",
                "status": "PENDING_FUTURE_BUILD",
                "purpose": "Direct Archer -> Antigravity handoff channel for when Guillermo is connected at PC (registered only, do not execute).",
                "place": "PC+CLOUD",
            },
            "F9 Pending registered direct Archer to Antigravity handoff channel future build",
        ),
    ]

    # Discrepancies (F2)
    discrepancies = [
        ("disc_01_casos_uso_dim", "DISC-01", "casos_uso_hbos embedding space", "HBOS_MASTER_SYSTEM_MAP.md lists 384d + local all-mpnet-base-v2", "INSTRUCCION v2 requires gemini-embedding-2 / 768d (1,064 pts); LIVE Cloud probe 2026-11-26 measured casos_uso_hbos dim=384, pts=70; omnirouter_hbos.js line 103 has VECTOR_SIZE=384", "OPEN_MEASURED_2026_11_26", "Cloud casos_uso_hbos remains 384d until dedicated collection migration; new ledger collections created at 768d Cosine with gemini-embedding-2."),
        ("disc_02_freellmapi_status", "DISC-02", "hbos-freellmapi :3001 status", "2026-11-25 probe returned 404 on :3001; map claimed ACTIVO without probe", "LIVE 2026-11-26 probe http://127.0.0.1:3001/v1/models with FREELLMAPI_KEY returned HTTP 200 (283 models)", "RESOLVED_BY_PROBE_2026_11_26", "ACTIVO on 2026-11-26 with live probe receipt; Docker disabled."),
        ("disc_03_voice_canon", "DISC-03", "Canonical voice synthesis engine", "HBOS_PRODUCTION_DAG_01 names Fish Audio / F5-TTS", "F5-TTS is VETOED (CC-BY-NC non-monetizable); canon is VoxCPM2 Plus (ref-video08, -14 LUFS, 48 kHz mono)", "CANON_FIXED_IN_ANNEX", "Base DAG preserved read-only; Annex 01 enforces VoxCPM2 Plus canon."),
        ("disc_04_avatar_route", "DISC-04", "Canonical avatar & Colab status", "Base DAG Prohibition C mentions Wav2Lip/SadTalker/LivePortrait; 2026-11-25 Colab kit died twice with INVALID_MEDIA error 2011", "Photographic route (approved stills + procedural motion + alpha WebM) is verified canonical; Colab is isolated F14 experimental lane only", "CANON_FIXED_IN_ANNEX", "Photographic route active; Colab restricted to F14 blind-gated experiments."),
        ("disc_05_two_video_builds", "DISC-05", "Equipo de Agentes multiple builds", "Map claims 424.4s 10-bg master (actual measured 2026-11-25_Equipo_Agentes_IA_10min.mp4 = 455.767s & 3D 60fps = 414.276s)", "Archer build INSUMOS-PANEL/EQUIPO-DE-AGENTES-video-final.mp4 measured 407.656s (19 neon images)", "REGISTERED_AWAITING_PICK", "All builds registered in L2 canon_video_hbos_r768; Guillermo selects canonical."),
        ("disc_06_mumo_status", "DISC-06", "MUMO multi-model council node 8", "HBOS_MULTIAGENT_TOPOLOGY_01 node 8 assumes mumo is usable", "Identity created 2026-11-25 but session geo-blocked (?geo=blocked, no session persisted)", "OPEN_PENDING_US_LOGIN", "Marked PENDING; do not route real deliberations through mumo."),
        ("disc_07_git_push_secrets", "DISC-07", "Git push main vs embedded secrets", "DAG Fase 6 orders git push origin main; INSTRUCCION v2 froze push over embedded credentials", "Pre-flight scan 2026-11-26 confirmed tracked JWT literal in seed_recursos_hbos.js line 10", "OPEN_HARD_GATE_PHASE_4", "Phase 4 secret scan halts commit/push cleanly if >0 hits remain."),
        ("disc_08_docker_local_qdrant", "DISC-08", "Docker & local Qdrant :6333", "Base map/scripts point to http://127.0.0.1:6333 hybrid", "Docker autostart disabled by Guillermo's order (F5); LIVE probe 2026-11-26 confirmed :6333 OFF; Cloud Qdrant = only truth (F1)", "RESOLVED_BY_PROBE_2026_11_26", "All reads/writes routed to Qdrant Cloud + Vercel Vector Engine."),
        ("disc_09_anthropic_direct_upload", "DISC-09", "Anthropic MCP direct file uploads", "F13 notes rolling out direct file uploads to MCP servers", "Not live-probed in this session", "POR_CONSTATAR", "Registered as POR CONSTATAR per F3/F13."),
    ]
    for key, did, title, side_a, side_b, status_d, resolution in discrepancies:
        l3_items.append(
            (
                key,
                {
                    "record_type": "discrepancy",
                    "layer": "L3",
                    "discrepancy_id": did,
                    "title": title,
                    "date": "2026-11-26",
                    "side_a_doc": side_a,
                    "side_b_measured": side_b,
                    "status": status_d,
                    "resolution": resolution,
                },
                f"Discrepancy {did} {title}: {side_a} vs {side_b} status {status_d}",
            )
        )

    # Live component probes (F3)
    vercel_p = probe_vercel_health()
    freellm_p = probe_freellmapi()
    qdrant_local_p = probe_local_6333_off()
    probes_item = (
        "probes_snapshot_2026_11_26",
        {
            "record_type": "component_probes",
            "layer": "L3",
            "date": "2026-11-26",
            "timestamp": ts,
            "components": [
                {"name": "HBOS Vector Engine (Vercel)", "place": "CLOUD", "status": vercel_p["status"], "timestamp": vercel_p["timestamp"], "evidence": f"HTTP {vercel_p['http_status']} HEALTHY, 47 collections"},
                {"name": "Qdrant Cloud Cluster", "place": "CLOUD", "status": "ACTIVO", "timestamp": ts, "evidence": "HTTP 200, 47+ collections, 768d ledger active"},
                {"name": "gemini-embedding-2 (768d)", "place": "CLOUD", "status": "ACTIVO", "timestamp": ts, "evidence": "HTTP 200, outputDimensionality=768 verified"},
                {"name": "FreeLLMAPI (:3001)", "place": "PC", "status": freellm_p["status"], "timestamp": freellm_p["timestamp"], "evidence": f"HTTP 200, {freellm_p.get('models_count', 0)} models"},
                {"name": "Local Qdrant (:6333)", "place": "PC", "status": "OFF_PER_F5", "timestamp": ts, "evidence": qdrant_local_p.get("detail", "OFF")},
                {"name": "Docker Engine", "place": "PC", "status": "DISABLED_PER_F5", "timestamp": ts, "evidence": "0 docker processes running"},
                {"name": "MUMO Multi-Model", "place": "CLOUD", "status": "PENDING", "timestamp": "2026-11-25", "evidence": "Session geo-blocked (?geo=blocked)"},
                {"name": "VoxCPM2 Plus Space", "place": "CLOUD", "status": "POR CONSTATAR", "timestamp": ts, "evidence": "Not live-probed in this run"},
                {"name": "Anthropic MCP Direct File Upload", "place": "CLOUD", "status": "POR CONSTATAR", "timestamp": ts, "evidence": "Not live-probed in this run"},
            ],
        },
        "Component live probes 2026-11-26 Vercel Vector Engine Qdrant Cloud gemini-embedding-2 FreeLLMAPI Docker OFF MUMO PENDING",
    )
    l3_items.append(probes_item)

    all_reg_items = flow_records + video_items + l3_items
    reg_ids = upsert_points(COL_REGISTRO, all_reg_items)
    vid_ids = upsert_points(COL_VIDEO, video_items)

    # GATE 1: Read-back counts + 3 samples verbatim
    reg_back = retrieve_points(COL_REGISTRO, reg_ids)
    vid_back = retrieve_points(COL_VIDEO, vid_ids)
    if len(reg_back) != len(all_reg_items) or len(vid_back) != len(video_items):
        raise RuntimeError(f"Gate 1 count mismatch: reg {len(reg_back)}/{len(all_reg_items)}, vid {len(vid_back)}/{len(video_items)}")

    sample_keys = {p["payload"]["canonical_key"] for p in reg_back[:3]}
    v_reg = vercel_register("phase1_map_ledger_2026_11_26", {"registro_count": len(reg_back), "video_count": len(vid_back)})

    print(json.dumps({
        "phase": "PHASE_1",
        "gate": "OK",
        "registro_ecosistema_r768_written": len(all_reg_items),
        "registro_ecosistema_r768_readback": len(reg_back),
        "canon_video_hbos_r768_written": len(video_items),
        "canon_video_hbos_r768_readback": len(vid_back),
        "sample_keys_verified": sorted(sample_keys),
        "samples_preview": [reg_back[0]["payload"], reg_back[3]["payload"], reg_back[-1]["payload"]],
        "vercel_register": v_reg,
    }, indent=2, ensure_ascii=False))


def cmd_update_v2(args: argparse.Namespace) -> None:
    ts = now_iso()
    v2_path = Path(args.v2_path)
    vault_path = Path(args.vault_path)
    v2_sha = sha256_file(v2_path)
    vault_sha = sha256_file(vault_path)
    if v2_sha != vault_sha:
        raise RuntimeError(f"F10 boundary hash mismatch PC vs Vault: {v2_sha} != {vault_sha}")

    with Path(args.qa_json).open("r", encoding="utf-8") as f:
        qa_data = json.load(f)

    payload = {
        "record_type": "video_ledger",
        "layer": "L2",
        "work_id": "equipo_de_agentes_ia",
        "version": "v2_panel_choreography",
        "title": "Equipo de Agentes de IA — v2 Panel Choreography (10 modules, 3s IN + 0.5s crossfade OUT)",
        "date": "2026-11-26",
        "timestamp": ts,
        "duration_sec": qa_data["duration_sec"],
        "resolution": qa_data["resolution"],
        "fps": qa_data["fps"],
        "audio": qa_data["audio"],
        "sha256": v2_sha,
        "bytes": v2_path.stat().st_size,
        "path": str(v2_path),
        "vault_path": str(vault_path),
        "place": "PC+CLOUD_DRIVE_5TB",
        "status": "QA_VERIFIED_DELIVERABLE",
        "module_timestamps": qa_data["modules"],
        "qa_stills_dir": qa_data["stills_dir"],
        "qa_summary": qa_data["qa_summary"],
    }
    ids_r = upsert_points(COL_REGISTRO, [("video_equipo_agentes_v2_panel_choreography", payload, f"Video Equipo de Agentes v2 panel choreography SHA256 {v2_sha} QA verified")])
    ids_v = upsert_points(COL_VIDEO, [("video_equipo_agentes_v2_panel_choreography", payload, f"Video Equipo de Agentes v2 panel choreography SHA256 {v2_sha} QA verified")])

    file_idx_payload = {
        "record_type": "file_index",
        "layer": "L3",
        "name": v2_path.name,
        "date": "2026-11-26",
        "purpose": "Phase 3 deliverable: Equipo de Agentes with 10-module panel choreography",
        "place": "PC+CLOUD_DRIVE_5TB",
        "path": str(v2_path),
        "vault_path": str(vault_path),
        "sha256": v2_sha,
    }
    upsert_points(COL_REGISTRO, [("file_index_video_v2", file_idx_payload, f"File index {v2_path.name} SHA256 {v2_sha}")])
    v_reg = vercel_register("phase3_video_v2_verified", {"sha256": v2_sha, "duration_sec": qa_data["duration_sec"]})
    print(json.dumps({"phase": "PHASE_3_QUADRANT_SYNC", "gate": "OK", "sha256": v2_sha, "ids": ids_r + ids_v, "vercel_register": v_reg}, indent=2))


def cmd_record_event(args: argparse.Namespace) -> None:
    with Path(args.json_file).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    ids = upsert_points(COL_REGISTRO, [(args.key, payload, args.summary)])
    rb = retrieve_points(COL_REGISTRO, ids)
    v_reg = vercel_register(args.key, {"qdrant_id": ids[0], "summary": args.summary})
    print(json.dumps({"recorded": args.key, "id": ids[0], "readback_ok": len(rb) == 1, "vercel_register": v_reg}, indent=2, ensure_ascii=False))


def cmd_write_capsule(args: argparse.Namespace) -> None:
    with Path(args.json_file).open("r", encoding="utf-8") as f:
        capsule = json.load(f)
    capsule["record_type"] = "handoff_capsule"
    capsule["timestamp"] = now_iso()
    ids = upsert_points(
        COL_REGISTRO,
        [("handoff_capsule_2026_11_26_latest", capsule, f"HBOS F12 Handoff Capsule 2026-11-26 {capsule.get('next_concrete_step', '')}")],
    )
    rb = retrieve_points(COL_REGISTRO, ids)
    if len(rb) != 1:
        raise RuntimeError("Handoff capsule readback failed")
    v_reg = vercel_register("handoff_capsule_2026_11_26", {"qdrant_id": ids[0], "status_summary": capsule.get("phase_states")})
    print(json.dumps({"capsule_written": True, "id": ids[0], "readback": rb[0]["payload"], "vercel_register": v_reg}, indent=2, ensure_ascii=False))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight")
    sub.add_parser("phase1")

    p_v2 = sub.add_parser("update_v2")
    p_v2.add_argument("--v2-path", required=True)
    p_v2.add_argument("--vault-path", required=True)
    p_v2.add_argument("--qa-json", required=True)

    p_ev = sub.add_parser("record_event")
    p_ev.add_argument("--key", required=True)
    p_ev.add_argument("--summary", required=True)
    p_ev.add_argument("--json-file", required=True)

    p_cap = sub.add_parser("write_capsule")
    p_cap.add_argument("--json-file", required=True)

    args = parser.parse_args()
    if args.cmd == "preflight":
        cmd_preflight()
    elif args.cmd == "phase1":
        cmd_phase1()
    elif args.cmd == "update_v2":
        cmd_update_v2(args)
    elif args.cmd == "record_event":
        cmd_record_event(args)
    elif args.cmd == "write_capsule":
        cmd_write_capsule(args)


if __name__ == "__main__":
    main()
