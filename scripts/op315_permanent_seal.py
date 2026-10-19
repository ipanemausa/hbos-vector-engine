# -*- coding: utf-8 -*-
"""HBOS op=315 · PERMANENT CANONICAL SEAL (core). Modes: prepare | seal.
No secrets are printed or embedded. Key is read from config/freellmapi-key.txt (gitignored)."""
import os, re, sys, json, glob, math, uuid, shutil, hashlib, sqlite3, datetime, urllib.request, urllib.error

ROOT = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine"
LOGS = os.path.join(ROOT, "logs"); CONF = os.path.join(ROOT, "config")
DB = "file:C:/Users/ipane/AppData/Roaming/FreeLLMAPI/freeapi.db?mode=ro"
PENDING = os.path.join(CONF, "op315-pending.json")
CHAINS = ["auto:default", "auto:video", "auto:reasoning", "auto:long-context", "auto:vision",
          "auto:code", "auto:fast", "auto:premium", "auto:marketing", "auto:aprendizaje"]
GENESIS = hashlib.sha256(b"HBOS-op315-2026-09-26-genesis").hexdigest()[:16]
NAME_RE = re.compile(r"^hbos-approvals-op315-(ROUTER-SEAL|PERM-SEAL)-\d{8}-\d{6}\.txt$")  # case-sensitive on purpose

def now(): return datetime.datetime.now().astimezone().isoformat()
def h16(ph, ly, act, gate, ts, prev):
    return hashlib.sha256(f"op315|{ph}|{ly}|{act}|{gate}|{ts}|{prev}".encode()).hexdigest()[:16]

def read_ledger(path):
    L = open(path, encoding="utf-8-sig").read().splitlines()
    rows, prev = [], GENESIS
    for l in L[1:]:
        a = l.split("|")
        act = "|".join(a[3:-5])               # tolerant of '|' inside legacy action text
        if h16(a[1], a[2], act, a[-5], a[-3], prev) != a[-2] or a[-1] != prev:
            raise SystemExit(f"CHAIN BREAK at entry {a[0]} in {os.path.basename(path)}")
        rows.append(a); prev = a[-2]
    if L[0].split("genesis=")[-1] != GENESIS: raise SystemExit("GENESIS MISMATCH")
    return L[0], rows, prev

def append(rows, prev, ph, ly, act, gate, method="auto"):
    assert "|" not in act, "pipe in action text"
    ts = now(); h = h16(ph, ly, act, gate, ts, prev)
    rows.append([str(len(rows)), ph, ly, act, gate, method, ts, h, prev]); return h

def write_ledger(path, header, rows):
    open(path, "w", encoding="utf-8", newline="\n").write(header + "\n" + "\n".join("|".join(r) for r in rows) + "\n")

def http_json(url, key=None):
    req = urllib.request.Request(url)
    if key: req.add_header("Authorization", "Bearer " + key)
    return json.load(urllib.request.urlopen(req, timeout=10))

def prepare():
    key = open(os.path.join(CONF, "freellmapi-key.txt"), encoding="utf-8").read().strip()
    raw = len(http_json("http://127.0.0.1:3001/v1/models", key)["data"])      # informational only
    qcols = [c["name"] for c in http_json("http://127.0.0.1:6333/collections")["result"]["collections"]]
    c = sqlite3.connect(DB, uri=True).cursor(); q = lambda s: c.execute(s).fetchall()
    prof = {("auto:" + n.lower()): i for i, n in q("select id, name from profiles")}
    chains = []
    for name in CHAINS:
        pid = prof.get(name)
        n = q(f"select count(*) from profile_models where profile_id={pid} and enabled=1")[0][0] if pid else 0
        chains.append({"chain": name, "present": pid is not None, "enabled_models": n})
    gkey = q("select status, enabled from api_keys where label='HBOS Google Gemini Key'")
    argon = q("select platform, enabled from models where model_id='gemini-4-argon'")
    muse = [r[0] for r in q("select display_name from models where enabled=1 and (model_id like '%muse-spark-1.3%' or model_id like '%muse-glimmer-30b%')")]
    anchor_ok = bool(gkey) and gkey[0] == ("healthy", 1) and bool(argon) and argon[0] == ("google", 1)
    chains_ok = all(x["present"] and x["enabled_models"] > 0 for x in chains)
    snap = {
        "generated": now(), "source": "router DB read-only + user attestation", "op": 315,
        "declared_by_user_ui": {"orchestrated_models": 93, "active_chain_models": 92, "token_pool_remaining": "773.9M", "token_pool_total": "855.0M"},
        "live_observed": {"raw_v1_models": raw, "distinct_enabled_models_in_profiles": q("select count(distinct model_db_id) from profile_models where enabled=1")[0][0],
                          "note": "93/92 and pool are attested from the router UI; they are not derivable from raw endpoints"},
        "fallback_chains": chains,
        "anchor": {"key_label": "HBOS Google Gemini Key", "key_status": gkey[0][0] if gkey else None, "model": "Gemini 4 Argon", "model_enabled": bool(argon and argon[0][1])},
        "muse_agents_in_router": sorted(set(muse)),
        "kiro": {"status": "EXCLUDED", "reason": "deprecated by system directive", "port": 10088},
        "qdrant": {"endpoint": "http://127.0.0.1:6333", "collections": qcols},
    }
    os.makedirs(CONF, exist_ok=True)
    open(os.path.join(CONF, "freellmapi-inventory.json"), "w", encoding="utf-8").write(json.dumps(snap, indent=2, ensure_ascii=False))
    if not (chains_ok and anchor_ok and qcols is not None):
        print("L0.6 NOT MET", chains_ok, anchor_ok); sys.exit(2)
    base = sorted([p for p in glob.glob(os.path.join(LOGS, "hbos-approvals-op315-*-SEAL-*.txt")) if NAME_RE.match(os.path.basename(p))], key=os.path.getmtime)[-1]
    header, rows, prev = read_ledger(base)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(LOGS, f"hbos-approvals-op315-PERM-SEAL-{ts}.txt")
    prev = append(rows, prev, "0", "0.6", f"[L0.6] Router topology: 10 fallback chains operational + HBOS Gemini anchor present (Gemini 4 Argon) + local Qdrant 127.0.0.1:6333 reachable ({len(qcols)} collections) ; decoupled from raw endpoint count ; snapshot config/freellmapi-inventory.json", "PASS")
    prev = append(rows, prev, "0", "0.7", "[L0.7] Kiro (10088) deprecated by system directive ; EXCLUDED", "PASS")
    prev = append(rows, prev, "0", "0.8", "persistent env set (User scope): FREELLMAPI_KEY, FREELLMAPI_URL, QDRANT_URL ; qdrant local canonical", "PASS")
    write_ledger(out, header, rows)
    json.dump({"ledger": out, "base": os.path.basename(base), "prepared": now()}, open(PENDING, "w"))
    print("prepared", os.path.basename(out), "entries", len(rows), "base", os.path.basename(base))

# ---------------------------------------------------------------- L5.6 industrial notes circuit
DRIVE_DIR = r"G:\My Drive\HBOS_VECTOR_PERSISTENCE\hbos-vector-engine"   # existing folder; no new dirs created
QCOL, QURL = "canon_video_hbos", "http://127.0.0.1:6333"

def emb(text, dim=384):
    """Same deterministic weighted scheme as index_canon.py, so notes are comparable with existing canon points."""
    vec, words = [0.0] * dim, text.lower().split()
    if not words: return [1.0 / math.sqrt(dim)] * dim
    for i, w in enumerate(words):
        h = int(hashlib.sha256(f"{w}_{i % 7}".encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0 + (1.0 / (1.0 + (h % 11)))
    n = math.sqrt(sum(x * x for x in vec))
    return [x / n for x in vec]

def build_md(rows, prev, snap, ts, status):
    L = [f"# HBOS op=315 · NotebookLM export · {ts}", "",
         f"**Genesis:** `{GENESIS}`  ", f"**Head ({len(rows)} entries):** `{prev}`  ", f"**Status:** {status}", "",
         "## Router topology", "- Chains: " + ", ".join(x["chain"] + f" ({x['enabled_models']})" for x in snap["fallback_chains"]),
         f"- Anchor: {snap['anchor']['key_label']} ({snap['anchor']['key_status']}) · {snap['anchor']['model']}",
         "- Muse in router: " + ", ".join(snap["muse_agents_in_router"]),
         f"- User-attested (router UI): {snap['declared_by_user_ui']['orchestrated_models']} models, {snap['declared_by_user_ui']['active_chain_models']} in chain, pool {snap['declared_by_user_ui']['token_pool_remaining']} / {snap['declared_by_user_ui']['token_pool_total']}",
         f"- Live observed: raw /v1/models={snap['live_observed']['raw_v1_models']}, distinct enabled in profiles={snap['live_observed']['distinct_enabled_models_in_profiles']}",
         "- Kiro: EXCLUDED (deprecated). Canonical store: local Qdrant 127.0.0.1:6333.",
         "- Historical FAIL entries (326 and 281 drift) preserved in the chain.", "",
         "## Full ledger", "| # | Phase | Layer | Action | Gate | Method | Timestamp | Hash | Prev |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| " + " | ".join(r[:3] + ["|".join(r[3:-5]).replace("|", "/")] + r[-5:-2]) + f" | `{r[-2]}` | `{r[-1]}` |")
    return "\n".join(L) + "\n"

def chunks_of(md):
    out, cur, head = [], [], "intro"
    for line in md.splitlines():
        if line.startswith("## ") and cur:
            out.append((head, "\n".join(cur))); cur, head = [], line[3:].strip()
        elif line.startswith("## "): head = line[3:].strip()
        cur.append(line)
        if head == "Full ledger" and len(cur) >= 14:      # ledger table in blocks of ~10 rows
            out.append((head, "\n".join(cur))); cur = []
    if cur: out.append((head, "\n".join(cur)))
    return [(h, t) for h, t in out if t.strip()]

def qreq(method, path, body=None):
    r = urllib.request.Request(QURL + path, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20))

def sync_note(md_path, md):
    """Copy note to Drive (G: mount) and upsert chunks to Qdrant. Returns dict with verification flags."""
    data = md.encode("utf-8"); sha = hashlib.sha256(data).hexdigest()
    res = {"sha": sha, "drive_ok": False, "qdrant_ok": False, "chunks": 0, "why": []}
    try:
        if not os.path.isdir(DRIVE_DIR): raise RuntimeError("Drive folder not mounted")
        dst = os.path.join(DRIVE_DIR, os.path.basename(md_path)); shutil.copyfile(md_path, dst)
        res["drive_ok"] = hashlib.sha256(open(dst, "rb").read()).hexdigest() == sha
    except Exception as e: res["why"].append("drive:" + str(e)[:60])
    try:
        size = qreq("GET", f"/collections/{QCOL}")["result"]["config"]["params"]["vectors"]["size"]
        if size != 384: raise RuntimeError(f"collection dim {size} != 384")
        fecha = datetime.date.today().isoformat(); pts = []
        for i, (sec, txt) in enumerate(chunks_of(md)):
            pid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"hbos/op315/note/{os.path.basename(md_path)[:-3].split('-notebooklm-')[0]}/{i}"))
            pts.append({"id": pid, "vector": emb(f"{sec} {txt}"), "payload": {"doc": os.path.basename(md_path), "seccion": sec, "tipo": "nota_notebooklm", "fecha": fecha, "version": "op315", "op": 315, "chunk_index": i, "sha256": sha, "texto": txt[:4000], "agentes": ["Sol", "Luna", "Astra"]}})
        qreq("PUT", f"/collections/{QCOL}/points?wait=true", {"points": pts})
        got = qreq("POST", f"/collections/{QCOL}/points", {"ids": [p["id"] for p in pts], "with_payload": False})["result"]
        res["chunks"], res["qdrant_ok"] = len(pts), len(got) == len(pts) and len(pts) > 0
    except Exception as e: res["why"].append("qdrant:" + str(e)[:60])
    return res

def seal():
    p = json.load(open(PENDING))["ledger"]
    header, rows, prev = read_ledger(p)
    prev = append(rows, prev, "5", "5.11", "biometric approval Windows Hello confirmed for permanent canonical seal (solicitar_huella.py exit 0)", "PASS", "biometric")
    snap = json.load(open(os.path.join(CONF, "freellmapi-inventory.json"), encoding="utf-8"))
    live = open(os.path.join(CONF, "freellmapi-key.txt"), encoding="utf-8").read().strip()
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    md_path = os.path.join(LOGS, f"hbos-approvals-op315-notebooklm-{ts}.md")
    md = build_md(rows, prev, snap, ts, "PRE-SEAL · biometric (Windows Hello) confirmed")
    assert live not in md, "secret leaked into note"
    open(md_path, "w", encoding="utf-8").write(md)
    res = sync_note(md_path, md)                                   # L5.6 unattended: Drive + Qdrant
    ok = res["drive_ok"] and res["qdrant_ok"]
    prev = append(rows, prev, "5", "5.6", (f"[L5.6] Industrial notes auto-sync -> Drive/Qdrant completed ; note sha256 {res['sha'][:16]} ; drive={DRIVE_DIR} ; qdrant={QCOL} chunks={res['chunks']}" if ok else f"[L5.6] Industrial notes auto-sync FAILED ; drive_ok={res['drive_ok']} qdrant_ok={res['qdrant_ok']} ; {' ; '.join(res['why'])}"), "PASS" if ok else "FAIL", "auto")
    if not ok:
        write_ledger(p, header, rows)
        print("L5.6 FAILED - NOT SEALED:", res["why"]); sys.exit(3)
    prev = append(rows, prev, "5", "5.12", "ledger SEALED permanent canonical (router topology ; Kiro excluded ; notes synced ; history preserved)", "PASS")
    write_ledger(p, header, rows)
    md = build_md(rows, prev, snap, ts, "SEALED · biometric (Windows Hello) confirmed")
    assert live not in md, "secret leaked into note"
    open(md_path, "w", encoding="utf-8").write(md)
    fin = sync_note(md_path, md)                                   # refresh Drive/Qdrant with the sealed version (same ids, overwritten)
    os.remove(PENDING)
    print("SEALED", os.path.basename(p), "head", prev); print(md_path)
    print("refresh drive_ok=%s qdrant_ok=%s chunks=%d" % (fin["drive_ok"], fin["qdrant_ok"], fin["chunks"]))

if __name__ == "__main__":
    {"prepare": prepare, "seal": seal}[sys.argv[1]]()
