# -*- coding: utf-8 -*-
import subprocess
import time
import os

exe = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\FreeLLMAPI.exe"
print(f"Lanzando {exe}...")
p = subprocess.Popen([exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Esperar 3 segundos y ver si sigue vivo
time.sleep(3)
poll = p.poll()
print("Process poll status:", poll)
if poll is not None:
    stdout, stderr = p.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
else:
    print(f"FreeLLMAPI sigue corriendo con PID {p.pid}!")
