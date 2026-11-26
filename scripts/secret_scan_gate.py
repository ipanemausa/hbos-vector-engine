"""
Phase 4 — PRE-DEBUG SECRET SCAN (Hard Gate).
Scans all git-tracked files and untracked non-ignored files in the repo for
embedded credentials (regex patterns + Shannon entropy on secret-like literals).

STRICT R30/F8: NEVER prints any secret value; outputs only file path, line number,
and matched rule name. Exits 0 iff 0 hits; exits 2 on any hit.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")

BINARY_EXTS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wav", ".mp3", ".aac", ".flac",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".pdf", ".zip",
    ".gz", ".tar", ".npy", ".pyc", ".db", ".sqlite", ".woff", ".woff2", ".ttf",
}

PATTERN_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("openai_or_sk_key", re.compile(r"\bsk-(?:proj-|ant-|live-|test-)?[A-Za-z0-9]{20,}")),
    ("groq_key", re.compile(r"\bgsk_[A-Za-z0-9]{20,}")),
    ("github_pat_classic", re.compile(r"\bghp_[A-Za-z0-9]{30,}")),
    ("github_pat_fine", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}")),
    ("jwt_token", re.compile(r"eyJhbGciOi[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

ASSIGN_RE = re.compile(
    r"""(?i)(?:api[_-]?key|secret|token|password|passwd|bearer|auth[_-]?key)\s*[:=]\s*["']([^"'\s]{24,})["']"""
)
HEX64_RE = re.compile(r"^[0-9a-fA-F]{64}$")
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def list_candidate_files() -> list[Path]:
    tracked = subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        text=True, encoding="utf-8", errors="replace",
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
        text=True, encoding="utf-8", errors="replace",
    ).splitlines()
    seen: set[Path] = set()
    files: list[Path] = []
    for rel in tracked + untracked:
        rel = rel.strip()
        if not rel:
            continue
        p = REPO_ROOT / rel
        if p in seen or not p.is_file():
            continue
        if p.suffix.lower() in BINARY_EXTS:
            continue
        seen.add(p)
        files.append(p)
    return sorted(files)


def scan_file(path: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return hits

    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    for lineno, line in enumerate(text.splitlines(), start=1):
        matched_here = False
        for rule_name, rx in PATTERN_RULES:
            if rx.search(line):
                hits.append({"file": rel, "line": lineno, "rule": rule_name})
                matched_here = True
        if not matched_here:
            for m in ASSIGN_RE.finditer(line):
                val = m.group(1)
                if HEX64_RE.match(val) or UUID_RE.match(val):
                    continue
                if any(tok in val.lower() for tok in ("example", "placeholder", "your_", "redacted", "process.env", "os.getenv")):
                    continue
                ent = shannon_entropy(val)
                if ent >= 4.3:
                    hits.append({"file": rel, "line": lineno, "rule": f"high_entropy_literal(H={ent:.2f})"})
    return hits


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    files = list_candidate_files()
    all_hits: list[dict[str, Any]] = []
    for f in files:
        all_hits.extend(scan_file(f))

    report = {
        "gate": "OK" if len(all_hits) == 0 else "KO",
        "files_scanned": len(files),
        "total_hits": len(all_hits),
        "hits": all_hits,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if len(all_hits) == 0 else 2)


if __name__ == "__main__":
    main()
