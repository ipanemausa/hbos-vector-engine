# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Abrir el Desktop interactivo "Default" del usuario
GENERIC_ALL = 0x10000000
hdesk_default = user32.OpenDesktopW("Default", 0, False, GENERIC_ALL)
print("Handle OpenDesktop('Default'):", hdesk_default)

if not hdesk_default:
    # Intentar con permisos de lectura/enumeracion
    DESKTOP_READOBJECTS = 0x0001
    DESKTOP_WRITEOBJECTS = 0x0080
    DESKTOP_SWITCHDESKTOP = 0x0100
    access = 0x01FF # DESKTOP_ALL
    hdesk_default = user32.OpenDesktopW("Default", 0, False, access)
    print("Handle OpenDesktop con access 0x01FF:", hdesk_default)

if hdesk_default:
    # Asignar temporalmente este hilo al escritorio Default del usuario interactivo
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    set_ok = user32.SetThreadDesktop(hdesk_default)
    print("SetThreadDesktop('Default'):", set_ok)
    
    # Enumerar ventanas en el escritorio Default
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
            
            if any(k in title.lower() for k in ['demis', 'ffplay', 'hbos', 'reproductor', 'media player', 'películas', 'video']):
                print(f"[TARGET FOUND] '{title}' en ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
                # Mover a Pantalla 3: (-1920, 0, 1280, 720)
                user32.ShowWindow(hwnd, 9)
                user32.SetWindowPos(hwnd, 0, -1920, 0, 1280, 720, 0x0040)
                print(f"[MOVED] '{title}' -> Pantalla 3 (-1920, 0, 1280, 720)")
            else:
                if length > 3 and user32.IsWindowVisible(hwnd):
                    print(f"  Visible: '{title}' -> ({rect.left}, {rect.top})")
        return True

    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
    
    # Restaurar hilo
    user32.SetThreadDesktop(prev_desk)
    user32.CloseDesktop(hdesk_default)
else:
    err = kernel32.GetLastError()
    print(f"Error abriendo escritorio Default: {err}")
