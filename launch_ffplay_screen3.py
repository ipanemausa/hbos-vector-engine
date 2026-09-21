# -*- coding: utf-8 -*-
import subprocess
import time
import os
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

video_path = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')
# Lanzar ffplay fijando ventana exacta en pantalla 3 (-1920, 0, 1280x720)
cmd = [
    'ffplay',
    '-window_title', 'Demis_Hassabis_HBOS_Ep04',
    '-x', '1280',
    '-y', '720',
    '-left', '-1920',
    '-top', '0',
    video_path
]

print("Iniciando ffplay...")
proc = subprocess.Popen(cmd)
print("PID ffplay:", proc.pid)

time.sleep(1)

# Asignar al escritorio Default y re-posicionar por si SDL2 uso offset local
hdesk_default = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk_default:
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    user32.SetThreadDesktop(hdesk_default)
    
    def enum_cb(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            t = buff.value
            if 'demis_hassabis' in t.lower() or 'ffplay' in t.lower():
                user32.ShowWindow(hwnd, 9)
                user32.ShowWindow(hwnd, 5)
                # Bounds Monitor 3: (-1920, 0, 1280, 720)
                user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
                print(f"[EXITO] Ventana '{t}' colocada en Pantalla 3 (-1920, 0, 1280, 720)")
        return True
        
    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
    
    user32.SetThreadDesktop(prev_desk)
    user32.CloseDesktop(hdesk_default)
