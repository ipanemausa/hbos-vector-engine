# -*- coding: utf-8 -*-
import win32service
import win32gui
import win32con

desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

hwnds = desk.EnumDesktopWindows()
chrome_hwnd = None
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'Google Chrome' in t and win32gui.IsWindowVisible(h):
        r = win32gui.GetWindowRect(h)
        if r[0] > -10000: # no minimizada
            chrome_hwnd = h
            print(f"Chrome encontrado: '{t}' en {r}")
            # Mover la ventana visible de Chrome a Pantalla 3:
            # Monitor 3 bounds: left=-1920, top=0, width=1280, height=720
            win32gui.ShowWindow(h, win32con.SW_RESTORE)
            win32gui.SetWindowPos(h, win32con.HWND_TOP, -1920, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
            print(f"--> Chrome MOVIDO a Pantalla 3: {win32gui.GetWindowRect(h)}")
            break

if not chrome_hwnd:
    print("No se encontro ventana visible de Chrome.")
