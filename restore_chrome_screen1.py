# -*- coding: utf-8 -*-
import win32service
import win32gui
import win32con

desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

hwnds = desk.EnumDesktopWindows()
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'Google Chrome' in t and win32gui.IsWindowVisible(h):
        r = win32gui.GetWindowRect(h)
        if r[0] > -10000:
            # Traer Chrome a Monitor 1 (0, 0, 1280, 720)
            win32gui.ShowWindow(h, win32con.SW_RESTORE)
            win32gui.SetWindowPos(h, win32con.HWND_TOP, 0, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
            print(f"Chrome restaurado a Monitor 1: {win32gui.GetWindowRect(h)}")
            break
