# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

hwnds = []
def enum_cb(hwnd, lParam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value
    
    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    vis = user32.IsWindowVisible(hwnd)
    
    if 'ffplay' in title.lower() or 'demis' in title.lower() or 'hbos' in title.lower() or pid.value == 8996:
        print(f"MATCH: hwnd={hwnd}, pid={pid.value}, vis={vis}, title='{title}', rect=({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
        # Mover inmediatamente a pantalla 3
        # Pantalla 3: x=-1920, y=0, width=1280, height=720
        # SWP_SHOWWINDOW = 0x0040
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        user32.SetWindowPos(hwnd, 0, -1920, 0, 1280, 720, 0x0040)
        print(f"MOVED: hwnd={hwnd} a (-1920, 0, 1280, 720)")
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_cb), 0)
