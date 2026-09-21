# -*- coding: utf-8 -*-
import subprocess
import time
import os
import win32service
import win32gui
import win32con

video_path = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')
mpv_path = r'C:\Users\ipane\bin\mpv\mpv.exe'

# Asignar al escritorio interactivo Default
desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

# Bounds Monitor 3: x=-1920, y=0, width=1280, height=720
# Forzamos:
# 1. --fs (pantalla completa) o geometry exacta
# 2. --screen=2 (en mpv la numeracion suele ser 0, 1, 2)
# 3. --fs-screen=2
# 4. --geometry=1280x720+-1920+0
# 5. --ontop (siempre al frente)
# 6. --loop=inf
cmd = [
    mpv_path,
    '--geometry=1280x720+-1920+0',
    '--title=DEMIS_HASSABIS_PANTALLA3',
    '--ontop=yes',
    '--loop=inf',
    '--keep-open=yes',
    video_path
]

print("Iniciando mpv...")
proc = subprocess.Popen(cmd)
print(f"PID: {proc.pid}")

# Esperar creación de ventana y forzar TOPMOST en Monitor 3
time.sleep(1.5)
hwnds = desk.EnumDesktopWindows()
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'DEMIS_HASSABIS_PANTALLA3' in t:
        win32gui.ShowWindow(h, win32con.SW_RESTORE)
        win32gui.ShowWindow(h, win32con.SW_SHOW)
        win32gui.SetWindowPos(h, win32con.HWND_TOPMOST, -1920, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
        r = win32gui.GetWindowRect(h)
        print(f"[CONFIRMADO VISUAL] '{t}' en Pantalla 3: Rect = {r}")
        break
