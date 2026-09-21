# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

print("Buscando ventana de reproductor de video...")
time.sleep(1)

moved = []
def enum_cb(hwnd, lParam):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            # Chequear si es reproductor de video, wmplayer, demis, o ffplay
            matches = ['windows media player', 'reproductor', 'media player', 'demis', 'hbos', 'ffplay']
            if any(m in title.lower() for m in matches):
                # Bounds Monitor 3: (-1920, 0, 1280, 720)
                user32.ShowWindow(hwnd, 9) # SW_RESTORE
                user32.SetWindowPos(hwnd, 0, -1920, 0, 1280, 720, 0x0040)
                moved.append(title)
                print(f"[MOVED] '{title}' -> Pantalla 3 (-1920, 0, 1280, 720)")
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_cb), 0)

if not moved:
    print("[INFO] No se encontro ventana especifica con ese titulo todavia. Listando todas las ventanas visibles:")
    def list_all_cb(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                if title not in ['Default IME', 'MSCTFIME UI']:
                    print(f"  - '{title}'")
        return True
    user32.EnumWindows(EnumWindowsProc(list_all_cb), 0)
