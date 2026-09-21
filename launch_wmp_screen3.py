# -*- coding: utf-8 -*-
import subprocess
import time
import os
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

video_path = os.path.abspath(r'assets\videos\demis_hassabis_final.mp4')
wmplayer_path = r'C:\Program Files (x86)\Windows Media Player\wmplayer.exe'

print(f"Lanzando reproductor para: {video_path}")
proc = subprocess.Popen([wmplayer_path, video_path])
print(f"Proceso iniciado con PID: {proc.pid}")

# Esperar a que la ventana se cree y moverla de inmediato a Pantalla 3
hdesk_default = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk_default:
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    user32.SetThreadDesktop(hdesk_default)
    
    moved = False
    for attempt in range(15):
        time.sleep(0.5)
        
        def enum_cb(hwnd, lParam):
            global moved
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == proc.pid:
                # Restaurar y mover a pantalla 3
                # Monitor 3: left=-1920, top=0, width=1280, height=720
                user32.ShowWindow(hwnd, 9) # SW_RESTORE
                user32.ShowWindow(hwnd, 5) # SW_SHOW
                user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
                print(f"[MOVED] Ventana de WMP (hwnd={hwnd}, pid={proc.pid}) situada en Pantalla 3 (-1920, 0, 1280, 720)")
                moved = True
            return True
            
        EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
        if moved:
            break
            
    user32.SetThreadDesktop(prev_desk)
    user32.CloseDesktop(hdesk_default)
