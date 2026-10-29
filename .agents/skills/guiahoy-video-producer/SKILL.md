---
name: guiahoy-video-producer
description: Habilidad dedicada de edición y generación multimedia autónoma estilo GuíaHoy (subtitulado animado ASS de alta conversión, cortes dinámicos por detección de silencios -35dB, zoom automático inteligente Ken Burns para Reels 9:16 y horizontales 16:9, avatares 3D Presentador + Mascota, B-Roll y normalización estricta a -14 LUFS EBU R128).
---

# GuíaHoy Autonomous Video Production Skill (`guiahoy-video-producer`)

Esta Skill dota al ecosistema **HBOS-Vector-Engine** de producción audiovisual end-to-end totalmente autónoma para contenidos técnicos y ejecutivos de alta retención (estilo **GuíaHoy** / **Screen Studio**).

## Capacidades Principales
1. **Subtitulado Animado de Alta Conversión (ASS Word/Chunk Highlight):**
   - Renderizado nativo con resaltado dinámico en colores corporativos (`#00E5FF` cian eléctrico y `#FFB300` ámbar sobre `#0A0E17`), bordes de alto contraste y animación pop-in.
2. **Cortes Dinámicos por Detección de Silencios (`silenceremove` + Jump-Cuts):**
   - Eliminación automática de pausas muertas (`<-35dB` por `>0.25s`) y alternancia rítmica cada `< 4.0s` para maximizar la retención.
3. **Zoom Automático Inteligente y Adaptación Vertical (9:16 Reels / Shorts) & Horizontal (16:9):**
   - Seguimiento guiado estilo Screen/Tutorial Studio con curvas de zoom suaves y reencuadre inteligente para formato vertical `1080x1920` y master `1920x1080`.
4. **Avatares 3D Interactivos (Presentador Guillermo + Mascota Diamantino) & Clonación de Voz:**
   - Integración de pistas vocales de estudio (`48kHz`) con avatares compuestos en HUD interactivo.
5. **Masterización Estricta de Audio a `-14.0 LUFS` (EBU R128):**
   - Normalización de doble paso (`loudnorm=I=-14:TP=-1.5:LRA=11`) validada con `ffprobe` / `ffmpeg ebur128`.

## Invocación
```powershell
python -m studio.video.guiahoy_pipeline
```

