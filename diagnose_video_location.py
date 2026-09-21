# -*- coding: utf-8 -*-
"""
diagnose_video_location.py — REGLA R54: DIAGNOSTICAR UBICACIÓN DE VIDEO
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
"""

import os
import psutil
import socket
import win32service
import win32gui
import win32con
import ctypes
from ctypes import wintypes

print("=" * 70)
print(">>> DIAGNÓSTICO EXHAUSTIVO DE UBICACIÓN DE VIDEO (REGLA R54) <<<")
print("=" * 70)

# 1. Monitores del Sistema
user32 = ctypes.windll.user32
monitors = []
def MonitorEnumProc(hMonitor, hdcMonitor, lprcMonitor, dwData):
    r = lprcMonitor.contents
    monitors.append((r.left, r.top, r.right, r.bottom))
    return 1

MonitorEnumProcType = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
user32.EnumDisplayMonitors(None, None, MonitorEnumProcType(MonitorEnumProc), 0)

print(f"\n1. MONITORES FÍSICOS ({len(monitors)} detectados):")
for idx, m in enumerate(monitors):
    w = m[2] - m[0]
    h = m[3] - m[1]
    name = f"Pantalla {idx+1}"
    if m[0] == 0 and m[1] == 0:
        name += " [PRINCIPAL]"
    print(f"   • {name}: Bounds = ({m[0]}, {m[1]}, {m[2]}, {m[3]}) | Resolución = {w}x{h}")

# 2. Procesos de Video
video_keywords = ['mpv', 'ffplay', 'vlc', 'wmplayer', 'chrome', 'msedge', 'media']
print(f"\n2. PROCESOS DE VIDEO / REPRODUCCIÓN ACTIVOS:")
found_procs = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        pname = p.info['name'] or ''
        cmd = ' '.join(p.info['cmdline'] or [])
        if any(k in pname.lower() for k in ['mpv', 'ffplay', 'vlc', 'wmplayer']) or 'demis' in cmd.lower():
            found_procs.append((p.info['pid'], pname, cmd))
            print(f"   • [PID {p.info['pid']}] {pname} | Comando: {cmd[:90]}...")
    except:
        pass
if not found_procs:
    print("   • [NINGUNO] No hay procesos multimedia reproduciendo en este instante.")

# 3. Puertos Activos Locales Clave
ports_to_check = [3001, 3002, 8000, 8080, 5000, 11434]
print(f"\n3. ESTADO DE PUERTOS CLAVE DEL ECOSISTEMA:")
for pt in ports_to_check:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    res = s.connect_ex(('127.0.0.1', pt))
    status = "ACTIVO / ESCUCHANDO" if res == 0 else "LIBRE"
    print(f"   • Puerto {pt}: {status}")
    s.close()

# 4. Ventanas en el Escritorio Interactivo Default
print(f"\n4. VENTANAS ACTIVAS EN EL ESCRITORIO INTERACTIVO (WinSta0\\Default):")
desk = win32service.OpenDesktop('Default', 0, False, win32con.GENERIC_ALL)
desk.SetThreadDesktop()
hwnds = desk.EnumDesktopWindows()

visible_windows = []
for h in hwnds:
    t = win32gui.GetWindowText(h)
    if t and win32gui.IsWindowVisible(h):
        r = win32gui.GetWindowRect(h)
        if r[0] > -10000: # excluir minimizadas virtuales de Windows
            visible_windows.append((h, t, r))
            # Determinar en qué pantalla cae
            pantalla = "Desconocida / Fuera de rango"
            for idx, m in enumerate(monitors):
                if m[0] <= r[0] < m[2] and m[1] <= r[1] < m[3]:
                    pantalla = f"Pantalla {idx+1}"
                    break
            print(f"   • [{pantalla}] '{t}' | Rect = {r}")

desk.CloseDesktop()
print("=" * 70)
