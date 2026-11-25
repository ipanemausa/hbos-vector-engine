# REGLA DURA: `HBOS_PRODUCTION_DAG_01` (DAG INDUSTRIALIZADO Y FAIL-FAST DE PRODUCCIÓN)

- **Identificador Canónico:** `HBOS_PRODUCTION_DAG_01`
- **Ámbito:** Toda producción multimedia, audiovisual, síntesis vocal y renderizado E2E en Antigravity 2.0 y HBOS Vector Engine.
- **Topología del DAG:**

```text
[FASE 0: Pre-flight y Bloqueo de Residuos]
  |-- Audita G:\My Drive\Guiahoy_Produccion\YYYY-MM-DD\
  |-- Bloquea audios/guiones/SRT viejos (MIT / Make / RAG 768D)
  |-- Exige: guion + 10 fondos 16:9 + poses RGBA + WAV nuevo del tema
        |
        +-- (Falta algo) --> FAIL-FAST HALT (se detiene sin mezclar archivos)
        |
        +-- (Todo OK) --> [FASE 1: Guion] -> [FASE 2: Visuales y Avatar]
                                                  |
                         [FASE 4: MP4 + SHA-256 + Reproductor] <-- [FASE 3: WAV + SRT]
                                                  |
                         [FASE 5: Actualizar/Probar .ps1] -> [FASE 6: Git Commit + Push/Sync]
```

### Especificación Estricta de Fases:

1. **FASE 0 (Pre-flight & Bloqueo de Residuos):**
   - Audita físicamente el directorio `G:\My Drive\Guiahoy_Produccion\YYYY-MM-DD\`.
   - Bloquea explícitamente pistas y módulos anteriores (`Guiahoy_MASTER_48k_menos14LUFS.wav`, Make, MIT, RAG 768D).
   - Exige los 4 insumos obligatorios del tema:
     1. Guion específico en `.md`.
     2. 10 fondos dedicados `16:9` (`bg_01.jpg` a `bg_10.jpg`).
     3. Poses de avatar transparente en `G:\My Drive\Avatar Guillermo - transparencias\`.
     4. Pista de audio `.wav` exclusiva en `02_voz_guiahoy\` con duración $> 0\text{ s}$ validada con `ffprobe`.
   - **FAIL-FAST:** Si falta cualquiera de estos 4 insumos, el DAG se DETIENE INMEDIATAMENTE con código de salida 1 y mensaje explícito. Queda estrictamente prohibido avanzar a las fases siguientes o inventar archivos puente.

2. **FASE 1 (Guion Temático):**
   - Valida la existencia de los 10 bloques estructurados y la ausencia de contaminación conceptual (drift).

3. **FASE 2 (Visuales y Avatar):**
   - Valida la resolución 1920x1080 de los 10 fondos y la disponibilidad de las poses RGBA con recorte limpio sin caja rectangular.

4. **FASE 3 (Audio y Subtítulos .SRT):**
   - Mide la duración exacta del audio con `ffprobe` y calcula la escala proporcional de tiempo para los 10 bloques.
   - Genera el `.srt` exclusivo a partir del audio y guion validados.

5. **FASE 4 (Ensamblaje, SHA-256 y Reproductor):**
   - Genera el video `.mp4` bajo la nomenclatura estricta del proyecto.
   - Computa el hash SHA-256 inmutable y genera el manifiesto JSON.
   - Actualiza el reproductor interactivo embebido (`RULE_AUTO_LAUNCH_01`).

6. **FASE 5 (Actualización y Pruebas .ps1):**
   - Actualiza el script PowerShell canónico y ejecuta la matriz de verificación reportando tabla PASS/FAIL.

7. **FASE 6 (Cierre Git Obligatorio):**
   - Ejecuta `git status`, `git add`, `git commit` y `git push origin main` para garantizar sincronización y trazabilidad total en el repositorio remoto.
