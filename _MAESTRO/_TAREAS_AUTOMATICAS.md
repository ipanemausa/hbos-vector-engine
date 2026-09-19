# TAREAS AUTOMÁTICAS CON SEGURIDAD — PLANTILLAS CANÓNICAS
### Sello: HBOS-Diamantino · Vector Engine
### Trazabilidad: `operation_id = 123` | Directiva Canónica ALEJAVI
### Patrón Asociado: P-43 · Lección: L-28 / L-29

---

## 1. INTRODUCCIÓN
Las **Tareas Automáticas con Seguridad (P-43)** definen el conjunto de procedimientos estandarizados que el Agente Orquestador y el Agente Navegador pueden ejecutar de manera desatendida o semiautónoma, con garantías formales de rollback, trazabilidad en Qdrant y aislamiento criptográfico.

---

## 2. CATÁLOGO DE PLANTILLAS CANÓNICAS

### Plantilla 1: `PRODUCIR_EPISODIO_COMPLETO`
- **Disparador:** Solicitud de nuevo episodio por parte del operador con slug y tema.
- **Flujo:**
  1. Generar guion bilingüe auditado (P-15, P-17).
  2. Construir Storyboard estructurado con 10 bloques y asignación de hosts (P-18).
  3. Despachar generación cinemática Wan 2.1 I2V en DashScope / fal-queue.
  4. Generar locución soberana y BGM masterizado a -14 LUFS (P-04 v2).
  5. Ensamblar en FFmpeg local con ducking de audio automático (P-05).
  6. Exportar los 4 formatos responsive (16:9, 9:16, 1:1, 4:5) y kit de thumbnails (P-11).
  7. Ejecutar sincronización de redundancia triple (P-03).

### Plantilla 2: `GENERAR_VOCES_NARRATIVAS`
- **Disparador:** Actualización de guion técnico o necesidad de síntesis de bloques.
- **Flujo:**
  1. Verificar cuota disponible en ElevenLabs.
  2. Si cuota agotada -> conmutar automáticamente a CosyVoice2 vía FreeLLMAPI.
  3. Normalizar volumen acústico a EBU R128 (-14.0 LUFS, TP -1.0 dBTP).
  4. Guardar WAV en `03_Assets\Voces\` con redundancia triple.

### Plantilla 3: `OPTIMIZAR_COMPRESION_CONTEXTO`
- **Disparador:** Contexto acumulado superior a 5,000 tokens o ejecución de Modo Fusión.
- **Flujo:**
  1. Activar módulo de compresión de contexto en FreeLLMAPI.
  2. Aplicar factorización semántica R768 en Antigravity para embeddings y memoria.
  3. Medir tokens brutos vs. compactados y registrar porcentaje de ahorro.

### Plantilla 4: `ROTAR_PROVEEDORES_FAILOVER`
- **Disparador:** Recepción de código HTTP 429 (Rate Limit) o 403 (Allocation Exhausted).
- **Flujo:**
  1. Aislar temporalmente la credencial agotada y activar temporizador de cooldown.
  2. Consultar siguiente nodo disponible en la cascada de proveedores (P-29).
  3. Reanudar la tarea en curso sin interrumpir el pipeline.
  4. Registrar evento de failover en `registro_ecosistema`.

### Plantilla 5: `VERIFICAR_CUOTAS_SISTEMA`
- **Disparador:** Inicio de jornada o intervalo cron programado.
- **Flujo:**
  1. Sondeo concurrente a ElevenLabs, DashScope, Gemini, Groq y OpenRouter.
  2. Alertar si algún proveedor posee menos del 20% de su límite mensual.
  3. Generar reporte consolidado de salud de cuotas en JSON.
