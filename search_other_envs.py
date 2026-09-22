# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

potential_envs = [
    r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env",
    r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local",
    r"C:\Users\ipane\hbos-deploy\omnirouter\.env",
    r"C:\Users\ipane\openclaw-operativo-2026\.env",
    r"C:\Users\ipane\.env",
]

found_keys = {}

for p in potential_envs:
    if os.path.exists(p):
        print(f"Found env file: {p}")
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if "KEY" in k.upper() or "TOKEN" in k.upper() or "SECRET" in k.upper() or "API" in k.upper():
                        masked = f"{v[:6]}...{v[-4:]}" if len(v) > 12 else f"(len={len(v)})"
                        if k not in found_keys:
                            found_keys[k] = (v, p)
                            print(f"  {k:25} from {os.path.basename(p)} = {masked}")

# Check system environment variables too
print("\nSystem environment variables matching KEY/TOKEN:")
for k, v in os.environ.items():
    if any(term in k.upper() for term in ["COHERE", "MISTRAL", "CEREBRAS", "CLOUDFLARE", "NVIDIA", "ZHIPU", "POLLINATIONS", "SPEECHIFY"]):
        masked = f"{v[:6]}...{v[-4:]}" if len(v) > 12 else f"(len={len(v)})"
        print(f"  [ENV] {k:25} = {masked}")
