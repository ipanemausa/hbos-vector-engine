# -*- coding: utf-8 -*-
import win32service
import win32gui
import win32con

desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()

hwnds = desk.EnumDesktopWindows()
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if 'DEMIS_HASSABIS_PANTALLA3' in t:
        print(f"Ventana de video encontrada: '{t}'")
        # Forzar restauración, primer plano y pantalla completa en Pantalla 3
        # Pantalla 3: x=-1920, y=0, width=1280, height=720
        win32gui.ShowWindow(h, win32con.SW_RESTORE)
        win32gui.ShowWindow(h, win32con.SW_SHOW)
        win32gui.SetWindowPos(h, win32con.HWND_TOPMOST, -1920, 0, 1280, 720, win32con.SWP_SHOWWINDOW)
        print(f"--> [MAXIMIZADO/VISUAL EN PANTALLA 3]: {win32gui.GetWindowRect(h)}")
        break
