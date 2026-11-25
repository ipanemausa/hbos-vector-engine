# INFORME DE AUDITORÍA REAL DE ACTIVOS: FONDOS, VOZ GUIAHOY Y AVATAR ANIMADO
**Fecha:** 2026-11-25 · **Entorno:** `G:\My Drive` & `C:\Users\ipane\hbos-deploy\hbos-vector-engine`  
**Gobernanza:** `HBOS_PRODUCTION_DAG_01` (Actualizada con Prohibiciones A, B y C)  

---

## 1. Localización Exacta de las 10 Imágenes Futuristas Originales (Pre-Sobrescritura)

Antes de que el script `generar_fondos_equipo_agentes.py` sobrescribiera la carpeta `G:\My Drive\Guiahoy_Produccion\2026-11-25\fondos_16x9\` con fondos con marcos y cajas de texto a las 10:15:00 del 2026-11-25, los 10 fondos originales 16:9 limpios (generados a las 09:14:18) fueron respaldados intactos en:

* **Ruta de Respaldo Canónico Local (Intacto):**
  `C:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\studio_vivo_final\mit_10min_stage\`
  - `bg_01.jpg` (241,421 bytes · SHA-256 corto: `bf9244837d01`)
  - `bg_02.jpg` (246,757 bytes · SHA-256 corto: `58ce79788096`)
  - `bg_03.jpg` (243,171 bytes · SHA-256 corto: `ac4a49839634`)
  - `bg_04.jpg` (249,389 bytes · SHA-256 corto: `14b234a6a3e9`)
  - `bg_05.jpg` (247,444 bytes · SHA-256 corto: `87ed62c71caa`)
  - `bg_06.jpg` (247,482 bytes · SHA-256 corto: `6110ba36dcda`)
  - `bg_07.jpg` (249,040 bytes · SHA-256 corto: `abbdf3c6b654`)
  - `bg_08.jpg` (244,927 bytes · SHA-256 corto: `d88d5b97d8aa`)
  - `bg_09.jpg` (245,841 bytes · SHA-256 corto: `a40526f2a20b`)
  - `bg_10.jpg` (244,045 bytes · SHA-256 corto: `592bc7817013`)

* **Paneles y Fondos Dinámicos Adicionales en Google Drive:**
  - `G:\My Drive\Guiahoy_Produccion\2026-11-24\panels\panel_01.png` a `panel_04.png` (Paneles futuristas 16:9 limpios).
  - `G:\My Drive\openclaw-operativo-2026-backup\runtime\productions\2026-08-24_guillermo_deepmind_full_bg_master\frames_hd\` (5,056 fotogramas HD de secuencias de video en movimiento).
  - `G:\My Drive\openclaw-operativo-2026-backup\runtime\productions\2026-08-24_deepmind_cinematic_full_bg\frames_hd\` (4,645 fotogramas HD cinemáticos).

---

## 2. Modelo, Archivos de Referencia y Pipeline de Clonación de Voz Masculina de Guía Hoy

La voz oficial de Guía Hoy es exclusivamente la voz masculina de **Guillermo Alonso Hoyos** ($f_0 \approx 109.2\text{ Hz}$, acento colombiano `es-CO` natural y cálido). Queda prohibido cualquier motor TTS genérico femenino o sintético no clonado.

* **Archivos Maestros de Referencia Acústica (Google Drive & Vault):**
  1. `G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_CLONE_REF_90s_48k.wav` (8.24 MB, 89.95s, 48kHz mono, SHA-256: `aad778f64acedd246bb6a1a068ec406fa34d30ba3dca3c2b9873715212023be8`). **(Referencia Canónica para ICL/Fish Audio/RVC)**.
  2. `G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_MASTER_48k_menos14LUFS.wav` (41.73 MB, 455.79s, 48kHz mono, -14.0 LUFS EBU R128).
  3. `G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_ICL_REF_30s_24k.wav` (1.37 MB, 30.0s, 24kHz, referencia rápida In-Context Learning).
  4. `G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\Guiahoy_CLONE_REF_90s_48k.wav` (Copia espejo inmutable en la Bóveda Final).
  5. `G:\My Drive\VozPropia\referencia.wav` (468 KB, muestra original aislada).

* **Manifiesto Oficial de Biometría Acústica:**
  - `G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_voice_clone_manifest.json`
  - Guardarraíles verificados:
    - Fundamental media: $f_0 = 109.2\text{ Hz}$ (rango $p_5 - p_{95} = [81.8 - 132.9]\text{ Hz}$)
    - Centroid espectral: $1755\text{ Hz}$
    - Relación armónico-ruido: $HNR = 2.3\text{ dB}$
    - Cadena de masterización obligatoria: `highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.5:LRA=11` (sin `afftdn`).

* **Pipelines de Clonación de Voz Masculina Disponibles en el Entorno:**
  1. **Fish Audio (Drama 3):**
     - Script ejecutor: `c:\Users\ipane\hbos-deploy\hbos-vector-engine\scripts\execute_extended_dag_rea_hiperframes_fish.py`
     - Configuración: `fish_audio_model: "drama-3"`, `voice_clone_id: "Guiahoy"`.
     - Tags de expresión: `(excited, authoritative hook)`, `(precise, analytical, studio chest)`, `(warm, friendly, expressive)`, `(inspiring, confident conclusion)`.
  2. **F5-TTS / Wav2Vec2 CTC Forced Alignment (Local / Deploy):**
     - Muestras clonadas activas:
       - `c:\Users\ipane\hbos-deploy\production_media\guillermo_voice_cloned_f5.wav`
       - `c:\Users\ipane\hbos-deploy\production_media\guillermo_voice_fm_48k.wav`
       - `c:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\assets\guillermo_voice_cloned_f5.wav`
     - Alineación fonética: `F5-TTS-Spanish` + `Wav2Vec2-Large-XLSR-53-Spanish` (resolución temporal de 20 ms).

---

## 3. Clips de Video Animados del Avatar de Guillermo y Nodos de Lip-Sync

Se prohíbe el uso de imágenes PNG estáticas congeladas sin movimiento ni sincronización labial.

* **Biblioteca Canónica de 15 Clips de Movimiento (Google Drive):**
  - Directorio en Drive: `G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library\`
  - Manifiesto: `canonical_15_avatar_clips_manifest.json` (ID: `HBOS_CANONICAL_AVATAR_MASCOT_15_CLIPS_V1`).
  - Clips listos para composición:
    1. `AVM_01_HOOK_OPENING.mp4` (8.0s · Guillermo + Diamantino · Hook y activación HUD)
    2. `AVM_02_EXPLAIN_CONCEPT.mp4` (8.0s · Guillermo Avatar · Cadencia técnica de manos)
    3. `AVM_03_POINT_SCREEN_LEFT.mp4` (8.0s · Guillermo + Rubí · Señalando a pantalla izquierda)
    4. `AVM_04_POINT_SCREEN_RIGHT.mp4` (8.0s · Guillermo + Esmeralda · Señalando a pantalla derecha)
    5. `AVM_05_DEEP_ARCHITECTURE.mp4` (8.0s · Guillermo + Zafiro · Postura analítica profunda)
    6. `AVM_06_DATA_EMPHASIS.mp4` (8.0s · Guillermo + Amatista · Énfasis en tarjeta métrica)
    7. `AVM_07_CODE_WALKTHROUGH.mp4` (8.0s · Guillermo + Topacio · Inspección activa de código)
    8. `AVM_08_TRANSITION_PIVOT.mp4` (8.0s · Guillermo + Turquesa · Pivote de transición visual)
    9. `AVM_09_MASCOT_SPOTLIGHT_A.mp4` (8.0s · 7 Gemas Mascota ensamble)
    10. `AVM_10_BENCHMARK_PROOF.mp4` (8.0s · Guillermo + Diamantino · Presentación de benchmark)
    11. `AVM_11_CLOUD_TOPOLOGY.mp4` (8.0s · Guillermo · Entrega ejecutiva de alta autoridad)
    12. `AVM_12_WARNING_GUARDRAIL.mp4` (8.0s · Guillermo + Rubí · Postura de seguridad y alerta)
    13. `AVM_13_BUBBLE_CORNER_IDLE.mp4` (8.0s · Guillermo + Diamantino · Asentimiento en burbuja)
    14. `AVM_14_SYNTHESIS_SUMMARY.mp4` (8.0s · Guillermo + Zafiro · Resumen y síntesis ejecutiva)
    15. `AVM_15_CLOSING_SIGNATURE.mp4` (8.0s · Guillermo + 7 Gemas · Cierre canónico GuíaHoy)

* **Carretes y Pruebas Maestras de Movimiento Continuo:**
  - `c:\Users\ipane\hbos-deploy\video-piloto\reel-mudo-movimientos-avatar-mascotas.mp4` (232.9s master reel, 1920x1080 @ 30fps).
  - `c:\Users\ipane\hbos-deploy\production_media\hbos_avatar_animated_test.mp4`
  - `c:\Users\ipane\hbos-deploy\production_media\HBOS_VIRAL_WAN22_REEL_1080P.mp4`
  - `G:\My Drive\avatar-prueba-movimiento.mp4`
  - `G:\My Drive\Guiahoy_Produccion\2026-11-23\guiahoy_con_avatar_20261123.mp4`

* **Activos con Lip-Sync Transparente ya Renderizados:**
  - `c:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\renders\guiahoy_alianzas_eficiencia_china_cadenas_2026_11_23_20261123_144317\03_avatar_guillermo_3d\avatar_guillermo_transparente_lipsync.mov`
  - `c:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\renders\guiahoy_alianzas_eficiencia_china_cadenas_2026_11_23_20261123_144351\03_avatar_guillermo_3d\avatar_guillermo_transparente_lipsync.mov`

* **Nodos y Enrutadores de Lip-Sync Disponibles en el Entorno:**
  1. **Enrutador Agéntico Local/Nube:**
     - `execute_marketing_expansion_dag_op228.py` implementa la arquitectura de sincronización facial multi-proveedor (**SadTalker**, **LivePortrait**, **Wan 2.1**, **D-ID**).
  2. **Infraestructura Nube Serverless (Runpod):**
     - Integración lista mediante las skills `flash` y `runpod-mcp` (GPU Serverless Endpoints para inferencia acelerada de **MuseTalk**, **EchoMimic** y **SadTalker** sin sobrecargar la máquina local).

---

## 4. Estado de Cumplimiento Normativo

La regla dura canónica `.agents\rules\HBOS_PRODUCTION_DAG_01.md` ha sido actualizada para incorporar las 3 Prohibiciones Terminantes (A, B y C) en la Fase 0 y en todos los gates de producción.
