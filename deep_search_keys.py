# -*- coding: utf-8 -*-
import os
import re

targets = [
    "cerebras", "sail", "electronhub", "experiential", "router9", "septor",
    "clod", "speechify", "blaze", "lucidity", "logfare", "bai", "radeon",
    "nvidia", "mistral", "cohere", "cloudflare", "zhipu", "pollinations", "opencode",
    "deepseek"
]

search_dirs = [
    r"C:\Users\ipane\hbos-deploy",
    r"C:\Users\ipane\openclaw-operativo-2026",
    r"C:\Users\ipane\.gemini\config",
    r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI"
]

found = {}

for d in search_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        # skip node_modules, git, venv
        dirs[:] = [sub for sub in dirs if sub not in ['node_modules', '.git', 'venv', '__pycache__', 'dist', 'build']]
        for f in files:
            if f.endswith(('.env', '.env.local', '.json', '.txt', '.md', '.py', '.js', '.mjs')):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                        for t in targets:
                            # look for KEY or TOKEN related to target
                            matches = re.findall(rf'{t}[-_a-zA-Z0-9]*\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{{15,}})["\']?', content, re.IGNORECASE)
                            if matches:
                                for m in matches:
                                    k_name = f"{t.upper()} in {os.path.basename(filepath)}"
                                    if k_name not in found:
                                        found[k_name] = m
                                        print(f"Found candidate: {k_name} = {m[:6]}...{m[-4:]} (len={len(m)})")
                except Exception:
                    pass

print(f"\nTotal potential keys discovered: {len(found)}")
