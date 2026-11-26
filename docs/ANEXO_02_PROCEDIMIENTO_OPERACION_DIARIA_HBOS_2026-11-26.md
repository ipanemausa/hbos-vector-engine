# ANEXO 02 · PROCEDIMIENTO DE OPERACIÓN DIARIA HBOS (2026-11-26)

- **Identificador:** `ANEXO_02_PROCEDIMIENTO_OPERACION_DIARIA_HBOS_2026-11-26`
- **Base Integrada:** `HBOS_MULTIAGENT_TOPOLOGY_01.md` + `HBOS_PRODUCTION_DAG_01.md` + `BLOQUE-ANTIGRAVITY-CURADO-2026-11-26.md` (Factores F1–F14).
- **Alcance:** Paso a paso operativo para que los modelos embebidos en Antigravity (**Gemini**, **GPT**, **Claude**) y los agentes por defecto (**`self`**, **`research`**, **`browser`**, **`image-generator`**) ejecuten tareas diarias bajo un flujo único controlado, delegándose subtareas mediante contratos JSON sin estado en RAM.

---

## 1. Mapa de Roles: Modelos Embebidos y Agentes por Defecto

| Rol en Topología | Quién lo Ejecuta | Lugar (F10) | Responsabilidad y Delegación |
| :--- | :--- | :---: | :--- |
| **Nodo 1 · Coordinador & Pre-Flight** | **Claude / Gemini** (sesión principal) + agente **`self`** + MCP `gdrive` / `hbos-chat-context` | `PC + CLOUD` | Lee la Cápsula F12 (`ESTADO-HILO.md` + Quadrant Cloud), mide RAM (`>= 1 GB`), verifica hashes SHA-256 de entrada, descompone el DAG, lanza **Tasks** paralelos (F13a) y detiene en **Elicitation** (F13b) para decisiones humanas de Guillermo. Nunca bloquea sondeando en bucle. |
| **Nodo 2 · Investigador & Semántico 768d** | Agente **`research`** + **Gemini / GPT** vía `hbos-freellmapi` (`:3001`) + `open-weight-models` + `gemini-embedding-2` (`768d`) | `CLOUD` (con lectura local) | Rastrea archivos y fuentes verificadas (prohibido opinar o simular), factoriza en `768d` exactos con `gemini-embedding-2` y consulta/escribe en Qdrant Cloud (`registro_ecosistema_r768`, `canon_video_hbos_r768`). |
| **Nodo 3 · Director de Arte 3D & Activos** | Subagente **`image-generator`** + MCPs `hbos-diamantino` / `diamantini-imagenes` + FLUX vía gateway | `CLOUD -> PC` | Genera o valida fondos `1920x1080` limpios (cero cajas de texto estáticas). Verifica hash SHA-256 al aterrizar en `G:\My Drive` / PC. |
| **Nodo 4 · Ejecutor Media, Voz y Render** | Subagente **`self`** / scripts Python + **VoxCPM2 Plus Space** + OpenCV/FFmpeg local + skill `guiahoy-video-producer` | `CLOUD` (Voz) / `PC` (FFmpeg) | Síntesis vocal exclusivamente con **VoxCPM2 Plus** (`ref-video08`, `-14 LUFS`, `48 kHz mono`; `F5-TTS` veto permanente). Avatar por **ruta fotográfica canónica** (o carril aislado **F14 Colab** solo para experimentos con pre-verificación de media y gate ciego). Render FFmpeg solo con RAM libre `>= 1 GB`. |
| **Nodo 5 · Auditor QA Multimodal** | **GPT / Claude / Gemini** (visión + scripts deterministas) + `ffprobe` / `blackdetect` | `PC + CLOUD` | Verifica visualmente stills clave (sin panel en mitad de módulo, panel correcto al inicio, transiciones limpias, 0 cuadros negros, A/V `±0.05 s`). Cero `PASS` simulados. |
| **Nodo 6 · Navegación Web Autenticada** | Subagente **`browser`** | `PC` (Chrome DevTools) | Opera interfaces web autenticadas (Spaces, Drive web, consolas) cuando no hay API directa. Deja artefacto verificado con SHA-256. |
| **Nodo 8 · Consejo Multi-Modelo & Arbitraje 429** | **Gemini + GPT + Claude** + `hbos-freellmapi` (`:3001`) + `open-weight-models` + `ollama` (`11434` offline) | `CLOUD / PC` | Aporta segunda opinión cruzada en contratos/código y conmuta ante `HTTP 429`. **Regla F7:** `mumo` permanece **PENDING** (geo-bloqueado); **PROHIBIDO** enrutar trabajo real por `mumo` hasta completar login US y medir sonda en vivo. |

---

## 2. Secuencia Diaria Obligatoria (Paso a Paso con Gates)

### Paso 0 · PRE-FLIGHT (F0 + F12)
1. **Leer Cápsula de Handoff (F12):** Leer `ESTADO-HILO.md` y consultar el último `handoff_capsule` en Quadrant Cloud (`registro_ecosistema_r768`). Nunca iniciar desde memoria de chat.
2. **Sondas en Vivo (F3):** Probar `https://hbos-vector-engine.vercel.app/v1/health`, Qdrant Cloud `/collections`, `gemini-embedding-2` (`768d`), y `http://127.0.0.1:3001/v1/models` (FreeLLMAPI). Confirmar Docker apagado y `:6333` OFF (F5).
3. **Medición de RAM (F6) e Insumos (F10):** Verificar RAM libre `>= 1.0 GB` (si es menor, cerrar Chrome/Edge/procesos ociosos primero) y validar SHA-256 de todos los insumos locales/Drive.
4. **GATE 0:** Si falta cualquier sonda, hay mismatch de SHA-256 o RAM `< 1.0 GB` -> **`HALT`** y registrar causa en Quadrant.

### Paso 1 · DISEÑO / ACTUALIZACIÓN DEL FLUJO EN QUADRANT (F11 + L1/L2/L3)
1. Si la tarea pertenece a un nodo nuevo (`financial`, `planning`, `direction`, `control`, `organization`, `project_feasibility_analysis`, `source_analysis`), registrar primero su **sub-flujo** en `registro_ecosistema_r768` con etapas etiquetadas `PC` o `CLOUD` y puntos SHA-256 de frontera.
2. Delegar subtareas independientes en paralelo mediante **Tasks / subagentes** (`research`, `image-generator`, `browser`) usando el Contrato JSON Ligero (`agent_id`, `phase`, `status: PASS|FAIL|BLOCKED`, `cause`, `fallback_used`, `verified_metrics`, `artifacts` con ruta y SHA-256).
3. **GATE 1:** Lectura de vuelta (*read-back*) desde Qdrant Cloud verificando conteo exacto y muestras, más regeneración automática de `MAPA-VIVO\mapa.html` (`scripts/generate_mapa_vivo_from_quadrant.py`).

### Paso 2 · EJECUCIÓN DE PRODUCCIÓN CON CONTROL DE FRONTERAS (F10)
1. **Regla de Frontera PC <-> CLOUD:** Ninguna etapa consume un archivo de otra etapa sin verificar **lugar + SHA-256** en destino.
2. **Control Humano (F13b Elicitation):** Cuando exista selección creativa o aprobación de versión (ej. elegir build canónico de video o aprobar experimento F14), el flujo se detiene y pregunta explícitamente a Guillermo.
3. **Versionado (F2):** Nunca sobrescribir entregables ni documentos base; versiones anteriores pasan a `superados/` o conservan su versión en `canon_video_hbos_r768`.

### Paso 3 · AUDITORÍA QA Y PRE-VISUALIZACIÓN (`RULE_AUTO_LAUNCH_01`)
1. Ejecutar verificación determinista (`ffprobe`, `blackdetect`, extracción y revisión visual de stills, pruebas unitarias o hash checks según el nodo).
2. Actualizar Quadrant Cloud y regenerar `MAPA-VIVO\mapa.html`.
3. Abrir automáticamente el entregable final en pantalla (`Start-Process` / `os.startfile`) apuntando a `G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\...` para verificación inmediata de Guillermo.

### Paso 4 · CIERRE GIT CON ESCANEO DE SECRETOS (HARD GATE)
1. Ejecutar `scripts/secret_scan_gate.py` (patrones + entropía) sobre todo el árbol rastreado y archivos nuevos a commitear.
2. **Si `hits > 0`:** **`HALT` inmediato**. No commitear ni hacer push; registrar el hallazgo (archivo y línea, **nunca el valor del secreto**, regla R30/F8) en Quadrant y reportar.
3. **Si `hits == 0`:** `git add`, `git commit`, `git push origin main`, verificar `git status` limpio y `HEAD == origin/main`, registrar recibo en Quadrant.

### Paso 5 · RESPALDO VERIFICADO, CÁPSULA F12 Y RESET DE RAM A CERO-TAREA
*(Solo tras Fase 4 en OK)*
1. **Respaldo 5TB:** Exportar colecciones Quadrant Cloud (`registro_ecosistema_r768`, `canon_video_hbos_r768`) + snapshot del workspace hacia Google Drive 5TB (`rclone`) y verificar por lectura de vuelta (conteo + SHA-256). Si alguna gate previa dio `KO`, ese estado fallido **nunca** se respalda como bueno: va a `superados/`/cuarentena con su reporte de fallo.
2. **Cápsula F12 (Hard Gate Obligatorio antes de cualquier cierre):** Escribir la Cápsula de Handoff en Quadrant Cloud **y** en `ESTADO-HILO.md` con: (1) estado por fase con evidencia, (2) próximo paso concreto, (3) discrepancias/cabos abiertos, (4) rutas exactas y hashes de artefactos. Verificar leyendo ambos de vuelta.
3. **Reset de RAM a Estado Cero-Tarea:** Cerrar procesos residuales (renders, ffmpeg, python workers, Chrome/Edge, helpers IDE, reproductores), conservar únicamente `FreeLLMAPI` y servicios del sistema, purgar standby cache (`EmptyStandbyList` o trim de working sets) y **medir RAM libre `>= 7.0 GB` de `11.8 GB`** (si es menor, nombrar cada proceso con `> 100 MB` y su causa).

---

## 3. Matriz de Arbitraje Ante Fallos (`HTTP 429` / Red / Tool Error)

1. **Nivel 1 (Fallback Determinista Local):** `rclone` si falla MCP `gdrive`; `libx264` si falla aceleración hardware; `ollama` (`11434`) solo si cae conectividad externa. *(Nunca usar `all-mpnet-base-v2` como sustituto silencioso de `gemini-embedding-2` 768d para escritura canónica en Quadrant: si falla `gemini-embedding-2`, reportar y detener).*
2. **Nivel 2 (Conmutación Multi-Modelo):** Alternar entre `hbos-freellmapi` (`:3001`) y `open-weight-models` (`query_gemini_free`, `query_groq_coder`, `query_deepseek_r1`, `query_qwen3_max`). **No usar `mumo`** mientras siga `PENDING`.
3. **Nivel 3 (Cómputo Remoto o UI):** Subagente `browser` para flujos interactivos; Colab exclusivamente bajo carril **F14** para experimentos de avatar.
4. **Nivel 4 (`FAIL` / `BLOCKED` Explícito):** Prohibido simular `PASS`. Detener, registrar estado y evidencia exacta en Quadrant y Cápsula F12, y reportar.
