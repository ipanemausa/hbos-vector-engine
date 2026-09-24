# HBOS · CREACIÓN DE CADENAS · op=291

## Proceso

### Opción A · Si hay tabla SQLite
1. Descubrir schema.
2. Insertar cadenas por SQL.
3. Verificar.

### Opción B · Si NO hay tabla
1. Automatizar UI con pyautogui.
2. Capturar coordenadas de:
   - Botón ⚙️ (settings)
   - Campo "Chain name"
   - Botón "Add chain"
   - Selector de modelos
   - Botón "Save"
3. Script que crea las 8 cadenas.

### Opción C · Manual (fallback)
1. Abrir UI.
2. Crear cada cadena manualmente.
3. Usar documento _CADENAS_FALLBACK_op290.md.

## Estado actual

- Cadenas existentes: auto, auto:default
- Cadenas pendientes: reasoning, code, fast, video, marketing, long-context, vision, premium

Fecha: 2026-09-24 11:35:25
