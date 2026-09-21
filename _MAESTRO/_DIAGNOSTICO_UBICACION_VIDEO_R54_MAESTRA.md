# REGLA R54 · DIAGNÓSTICO DE UBICACIÓN Y VERIFICACIÓN MULTIPANTALLA
**Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**

## 1. PRINCIPIO RECTOR (R54)
- Antes de cualquier acción sobre activos audiovisuales, se debe diagnosticar con precisión matemática en qué estación, escritorio y coordenadas de pantalla se proyecta la ventana interactiva.
- Prohibida la dispersión a ciegas o ventanas en segundo plano desvinculadas de la sesión visual del operador humano.

---

## 2. TOPOLOGÍA DE MONITORES FÍSICOS

| Monitor | Dispositivo | Coordenadas Bounds | Resolución | Función en el Ecosistema |
|---|---|---|---|---|
| **Pantalla 1** | `\\.\DISPLAY1` | `(0, 0, 1280, 720)` | 1280x720 | Navegación, Chrome, Consola Principal |
| **Pantalla 2** | `\\.\DISPLAY2` | `(1920, 0, 3840, 1080)` | 1920x1080 | Entorno de Desarrollo (Antigravity IDE) |
| **Pantalla 3** | `\\.\DISPLAY5` | `(-1920, 0, -640, 720)` | 1280x720 | **Canvas de Visualización Dedicado (Video Master)** |

---

## 3. DISTRIBUCIÓN DE VENTANAS ACTIVAS EN `WinSta0\Default`

- **Pantalla 3 (`-1920, 0, -640, 720`):**
  - Ventana: `DEMIS_HASSABIS_PANTALLA3` (`mpv.exe`).
  - Estado: `HWND_TOPMOST`, Pantalla completa, sin solapamiento.
- **Pantalla 2 (`1909, 0, 3851, 1054`):**
  - Ventana: `hbos-vector-engine - Antigravity IDE - Review`.
- **Pantalla 1 (`0, 0, 1280, 720`):**
  - Ventana: `Contexto total DAG R768 - DeepSeek - Google Chrome`.

---

## 4. HERRAMIENTAS Y SCRIPTS MOTORES
- **Diagnóstico Integral:** [`diagnose_video_location.py`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/diagnose_video_location.py)
- **Lanzador Interactivo:** [`launch_video_p3_verified.py`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/launch_video_p3_verified.py)
- **Alineador Topmost:** [`maximize_mpv_p3.py`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/maximize_mpv_p3.py)
