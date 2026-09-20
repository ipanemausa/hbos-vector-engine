import sys
import subprocess

print("[*] Lanzando HBOS-Unified-Gateway en segundo plano (puerto 3002)...")
cmd = [sys.executable, "hbos_unified_gateway.py"]
subprocess.run(cmd)
