# -*- coding: utf-8 -*-
import subprocess
import time
import os
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

mpv_bin = r'C:\Users\ipane\bin\mpv\mpv.exe'
video_file = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')

# Pantalla 3: x=-1920, y=0, width=1280, height=720
# mpv soporta flags nativos de posicion y pantalla:
# --geometry=1280x720+-1920+0 --title="HBOS_DEMIS_PANTALLA3" --loop=inf
cmd = [
    mpv_bin,
    f'--geometry=1280x720+-1920+0',
    '--title=HBOS_DEMIS_PANTALLA3',
    '--loop=inf',
    '--keep-open=yes',
    video_file
]

print(f"Lanzando mpv en Pantalla 3 (-1920, 0, 1280x720)...")
proc = subprocess.Popen(cmd)
print(f"Proceso mpv iniciado con PID: {proc.pid}")

time.sleep(1.5)

# Verificar coordenadas reales de la ventana creada
hdesk_default = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk_default:
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    user32.SetThreadDesktop(hdesk_default)
    
    coords = []
    def enum_cb(hwnd, lParam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == proc.pid:
            class RECT(ctypes.Structure):
                _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Asegurar posicion exacta en Pantalla 3
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.ShowWindow(hwnd, 5) # SW_SHOW
            user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
            
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            found_coords = (rect.left, rect.top, rect.right, rect.bottom)
            print(f"[VERIFICADO] Ventana mpv (PID {proc.pid}) Posicion Real: {found_coords}")
        return True

    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
    
    user32.SetThreadDesktop(prev_desk)
    user32.CloseDesktop(hdesk_default)
