"""
HBOS CREATIVE CLOUD + LOCAL VIDEO GENERATOR
- Guiahoy Cloned Voice (48 kHz / -14 LUFS, NO afftdn)
- Interactive App + Graphics + Analytics Layers (Pillow generated 1080p HUD)
- Avatar RGBA without rectangular boxes (M-COMPOSICION-01, M-IDLE-01, Ground Shadow, Anti-Occlusion)
- SIN 7 GEMAS (R-LASER-01 disabled)
- Non-destructive export to G:\\My Drive\\HBOS_Qdrant_Engine\\03_MEDIA_VAULT_FINAL\\
"""

import os, sys, json, hashlib, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

# 1. Definición de rutas
AUDIO_SRC = r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_ELEVENLABS_CLON_VERIFICADO_menos14LUFS.wav"
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
OUT_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-24"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"
ART_DIR = r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(VAULT_DIR, exist_ok=True)

OUT_NAME = "guiahoy_nube_creativo_analitica_20261124_1525.mp4"
LOCAL_DIR = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\studio_vivo_final"
os.makedirs(LOCAL_DIR, exist_ok=True)
LOCAL_OUT = os.path.join(LOCAL_DIR, OUT_NAME)
OUT_PATH = os.path.join(OUT_DIR, OUT_NAME)
VAULT_PATH = os.path.join(VAULT_DIR, OUT_NAME)
ART_PATH = os.path.join(ART_DIR, OUT_NAME)

POSES = {
    "P1": os.path.join(AVATAR_DIR, "avatar-pose-t-wave-palm-front.png"),
    "P2": os.path.join(AVATAR_DIR, "avatar-pose-t-chin-stroke-R.png"),
    "P3": os.path.join(AVATAR_DIR, "avatar-pose-t-double-point.png"),
    "P4": os.path.join(AVATAR_DIR, "avatar-pose-t-both-thumbs-up.png")
}

# 2. Generar Paneles de la App Interactiva y Capas Analíticas (1920x1080 RGBA)
PANELS_DIR = os.path.join(OUT_DIR, "panels")
os.makedirs(PANELS_DIR, exist_ok=True)

def get_font(size, bold=False):
    names = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except:
            pass
    return ImageFont.load_default()

font_title = get_font(32, bold=True)
font_subtitle = get_font(20, bold=False)
font_card_h = get_font(22, bold=True)
font_card_t = get_font(16, bold=False)
font_kpi_big = get_font(44, bold=True)
font_kpi_sub = get_font(14, bold=False)
font_badge = get_font(13, bold=True)
font_subtitles = get_font(24, bold=True)

def base_hud(view_num, view_title):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Header de la App
    d.rounded_rectangle([60, 50, 1160, 120], radius=14, fill=(15, 23, 42, 230), outline=(56, 189, 248, 120), width=1)
    # Status dot
    d.ellipse([85, 78, 97, 90], fill=(52, 211, 153, 255))
    d.text((110, 68), "HBOS OPERATING SYSTEM", fill=(255, 255, 255), font=font_title)
    
    # Badge vista
    d.rounded_rectangle([860, 68, 1135, 102], radius=8, fill=(56, 189, 248, 40), outline=(56, 189, 248, 180), width=1)
    d.text((875, 76), f"VISTA {view_num} · {view_title}", fill=(56, 189, 248), font=font_badge)
    
    # Marco de la App Interactiva
    d.rounded_rectangle([60, 140, 1160, 840], radius=18, fill=(11, 15, 25, 240), outline=(30, 41, 59, 200), width=2)
    
    return img, d

# Panel 1: Automatización Multi-Redes (0.0s - 6.5s)
p1_img, d1 = base_hud(1, "MULTI-PLATFORM DISPATCH")
d1.text((95, 175), "Módulo de Despliegue Autónomo de Contenido", fill=(248, 250, 252), font=font_card_h)
d1.text((95, 210), "Orquestación centralizada sin programar · Distribución instantánea", fill=(148, 163, 184), font=font_card_t)

# Tarjetas de Redes Sociales
networks = [
    ("Instagram Reels", "100% Sincronizado", "9:16 Video + ASS"),
    ("YouTube Shorts", "Publicación Directa", "4K / 1080p Master"),
    ("TikTok", "Cero Fricción", "Viral Audio Hook"),
    ("LinkedIn Video", "Formato Ejecutivo", "Transparencia B2B")
]
for i, (net, st, detail) in enumerate(networks):
    col = i % 2
    row = i // 2
    x0 = 95 + col * 520
    y0 = 260 + row * 130
    x1 = x0 + 490
    y1 = y0 + 110
    d1.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(19, 27, 46, 255), outline=(56, 189, 248, 60), width=1)
    d1.ellipse([x0 + 20, y0 + 24, x0 + 36, y0 + 40], fill=(56, 189, 248, 255))
    d1.text((x0 + 50, y0 + 20), net, fill=(255, 255, 255), font=font_card_h)
    d1.text((x0 + 50, y0 + 52), st, fill=(52, 211, 153), font=font_card_t)
    d1.text((x0 + 50, y0 + 74), detail, fill=(148, 163, 184), font=font_badge)

# KPI Card Grande
d1.rounded_rectangle([95, 540, 1125, 700], radius=14, fill=(15, 23, 42, 255), outline=(52, 211, 153, 90), width=1)
d1.text((130, 565), "COBERTURA TOTAL DE AUDIENCIA", fill=(148, 163, 184), font=font_card_t)
d1.text((130, 600), "100% AUTOMATIZADO · 0 LÍNEAS DE CÓDIGO", fill=(52, 211, 153), font=font_kpi_big)
d1.text((130, 660), "Costo de ejecución por video: $0.00 USD (Arquitectura Local/Drive)", fill=(203, 213, 225), font=font_kpi_sub)

# Subtítulo de voz
d1.rounded_rectangle([95, 730, 1125, 810], radius=12, fill=(2, 6, 23, 230), outline=(56, 189, 248, 100), width=1)
d1.text((120, 752), "\"Y lo publica todo sola, en todas tus redes sociales...\"", fill=(255, 255, 255), font=font_subtitles)

p1_path = os.path.join(PANELS_DIR, "panel_01.png")
p1_img.save(p1_path)

# Panel 2: Analítica de Rendimiento & KPIs (6.5s - 13.0s)
p2_img, d2 = base_hud(2, "EFFICIENCY BENCHMARKS")
d2.text((95, 175), "Métricas de Rendimiento y Ahorro Operativo", fill=(248, 250, 252), font=font_card_h)
d2.text((95, 210), "Comparativa directa: Flujo Tradicional vs. Ecosistema HBOS", fill=(148, 163, 184), font=font_card_t)

# 3 KPIs Superiores
kpis = [
    ("+38.4%", "Margen Operativo", (52, 211, 153)),
    ("120 hrs", "Ahorradas / Mes", (56, 189, 248)),
    ("14.2 ms", "Latencia Qdrant 768d", (192, 132, 252))
]
for i, (val, lbl, c) in enumerate(kpis):
    x0 = 95 + i * 350
    y0 = 260
    d2.rounded_rectangle([x0, y0, x0 + 330, y0 + 130], radius=12, fill=(19, 27, 46, 255), outline=c, width=1)
    d2.text((x0 + 25, y0 + 20), val, fill=c, font=font_kpi_big)
    d2.text((x0 + 25, y0 + 85), lbl, fill=(203, 213, 225), font=font_card_t)

# Gráfico Comparativo
d2.rounded_rectangle([95, 420, 1125, 700], radius=14, fill=(15, 23, 42, 255), outline=(56, 189, 248, 60), width=1)
d2.text((125, 445), "TIEMPO REQUERIDO POR ENTREGA (MINUTOS)", fill=(148, 163, 184), font=font_card_t)
# Barra tradicional
d2.text((125, 490), "Edición Tradicional (Premiere / Manual)", fill=(226, 232, 240), font=font_badge)
d2.rounded_rectangle([125, 520, 950, 560], radius=8, fill=(244, 63, 94, 200))
d2.text((965, 528), "180 min", fill=(244, 63, 94), font=font_badge)
# Barra HBOS
d2.text((125, 580), "HBOS Autonomous Vector Pipeline", fill=(226, 232, 240), font=font_badge)
d2.rounded_rectangle([125, 610, 320, 650], radius=8, fill=(52, 211, 153, 240))
d2.text((335, 618), "2.5 min (-98.6%)", fill=(52, 211, 153), font=font_badge)

# Subtítulo de voz
d2.rounded_rectangle([95, 730, 1125, 810], radius=12, fill=(2, 6, 23, 230), outline=(56, 189, 248, 100), width=1)
d2.text((120, 752), "\"Sin programar, empezando gratis, decirme, míralo...\"", fill=(255, 255, 255), font=font_subtitles)

p2_path = os.path.join(PANELS_DIR, "panel_02.png")
p2_img.save(p2_path)

# Panel 3: Arquitectura DAG & Qdrant 768d (13.0s - 19.5s)
p3_img, d3 = base_hud(3, "VECTOR TOPOLOGY & NODES")
d3.text((95, 175), "Topología del Motor Vectorial Qdrant (768d)", fill=(248, 250, 252), font=font_card_h)
d3.text((95, 210), "Segregación estricta de 5 nodos con trazabilidad criptográfica SHA256", fill=(148, 163, 184), font=font_card_t)

# Diagrama de 3 Nodos Conectados
dag_nodes = [
    ("NODO 1: INGESTA REA", "Reverse-Engineering", "YouTube / Drive / Raw", (56, 189, 248)),
    ("NODO 2: QDRANT 768D", "Indexación Segregada", "Voz + Avatar + Video", (192, 132, 252)),
    ("NODO 3: RENDER E2E", "M-COMPOSICION-01", "1080p @ 30fps Master", (52, 211, 153))
]
for i, (title, sub, meta, col) in enumerate(dag_nodes):
    x0 = 95 + i * 350
    y0 = 260
    d3.rounded_rectangle([x0, y0, x0 + 330, y0 + 170], radius=14, fill=(19, 27, 46, 255), outline=col, width=2)
    d3.text((x0 + 20, y0 + 20), title, fill=col, font=font_card_h)
    d3.text((x0 + 20, y0 + 60), sub, fill=(255, 255, 255), font=font_card_t)
    d3.text((x0 + 20, y0 + 110), meta, fill=(148, 163, 184), font=font_badge)
    # Flecha conectora
    if i < 2:
        d3.line([x0 + 335, y0 + 85, x0 + 345, y0 + 85], fill=(56, 189, 248), width=3)

# Tabla de Certificación Técnica
d3.rounded_rectangle([95, 460, 1125, 700], radius=14, fill=(15, 23, 42, 255), outline=(56, 189, 248, 60), width=1)
d3.text((125, 485), "AUDITORÍA EN VIVO QDRANT (HTTP://LOCALHOST:6333)", fill=(148, 163, 184), font=font_badge)
rows = [
    ("canon_video_hbos_r768", "768d Cosine", "169 Pts", "ACTIVA"),
    ("hbos-voice-profiles_r768", "768d Cosine", "5 Pts", "ACTIVA (ID: 5ebd8c4f)"),
    ("registro_ecosistema_r768", "768d Cosine", "10 Pts", "VERIFICADO (IDs Deterministas)")
]
for r_i, (c_name, c_dim, c_pts, c_st) in enumerate(rows):
    ry = 525 + r_i * 50
    d3.text((125, ry), c_name, fill=(248, 250, 252), font=font_card_t)
    d3.text((500, ry), c_dim, fill=(56, 189, 248), font=font_card_t)
    d3.text((700, ry), c_pts, fill=(203, 213, 225), font=font_card_t)
    d3.text((880, ry), c_st, fill=(52, 211, 153), font=font_badge)

# Subtítulo de voz
d3.rounded_rectangle([95, 730, 1125, 810], radius=12, fill=(2, 6, 23, 230), outline=(56, 189, 248, 100), width=1)
d3.text((120, 752), "\"Esto se llama automatización con Make...\"", fill=(255, 255, 255), font=font_subtitles)

p3_path = os.path.join(PANELS_DIR, "panel_03.png")
p3_img.save(p3_path)

# Panel 4: Síntesis Ejecutiva & Aprobación (19.5s - 25.0s)
p4_img, d4 = base_hud(4, "SYSTEM SIGNATURE")
d4.text((95, 175), "Síntesis Ejecutiva & Veredicto de Operador", fill=(248, 250, 252), font=font_card_h)
d4.text((95, 210), "Cadena limpia: 100% Avatar Canónico + Voz Calibrada sin artefactos", fill=(148, 163, 184), font=font_card_t)

# Checklist de Conformidad
checklist = [
    ("[OK] Identidad Bloqueada", "Guillermo Alonso Hoyos · Camiseta HB.OS · Gafas · Pelo Gris", (52, 211, 153)),
    ("[OK] Master Vocal Calibrado", "48 kHz · -14.0 LUFS EBU R128 · Highpass 65Hz · Cero afftdn", (52, 211, 153)),
    ("[OK] Protocolo M-COMPOSICION-01", "Cero cajas rectangulares · Sombra a piso · Oscilación M-IDLE-01", (52, 211, 153)),
    ("[OK] Cero 7 Gemas / Sin Láser", "R-LASER-01 Desactivado · Solo avatar transparente sincronizado", (52, 211, 153))
]
for i, (item_h, item_desc, col) in enumerate(checklist):
    y0 = 260 + i * 105
    d4.rounded_rectangle([95, y0, 1125, y0 + 90], radius=12, fill=(19, 27, 46, 255), outline=col, width=1)
    d4.text((125, y0 + 18), item_h, fill=col, font=font_card_h)
    d4.text((125, y0 + 52), item_desc, fill=(148, 163, 184), font=font_card_t)

# Subtítulo de voz
d4.rounded_rectangle([95, 730, 1125, 810], radius=12, fill=(2, 6, 23, 230), outline=(56, 189, 248, 100), width=1)
d4.text((120, 752), "\"Make es una herramienta, y la superinteligencia es el motor.\"", fill=(255, 255, 255), font=font_subtitles)

p4_path = os.path.join(PANELS_DIR, "panel_04.png")
p4_img.save(p4_path)

print("Paneles analíticos generados exitosamente en:", PANELS_DIR)

# 3. Construir comando ffmpeg maestro (1920x1080 @ 30fps, 25.0 segundos)
# - Input 0: Audio clonado verificado ElevenLabs / REA (25.0s)
# - Inputs 1-4: Paneles analíticos generados
# - Inputs 5-8: Poses del avatar RGBA
filter_complex = (
    # Fondo base de estudio tecnológico
    "color=c=#050812:s=1920x1080:r=30:d=25.0[bg];"
    # Sombra de piso suave elíptica bajo los pies del avatar (X=1260, Y=985)
    "color=c=black@0.58:s=350x75:r=30:d=25.0,format=rgba,boxblur=14:enable='between(t,0,25.0)'[shadow];"
    "[bg][shadow]overlay=1260:985[bg_shadow];"
    
    # Capas analíticas animadas en los dos tercios izquierdos
    # Panel 1: 0 - 6.5s
    "[bg_shadow][1:v]overlay=0:0:enable='between(t,0,6.5)'[v_hud1];"
    # Panel 2: 6.5 - 13.0s
    "[v_hud1][2:v]overlay=0:0:enable='between(t,6.5,13.0)'[v_hud2];"
    # Panel 3: 13.0 - 19.5s
    "[v_hud2][3:v]overlay=0:0:enable='between(t,13.0,19.5)'[v_hud3];"
    # Panel 4: 19.5 - 25.0s
    "[v_hud3][4:v]overlay=0:0:enable='between(t,19.5,25.0)'[v_hud_all];"
    
    # Escalar poses avatar a 920px de alto preservando transparencia
    "[5:v]scale=-1:920,format=rgba[p1];"
    "[6:v]scale=-1:920,format=rgba[p2];"
    "[7:v]scale=-1:920,format=rgba[p3];"
    "[8:v]scale=-1:920,format=rgba[p4];"
    
    # Overlay del avatar con M-IDLE-01 respiración (150 + 5*sin(2*PI*t/3.2)) y anclaje anti-oclusión X=1220
    "[v_hud_all][p1]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,0,6.5)'[v_av1];"
    "[v_av1][p2]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,6.5,13.0)'[v_av2];"
    "[v_av2][p3]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,13.0,19.5)'[v_av3];"
    "[v_av3][p4]overlay=1220:'150+5*sin(2*PI*t/3.2)':enable='between(t,19.5,25.0)'[vfinal];"
    
    # Cadena estricta de audio VOZ_GUIAHOY (highpass=65, eq=115Hz +1.6dB, loudnorm=-14 LUFS, CERO afftdn)
    "[0:a]highpass=f=65,equalizer=f=115:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.0:LRA=11,aformat=sample_rates=48000:channel_layouts=mono[afinal]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", AUDIO_SRC,
    "-loop", "1", "-i", p1_path,
    "-loop", "1", "-i", p2_path,
    "-loop", "1", "-i", p3_path,
    "-loop", "1", "-i", p4_path,
    "-loop", "1", "-i", POSES["P1"],
    "-loop", "1", "-i", POSES["P2"],
    "-loop", "1", "-i", POSES["P3"],
    "-loop", "1", "-i", POSES["P4"],
    "-filter_complex", filter_complex,
    "-map", "[vfinal]",
    "-map", "[afinal]",
    "-t", "25.0",
    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    LOCAL_OUT
]

print("Iniciando renderizado del video final...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Error ffmpeg:")
    print(res.stderr[-1200:])
    sys.exit(1)

# Guardar copia en Producción, Bóveda Final y Artefacto
print("Copiando a Producción:", OUT_PATH)
shutil.copy2(LOCAL_OUT, OUT_PATH)
print("Copiando a Bóveda Final:", VAULT_PATH)
shutil.copy2(LOCAL_OUT, VAULT_PATH)
print("Copiando a Artefacto:", ART_PATH)
shutil.copy2(LOCAL_OUT, ART_PATH)

# Calcular SHA256
h = hashlib.sha256()
with open(LOCAL_OUT, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        h.update(chunk)
sha256_hash = h.hexdigest()
file_size = os.path.getsize(LOCAL_OUT)

print("\n=== VIDEO GENERADO CON EXITO ===")
print("Ruta Local:", LOCAL_OUT)
print("Ruta Produccion:", OUT_PATH)
print("Ruta Vault Final:", VAULT_PATH)
print("Tamano:", file_size, "bytes")
print("SHA256:", sha256_hash)

# Auto Launch per RULE_AUTO_LAUNCH_01
try:
    print(f"Lanzando reproductor local: {VAULT_PATH}")
    os.startfile(VAULT_PATH)
except Exception as e:
    print(f"Auto-launch advertencia: {e}")
