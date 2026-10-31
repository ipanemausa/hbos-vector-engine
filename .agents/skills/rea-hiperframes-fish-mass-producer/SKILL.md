---
name: rea-hiperframes-fish-mass-producer
description: Skill empaquetada de producción masiva (1 a 15+ videos consistentes) que integra Ingeniería Inversa visual (REA con gallery-dl/yt-dlp + contact sheets), Motion Graphics vectoriales (Hiperframes + Higgsfield / Nano Banana MCP), API vocal Fish Audio (modelo Drama 3 con clon canónico Guiahoy a 109.2 Hz y -14 LUFS sin afftdn), composición en 3 planos (M-COMPOSICION-01), telemetría smoothstep_c1 + autozoom 1.35x + 7 gemas canónicas con láser (R-LASER-01) y alineación fonética CTC cada 20 ms.
---

# REA + Hiperframes + Fish Audio (Drama 3) Mass Video Producer Skill

Esta skill empaquetada en scope local ejecuta el **DAG Extendido Zero-Drift** del ecosistema **HBOS Qdrant Engine (`G:\My Drive\HBOS_Qdrant_Engine`)** para producir lotes de **1 a 15+ videos consistentes** sin editores tradicionales y con **0 MB de peso en el disco local del PC**.

## Arquitectura de Nodos Sellados

1. **Nodo 1 — Factorización Acústica & API Vocal (`Fish Audio / Drama 3`):**
   - **Clon Oficial:** `Guiahoy` (unido, referencia `Guiahoy_CLONE_REF_90s_48k.wav` = 60s Pista #3 + 30s Pista #2, $f_0 = 109.2\text{ Hz}$).
   - **Cadena EQ Estricta:** `highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,afade=t=in:st=0:d=0.05,loudnorm=I=-14:TP=-1.5:LRA=11` (**prohibido `afftdn`**).
   - **Conector Fish Audio (`Drama 3`):** Inyección de etiquetas de expresión por lote según la Matriz Emocional de 5 Modos (`IMPACTO_HOOK`, `INGENIERIA_PRECISA`, `ASOMBRO_DEMO_EN_VIVO`, `CALIDEZ_PERSONAJES`, `CIERRE_INSPIRADOR`).
2. **Nodo 2 — Ingeniería Inversa (`REA`) & Motion Graphics (`Hiperframes`):**
   - **Ingesta REA:** Descarga de referencias virales (`Pinterest` / `Reels` / `TikTok`) mediante `gallery-dl` y `yt-dlp`, generando automáticamente *contact sheets* de tipografías, keyframes y curvas de ritmo.
   - **Motor Hiperframes + MCP (`Higgsfield` / `Nano Banana`):** Renderizado declarativo de capas vectoriales y animaciones tipográficas dinámicas.
   - **Regla `M-COMPOSICION-01` (Efecto JH en 3 Planos):** Eliminación total de cajas rectangulares pegadas; integración directa de poses RGBA (`avatar-pose-t-*.png`) con *rim light* cian/dorado, sombra de contacto a piso y respiración `M-IDLE-01`.
3. **Nodo 3 — Telemetría de Interacción & Sistema de 7 Gemas (`R-LASER-01`):**
   - Polinomio `smoothstep_c1` ($6x^5 - 15x^4 + 10x^3$), autozoom `1.35x` en el punto de clic, anti-oclusión automática (`Derecha <-> Izquierda`) y puntero láser dual disparado por `Diamantino`, `Rubin`, `Zafir`, `Esmeralda`, `Amatista`, `Citrilo` y `Grafito`.
4. **Nodo 4 — Alineación Fonética (`20 ms`) & SFX (`clicks/wash`):**
   - `F5-TTS-Spanish` + `Wav2Vec2-Large-XLSR-53-Spanish` (`CTC Forced Alignment` cada `20 ms`), mapa `sync_map.json` con triggers de efectos (`ui_click`, `whoosh_transition`, `ambient_wash`) y subtítulos `.ass` palabra por palabra a `-14 LUFS`.
5. **Nodo 5 & Debug — Zero-Drift & Bóveda Google Drive (`03_MEDIA_VAULT_FINAL`):**
   - Verificación SHA-256 y registro versionado append-only en Qdrant Cloud (`registro_ecosistema: true`).
6. **Regla Dura `RULE_AUTO_LAUNCH_01` (Auto-Preview & Instant File Launch Post-Render):**
   - Todo activo multimedia generado (`.mp4`, `.wav`, `.png`, `.ass`, `.md`) dispara automáticamente `os.startfile(str(vault_path))` desde `G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\...` más reproductor embebido `<agent-embed>` en el chat. Prohibido dejar archivos huérfanos sin previsualización inmediata.

## Ejecución
```powershell
python scripts/execute_extended_dag_rea_hiperframes_fish.py
```

