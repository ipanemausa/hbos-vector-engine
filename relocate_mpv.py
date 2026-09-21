# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

target_pids = [7912, 16448]

def inspect_desktop(desk_name, hdesk):
    print(f"\n--- Inspeccionando Escritorio: {desk_name} ---")
    prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    user32.SetThreadDesktop(hdesk)
    
    found = []
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
        
        if pid.value in target_pids or 'mpv' in title.lower() or 'demis' in title.lower():
            print(f"[MATCH EN {desk_name}] hwnd={hwnd}, pid={pid.value}, vis={vis}, title='{title}', rect=({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
            
            # MOVER A PANTALLA 3: (-1920, 0, 1280, 720)
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.ShowWindow(hwnd, 5) # SW_SHOW
            user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
            
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            print(f"--> [MOVED A PANTALLA 3]: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
            found.append(hwnd)
        return True

    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk, EnumDesktopWindowsProc(enum_cb), 0)
    user32.SetThreadDesktop(prev_desk)
    return len(found)

# 1. Desktop actual del hilo
cur_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
inspect_desktop("CurrentThreadDesktop", cur_desk)

# 2. Desktop Default
hdesk_def = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk_def:
    inspect_desktop("Default", hdesk_def)
    user32.CloseDesktop(hdesk_def)
