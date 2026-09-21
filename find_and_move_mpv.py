# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import sys

user32 = ctypes.windll.user32
hdesk_default = user32.OpenDesktopW('Default', 0, False, 0x01FF)
if not hdesk_default:
    print("No se pudo abrir Default desktop")
    sys.exit(1)

found = False
def enum_cb(hwnd, lParam):
    global found
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        t = buff.value
        if any(k in t.lower() for k in ['demis', 'mpv']):
            class RECT(ctypes.Structure):
                _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            print(f'ENCONTRADO MPV: "{t}" en ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})')
            user32.ShowWindow(hwnd, 9)
            user32.ShowWindow(hwnd, 5)
            user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            print(f'MOVIDO MPV A PANTALLA 3: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})')
            found = True
    return True

EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumDesktopWindows(hdesk_default, EnumDesktopWindowsProc(enum_cb), 0)
user32.CloseDesktop(hdesk_default)

if not found:
    print("MPV aun no ha creado ventana o no esta visible en Default.")
