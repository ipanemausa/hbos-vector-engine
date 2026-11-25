# REGLA DURA: `HBOS_PRODUCTION_DAG_01` (DAG INDUSTRIALIZADO Y FAIL-FAST DE PRODUCCIÓN)

- **Identificador Canónico:** `HBOS_PRODUCTION_DAG_01`
- **Ámbito:** Toda producción multimedia, audiovisual, síntesis vocal y renderizado E2E en Antigravity 2.0 y HBOS Vector Engine.
- **Topología del DAG:**

```text
[FASE 0: Pre-flight y Bloqueo de Residuos]
  |-- Audita G:\My Drive\Guiahoy_Produccion\YYYY-MM-DD\
  |-- Bloquea audios/guiones/SRT viejos (MIT / Make / RAG 768D)
  |-- Bloquea terminantemente TTS genérico, fondos con cajas de texto y PNGs estáticos
  |-- Exige: guion + fondos dinámicos/video + avatar con movimiento/lip-sync + WAV clon Guiahoy
        |
        +-- (Falta algo) --> FAIL-FAST HALT (se detiene sin mezclar archivos)
        |
        +-- (Todo OK) --> [FASE 1: Guion] -> [FASE 2: Visuales Cinemáticos y Avatar Animado]
                                                  |
                         [FASE 4: MP4 + SHA-256 + Reproductor] <-- [FASE 3: Voz Clonada + SRT]
                                                  |
                         [FASE 5: Actualizar/Probar .ps1] -> [FASE 6: Git Commit + Push/Sync]
```

---

## PROHIBICIONES TERMINANTES E INVIOLABLES (CERO TOLERANCIA)

1. **PROHIBICIÓN A — VOCES TTS GENÉRICAS FEMENINAS O SIN CLONAR:**
   - **Queda estrictamente prohibido** utilizar voces sintéticas genéricas del sistema operativo (SAPI como Helena, Sabina, Zira, David), voces TTS no autorizadas o voces femeninas para encarnar la voz de Guía Hoy.
   - **Obligatorio:** La voz debe ser exclusivamente la voz masculina clonada de Guillermo Alonso Hoyos (**Guiahoy**, acento `es-CO natural masculino`, frecuencia fundamental $f_0 \approx 109.2\text{ Hz}$), procesada mediante el pipeline oficial (Fish Audio / Drama 3, F5-TTS o el master acústico oficial `Guiahoy_CLONE_REF_90s_48k.wav` a 48 kHz mono, ecualización `highpass=65Hz, eq=115Hz +1.6dB` y normalizada a `-14.0 LUFS EBU R128` sin filtro destructivo `afftdn`).

2. **PROHIBICIÓN B — FONDOS CON CAJAS DE TEXTO ESTÁTICAS (DIAPOSITIVAS):**
   - **Queda estrictamente prohibido** generar o ensamblar videos utilizando fondos planos con marcos o cajas de texto estáticas simulando diapositivas de presentación.
   - **Obligatorio:** Los fondos deben ser imágenes futuristas cinemáticas limpias de alta fidelidad (1920x1080) o fondos de video continuo en movimiento (B-roll, secuencias de frames HD, Hiperframes vectoriales o animación generativa). Los textos y metadatos se despliegan exclusivamente como subtítulos dinámicos `.srt`/`.ass` o HUDs animados vectoriales.

3. **PROHIBICIÓN C — AVATARES PNG ESTÁTICOS SIN MOVIMIENTO NI LIP-SYNC:**
   - **Queda estrictamente prohibido** incrustar imágenes PNG fijas del avatar como elemento congelado sin sincronización labial ni animación gestual.
   - **Obligatorio:** El avatar de Guillermo debe operar con movimiento continuo real mediante la biblioteca de clips animados (`G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library\`, carrete maestro `reel-mudo-movimientos-avatar-mascotas.mp4`, o `hbos_avatar_animated_test.mp4`), integrando sincronización labial (lip-sync via MuseTalk, SadTalker, EchoMimic, LivePortrait o pipelines nube) con canal alfa / transparencia RGBA (`.mov`/`.webm` ProRes/VP9).

---

## Especificación Estricta de Fases del DAG:

1. **FASE 0 (Pre-flight & Bloqueo de Residuos):**
   - Audita físicamente el directorio `G:\My Drive\Guiahoy_Produccion\YYYY-MM-DD\`.
   - Bloquea explícitamente pistas y módulos anteriores (`Guiahoy_MASTER_48k_menos14LUFS.wav`, Make, MIT, RAG 768D).
   - Verifica el cumplimiento de las 3 Prohibiciones Terminantes (A, B y C).
   - Exige los 4 insumos canónicos del tema:
     1. Guion específico en `.md` (10 bloques modulares).
     2. Fondos visuales cinemáticos dinámicos o secuencias de video en 16:9 (`bg_01.jpg` a `bg_10.jpg` o video frames).
     3. Clips de avatar con movimiento gestual / lip-sync transparente en `G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library\` o pipeline de animación activo.
     4. Pista de audio `.wav` exclusiva de la voz clonada masculina de Guiahoy en `02_voz_guiahoy\` con duración $> 0\text{ s}$ validada con `ffprobe` a -14.0 LUFS.
   - **FAIL-FAST:** Si falta cualquiera de estos insumos o se detecta TTS genérico, diapositivas estáticas o PNGs congelados, el DAG se **DETIENE INMEDIATAMENTE** con código de salida 1 y mensaje explícito.

2. **FASE 1 (Guion Temático):**
   - Valida la existencia de los 10 bloques estructurados y la ausencia de contaminación conceptual (drift).

3. **FASE 2 (Visuales Cinemáticos y Avatar Animado):**
   - Valida la resolución 1920x1080 de los fondos cinemáticos y la composición multicapa en 3 planos (M-COMPOSICION-01) con avatar animado en movimiento continuo.

4. **FASE 3 (Audio y Subtítulos .SRT):**
   - Mide la duración exacta del audio con `ffprobe` y calcula la escala proporcional de tiempo para los 10 bloques.
   - Genera el `.srt` exclusivo sincronizado al milisegundo a partir del audio de la voz clonada de Guiahoy.

5. **FASE 4 (Ensamblaje, SHA-256 y Reproductor):**
   - Genera el video `.mp4` bajo la nomenclatura estricta del proyecto (`YYYY-MM-DD_<Tema>_10min.mp4`).
   - Computa el hash SHA-256 inmutable y genera el manifiesto JSON.
   - Clona copia de seguridad en `G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\`.
   - Indexa vector y metadatos en Qdrant (`canon_video_hbos_r768`).
   - Actualiza el reproductor interactivo embebido (`RULE_AUTO_LAUNCH_01`).

6. **FASE 5 (Actualización y Pruebas .ps1):**
   - Actualiza el script PowerShell canónico y ejecuta la matriz de verificación reportando tabla PASS/FAIL con validación estricta de las reglas A, B y C.

7. **FASE 6 (Cierre Git Obligatorio):**
   - Ejecuta `git status`, `git add`, `git commit` y `git push origin main` para garantizar sincronización y trazabilidad total en el repositorio remoto.
