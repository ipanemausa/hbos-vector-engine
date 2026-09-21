# -*- coding: utf-8 -*-
import subprocess
import time
import os
import win32service
import win32gui
import win32con

video_path = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')
mpv_path = r'C:\Users\ipane\bin\mpv\mpv.exe'

# Asignar hilo actual al escritorio Default interactivo del usuario
desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

# Iniciar mpv directamente con flags para situarse en Monitor 3:
# Pantalla 3 bounds: left=-1920, top=0, width=1280, height=720
cmd = [
    mpv_path,
    '--geometry=1280x720+-1920+0',
    '--title=DEMIS_HASSABIS_PANTALLA3',
    '--loop=inf',
    '--ontop=yes',
    '--force-window=yes',
    video_path
]

print(f"Lanzando mpv en escritorio Default para Pantalla 3...")
proc = subprocess.Popen(cmd)
print(f"PID mpv: {proc.pid}")

# Dar 1 segundo y verificar/forzar la ventana en Pantalla 3
time.sleep(1.5)
hwnds = desk.EnumDesktopWindows()
found = False
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'DEMIS_HASSABIS_PANTALLA3' in t or 'demis_hassabis' in t.lower() or 'mpv' in t.lower():
        win32gui.ShowWindow(h, win32con.SW_RESTORE)
        win32gui.ShowWindow(h, win32con.SW_SHOW)
        # Situar en Pantalla 3: x=-1920, y=0, width=1280, height=720
        win32gui.SetWindowPos(h, win32con.HWND_TOPMOST, -1920, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
        rect = win32gui.GetWindowRect(h)
        print(f"[EXITO VISUAL] Ventana '{t}' visible y fijada en Pantalla 3: {rect}")
        found = True
        break

if not found:
    print("[INFO] Buscando por proceso:")
    for h in hwnds:
        _, p = win32process.GetWindowThreadProcessId(h) if 'win32process' in globals() else (0, 0)
