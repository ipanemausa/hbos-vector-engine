import os
import sys
import json

paths_to_verify = {
    "ep02_master_v1": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v1.mp4",
    "ep02_backup_v1": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\_backup_ep02_master_v1.mp4",
    "ep02_master_v2": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v2.mp4",
    "ep02_master_v3": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v3.mp4",
    "ep02_backup_v3": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\_backup_ep02_master_v3.mp4",
    "ep02_master_v4": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v4.mp4",
    "ep02_master_v5": r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v5.mp4",
    "ep03_master_v1": r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master\ep03_master_v1.mp4",
    "ep03_backup_v1": r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master\_backup_ep03_master_v1.mp4",
    "ep03_master_v2": r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master\ep03_master_v2.mp4"
}

results = {}
for k, p in paths_to_verify.items():
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    results[k] = {
        "ruta": p,
        "existe": exists,
        "bytes": size,
        "mb": round(size / (1024*1024), 2)
    }

print(json.dumps(results, indent=2))
