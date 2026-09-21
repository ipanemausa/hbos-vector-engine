# -*- coding: utf-8 -*-
import win32process
import os

si = win32process.STARTUPINFO()
si.lpDesktop = r"WinSta0\Default"
mpv = r"C:\Users\ipane\bin\mpv\mpv.exe"
vid = os.path.abspath(r"assets\videos\demis_hassabis_final.mp4")

cmd = f'"{mpv}" --loop=inf "{vid}"'
hProc, hThread, dwProcId, dwThreadId = win32process.CreateProcess(
    None, cmd, None, None, False, 0, None, None, si
)
print("PID lanzado en WinSta0\\Default:", dwProcId)
