# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path

target = "ref-video08"
print(f"[*] Buscando '{target}' en C:\\Users\\ipane\\.gemini\\antigravity\\brain...")
brain_dir = Path(r"C:\Users\ipane\.gemini\antigravity\brain")
for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith((".jsonl", ".md", ".txt", ".py", ".json")):
            p = Path(root) / f
            if "3a88e6c0" in str(p):
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if target in content:
                    print(f"[+] ENCONTRADO EN: {p}")
                    for line in content.splitlines():
                        if target in line or "VoxCPM" in line or "guide_scale" in line:
                            print(f"    {line[:150]}")
            except Exception:
                pass
