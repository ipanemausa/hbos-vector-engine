# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
target_pids = [7912, 16448]

def enum_all_cb(hwnd, lParam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in target_pids:
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        
        class RECT(ctypes.Structure):
            _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        print(f"[FOUND VIA ENUMWINDOWS] hwnd={hwnd}, pid={pid.value}, title='{buff.value}', rect=({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
        
        user32.ShowWindow(hwnd, 9)
        user32.ShowWindow(hwnd, 5)
        user32.SetWindowPos(hwnd, -1, -1920, 0, 1280, 720, 0x0040)
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        print(f"--> [MOVED]: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_all_cb), 0)
