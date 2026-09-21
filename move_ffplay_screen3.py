# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import subprocess

user32 = ctypes.windll.user32

# Obtener PID de ffplay
out = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq ffplay.exe'], text=True)
pids = []
for line in out.splitlines():
    if 'ffplay.exe' in line:
        parts = line.split()
        pids.append(int(parts[1]))

print('PIDs ffplay encontrados:', pids)

hwnds = []
def enum_win_cb(hwnd, lParam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in pids:
        hwnds.append((hwnd, pid.value))
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_win_cb), 0)

print(f"Total ventanas encontradas para ffplay: {len(hwnds)}")
for h, pid in hwnds:
    length = user32.GetWindowTextLengthW(h)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(h, buff, length + 1)
    vis = user32.IsWindowVisible(h)
    print(f"Hwnd {h} (pid {pid}): title='{buff.value}', visible={vis}")
    
    # Mover y forzar visibilidad en Pantalla 3
    # Bounds Pantalla 3: x=-1920, y=0, width=1280, height=720
    user32.ShowWindow(h, 9) # SW_RESTORE
    user32.ShowWindow(h, 5) # SW_SHOW
    user32.SetWindowPos(h, -1, -1920, 0, 1280, 720, 0x0040)
    print(f"-> Movido y restaurado a Pantalla 3 (-1920, 0, 1280, 720)")
