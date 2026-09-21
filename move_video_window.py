# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

hdesk_default = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk_default:
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    user32.SetThreadDesktop(hdesk_default)
    
    found = []
    def enum_cb(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            class RECT(ctypes.Structure):
                _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Buscar cualquier ventana relacionada con reproductor, video, o mp4
            # Ignorar la ventana del IDE
            if 'antigravity' not in title.lower():
                # Comprobar si coincide con reproductor o archivo
                targets = ['reproductor', 'media player', 'películas', 'films', 'tv', 'demis', 'final.mp4', 'video', 'vlc']
                if any(t in title.lower() for t in targets):
                    print(f"ENCONTRADA: '{title}' en ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
                    user32.ShowWindow(hwnd, 9) # SW_RESTORE
                    user32.SetWindowPos(hwnd, 0, -1920, 0, 1280, 720, 0x0040)
                    print(f"MOVIDA a Pantalla 3: '{title}' -> (-1920, 0, 1280, 720)")
                    found.append(title)
        return True

    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
    
    if not found:
        print("[INFO] No se encontro reproductor abierto. Listado de ventanas activas en Default:")
        def list_all(hwnd, lParam):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0 and user32.IsWindowVisible(hwnd):
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                t = buff.value
                if 'antigravity' not in t.lower() and t not in ['Default IME', 'MSCTFIME UI']:
                    print(f"   * '{t}'")
            return True
        user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(list_all), 0)

    user32.SetThreadDesktop(prev_desk)
    user32.CloseDesktop(hdesk_default)
