# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

hwinsta = user32.GetProcessWindowStation()
desks = []
def enum_desk_cb(desk_name, lParam):
    desks.append(desk_name)
    return True

EnumDesktopsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_wchar_p, wintypes.LPARAM)
user32.EnumDesktopsW(hwinsta, EnumDesktopsProc(enum_desk_cb), 0)

target_pids = [7912, 16448]
prev_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())

print("Escritorios detectados:", desks)

for dname in desks:
    hdesk = user32.OpenDesktopW(dname, 0, False, 0x01FF)
    if not hdesk:
        continue
    user32.SetThreadDesktop(hdesk)
    
    def enum_win_cb(hwnd, lParam):
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
            print(f"[FOUND EN {dname}] hwnd={hwnd}, pid={pid.value}, vis={vis}, title='{title}', rect=({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
            user32.ShowWindow(hwnd, 9)
            user32.ShowWindow(hwnd, 5)
            # Mover a Pantalla 3: (-1920, 0, 1280, 720)
            user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            print(f"--> [MOVED A PANTALLA 3]: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
        return True

    EnumDesktopWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumDesktopWindows(hdesk, EnumDesktopWindowsProc(enum_win_cb), 0)
    user32.CloseDesktop(hdesk)

user32.SetThreadDesktop(prev_desk)
