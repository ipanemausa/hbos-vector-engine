# -*- coding: utf-8 -*-
import json, subprocess
from pathlib import Path

p = Path(r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_Pista3_Video08_Make_menos14LUFS.wav")
print("Exists:", p.exists(), "Size:", p.stat().st_size)

res = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(p)], capture_output=True, text=True)
info = json.loads(res.stdout)
print("Duration:", info["format"]["duration"])

