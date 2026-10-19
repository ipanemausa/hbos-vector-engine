# -*- coding: utf-8 -*-
"""op315 sanitizer: remove hardcoded freellmapi-* literals from git-TRACKED files. Never prints key values.
Usage: python op315_sanitize.py [--apply]   (default = dry run)"""
import os, re, sys, json, py_compile, subprocess, tempfile, hashlib

ROOT = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine"
APPLY = "--apply" in sys.argv
LIVE = open(os.path.join(ROOT, "config", "freellmapi-key.txt"), encoding="utf-8").read().strip()
PAT = re.compile(r"freellmapi-[0-9a-f]{20,}")
STAND = re.compile(r"(?P<q>[\"'])(?P<k>freellmapi-[0-9a-f]{20,})(?P=q)")
REDACT = "freellmapi-REDACTED"
PY_EXPR = r'''(__import__("os").environ.get("FREELLMAPI_KEY") or (lambda p: open(p, encoding="utf-8").read().strip() if __import__("os").path.exists(p) else "")(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\config\freellmapi-key.txt"))'''
sh = lambda s: hashlib.sha256(s.encode()).hexdigest()[:10]

def git_tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True).stdout.decode("utf-8", "ignore")
    return [p for p in out.split("\0") if p]

def transform(ext, text, safe=False):
    def not_live(k): return k != LIVE
    if safe or ext in (".md", ".txt"):
        return PAT.sub(lambda m: m.group(0) if m.group(0) == LIVE else REDACT, text)
    if ext in (".py", ".pyw"): repl = lambda m: PY_EXPR if not_live(m.group("k")) else m.group(0)
    elif ext == ".js": repl = lambda m: '(process.env.FREELLMAPI_KEY || "")' if not_live(m.group("k")) else m.group(0)
    elif ext == ".json": repl = lambda m: '"env:FREELLMAPI_KEY"' if not_live(m.group("k")) else m.group(0)
    elif ext == ".ps1": repl = lambda m: "$env:FREELLMAPI_KEY" if not_live(m.group("k")) else m.group(0)
    else: return PAT.sub(lambda m: m.group(0) if m.group(0) == LIVE else REDACT, text)
    text = STAND.sub(repl, text)
    if ext == ".ps1":  # embedded inside a double-quoted string -> interpolate, else redact
        out = []
        for line in text.split("\n"):
            def emb(m, line=line):
                if m.group(0) == LIVE: return m.group(0)
                return "$env:FREELLMAPI_KEY" if line[:m.start()].count('"') % 2 == 1 else REDACT
            # positions refer to the original line; recompute using finditer on the line
            res, last = [], 0
            for m in PAT.finditer(line):
                res.append(line[last:m.start()]); res.append(emb(m)); last = m.end()
            res.append(line[last:]); out.append("".join(res))
        return "\n".join(out)
    return PAT.sub(lambda m: m.group(0) if m.group(0) == LIVE else REDACT, text)

def validate(ext, path, text):
    if ext == ".json":
        try: json.loads(text); return True, ""
        except Exception as e: return False, str(e)[:60]
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, "x" + ext)
        open(t, "w", encoding="utf-8", newline="").write(text)
        if ext in (".py", ".pyw"):
            try: py_compile.compile(t, doraise=True, cfile=os.path.join(d, "x.pyc")); return True, ""
            except Exception as e: return False, str(e)[:60]
        if ext == ".js":
            r = subprocess.run(["node", "--check", t], capture_output=True, text=True)
            return r.returncode == 0, r.stderr[:60]
        if ext == ".ps1":
            cmd = f"$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('{t}',[ref]$null,[ref]$e);if($e.Count -gt 0){{exit 1}}"
            r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
            return r.returncode == 0, "ps parse errors"
    return True, ""

report = []
for rel in git_tracked():
    p = os.path.join(ROOT, rel)
    ext = os.path.splitext(rel)[1].lower()
    try:
        raw = open(p, "rb").read()
        if len(raw) > 3_000_000: continue
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
    except Exception: continue
    old = [k for k in set(PAT.findall(text)) if k != LIVE]
    if not old: continue
    new, mode = transform(ext, text), "full"
    ok, why = validate(ext, p, new)
    if not ok:
        new, mode = transform(ext, text, safe=True), "redact-only"
        ok, why = validate(ext, p, new)
    left = [k for k in set(PAT.findall(new)) if k != LIVE]
    status = "OK" if ok and not left else "SKIPPED(" + why + ")"
    if ok and not left and APPLY:
        data = new.encode("utf-8")
        open(p, "wb").write((b"\xef\xbb\xbf" if bom else b"") + data)
    report.append((rel, ",".join(sorted(sh(k) for k in old)), mode, status))

w = max([len(r[0]) for r in report] + [10])
print(("APPLIED" if APPLY else "DRY-RUN"), "| files with old literals:", len(report))
for r in report: print(f"{r[0]:{w}}  keys[{r[1]}]  {r[2]:11}  {r[3]}")
bad = [r for r in report if not r[3].startswith("OK")]
print("skipped/failed:", len(bad))
