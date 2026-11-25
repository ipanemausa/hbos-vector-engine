# REGLA MAESTRA CANÓNICA: `HBOS_DAILY_VIDEO_MASTER_PROMPT`
## Gobernanza de Producción Diaria de Video Autónomo en HBOS Vector Engine

- **Identificador Canónico:** `HBOS_DAILY_VIDEO_MASTER_PROMPT`
- **Ámbito:** Flujo diario unificado de producción audiovisual de alta retención (10 minutos / 10 bloques modulares) en Antigravity 2.0 y HBOS Vector Engine.
- **Script Canónico Ejecutable:** `scripts\hbos_daily_video_master.ps1`
- **Destino Primario de Producción:** `G:\My Drive\Guiahoy_Produccion\YYYY-MM-DD\`
- **Destino Bóveda Definitiva:** `G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\`
- **Memoria Vectorial:** Colecciones `canon_video_hbos_r768` (768D) y `canon_video_hbos` (384D) en Qdrant (`http://127.0.0.1:6333`).

---

## 1. PRINCIPIOS ARQUITECTÓNICOS FUNDAMENTALES

### 1.1 Aislamiento Estricto por Corrida (Zero Residual Contamination)
1. **Limpieza y Segregación:** En cada ejecución diaria, cualquier activo generado por corridas anteriores u otros temas (ej. clases previas como *Clase 01 MIT*, *Make*, *RAG 768D*) se aísla automáticamente en una subcarpeta dedicada de archivo `_archive_previous_runs/` dentro del directorio de la fecha.
2. **Exclusividad del Entregable:** El reproductor interactivo local, los manifiestos JSON, los archivos SRT y el auto-launch canónico (`RULE_AUTO_LAUNCH_01`) deben apuntar **estricta y exclusivamente al MP4 final recién generado** para el tema asignado (`YYYY-MM-DD_<Tema>_10min.mp4`).
3. **Prohibición de Mezcla:** Queda terminantemente prohibido concatenar, referenciar o reutilizar fragmentos de audio o video de proyectos diferentes.

### 1.2 Pre-debug de 5 Segundos en Fase 0 (Fail-Fast Anti-Hanging)
1. **Prueba Corta Obligatoria:** Antes de iniciar cualquier renderizado pesado de los 10 bloques (450s+), el sistema **debe** ejecutar un render de prueba de 5 segundos (`predebug_5s_test.mp4`) evaluando:
   - Capacidad de FFmpeg para procesar el fondo 16:9 con movimiento de cámara (`zoompan`).
   - Inserción y loop del clip de avatar PIP de Guillermo A. Hoyos (`06_Avatar_Clip_Library`).
   - Muxing y codificación H.264/AAC.
2. **Timeout Estricto de 15 Segundos:** El pre-debug tiene un temporizador de corte (timeout) de 15 segundos. Si la prueba falla o se excede el timeout:
   - **FAIL-FAST HALT:** El script se detiene de inmediato con error explícito antes de consumir recursos en el render largo.

### 1.3 Compuertas PASS/FAIL por Capas y Timeout por Bloque en Fase 4
1. **Capa Guion / SRT:**
   - El guion debe contener exactamente 10 bloques modulares (`### BLOQUE 01` a `10`).
   - Los subtítulos sincronizados `.srt` deben calcularse proporcionalmente a la duración exacta del audio master con `ffprobe`. Cero desfases temporales.
2. **Capa Voz Masculina Clonada de Guía Hoy:**
   - Prohibido cualquier TTS genérico del sistema operativo (SAPI como Helena, Sabina, David) o voces femeninas.
   - Pista master a 48 kHz mono, frecuencia fundamental $f_0 \approx 109.2\text{ Hz}$ (acento `es-CO` masculino natural) y normalización auditada a `-14.0 LUFS EBU R128`.
3. **Capa Fondos Cinemáticos Limpios:**
   - 10 fondos en 16:9 (`bg_01.jpg` a `bg_10.jpg`) limpios de alta fidelidad futurista.
   - Prohibido generar fondos con cajas de texto estáticas o marcos de presentación tipo diapositiva.
   - Movimiento cinemático continuo obligatorio (`zoompan` dinámico `1.0x -> 1.08x`).
4. **Capa Avatar en Movimiento Continuo / Lip-Sync:**
   - Prohibido el uso de imágenes PNG estáticas congeladas.
   - Inserción activa en esquina PIP (640x360) de clips de video de la biblioteca de movimiento continuo de Guillermo (`06_Avatar_Clip_Library`, clips `AVM_01` a `AVM_15`) o video con canal alfa / lip-sync transparente (`.mov` ProRes/qtrle).
5. **Timeout por Bloque en Fase 4:**
   - Cada uno de los 10 bloques cinemáticos cuenta con un timeout individual estricto de **90 segundos**. Si un bloque excede ese tiempo, el proceso se aborta de forma controlada sin dejar procesos de FFmpeg colgados en segundo plano.

### 1.4 Memoria Vectorial y Entorno Completo en Qdrant (Cero Costo)
Al finalizar con éxito la Fase 4:
1. El script indexa automáticamente el vector semántico (768D y 384D) y el payload institucional en las colecciones `canon_video_hbos_r768` y `canon_video_hbos`.
2. El registro incluye el entorno completo:
   - Rutas absolutas en Google Drive 5TB (`G:\My Drive\Guiahoy_Produccion\...`).
   - Ruta de copia inmutable en Bóveda (`G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\...`).
   - Ruta del repositorio local Git (`C:\Users\ipane\hbos-deploy\hbos-vector-engine`).
   - Parámetros de audio (109.2 Hz, 48 kHz, -14.0 LUFS) y video (1920x1080 30fps H.264, zoompan continuo, PIP 640x360).
   - Manifiesto SHA-256 del entregable.
   - Certificación de **Cero Costo:** Infraestructura local + almacenamiento en Google Drive 5TB sin consumo de APIs pagas ni servicios cloud externos innecesarios.

---

## 2. FLUJO FACTORIZADO DEL LANZADOR DIARIO (`hbos_daily_video_master.ps1`)

```text
[INICIO: hbos_daily_video_master.ps1]
  |
  +--> [PASO 0: Aislamiento & Segregación]
  |      |-- Archiva residuos de otros temas en _archive_previous_runs/
  |      \-- Garantiza entorno limpio para la fecha y tema solicitados
  |
  +--> [FASE 0: Pre-Debug 5s Fail-Fast & Auditoría Insumos]
  |      |-- Ejecuta prueba de 5 segundos de FFmpeg (timeout 15s)
  |      |   \--> [Fallo/Timeout] --> HALT INMEDIATO
  |      \--> [Paso] Audita: Guion (10 bloques), 10 fondos 16:9, clips avatar, audio clonado
  |
  +--> [FASE 1: Capa de Guion & Sincronía Temporal]
  |      \-- Valida 10 bloques sin drift conceptual y calcula marcas de tiempo
  |
  +--> [FASE 2: Capa Visual & Avatar PIP]
  |      \-- Valida 10 fondos limpios sin texto y clips AVM_01..15
  |
  +--> [FASE 3: Capa Vocal & Subtítulos SRT]
  |      \-- ffprobe audio (>0s, -14 LUFS, 109.2 Hz) y genera .srt exclusivo
  |
  +--> [FASE 4: Ensamble Cinemático Concurrente (Timeout 90s/bloque)]
  |      |-- Render multihilo de los 10 bloques con zoompan continuo
  |      |-- Concatenación y muxing con audio master Guiahoy
  |      |-- Cálculo de hash SHA-256 y replicación en Media Vault
  |      |-- Actualización de reproductor HTML exclusivo
  |      \-- RULE_AUTO_LAUNCH_01: Apertura inmediata del video en Windows
  |
  +--> [FASE 5: Registro Vectorial en Qdrant (768D y 384D) & Cero Costo]
  |      \-- Indexa prompt maestro, entorno, rutas y métricas en canon_video_hbos*
  |
  +--> [FASE 6: Matriz de Pruebas PASS/FAIL (13 Compuertas)]
  |      \-- Reporta tabla consolidada con estado de cada gate
  |
  \--> [FASE 7: Cierre Git Institucional]
         \-- git status, add, commit con mensaje estándar y push origin main
```

---

## 3. PROHIBICIONES Y PENALIZACIONES
- **PROHIBICIÓN ESTRICTA:** Queda prohibido modificar el flujo para saltear el pre-debug de 5 segundos o relajar las compuertas de verificación de las 3 Prohibiciones Canónicas (A: Cero TTS genérico, B: Cero diapositivas estáticas, C: Cero PNGs congelados).
- Cualquier falla en cualquier compuerta debe provocar el **detenimiento inmediato (Fail-Fast)** del lanzador, reportando en color rojo el insumo o paso que no cumplió con el estándar.
