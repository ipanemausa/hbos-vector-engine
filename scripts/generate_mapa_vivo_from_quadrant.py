r"""
Regenerate MAPA-VIVO\mapa.html strictly FROM Quadrant Cloud (Qdrant Cloud 768d).
Never hand-edited (F1). Reads registro_ecosistema_r768 and canon_video_hbos_r768
and renders a self-contained HTML view with Flow, Video Ledger, File Index,
Discrepancies, Component Probes, F9 Pending, and F12 Handoff Capsule.
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

REPO_ROOT = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
DEPLOY_ROOT = Path(r"C:\Users\ipane\hbos-deploy")

_ENV_LOCAL = dotenv_values(REPO_ROOT / ".env.local")

QDRANT_URL = (_ENV_LOCAL.get("QDRANT_URL") or "").strip().strip('"').rstrip("/")
QDRANT_API_KEY = (_ENV_LOCAL.get("QDRANT_API_KEY") or "").strip().strip('"')
if not QDRANT_URL.startswith("https://"):
    raise RuntimeError(f"F1/F5 guard: QDRANT_URL must be https://..., got {QDRANT_URL!r}")

OUT_DEPLOY = DEPLOY_ROOT / "MAPA-VIVO" / "mapa.html"
OUT_REPO = REPO_ROOT / "MAPA-VIVO" / "mapa.html"


def scroll_collection(name: str, limit: int = 250) -> list[dict[str, Any]]:
    url = f"{QDRANT_URL}/collections/{name}/points/scroll"
    body = json.dumps({"limit": limit, "with_payload": True, "with_vector": False}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"api-key": QDRANT_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [p.get("payload", {}) for p in data.get("result", {}).get("points", [])]


def esc(val: Any) -> str:
    return html.escape("" if val is None else str(val))


def badge(text: str) -> str:
    t = str(text)
    upper = t.upper()
    cls = "badge-neutral"
    if any(k in upper for k in ("OK", "ACTIVO", "VERIFIED", "RESOLVED", "PASS")):
        cls = "badge-ok"
    elif any(k in upper for k in ("PENDING", "CONSTATAR", "SKELETON", "AWAITING", "EXPERIMENTAL")):
        cls = "badge-warn"
    elif any(k in upper for k in ("KO", "FAIL", "VETO", "BLOCK", "DISABLED", "OFF", "OPEN")):
        cls = "badge-err"
    return f'<span class="badge {cls}">{esc(t)}</span>'


def render_html(reg: list[dict[str, Any]], vid: list[dict[str, Any]]) -> str:
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    by_type: dict[str, list[dict[str, Any]]] = {}
    for p in reg:
        by_type.setdefault(p.get("record_type", "other"), []).append(p)

    master_flow = next((x for x in by_type.get("master_flow", [])), {})
    subflows = by_type.get("subflow", [])
    isolated_lanes = by_type.get("isolated_lane", [])
    probes = next((x for x in by_type.get("component_probes", [])), {})
    discrepancies = sorted(by_type.get("discrepancy", []), key=lambda x: x.get("discrepancy_id", ""))
    file_index = sorted(by_type.get("file_index", []), key=lambda x: x.get("name", ""))
    pendings = by_type.get("pending_registered", [])
    gate_reports = sorted(by_type.get("phase_gate_report", []), key=lambda x: x.get("phase", ""))
    capsules = by_type.get("handoff_capsule", [])
    videos = sorted(vid, key=lambda x: (x.get("date", ""), x.get("work_id", ""), x.get("version", "")), reverse=True)

    # Nodes table (F11)
    nodes_rows = "".join(
        f"<tr><td><code>{esc(n.get('node'))}</code></td><td>{badge(n.get('status'))}</td><td><code>{esc(n.get('subflow_key'))}</code></td></tr>"
        for n in master_flow.get("nodes", [])
    )

    # Subflow stages (F10)
    stages_rows = ""
    for sf in subflows:
        for st in sf.get("stages", []):
            stages_rows += (
                f"<tr><td>{esc(st.get('order'))}</td>"
                f"<td><strong>{esc(st.get('stage'))}</strong></td>"
                f"<td>{badge(st.get('place'))}</td>"
                f"<td>{esc(st.get('owner_models_agents'))}</td>"
                f"<td>{esc(st.get('gate'))}</td>"
                f"<td><code>{esc(st.get('boundary_hash_check'))}</code></td></tr>"
            )

    # Video ledger
    video_rows = ""
    for v in videos:
        sha = esc(v.get("sha256", ""))
        sha_short = sha[:16] + "..." if len(sha) > 18 else sha
        video_rows += (
            f"<tr><td>{esc(v.get('date'))}</td>"
            f"<td><strong>{esc(v.get('title'))}</strong><br><small>work={esc(v.get('work_id'))} | ver={esc(v.get('version'))}</small></td>"
            f"<td>{badge(v.get('status'))}</td>"
            f"<td>{esc(v.get('duration_sec', '-'))} s</td>"
            f"<td><code title='{sha}'>{sha_short}</code></td>"
            f"<td>{badge(v.get('place'))}</td>"
            f"<td><code>{esc(v.get('path'))}</code>"
            + (f"<br><small>Vault: <code>{esc(v.get('vault_path'))}</code></small>" if v.get("vault_path") else "")
            + "</td></tr>"
        )

    # Probes
    probe_rows = "".join(
        f"<tr><td><strong>{esc(c.get('name'))}</strong></td><td>{badge(c.get('place'))}</td><td>{badge(c.get('status'))}</td><td><code>{esc(c.get('timestamp'))}</code></td><td>{esc(c.get('evidence'))}</td></tr>"
        for c in probes.get("components", [])
    )

    # Discrepancies
    disc_rows = "".join(
        f"<tr><td><strong>{esc(d.get('discrepancy_id'))}</strong></td><td>{esc(d.get('title'))}</td><td>{esc(d.get('side_a_doc'))}</td><td>{esc(d.get('side_b_measured'))}</td><td>{badge(d.get('status'))}</td><td>{esc(d.get('resolution'))}</td></tr>"
        for d in discrepancies
    )

    # File index + F9 pending
    file_rows = "".join(
        f"<tr><td><code>{esc(f.get('name'))}</code></td><td>{esc(f.get('date'))}</td><td>{esc(f.get('purpose'))}</td><td>{badge(f.get('place'))}</td><td><code>{esc(str(f.get('sha256', '-'))[:18])}...</code></td></tr>"
        for f in file_index
    )
    pending_rows = "".join(
        f"<tr><td><strong>{esc(p.get('factor'))}</strong> · <code>{esc(p.get('name'))}</code></td><td>{badge(p.get('status'))}</td><td>{esc(p.get('purpose'))}</td><td>{badge(p.get('place'))}</td></tr>"
        for p in pendings
    )

    # Gate reports + Capsule
    gate_cards = "".join(
        f"<div class='card-mini'><strong>{esc(g.get('phase'))}</strong> {badge(g.get('gate_status'))}<br><small>{esc(g.get('timestamp'))}</small></div>"
        for g in gate_reports
    )
    capsule_html = "<p><em>No handoff capsule written yet.</em></p>"
    if capsules:
        cap = capsules[-1]
        capsule_html = f"<pre>{esc(json.dumps(cap, indent=2, ensure_ascii=False))}</pre>"

    colab_html = ""
    for lane in isolated_lanes:
        limits = "".join(f"<li>{esc(x)}</li>" for x in lane.get("hard_limits", []))
        colab_html += f"<div class='panel'><h3>{esc(lane.get('title'))} {badge(lane.get('status'))}</h3><ul>{limits}</ul></div>"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HBOS MAPA-VIVO — Generado desde Quadrant Cloud</title>
<style>
  :root {{ --bg:#0b1020; --panel:#131a2e; --border:#253152; --text:#e8eefc; --muted:#9fb0d9; --accent:#f5b700; --cyan:#2dd4bf; --ok:#22c55e; --warn:#f59e0b; --err:#ef4444; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); line-height:1.45; }}
  header {{ padding:20px 28px; background:linear-gradient(135deg,#0f172a,#172554); border-bottom:2px solid var(--accent); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }}
  header h1 {{ margin:0; font-size:22px; color:var(--accent); }}
  header .meta {{ font-size:13px; color:var(--muted); }}
  main {{ max-width:1400px; margin:0 auto; padding:24px; display:grid; gap:20px; }}
  .panel {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:18px 20px; overflow-x:auto; }}
  .panel h2, .panel h3 {{ margin-top:0; color:var(--cyan); font-size:17px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--border); vertical-align:top; }}
  th {{ color:var(--accent); font-weight:600; background:#0f1629; }}
  code {{ background:#0a0f1d; padding:2px 5px; border-radius:4px; color:#bae6fd; font-size:12px; word-break:break-all; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
  .badge-ok {{ background:rgba(34,197,94,.18); color:#4ade80; border:1px solid rgba(34,197,94,.4); }}
  .badge-warn {{ background:rgba(245,158,11,.18); color:#fbbf24; border:1px solid rgba(245,158,11,.4); }}
  .badge-err {{ background:rgba(239,68,68,.18); color:#f87171; border:1px solid rgba(239,68,68,.4); }}
  .badge-neutral {{ background:rgba(148,163,184,.18); color:#cbd5e1; border:1px solid rgba(148,163,184,.4); }}
  .grid-cards {{ display:flex; flex-wrap:wrap; gap:10px; }}
  .card-mini {{ background:#0e1526; border:1px solid var(--border); border-radius:8px; padding:10px 14px; min-width:210px; }}
  pre {{ background:#070b15; padding:12px; border-radius:8px; overflow-x:auto; font-size:12px; color:#cbd5e1; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>HBOS MAPA-VIVO — Fuente Única de Verdad: Quadrant Cloud (768d)</h1>
    <div class="meta">Generado automáticamente desde <code>registro_ecosistema_r768</code> ({len(reg)} puntos) y <code>canon_video_hbos_r768</code> ({len(vid)} puntos) · Never hand-edited (F1)</div>
  </div>
  <div class="meta">Sync: <code>{esc(generated_at)}</code></div>
</header>
<main>
  <section class="panel">
    <h2>Gate Reports &amp; Estado de Fases</h2>
    <div class="grid-cards">{gate_cards}</div>
  </section>

  <section class="panel">
    <h2>L1 · Master Flow Skeleton (F11 One Flow · Todos los Nodos)</h2>
    <table><thead><tr><th>Nodo</th><th>Estado</th><th>Sub-flow</th></tr></thead><tbody>{nodes_rows}</tbody></table>
  </section>

  <section class="panel">
    <h2>L1 · Sub-flow Creative Video (F10 Split PC/CLOUD + SHA-256 Boundaries + F13 MCP)</h2>
    <table><thead><tr><th>#</th><th>Etapa</th><th>Lugar</th><th>Modelos / Agentes</th><th>Gate</th><th>Boundary Hash Check</th></tr></thead><tbody>{stages_rows}</tbody></table>
  </section>

  {colab_html}

  <section class="panel">
    <h2>L2 · Video Ledger (canon_video_hbos_r768)</h2>
    <table><thead><tr><th>Fecha</th><th>Obra / Versión</th><th>Estado</th><th>Duración</th><th>SHA-256</th><th>Lugar</th><th>Ruta / Vault</th></tr></thead><tbody>{video_rows}</tbody></table>
  </section>

  <section class="panel">
    <h2>L3 · Sondas en Vivo de Componentes (F3 · Mismo Día)</h2>
    <table><thead><tr><th>Componente</th><th>Lugar</th><th>Estado</th><th>Timestamp</th><th>Evidencia</th></tr></thead><tbody>{probe_rows}</tbody></table>
  </section>

  <section class="panel">
    <h2>L3 · Discrepancias Registradas (F2 · Evidencia Ambos Lados)</h2>
    <table><thead><tr><th>ID</th><th>Tema</th><th>Documento Base / Anterior</th><th>Medición en Vivo / Canon</th><th>Estado</th><th>Resolución</th></tr></thead><tbody>{disc_rows}</tbody></table>
  </section>

  <section class="panel">
    <h2>L3 · F9 Pendiente Registrado &amp; Índice de Archivos</h2>
    <h3>F9 Pendiente (Solo Registro)</h3>
    <table><thead><tr><th>Ítem</th><th>Estado</th><th>Propósito</th><th>Lugar</th></tr></thead><tbody>{pending_rows}</tbody></table>
    <h3 style="margin-top:16px;">Índice de Archivos</h3>
    <table><thead><tr><th>Archivo</th><th>Fecha</th><th>Propósito</th><th>Lugar</th><th>SHA-256</th></tr></thead><tbody>{file_rows}</tbody></table>
  </section>

  <section class="panel">
    <h2>F12 · Cápsula de Handoff en Quadrant</h2>
    {capsule_html}
  </section>
</main>
</body>
</html>
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    reg = scroll_collection("registro_ecosistema_r768")
    vid = scroll_collection("canon_video_hbos_r768")
    html_text = render_html(reg, vid)
    for out in (OUT_DEPLOY, OUT_REPO):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_text, encoding="utf-8")
    print(json.dumps({
        "generated": True,
        "registro_points": len(reg),
        "video_points": len(vid),
        "outputs": [
            {"path": str(OUT_DEPLOY), "bytes": OUT_DEPLOY.stat().st_size},
            {"path": str(OUT_REPO), "bytes": OUT_REPO.stat().st_size},
        ],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
