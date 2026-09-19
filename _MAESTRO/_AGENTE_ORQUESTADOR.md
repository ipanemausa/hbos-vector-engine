# AGENTE ORQUESTADOR DE PROVEEDORES — ESPECIFICACIÓN TÉCNICA
### Sello: HBOS-Diamantino · Vector Engine
### Trazabilidad: `operation_id = 122` | Directiva Canónica ALEJAVI
### Patrón Asociado: P-42 · Lección: L-28

---

## 1. MISIÓN Y PROPÓSITO
El **Agente Orquestador de Proveedores** es la entidad inteligente encargada de coordinar dinámicamente la selección, autenticación, navegación y ejecución de tareas entre modelos de IA y herramientas del ecosistema.
Permite delegar operaciones complejas con un ahorro del 90% en tiempo operativo (L-28), asegurando estricto apego a las directivas canónicas de HBOS.

---

## 2. FLUJO DE EJECUCIÓN (PIPELINE DE 7 FASES)

```
 [1. Entrada de Tarea] ─────────► [2. Consulta Qdrant] ─────────► [3. Decisión de Proveedor]
 (Instrucción estructurada)      (Matriz de Casos de Uso)        (FreeLLMAPI, Gemini, etc.)
                                                                            │
                                                                            ▼
 [6. Ejecución & Inferencia] ◄─── [5. Configuración Key] ◄────── [4. Navegación / Conexión]
 (Proceso de tarea en Nube)       (Inyección segura en Vault)     (Navegador Playwright / API)
              │
              ▼
 [7. Reporte & Auditoría]
 (Registro en Qdrant op_id)
```

### Detalle de Fases:
1. **Recepción de Tarea:** Valida la estructura del payload (tipo de tarea, requisitos de calidad, latencia y privacidad).
2. **Consulta a Memoria Vectorial (Qdrant):** Consulta las colecciones `diamantino_casos_uso`, `diamantino_patrones` y `diamantino_apps` mediante embeddings R384/R768 para ubicar la mejor estrategia comprobada.
3. **Decisión de Proveedor:** Aplica el Árbol de Decisión Canónico (P-26) y la Matriz de Prioridad (P-27) evaluando el estado de cuota en tiempo real.
4. **Navegación de la Aplicación:** Si la tarea requiere interacción con interfaz web (ej. dashboard de FreeLLMAPI, consola Cloud), el agente orquestador instruye al subagente navegador (Playwright) para recorrer las rutas mapeadas.
5. **Configuración de Key:** Solicita al `HBOS-API Key Vault` (P-41) la clave temporal descifrada en memoria, inyectándola sin persistencia en disco.
6. **Ejecución de Tarea:** Despacha la solicitud aplicando compresión de contexto R768 si la tarea excede 5,000 tokens.
7. **Reporte y Auditoría:** Recolecta métricas de latencia, tokens y éxito, vectorizando el resultado bajo un `operation_id` consecutivo en `registro_ecosistema`.

---

## 3. GUARD RAILS DEL AGENTE ORQUESTADOR (L-29)
- **Principio de Mínima Acción (L-29):** El agente orquestador hace **estrictamente** lo ordenado por el operador. Prohibido ejecutar acciones no solicitadas, crear dependencias fantasma o alterar configuraciones de producción.
- **Failover Autónomo:** Si un proveedor responde con HTTP 429 (rate limit) o 5xx, conmuta automáticamente al siguiente escalón de la cascada y lo documenta en el log sin detener la ejecución global.
