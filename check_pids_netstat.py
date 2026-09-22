# -*- coding: utf-8 -*-
import subprocess
import re

out = subprocess.check_output("netstat -ano", shell=True).decode()
pids_out = subprocess.check_output('tasklist /FI "IMAGENAME eq FreeLLMAPI.exe"', shell=True).decode()
print("FreeLLMAPI tasks:\n", pids_out)
pids = set(re.findall(r"FreeLLMAPI\.exe\s+(\d+)", pids_out))
print("PIDs:", pids)

print("\nConnections for FreeLLMAPI:")
matched = False
for line in out.splitlines():
    parts = line.split()
    if len(parts) >= 5 and parts[-1] in pids:
        print(line)
        matched = True
if not matched:
    print("No listening ports found for FreeLLMAPI PIDs!")
