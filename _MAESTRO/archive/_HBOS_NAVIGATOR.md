# HBOS NAVIGATOR — AGENTE NAVEGADOR DE APLICACIONES
### Ecosistema: HBOS-Diamantino · Vector Engine
### Tipo: Agente Interno · Categoría: Navegación Visual
### Trazabilidad: operation_id = 148 | Estado: Pendiente

---

## 1. DESCRIPCIÓN
HBOS NAVIGATOR es el agente autónomo encargado de interactuar visual y programáticamente con aplicaciones de escritorio y web mediante Playwright. Su propósito es automatizar configuraciones, recorrer rutas de menús, presionar botones y verificar estados en UIs sin requerir intervención humana directa.

## 2. FUNCIONES
- Mapeo automatizado de árboles de componentes e identificadores CSS (`map_app.py`).
- Navegación dirigida botón por botón guiada por memoria vectorial (`navigate_app.py`).
- Detección y verificación de estados en el DOM (visibilidad, habilitación, texto).
- Generación de capturas y logs de auditoría visual para la bóveda de estado.

## 3. CÓMO USARLO
```python
from navigate_app import navigate_and_execute

# Ejecución autónoma de una tarea en la app FreeLLMAPI
resultado = navigate_and_execute(
    app_name="FreeLLMAPI",
    task_description="activar compresion de contexto",
    base_url="http://localhost:3001"
)
print("Resultado:", resultado["exito"])
```

## 4. DEPENDENCIAS
- Playwright (Chromium headless/headed).
- Qdrant Cloud (colección `diamantino_apps`).
- Python 3.13 / Async IO.

## 5. ESTADO
- **Estado Actual:** Pendiente de activación en producción (Sandbox Playwright configurado en Drive).
