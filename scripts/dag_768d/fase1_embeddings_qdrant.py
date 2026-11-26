#!/usr/bin/env python3
"""FASE 1 — 768D Semantic Factorization, Qdrant Indexing, and Gapless 60fps Timeline."""

import json
import math
import re
import sys
import uuid
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

BG_SEMANTICS = {
    1: "Estudio futurista Rionegro Antioquia escritorio ejecutivo equipo agentes IA versus modelo unico sobrecargado iluminacion ambar cian",
    2: "Agente Coordinador director de orquesta autonomo descomposicion de tareas liderazgo operaciones flujo central",
    3: "Agente Investigador mineria de datos tiempo real evidencia verificada bases de datos fuentes confiables sin improvisar",
    4: "Agente Ejecutor artesano tecnico codigo automatizacion propuestas comerciales diseno visual precision quirurgica",
    5: "Agente Auditor control de calidad esceptico profesional cero alucinacion validacion numerica ciclo retroalimentacion",
    6: "Protocolos comunicacion handoffs estructurados linea de produccion industrial estados claros entradas salidas",
    7: "Humano en el Bucle Human in the Loop mesa de trabajo unificada criterio humano aprobacion estrategica un clic",
    8: "Aplicacion empresarial Antioquia Colombia ventas respuesta menos de diez segundos cotizaciones auditoria facturas infraestructura propia",
    9: "Metricas productividad impacto operativo cinco especialistas en una maquina reduccion tiempos ciclo mas del noventa por ciento",
    10: "Conclusion hoja de ruta despliegue equipo agentes autonomia soberania 0 SaaS Tax Guia Hoy mesa de trabajo",
}

BLOCK_VISUAL_CARDS = {
    1: {
        "eyebrow": "BLOQUE 01 · PARADIGMA MULTI-AGENTE",
        "headline": "De un Chatbot Saturado a un Equipo de IA",
        "diagram_type": "vs_bottleneck",
        "kpis": [
            {"label": "ERROR COMÚN", "value": "1 Modelo = Todo", "tone": "amber"},
            {"label": "RESULTADO", "value": "Superficial / Confuso", "tone": "amber"},
            {"label": "ARQUITECTURA HBOS", "value": "Equipo Especializado", "tone": "cyan"},
        ],
        "bullets": [
            "Rionegro, Antioquia · Enfoque Empresarial Real",
            "Roles claros: Investigar · Redactar · Auditar · Ejecutar",
            "Cero improvisación: herramientas y objetivos dedicados",
        ],
        "camera_mode": "dolly_in",
        "preferred_poses": ["avatar-pose-t-arms-open-narrower.png", "avatar-pose-t-arms-open-palms-front.png", "avatar-pose-t-calm-both.png"],
    },
    2: {
        "eyebrow": "BLOQUE 02 · ARQUITECTURA DE CONTROL",
        "headline": "Agente Coordinador: Director de Orquesta",
        "diagram_type": "orchestrator_hub",
        "kpis": [
            {"label": "ROL CENTRAL", "value": "Líder de Operaciones", "tone": "cyan"},
            {"label": "FUNCIÓN", "value": "Descomponer Tareas", "tone": "cyan"},
            {"label": "CALIDAD", "value": "Control de Tiempos", "tone": "amber"},
        ],
        "bullets": [
            "Analiza solicitudes complejas y asigna al especialista",
            "Evalúa criterios mínimos antes de avanzar fase",
            "Elimina el ruido y los reprocesos entre agentes",
        ],
        "camera_mode": "parallax_right",
        "preferred_poses": ["avatar-pose-t-calm-both.png", "avatar-pose-t-explain-R.png", "avatar-pose-t-point-up-R.png"],
    },
    3: {
        "eyebrow": "BLOQUE 03 · MINERÍA DE EVIDENCIA",
        "headline": "Agente Investigador: Contexto en Tiempo Real",
        "diagram_type": "data_mining",
        "kpis": [
            {"label": "REGLA DE ORO", "value": "Cero Opinión", "tone": "amber"},
            {"label": "INSUMOS", "value": "Evidencia Pura", "tone": "cyan"},
            {"label": "SALIDA", "value": "Datos + Citas", "tone": "cyan"},
        ],
        "bullets": [
            "Rastrea documentos internos, bases y portales sectoriales",
            "Condensa hallazgos en hechos verificados al minuto",
            "Base objetiva para cotizaciones y análisis competitivo",
        ],
        "camera_mode": "dolly_out",
        "preferred_poses": ["avatar-pose-t-chin-stroke-L.png", "avatar-pose-t-explain-R.png", "avatar-pose-t-point-left-L.png"],
    },
    4: {
        "eyebrow": "BLOQUE 04 · PRODUCCIÓN TÉCNICA",
        "headline": "Agente Ejecutor: Precisión Quirúrgica",
        "diagram_type": "executor_forge",
        "kpis": [
            {"label": "ENFOQUE", "value": "100% Producción", "tone": "cyan"},
            {"label": "VELOCIDAD", "value": "Borradores en Segundos", "tone": "cyan"},
            {"label": "RIGOR", "value": "Estilo Corporativo", "tone": "amber"},
        ],
        "bullets": [
            "Diseña propuestas, código de automatización y piezas",
            "Aplica fórmulas técnicas sin distraerse investigando",
            "Construye sobre evidencia del Investigador y pauta del Líder",
        ],
        "camera_mode": "parallax_left",
        "preferred_poses": ["avatar-pose-t-arms-open-palms-up.png", "avatar-pose-t-count-three-R.png", "avatar-pose-t-point-right-R.png"],
    },
    5: {
        "eyebrow": "BLOQUE 05 · CONTROL DE CALIDAD",
        "headline": "Agente Auditor: Cero Alucinación",
        "diagram_type": "auditor_gate",
        "kpis": [
            {"label": "PERFIL", "value": "Escéptico Profesional", "tone": "amber"},
            {"label": "VERIFICACIÓN", "value": "100% Respaldado", "tone": "cyan"},
            {"label": "GARANTÍA", "value": "Rigor Institucional", "tone": "cyan"},
        ],
        "bullets": [
            "Revisa sumas numéricas y coherencia lógica antes de salir",
            "Rechaza desfases con reporte detallado para ajuste inmediato",
            "Ciclo cerrado de retroalimentación y cero alucinaciones",
        ],
        "camera_mode": "dolly_in",
        "preferred_poses": ["avatar-pose-t-chin-stroke-R.png", "avatar-pose-t-arms-crossed.png", "avatar-pose-t-point-up-R.png"],
    },
    6: {
        "eyebrow": "BLOQUE 06 · PROTOCOLO DE TRANSFERENCIA",
        "headline": "Handoffs Estructurados entre Agentes",
        "diagram_type": "handoff_pipeline",
        "kpis": [
            {"label": "FORMATO", "value": "Datos Estándar", "tone": "cyan"},
            {"label": "ACTIVACIÓN", "value": "Automática", "tone": "cyan"},
            {"label": "FRICCIÓN", "value": "Cero Mensajes Vagos", "tone": "amber"},
        ],
        "bullets": [
            "Entradas, salidas y condiciones de éxito bien definidas",
            "Flujo tipo línea de producción industrial sin desorden",
            "Cada estación agrega valor verificado sobre la anterior",
        ],
        "camera_mode": "parallax_right",
        "preferred_poses": ["avatar-pose-t-arms-open-wider.png", "avatar-pose-t-explain-R.png", "avatar-pose-t-arms-open-palms-down.png"],
    },
    7: {
        "eyebrow": "BLOQUE 07 · METODOLOGÍA GUÍA HOY",
        "headline": "Humano en el Bucle (Human-in-the-Loop)",
        "diagram_type": "human_in_loop",
        "kpis": [
            {"label": "TRABAJO PESADO", "value": "Equipo de Agentes", "tone": "cyan"},
            {"label": "DECISIÓN FINAL", "value": "Líder del Negocio", "tone": "amber"},
            {"label": "APROBACIÓN", "value": "1 Clic Ejecutivo", "tone": "cyan"},
        ],
        "bullets": [
            "Los agentes amplifican el juicio humano, no lo reemplazan",
            "Busca, clasifica, redacta y verifica opciones viables",
            "Usted evoluciona de redactor operativo a Director General",
        ],
        "camera_mode": "dolly_out",
        "preferred_poses": ["avatar-pose-t-arms-open-palms-front.png", "avatar-pose-t-calm-both.png", "avatar-pose-t-beckon-L.png"],
    },
    8: {
        "eyebrow": "BLOQUE 08 · ANTIOQUIA Y COLOMBIA",
        "headline": "Aplicación Real: Ventas, Operaciones y Soporte",
        "diagram_type": "regional_kpis",
        "kpis": [
            {"label": "RESPUESTA CATÁLOGO", "value": "< 10 Segundos", "tone": "cyan"},
            {"label": "AUDITORÍA DIARIA", "value": "Sin Errores", "tone": "cyan"},
            {"label": "DESPLIEGUE", "value": "Infra Propia", "tone": "amber"},
        ],
        "bullets": [
            "Calificación de leads y cotizaciones a medida 24/7",
            "Auditoría de facturas, inventarios y reportes financieros",
            "Datos protegidos sobre infraestructura propia y controlada",
        ],
        "camera_mode": "parallax_left",
        "preferred_poses": ["avatar-pose-t-count-two-R.png", "avatar-pose-t-point-right-R.png", "avatar-pose-t-arms-open-narrower.png"],
    },
    9: {
        "eyebrow": "BLOQUE 09 · IMPACTO OPERATIVO REAL",
        "headline": "La Fuerza de 5 Especialistas en 1 Máquina",
        "diagram_type": "impact_chart",
        "kpis": [
            {"label": "ANTES (MANUAL)", "value": "5 Pers. · 1 Semana", "tone": "amber"},
            {"label": "CON AGENTES IA", "value": "Flujo en Minutos", "tone": "cyan"},
            {"label": "REDUCCIÓN DE CICLO", "value": "> 90%", "tone": "cyan"},
        ],
        "bullets": [
            "Elimina el esfuerzo fragmentado en procesos repetitivos",
            "Libera al equipo humano para innovar y negociar",
            "Atención cara a cara al cliente con empatía y excelencia",
        ],
        "camera_mode": "dolly_in",
        "preferred_poses": ["avatar-pose-t-both-thumbs-up.png", "avatar-pose-t-count-three-R.png", "avatar-pose-t-arms-open-palms-up.png"],
    },
    10: {
        "eyebrow": "BLOQUE 10 · SOBERANÍA TECNOLÓGICA",
        "headline": "Despliega tu Propio Equipo de Agentes",
        "diagram_type": "closing_roadmap",
        "kpis": [
            {"label": "MODELO", "value": "Autonomía Total", "tone": "cyan"},
            {"label": "ECONOMÍA", "value": "0 SaaS Tax", "tone": "cyan"},
            {"label": "INVITACIÓN", "value": "Mesa Guía Hoy", "tone": "amber"},
        ],
        "bullets": [
            "Construya sistemas organizados, no juguetes aislados",
            "Transferencia práctica de conocimiento para su empresa",
            "Configuración guiada de su primer Equipo de Agentes",
        ],
        "camera_mode": "dolly_out",
        "preferred_poses": ["avatar-pose-t-beckon-R.png", "avatar-pose-t-wave-R.png", "avatar-pose-t-arms-relaxed.png"],
    },
}


def split_into_beats(text: str) -> list[str]:
    """Split block narration text into concise spoken beats suitable for 2-line HUD captions."""
    raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    beats: list[str] = []
    for sent in raw_sentences:
        words = sent.split()
        if len(words) <= 24:
            beats.append(sent)
        else:
            # Split long sentences cleanly near midpoint at punctuation or word boundary
            mid = len(words) // 2
            best_idx = mid
            for offset in range(0, min(8, mid)):
                for cand in (mid - offset, mid + offset):
                    if 4 < cand < len(words) - 4 and words[cand - 1].endswith((",", ";", ":")):
                        best_idx = cand
                        break
                else:
                    continue
                break
            beats.append(" ".join(words[:best_idx]))
            beats.append(" ".join(words[best_idx:]))
    return beats


def allocate_integer_frames(weights: list[float], total_frames: int) -> list[int]:
    """Distribute exact integer frames summing strictly to total_frames."""
    wsum = sum(weights) or 1.0
    exact = [w / wsum * total_frames for w in weights]
    floored = [max(1, int(math.floor(x))) for x in exact]
    diff = total_frames - sum(floored)
    remainders = sorted(range(len(exact)), key=lambda i: exact[i] - floored[i], reverse=(diff > 0))
    idx = 0
    while diff != 0:
        target = remainders[idx % len(remainders)]
        if diff > 0:
            floored[target] += 1
            diff -= 1
        elif floored[target] > 1:
            floored[target] -= 1
            diff += 1
        idx += 1
    return floored


def main() -> None:
    print("=== FASE 1: FACTORIZACION 768D + QDRANT + TIMELINE ===", flush=True)
    fase0_path = cfg.BUILD_DIR / "debug_fase0.json"
    if not fase0_path.exists():
        print("FAIL-FAST: Falta debug_fase0.json", flush=True)
        sys.exit(1)
    fase0 = json.loads(fase0_path.read_text(encoding="utf-8"))
    if fase0.get("gate_0_to_1") != "PASS":
        print("FAIL-FAST: Gate 0->1 no esta en PASS", flush=True)
        sys.exit(1)

    audio_dur = float(fase0["audio_metrics"]["duration_sec"])
    total_frames = int(round(audio_dur * cfg.TARGET_FPS))
    tiempos = json.loads(cfg.TIEMPOS_SRC.read_text(encoding="utf-8"))
    bloques_src = sorted(tiempos["bloques"], key=lambda b: b["block_id"])

    # Load 768D local embedding model
    print("[L1.2] Cargando SentenceTransformer all-mpnet-base-v2 (768D)...", flush=True)
    try:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", local_files_only=True)
    except Exception:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    # Prepare texts for 768D embeddings
    available_poses = [p["name"] for p in fase0["files"]["avatar_poses"]]
    clips_manifest = json.loads((cfg.AVATAR_CLIP_LIB / "canonical_15_avatar_clips_manifest.json").read_text(encoding="utf-8"))["clips"]

    texts_to_embed: list[str] = []
    meta_records: list[dict] = []

    # 1. Blocks
    for b in bloques_src:
        texts_to_embed.append(f"{b['title']}. {b['text']}")
        meta_records.append({"kind": "script_block", "block_id": b["block_id"], "title": b["title"], "text": b["text"]})

    # 2. Backgrounds
    for i in range(1, 11):
        desc = BG_SEMANTICS[i]
        texts_to_embed.append(desc)
        meta_records.append({"kind": "background_3d", "bg_id": i, "file": f"bg_{i:02d}.jpg", "semantic": desc})

    # 3. Avatar poses
    for pname in available_poses:
        clean_desc = pname.replace("avatar-pose-t-", "").replace(".png", "").replace("-", " ")
        desc = f"Guillermo Alonso Hoyos pose presentador {clean_desc}"
        texts_to_embed.append(desc)
        meta_records.append({"kind": "avatar_pose", "file": pname, "semantic": desc})

    # 4. AVM motion clips
    for c in clips_manifest:
        desc = f"{c['clip_id']} {c['role']} {c['gesture']}"
        texts_to_embed.append(desc)
        meta_records.append({"kind": "avatar_clip", "clip_id": c["clip_id"], "file": Path(c["drive_path"]).name, "semantic": desc})

    # Compute beats first so we also embed every beat in 768D
    block_spans = []
    for idx, b in enumerate(bloques_src):
        start_s = float(b["start_sec"]) if idx > 0 else 0.0
        end_s = float(bloques_src[idx + 1]["start_sec"]) if idx < len(bloques_src) - 1 else audio_dur
        beats = split_into_beats(b["text"])
        block_spans.append({"block": b, "start_sec": start_s, "end_sec": end_s, "dur_sec": end_s - start_s, "beats": beats})

    for sp in block_spans:
        bid = sp["block"]["block_id"]
        for bi, bt in enumerate(sp["beats"], 1):
            texts_to_embed.append(bt)
            meta_records.append({"kind": "script_beat", "block_id": bid, "beat_index": bi, "text": bt})

    embeddings = model.encode(texts_to_embed, normalize_embeddings=True, show_progress_bar=False)
    embeddings = np.asarray(embeddings, dtype=np.float32)

    # Strict 768D gate assertions
    assert embeddings.ndim == 2 and embeddings.shape[1] == 768, f"Dim invalida: {embeddings.shape}"
    assert not np.isnan(embeddings).any(), "NaN detectado en embeddings 768D"
    assert not np.isinf(embeddings).any(), "Inf detectado en embeddings 768D"
    print(f"[L1.2] Embeddings generados: shape={embeddings.shape} | NaN=0 | Inf=0", flush=True)

    # Split embeddings by group
    n_blocks = len(bloques_src)
    n_bgs = 10
    n_poses = len(available_poses)
    n_clips = len(clips_manifest)

    emb_blocks = embeddings[0:n_blocks]
    emb_bgs = embeddings[n_blocks:n_blocks + n_bgs]
    emb_poses = embeddings[n_blocks + n_bgs:n_blocks + n_bgs + n_poses]
    emb_clips = embeddings[n_blocks + n_bgs + n_poses:n_blocks + n_bgs + n_poses + n_clips]

    # Index in Qdrant (hbos_equipo_agentes_768)
    print(f"[L1.3] Creando coleccion Qdrant '{cfg.QDRANT_COLLECTION}' (768D Cosine)...", flush=True)
    try:
        cfg.qdrant_http(f"/collections/{cfg.QDRANT_COLLECTION}", method="DELETE")
    except Exception:
        pass
    cfg.qdrant_http(
        f"/collections/{cfg.QDRANT_COLLECTION}",
        method="PUT",
        data={"vectors": {"size": 768, "distance": "Cosine"}},
    )

    points = []
    for i, meta in enumerate(meta_records):
        vec_list = [float(x) for x in embeddings[i]]
        if len(vec_list) != 768:
            raise AssertionError(f"Vector {i} tiene dimension {len(vec_list)} != 768")
        pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"hbos_eq_ag_{meta['kind']}_{i}"))
        points.append({"id": pid, "vector": vec_list, "payload": meta})

    batch_size = 32
    for start in range(0, len(points), batch_size):
        cfg.qdrant_http(
            f"/collections/{cfg.QDRANT_COLLECTION}/points?wait=true",
            method="PUT",
            data={"points": points[start:start + batch_size]},
        )

    q_info = cfg.qdrant_http(f"/collections/{cfg.QDRANT_COLLECTION}")["result"]
    q_points = int(q_info.get("points_count", 0))
    q_dim = int(q_info["config"]["params"]["vectors"]["size"])
    assert q_points == len(points) and q_dim == 768, f"Qdrant mismatch: count={q_points}/{len(points)}, dim={q_dim}"
    print(f"[L1.3] Qdrant verificado: coleccion={cfg.QDRANT_COLLECTION} | points={q_points} | dim={q_dim}", flush=True)

    # Build gapless 60fps master timeline
    block_frame_counts = allocate_integer_frames([sp["dur_sec"] for sp in block_spans], total_frames)
    assert sum(block_frame_counts) == total_frames

    timeline_blocks = []
    cursor_frame = 0
    for idx, sp in enumerate(block_spans):
        b = sp["block"]
        bid = b["block_id"]
        n_frames = block_frame_counts[idx]
        start_frame = cursor_frame
        end_frame = cursor_frame + n_frames
        cursor_frame = end_frame

        card_spec = BLOCK_VISUAL_CARDS[bid]
        # Semantic similarity block -> background & top poses
        bg_sim = float(np.dot(emb_blocks[idx], emb_bgs[bid - 1]))
        pose_sims = emb_poses @ emb_blocks[idx]
        ranked_pose_indices = np.argsort(-pose_sims)
        top_semantic_pose = available_poses[int(ranked_pose_indices[0])]

        preferred = [p for p in card_spec["preferred_poses"] if p in available_poses]
        if top_semantic_pose not in preferred:
            preferred.append(top_semantic_pose)
        if not preferred:
            preferred = available_poses[:3]

        clip_sims = emb_clips @ emb_blocks[idx]
        top_clip = clips_manifest[int(np.argmax(clip_sims))]

        beat_weights = [max(3, len(bt.split())) for bt in sp["beats"]]
        beat_frames = allocate_integer_frames(beat_weights, n_frames)
        beats_out = []
        b_cursor = start_frame
        for bi, bt in enumerate(sp["beats"]):
            bf = beat_frames[bi]
            pose_name = preferred[bi % len(preferred)]
            beats_out.append({
                "beat_index": bi + 1,
                "text": bt,
                "start_frame": b_cursor,
                "end_frame": b_cursor + bf,
                "num_frames": bf,
                "start_sec": round(b_cursor / cfg.TARGET_FPS, 4),
                "end_sec": round((b_cursor + bf) / cfg.TARGET_FPS, 4),
                "avatar_pose": pose_name,
            })
            b_cursor += bf
        assert b_cursor == end_frame

        timeline_blocks.append({
            "block_id": bid,
            "title": b["title"],
            "bg_file": f"bg_{bid:02d}.jpg",
            "bg_semantic_similarity": round(bg_sim, 4),
            "avm_reference_clip": Path(top_clip["drive_path"]).name,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "num_frames": n_frames,
            "start_sec": round(start_frame / cfg.TARGET_FPS, 4),
            "end_sec": round(end_frame / cfg.TARGET_FPS, 4),
            "camera_mode": card_spec["camera_mode"],
            "hud": {
                "eyebrow": card_spec["eyebrow"],
                "headline": card_spec["headline"],
                "diagram_type": card_spec["diagram_type"],
                "kpis": card_spec["kpis"],
                "bullets": card_spec["bullets"],
            },
            "beats": beats_out,
        })

    # Verify zero gaps and exact end coverage
    assert timeline_blocks[0]["start_frame"] == 0
    for i in range(len(timeline_blocks) - 1):
        assert timeline_blocks[i]["end_frame"] == timeline_blocks[i + 1]["start_frame"], f"Hueco/solapamiento entre bloque {i+1} y {i+2}"
    assert timeline_blocks[-1]["end_frame"] == total_frames

    timeline_doc = {
        "project": "Equipo de Agentes de IA",
        "author": "Guillermo Alonso Hoyos (Guía Hoy · Rionegro, Antioquia)",
        "fps": cfg.TARGET_FPS,
        "resolution": f"{cfg.TARGET_W}x{cfg.TARGET_H}",
        "audio_duration_sec": audio_dur,
        "video_target_duration_sec": round(total_frames / cfg.TARGET_FPS, 4),
        "total_frames": total_frames,
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",
        "embedding_dim": 768,
        "qdrant_collection": cfg.QDRANT_COLLECTION,
        "blocks": timeline_blocks,
    }

    tl_path = cfg.BUILD_DIR / "timeline_768.json"
    tl_path.write_text(json.dumps(timeline_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    debug_f1 = {
        "phase": "FASE_1",
        "gate_1_to_2": "PASS",
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",
        "embedding_dim": 768,
        "total_vectors_indexed": q_points,
        "nan_count": 0,
        "inf_count": 0,
        "qdrant_collection": cfg.QDRANT_COLLECTION,
        "timeline_path": str(tl_path),
        "total_frames": total_frames,
        "total_beats": sum(len(b["beats"]) for b in timeline_blocks),
        "coverage_start_sec": 0.0,
        "coverage_end_sec": timeline_doc["video_target_duration_sec"],
        "gapless_verified": True,
    }
    df1_path = cfg.BUILD_DIR / "debug_fase1.json"
    df1_path.write_text(json.dumps(debug_f1, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[GATE 1->2] Status=PASS | Beats={debug_f1['total_beats']} | Frames={total_frames} | Qdrant={q_points}x768D", flush=True)


if __name__ == "__main__":
    main()
