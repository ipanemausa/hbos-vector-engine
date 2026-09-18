# GUÍA MAESTRA DE FORMATOS RESPONSIVE Y MULTI-PLATAFORMA
### Ecosistema: HBOS-Diamantino · Trazabilidad: `operation_id = 62`
### Módulo: Distribución Social Omnicanal y Transcodificación Automática

---

## 1. OBJETIVO Y ARQUITECTURA DEL MÓDULO

El pipeline de distribución de HBOS-Diamantino genera automáticamente versiones derivadas optimizadas para cada red social y dispositivo a partir del Master Oficial 1080p (`05_Master/epXX_master_vX.mp4`).

Cada versión aplica un algoritmo de recorte y recomposición inteligente con fondo ambiental desenfocado (`boxblur=20:5`, overlay centrado) para preservar la integridad de los avatares 3D minerales sin cortes abruptos ni distorsión de relación de aspecto.

---

## 2. MATRIZ DE FORMATOS Y PLATAFORMAS DESTINO

| Formato | Resolución | Relación | Plataformas Destino | Bitrate Sugerido | Audio Códec |
| :---: | :---: | :---: | :--- | :---: | :---: |
| **16:9** | $1920 	imes 1080$ | Landscape | YouTube, LinkedIn, X, Web Desktop | CRF 23 (~8.5 Mbps) | AAC 128 kbps · 44.1 kHz |
| **9:16** | $1080 	imes 1920$ | Vertical | TikTok, Instagram Reels, YouTube Shorts | CRF 23 (~6.5 Mbps) | AAC 128 kbps · 44.1 kHz |
| **1:1** | $1080 	imes 1080$ | Square | Instagram Feed, Facebook Feed | CRF 23 (~5.0 Mbps) | AAC 128 kbps · 44.1 kHz |
| **4:5** | $1080 	imes 1350$ | Portrait | Instagram Timeline Portrait | CRF 23 (~5.5 Mbps) | AAC 128 kbps · 44.1 kHz |

---

## 3. ESPECIFICACIONES DE LOS FILTROS FFMPEG

### 3.1. Recomposición Vertical Cinemática (9:16, 1:1, 4:5):
Para evitar bandas negras vacías en dispositivos móviles, se utiliza un filtro de doble flujo en FFmpeg:
1. **Flujo de Fondo (`bg`):** El video original se escala al tamaño destino forzando el llenado total, se recorta al centro y se aplica un desenfoque de caja (`boxblur=20:5`) con atenuación de brillo (`eq=brightness=-0.15`).
2. **Flujo Principal (`fg`):** El video original se escala respetando su proporción nativa 16:9.
3. **Composición (`overlay`):** Se superpone el video nítido centrado sobre el fondo ambiental.

```bash
# Ejemplo para 9:16 (1080x1920):
ffmpeg -i ep02_master_v3.mp4 \
  -filter_complex "[0:v]split=2[bg_in][fg_in]; [bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5,eq=brightness=-0.15[bg]; [fg_in]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; [bg][fg]overlay=(W-w)/2:(H-h)/2[v]" \
  -map "[v]" -map 0:a:0 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -movflags +faststart \
  ep02_master_v3_9x16.mp4
```

---

## 4. ASSETS ADICIONALES GENERADOS

1. **GIF Preview Cinemático (10s):**
   - Ruta: `06_Publicado/formatos/ep02_preview.gif`
   - Generado con paleta de 256 colores optimizada mediante filtro `palettegen` y `paletteuse` a 15 fps (480px ancho).
2. **HTML5 Embed Responsive:**
   - Ruta: `06_Publicado/embed/ep02_embed.html`
   - Interfaz web interactiva con cambio dinámico de formato sin perder el punto de reproducción (`currentTime`), glassmorphism, modo oscuro y metadatos técnicos integrados.

---

## 5. CÓMO AGREGAR NUEVOS FORMATOS

Para agregar un formato nuevo (ej. 21:9 Ultrawide o 3:4 Tablet):
1. Abrir `convert_to_formats.py`.
2. Agregar un nuevo diccionario a la lista `FORMATS` con `width`, `height`, `name` y el `filter_complex` correspondiente.
3. Ejecutar `python convert_to_formats.py`.
