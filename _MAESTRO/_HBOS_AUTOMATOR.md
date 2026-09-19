# HBOS AUTOMATOR — AGENTE DE EJECUCIÓN DE TAREAS DESATENDIDAS
### Ecosistema: HBOS-Diamantino · Vector Engine
### Tipo: Agente Interno · Categoría: Automatización y Pipelines
### Trazabilidad: operation_id = 148 | Estado: Pendiente

---

## 1. DESCRIPCIÓN
HBOS AUTOMATOR coordina la ejecución de flujos de trabajo multi-paso desatendidos basados en plantillas estandarizadas (P-43). Ejecuta desde la generación de guiones hasta el renderizado de video y verificación de redundancia sin fricción humana.

## 2. FUNCIONES
- Ejecución secuencial y paralela de plantillas canónicas (ej. `PRODUCIR_EPISODIO`).
- Auto-verificación de pre-requisitos antes de cada fase (auditoría de cuotas y assets).
- Activación de mecanismos de rollback automático si un paso crítico falla.
- Sincronización inmutable en triple redundancia (Local + Drive + Backup).

## 3. CÓMO USARLO
```python
# Disparo desatendido de producción de episodio
tarea_id = automator.ejecutar_plantilla(
    nombre="PRODUCIR_EPISODIO_COMPLETO",
    parametros={"episodio": "Ep05", "slug": "Biocomputacion-Cuantica"}
)
print("Tarea lanzada con ID:", tarea_id)
```

## 4. DEPENDENCIAS
- Qdrant Cloud (colecciones `registro_ecosistema` y `casos_uso_hbos`).
- FFmpeg con librerías de filtrado y masterización EBU R128.
- Sistema de archivos en triple redundancia P-03.

## 5. ESTADO
- **Estado Actual:** Pendiente de validación de orquestador de cron desatendido.
