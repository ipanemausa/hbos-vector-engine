# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_path = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local"
keys = {}

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                keys[k] = v

print(f"Total keys in .env.local: {len(keys)}")
for k, v in sorted(keys.items()):
    masked = f"{v[:6]}...{v[-4:]}" if len(v) > 12 else f"(len={len(v)})"
    print(f"  {k:25} = {masked}")
