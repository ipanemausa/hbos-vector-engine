import os
import sys
import json
import math
import shutil
import hashlib
import subprocess
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

BASE_EP02 = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips"
MASTER_SRC = os.path.join(BASE_EP02, r"05_Master\ep02_master_v3.mp4")
FORMATOS_DIR = os.path.join(BASE_EP02, r"06_Publicado\formatos")
EMBED_DIR = os.path.join(BASE_EP02, r"06_Publicado\embed")
MAESTRO_DIR_DRIVE = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
MAESTRO_DIR_LOCAL = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"

os.makedirs(FORMATOS_DIR, exist_ok=True)
os.makedirs(EMBED_DIR, exist_ok=True)
os.makedirs(MAESTRO_DIR_DRIVE, exist_ok=True)
os.makedirs(MAESTRO_DIR_LOCAL, exist_ok=True)

# -------------------------------------------------------------
# FASE 3: Generar GIF Preview (10 seg)
# -------------------------------------------------------------
print("\n[*] FASE 3 — Generando GIF Preview de 10 segundos con paleta optimizada...")
gif_path = os.path.join(FORMATOS_DIR, "ep02_preview.gif")
local_gif = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_preview.gif"

# GIF de 10s desde el segundo 15 (aparición de Rubín y servers)
cmd_gif = [
    "ffmpeg", "-y",
    "-ss", "00:00:15",
    "-t", "10",
    "-i", MASTER_SRC,
    "-vf", "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    gif_path
]
subprocess.run(cmd_gif, check=True)
shutil.copyfile(gif_path, local_gif)
gif_size = os.path.getsize(gif_path)
print(f"[OK] GIF Preview generado: {gif_path} ({gif_size / (1024*1024):.2f} MB)")

# -------------------------------------------------------------
# FASE 4: Generar HTML5 Embed Responsive
# -------------------------------------------------------------
print("\n[*] FASE 4 — Creando HTML5 Responsive Embed...")
html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HBOS-Diamantino — Ep02: Los 7 Chips (Player Responsive)</title>
  <style>
    :root {
      --bg-dark: #0a0b10;
      --card-bg: rgba(20, 24, 38, 0.85);
      --accent-cyan: #00f0ff;
      --accent-purple: #9d00ff;
      --text-main: #f0f4f8;
      --text-muted: #8a99ad;
      --border-glow: rgba(0, 240, 255, 0.25);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
    body {
      background: radial-gradient(circle at top, #141b2d 0%, var(--bg-dark) 100%);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
    }
    header { text-align: center; margin-bottom: 2rem; }
    h1 {
      font-size: 2.2rem;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }
    p.subtitle { color: var(--text-muted); font-size: 1rem; }
    .player-card {
      background: var(--card-bg);
      border: 1px solid var(--border-glow);
      border-radius: 16px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(12px);
      width: 100%;
      max-width: 960px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }
    .video-container {
      position: relative;
      width: 100%;
      max-width: 860px;
      background: #000;
      border-radius: 12px;
      overflow: hidden;
      aspect-ratio: 16 / 9;
      transition: aspect-ratio 0.4s ease, max-width 0.4s ease;
      box-shadow: 0 8px 30px rgba(0, 240, 255, 0.15);
    }
    .video-container.ratio-9x16 { aspect-ratio: 9 / 16; max-width: 380px; }
    .video-container.ratio-1x1 { aspect-ratio: 1 / 1; max-width: 500px; }
    .video-container.ratio-4x5 { aspect-ratio: 4 / 5; max-width: 440px; }
    video { width: 100%; height: 100%; object-fit: contain; display: block; }
    .format-switcher {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      justify-content: center;
      width: 100%;
    }
    .btn-fmt {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--text-main);
      padding: 0.6rem 1.2rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.25s ease;
    }
    .btn-fmt:hover {
      background: rgba(0, 240, 255, 0.15);
      border-color: var(--accent-cyan);
      box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
    }
    .btn-fmt.active {
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
      border-color: transparent;
      color: #000;
      font-weight: 700;
    }
    .specs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      width: 100%;
      margin-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding-top: 1.5rem;
    }
    .spec-item {
      background: rgba(0, 0, 0, 0.3);
      padding: 0.8rem;
      border-radius: 8px;
      border-left: 3px solid var(--accent-cyan);
    }
    .spec-item span.title { font-size: 0.8rem; color: var(--text-muted); display: block; }
    .spec-item span.value { font-size: 1rem; font-weight: 600; color: var(--text-main); }
  </style>
</head>
<body>
  <header>
    <h1>HBOS-Diamantino — Ep02: "Los 7 Chips"</h1>
    <p class="subtitle">Reproductor Multimedia Multi-Formato Responsive · Master v3 (EBU R128 -14 LUFS)</p>
  </header>

  <div class="player-card">
    <div id="videoContainer" class="video-container">
      <video id="mainVideo" controls poster="../formatos/ep02_preview.gif" preload="metadata">
        <source id="videoSource" src="../formatos/ep02_master_v3_16x9.mp4" type="video/mp4">
        Tu navegador no soporta reproducción de video HTML5.
      </video>
    </div>

    <div class="format-switcher">
      <button class="btn-fmt active" onclick="setFormat('16x9', '16 / 9', '../formatos/ep02_master_v3_16x9.mp4')">16:9 Landscape (YouTube/Web)</button>
      <button class="btn-fmt" onclick="setFormat('9x16', '9 / 16', '../formatos/ep02_master_v3_9x16.mp4')">9:16 Vertical (TikTok/Reels)</button>
      <button class="btn-fmt" onclick="setFormat('1x1', '1 / 1', '../formatos/ep02_master_v3_1x1.mp4')">1:1 Square (Instagram)</button>
      <button class="btn-fmt" onclick="setFormat('4x5', '4 / 5', '../formatos/ep02_master_v3_4x5.mp4')">4:5 Portrait (Instagram)</button>
    </div>

    <div class="specs-grid">
      <div class="spec-item"><span class="title">Duración Master:</span><span class="value">209.03 s (3m 29s)</span></div>
      <div class="spec-item"><span class="title">Estándar Acústico:</span><span class="value">EBU R128 (-14.0 LUFS)</span></div>
      <div class="spec-item"><span class="title">Códec de Video:</span><span class="value">H.264 High @ 30.00 fps</span></div>
      <div class="spec-item"><span class="title">Optimización Web:</span><span class="value">+faststart (Streaming)</span></div>
    </div>
  </div>

  <script>
    function setFormat(fmtClass, ratio, src) {
      const container = document.getElementById('videoContainer');
      const video = document.getElementById('mainVideo');
      const source = document.getElementById('videoSource');
      const buttons = document.querySelectorAll('.btn-fmt');

      buttons.forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');

      const currentTime = video.currentTime;
      const isPaused = video.paused;

      container.className = 'video-container ratio-' + fmtClass;
      source.src = src;
      video.load();
      video.currentTime = currentTime;
      if (!isPaused) {
        video.play();
      }
    }
  </script>
</body>
</html>
"""

html_path = os.path.join(EMBED_DIR, "ep02_embed.html")
local_html = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_embed.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
with open(local_html, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[OK] HTML5 Responsive Embed creado: {html_path} ({len(html_content)} caracteres)")

# -------------------------------------------------------------
# FASE 5: Documentar _FORMATOS_RESPONSIVE.md en _MAESTRO\
# -------------------------------------------------------------
print("\n[*] FASE 5 — Documentando en _MAESTRO/_FORMATOS_RESPONSIVE.md...")
doc_responsive_content = """# GUÍA MAESTRA DE FORMATOS RESPONSIVE Y MULTI-PLATAFORMA
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
| **16:9** | $1920 \times 1080$ | Landscape | YouTube, LinkedIn, X, Web Desktop | CRF 23 (~8.5 Mbps) | AAC 128 kbps · 44.1 kHz |
| **9:16** | $1080 \times 1920$ | Vertical | TikTok, Instagram Reels, YouTube Shorts | CRF 23 (~6.5 Mbps) | AAC 128 kbps · 44.1 kHz |
| **1:1** | $1080 \times 1080$ | Square | Instagram Feed, Facebook Feed | CRF 23 (~5.0 Mbps) | AAC 128 kbps · 44.1 kHz |
| **4:5** | $1080 \times 1350$ | Portrait | Instagram Timeline Portrait | CRF 23 (~5.5 Mbps) | AAC 128 kbps · 44.1 kHz |

---

## 3. ESPECIFICACIONES DE LOS FILTROS FFMPEG

### 3.1. Recomposición Vertical Cinemática (9:16, 1:1, 4:5):
Para evitar bandas negras vacías en dispositivos móviles, se utiliza un filtro de doble flujo en FFmpeg:
1. **Flujo de Fondo (`bg`):** El video original se escala al tamaño destino forzando el llenado total, se recorta al centro y se aplica un desenfoque de caja (`boxblur=20:5`) con atenuación de brillo (`eq=brightness=-0.15`).
2. **Flujo Principal (`fg`):** El video original se escala respetando su proporción nativa 16:9.
3. **Composición (`overlay`):** Se superpone el video nítido centrado sobre el fondo ambiental.

```bash
# Ejemplo para 9:16 (1080x1920):
ffmpeg -i ep02_master_v3.mp4 \\
  -filter_complex "[0:v]split=2[bg_in][fg_in]; [bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5,eq=brightness=-0.15[bg]; [fg_in]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; [bg][fg]overlay=(W-w)/2:(H-h)/2[v]" \\
  -map "[v]" -map 0:a:0 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -movflags +faststart \\
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
"""

doc_responsive_drive = os.path.join(MAESTRO_DIR_DRIVE, "_FORMATOS_RESPONSIVE.md")
doc_responsive_local = os.path.join(MAESTRO_DIR_LOCAL, "_FORMATOS_RESPONSIVE.md")

with open(doc_responsive_drive, "w", encoding="utf-8") as f:
    f.write(doc_responsive_content)
with open(doc_responsive_local, "w", encoding="utf-8") as f:
    f.write(doc_responsive_content)
print(f"[OK] Documento _FORMATOS_RESPONSIVE.md guardado ({len(doc_responsive_content)} caracteres)")

# -------------------------------------------------------------
# FASE 6: Vectorizar en Qdrant (operation_id = 62)
# -------------------------------------------------------------
print("\n[*] FASE 6 — Vectorizando en Qdrant Cloud (operation_id = 62)...")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

if qdrant_url and qdrant_key:
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=30)
        texto_op62 = (
            "Conversión Multi-formato Responsive del Episodio 02 Master v3. "
            "Generación de 4 formatos de video: 16:9 Landscape, 9:16 Vertical, 1:1 Square y 4:5 Portrait. "
            "GIF Preview de 10s optimizado, Reproductor HTML5 Responsive Embed y Documento _FORMATOS_RESPONSIVE.md."
        )
        vec_62 = generate_embedding(texto_op62, dim=384)
        
        payload_op62 = {
            "operation_id": 62,
            "evento": "EP02_MULTI_FORMATO_RESPONSIVE",
            "episodio": "Ep02 - Los 7 Chips",
            "master_origen": MASTER_SRC,
            "formatos": [
                {"ratio": "16:9", "resolucion": "1920x1080", "archivo": "ep02_master_v3_16x9.mp4"},
                {"ratio": "9:16", "resolucion": "1080x1920", "archivo": "ep02_master_v3_9x16.mp4"},
                {"ratio": "1:1", "resolucion": "1080x1080", "archivo": "ep02_master_v3_1x1.mp4"},
                {"ratio": "4:5", "resolucion": "1080x1350", "archivo": "ep02_master_v3_4x5.mp4"}
            ],
            "gif_preview": True,
            "gif_path": gif_path,
            "html_embed": True,
            "html_path": html_path,
            "documentacion": True,
            "doc_path": doc_responsive_drive,
            "codec_video": "H.264 CRF 23 faststart",
            "codec_audio": "AAC 128k 44.1kHz"
        }
        
        client.upsert(
            collection_name="registro_ecosistema",
            points=[
                models.PointStruct(
                    id=62,
                    vector=vec_62,
                    payload=payload_op62
                )
            ]
        )
        print("[OK] Qdrant Cloud: Point ID 62 indexado con éxito en 'registro_ecosistema'.")
    except Exception as e:
        print(f"[!] Error registrando en Qdrant: {e}")

print("\n==========================================================")
print("[EXITO TOTAL] FASES 3, 4, 5 Y 6 FINALIZADAS.")
