# -*- coding: utf-8 -*-
import win32process
import os
import time

video_path = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')
mpv_path = r'C:\Users\ipane\bin\mpv\mpv.exe'

si = win32process.STARTUPINFO()
si.lpDesktop = r"WinSta0\Default"

cmd = f'"{mpv_path}" --geometry=1280x720+-1920+0 --title="DEMIS_HASSABIS_PANTALLA3" --loop=inf --ontop=yes --keep-open=yes "{video_path}"'
print(f"Lanzando CreateProcess con lpDesktop='WinSta0\\\\Default'...")

hProc, hThread, dwProcId, dwThreadId = win32process.CreateProcess(
    None,
    cmd,
    None,
    None,
    False,
    0,
    None,
    os.path.abspath('.'),
    si
)

print(f"[OK] Proceso mpv lanzado con PID: {dwProcId} en WinSta0\\Default!")
