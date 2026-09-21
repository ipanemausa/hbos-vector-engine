# -*- coding: utf-8 -*-
import win32service
import win32gui
import win32con

desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

hwnds = desk.EnumDesktopWindows()
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'antigravity' in t.lower():
        win32gui.ShowWindow(h, 9)
        # Devolver a Monitor 1 (0, 0, 1280, 720)
        win32gui.SetWindowPos(h, 0, 0, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
        print(f"Antigravity IDE devuelto a Monitor 1: {win32gui.GetWindowRect(h)}")
desk.CloseDesktop()
