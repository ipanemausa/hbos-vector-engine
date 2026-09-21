# -*- coding: utf-8 -*-
import win32service
import win32gui
import win32con

desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
hwnds = desk.EnumDesktopWindows()
print(f"Total ventanas en escritorio interactivo Default: {len(hwnds)}")
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if t and win32gui.IsWindowVisible(h):
        r = win32gui.GetWindowRect(h)
        print(f"  [{h}] '{t}' -> Rect: {r}")
desk.CloseDesktop()
