import os
import subprocess
import json

appdata_cfg = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\config.json"
if os.path.exists(appdata_cfg):
    try:
        with open(appdata_cfg, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["port"] = 3001
        with open(appdata_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except:
        pass

exe_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe"
work_dir = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app"

print(f"[*] Iniciando FreeLLMAPI en modo daemon desde {exe_path}...")
subprocess.run([exe_path], cwd=work_dir)
