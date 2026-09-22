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

LOCAL_EXE = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\FreeLLMAPI.exe"
GDRIVE_EXE = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe"

exe_path = LOCAL_EXE if os.path.exists(LOCAL_EXE) else GDRIVE_EXE
work_dir = os.path.dirname(exe_path)

print(f"[*] Iniciando FreeLLMAPI en modo daemon desde {exe_path}...")
subprocess.run([exe_path], cwd=work_dir)
