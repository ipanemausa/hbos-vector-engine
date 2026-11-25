"""
HBOS · ENSAMBLADOR DE CLASE 01 MIT (10 MINUTOS / MODULAR E2E)
Script: ensamblar_clase01_guiahoy_completo.py
Salida: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\guiahoy_clase01_mit_10min.mp4

Reglas HBOS:
1. Audio master canónico Guiahoy (48 kHz / -14 LUFS, cero afftdn).
2. 10 fondos 16:9 (bg_01.jpg a bg_10.jpg) emparejados con 10 bloques.
3. 10 poses avatar transparente en overlay=W-w-40:H-h:format=auto con scale=-1:780,format=rgba.
4. Generación de subtítulos .srt sincronizados a la duración real del audio ffprobe.
5. Manifiesto y registro en Qdrant (localhost:6333).
6. Auto-apertura del archivo final MP4 (RULE_AUTO_LAUNCH_01).
"""

import os
import sys
import json
import time
import shutil
import hashlib
import urllib.request
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

print("==========================================================")
print("   HBOS ENGINE · ENSAMBLADOR CLASE 01 MIT (GUIAHOY 10M)   ")
print("==========================================================")

# -------------------------------------------------------------
# 1. Definición de Rutas
# -------------------------------------------------------------
PROD_DATE_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-25"
FONDOS_DIR = os.path.join(PROD_DATE_DIR, "fondos_16x9")
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"
ART_DIR = r"C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83"
LOCAL_STAGE_DIR = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\studio_vivo_final\mit_10min_stage"

os.makedirs(PROD_DATE_DIR, exist_ok=True)
os.makedirs(FONDOS_DIR, exist_ok=True)
os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(LOCAL_STAGE_DIR, exist_ok=True)

OUT_NAME = "guiahoy_clase01_mit_10min.mp4"
SRT_NAME = "guiahoy_clase01_mit_10min.srt"

OUT_FINAL_PATH = os.path.join(PROD_DATE_DIR, OUT_NAME)
SRT_FINAL_PATH = os.path.join(PROD_DATE_DIR, SRT_NAME)
VAULT_FINAL_PATH = os.path.join(VAULT_DIR, OUT_NAME)
ART_FINAL_PATH = os.path.join(ART_DIR, OUT_NAME)

# -------------------------------------------------------------
# 2. Localizar Audio Locutado con Voz Canónica de Guiahoy
# -------------------------------------------------------------
AUDIO_CANDIDATES = [
    r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\Guiahoy_MASTER_48k_menos14LUFS.wav",
    r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_MASTER_48k_menos14LUFS.wav",
    r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\Guiahoy_CLONE_REF_90s_48k.wav",
    r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_CLONE_REF_90s_48k.wav",
    r"G:\My Drive\HBOS_Creative\02_Voice_Profiles\Guiahoy_ELEVENLABS_CLON_VERIFICADO_menos14LUFS.wav"
]

AUDIO_PATH = None
for cand in AUDIO_CANDIDATES:
    if os.path.isfile(cand):
        AUDIO_PATH = cand
        break

if not AUDIO_PATH:
    print("[ERROR] No se localizó ningún audio maestro en las rutas auditadas.")
    sys.exit(1)

print(f"[OK] Audio maestro localizado: {AUDIO_PATH}")

# Medir duración real con ffprobe
ffprobe_cmd = [
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    AUDIO_PATH
]
res_dur = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
if res_dur.returncode != 0 or not res_dur.stdout.strip():
    print("[ERROR] ffprobe no pudo determinar la duración del audio.")
    sys.exit(1)

REAL_AUDIO_DURATION = float(res_dur.stdout.strip())
print(f"[OK] Duración real del audio (ffprobe): {REAL_AUDIO_DURATION:.2f}s ({REAL_AUDIO_DURATION/60:.2f} min)")

# -------------------------------------------------------------
# 3. Definición de los 10 Bloques Canónicos
# -------------------------------------------------------------
NOMINAL_BLOCKS = [
    {
        "id": 1,
        "bg": "bg_01.jpg",
        "avatar": "avatar-pose-t-arms-open-narrower.png",
        "nom_start": 0.0,
        "nom_end": 55.0,
        "title": "MÓDULO 01: EL MOLDE REPRODUCIBLE",
        "subtitle": "Soberanía Tecnológica MIT & Ecosistema HBOS 2026",
        "points": [
            "Arquitectura agentica on-premise sin ataduras propietarias",
            "Sustitución de licencias mensuales por pipelines locales",
            "Marco metodológico de ingeniería inversa y soberanía técnica"
        ]
    },
    {
        "id": 2,
        "bg": "bg_02.jpg",
        "avatar": "avatar-pose-t-calm-both.png",
        "nom_start": 55.0,
        "nom_end": 130.0,
        "title": "MÓDULO 02: COSTO CERO & INFRAESTRUCTURA",
        "subtitle": "Ahorro Radical para PYMEs y Universidades en Colombia",
        "points": [
            "Computación híbrida: Hardware local + n8n + Qdrant OSS",
            "Cero suscripciones en dólares por usuario o token recurrente",
            "Despliegue verificado en máquinas estándar de oficina"
        ]
    },
    {
        "id": 3,
        "bg": "bg_03.jpg",
        "avatar": "avatar-pose-t-chin-stroke-L.png",
        "nom_start": 130.0,
        "nom_end": 195.0,
        "title": "MÓDULO 03: MOTOR VECTORIAL RAG 768D",
        "subtitle": "Indexación Segregada con Cero Alucinación",
        "points": [
            "Topología de 5 nodos: Texto, Voz, Avatar, Video y Manifiesto",
            "Consultas cosine similarity a < 15ms de latencia local",
            "Respaldo criptográfico SHA-256 en Google Drive Bóveda"
        ]
    },
    {
        "id": 4,
        "bg": "bg_04.jpg",
        "avatar": "avatar-pose-t-arms-open-palms-up.png",
        "nom_start": 195.0,
        "nom_end": 285.0,
        "title": "MÓDULO 04: AGENTES AUTÓNOMOS Y WORKFORCE",
        "subtitle": "Orquestación Multimodal y Calificación B2B Inmediata",
        "points": [
            "Agente calificador: respuesta y agenda en menos de 10 segundos",
            "Eliminación de cuellos de botella en embudos comerciales",
            "Integración de modelos abiertos de frontera (EE.UU. y China)"
        ]
    },
    {
        "id": 5,
        "bg": "bg_05.jpg",
        "avatar": "avatar-pose-t-chin-stroke-R.png",
        "nom_start": 285.0,
        "nom_end": 355.0,
        "title": "MÓDULO 05: PIPELINE REA & INGENIERÍA INVERSA",
        "subtitle": "Extracción Autónoma de Patrones y Topologías de Código",
        "points": [
            "Deconstrucción de aplicaciones líderes y flujos de trabajo",
            "Reconstrucción limpia en componentes reutilizables HBOS",
            "Validación estricta de licencias y trazabilidad de activos"
        ]
    },
    {
        "id": 6,
        "bg": "bg_06.jpg",
        "avatar": "avatar-pose-t-arms-open-wider.png",
        "nom_start": 355.0,
        "nom_end": 425.0,
        "title": "MÓDULO 06: MULTI-PLATAFORMA AUTÓNOMO",
        "subtitle": "Distribución Simultánea a Redes Sociales sin Programar",
        "points": [
            "Publicación automatizada a Instagram Reels, Shorts, TikTok y LinkedIn",
            "Subtitulado animado ASS con renderizado cinemático 1080p",
            "Normalización de audio broadcast -14.0 LUFS EBU R128"
        ]
    },
    {
        "id": 7,
        "bg": "bg_07.jpg",
        "avatar": "avatar-pose-t-calm-both.png",
        "nom_start": 425.0,
        "nom_end": 485.0,
        "title": "MÓDULO 07: AUDITORÍA CRIPTOGRÁFICA SHA-256",
        "subtitle": "Registro Inmutable y Certificación de Entregables",
        "points": [
            "Hasheo determinista SHA-256 por cada fotograma y audio master",
            "DAG de verificación que impide el uso de activos viejos o corruptos",
            "Libro mayor de producción E2E en Qdrant y Bóveda Segura"
        ]
    },
    {
        "id": 8,
        "bg": "bg_08.jpg",
        "avatar": "avatar-pose-t-arms-open-palms-front.png",
        "nom_start": 485.0,
        "nom_end": 535.0,
        "title": "MÓDULO 08: IMPACTO REAL EN ANTIOQUIA",
        "subtitle": "Transferencia de Conocimiento a PYMEs y Universidades",
        "points": [
            "Despliegues en el Oriente Antioqueño y Valle de Aburrá",
            "Capacitación ejecutiva práctica con entregables inmediatos",
            "Independencia tecnológica regional comprobada sobre hardware común"
        ]
    },
    {
        "id": 9,
        "bg": "bg_09.jpg",
        "avatar": "avatar-pose-t-both-thumbs-up.png",
        "nom_start": 535.0,
        "nom_end": 570.0,
        "title": "MÓDULO 09: MÉTRICAS Y RETORNO OPERATIVO",
        "subtitle": "-98.6% Tiempo de Ciclo y Margen Operativo +38.4%",
        "points": [
            "De 180 minutos de edición manual a 2.5 minutos de render E2E",
            "120 horas de trabajo humano ahorradas al mes por empresa",
            "Costo marginal por video generado: $0.00 USD"
        ]
    },
    {
        "id": 10,
        "bg": "bg_10.jpg",
        "avatar": "avatar-pose-t-beckon-R.png",
        "nom_start": 570.0,
        "nom_end": 600.0,
        "title": "MÓDULO 10: CONCLUSIÓN & HOJA DE RUTA",
        "subtitle": "Mesa de Trabajo en Vivo · Guillermo Alonso Hoyos",
        "points": [
            "Puesta en marcha paso a paso en tus propios servidores",
            "Superinteligencia práctica aplicada a la productividad diaria",
            "Contacto directo: GuíaHoy / HBOS Sovereign AI 2026"
        ]
    }
]

# Ajustar duración de cada bloque proporcionalmente a la duración real del audio ffprobe
TOTAL_NOMINAL = 600.0
TIME_SCALE = REAL_AUDIO_DURATION / TOTAL_NOMINAL

BLOCKS = []
accum_t = 0.0
for b in NOMINAL_BLOCKS:
    dur_nom = b["nom_end"] - b["nom_start"]
    dur_real = dur_nom * TIME_SCALE
    start_real = accum_t
    end_real = accum_t + dur_real
    accum_t = end_real
    b_copy = dict(b)
    b_copy["real_start"] = start_real
    b_copy["real_end"] = end_real
    b_copy["real_duration"] = dur_real
    BLOCKS.append(b_copy)

# Forzar que el último termine exactamente en REAL_AUDIO_DURATION
BLOCKS[-1]["real_end"] = REAL_AUDIO_DURATION
BLOCKS[-1]["real_duration"] = REAL_AUDIO_DURATION - BLOCKS[-1]["real_start"]

print("\n--- Plan de Bloques Sincronizados con ffprobe ---")
for b in BLOCKS:
    print(f"Bloque {b['id']:02d}: [{b['real_start']:06.2f}s - {b['real_end']:06.2f}s] ({b['real_duration']:05.2f}s) -> {b['title']}")

# -------------------------------------------------------------
# 4. Generación y Validación de Fondos 16:9 (bg_01.jpg a bg_10.jpg)
# -------------------------------------------------------------
def get_font(size, bold=False):
    fonts = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

f_head = get_font(30, bold=True)
f_mod = get_font(18, bold=True)
f_title = get_font(34, bold=True)
f_sub = get_font(20, bold=False)
f_card_t = get_font(18, bold=True)
f_card_d = get_font(15, bold=False)
f_badge = get_font(14, bold=True)

print("\nVerificando/Generando fondos 16:9 en:", FONDOS_DIR)
for b in BLOCKS:
    bg_path = os.path.join(FONDOS_DIR, b["bg"])
    if not os.path.exists(bg_path):
        img = Image.new("RGB", (1920, 1080), (8, 13, 24))
        d = ImageDraw.Draw(img)
        
        # Gradiente / Grid tecnológico de fondo
        for y_line in range(0, 1080, 40):
            d.line([(0, y_line), (1920, y_line)], fill=(15, 23, 42), width=1)
        for x_line in range(0, 1920, 40):
            d.line([(x_line, 0), (x_line, 1080)], fill=(15, 23, 42), width=1)
            
        # Banner Header Superior
        d.rounded_rectangle([60, 45, 1160, 120], radius=14, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
        d.ellipse([85, 74, 99, 88], fill=(52, 211, 153))
        d.text((115, 66), "HBOS SOVEREIGN ARCHITECTURE · CLASE 01 MIT", fill=(255, 255, 255), font=f_head)
        
        # Badge Bloque
        d.rounded_rectangle([860, 64, 1135, 100], radius=8, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
        d.text((880, 72), f"BLOQUE {b['id']:02d} / 10", fill=(56, 189, 248), font=f_badge)
        
        # Contenedor Principal (dos tercios izquierdos, anti-oclusión)
        d.rounded_rectangle([60, 140, 1160, 840], radius=18, fill=(11, 17, 33), outline=(30, 41, 59), width=2)
        
        # Título y Subtítulo
        d.text((95, 175), b["title"], fill=(248, 250, 252), font=f_title)
        d.text((95, 225), b["subtitle"], fill=(56, 189, 248), font=f_sub)
        d.line([(95, 265), (1125, 265)], fill=(51, 65, 85), width=2)
        
        # Tarjetas de Puntos Clave
        card_colors = [(56, 189, 248), (52, 211, 153), (192, 132, 252)]
        for i, pt in enumerate(b["points"]):
            y0 = 295 + i * 155
            y1 = y0 + 130
            c = card_colors[i % len(card_colors)]
            d.rounded_rectangle([95, y0, 1125, y1], radius=14, fill=(19, 27, 46), outline=c, width=1)
            # Dot
            d.ellipse([125, y0 + 35, 145, y0 + 55], fill=c)
            d.text((165, y0 + 25), f"Pilar {i+1}", fill=c, font=f_card_t)
            d.text((165, y0 + 58), pt, fill=(226, 232, 240), font=f_card_d)
            
        # Barra Inferior de Métricas / Estado
        d.rounded_rectangle([60, 860, 1160, 930], radius=12, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
        d.text((95, 882), f"Canal de Audio: Guiahoy Master 48kHz / -14 LUFS | Duración: {b['real_duration']:.1f}s | Trazabilidad Qdrant 768d", fill=(148, 163, 184), font=f_badge)
        
        img.save(bg_path, quality=95)
        print(f"  [+] Creado fondo: {b['bg']}")
    else:
        print(f"  [OK] Fondo existente: {b['bg']}")

# -------------------------------------------------------------
# 5. Generación de Subtítulos .SRT Sincronizados
# -------------------------------------------------------------
def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

print("\nGenerando archivo de subtítulos .srt en:", SRT_FINAL_PATH)
with open(SRT_FINAL_PATH, "w", encoding="utf-8") as f_srt:
    for b in BLOCKS:
        t_start = format_srt_time(b["real_start"])
        t_end = format_srt_time(b["real_end"])
        f_srt.write(f"{b['id']}\n")
        f_srt.write(f"{t_start} --> {t_end}\n")
        f_srt.write(f"{b['title']} - {b['subtitle']}\n\n")

print(f"[OK] Subtítulos .srt generados con {len(BLOCKS)} bloques sincronizados.")

# -------------------------------------------------------------
# 6. Renderizado de Bloques y Ensamble Final con FFmpeg
# -------------------------------------------------------------
# Para garantizar velocidad máxima y evitar latencias de red en Google Drive,
# renderizamos cada segmento localmente en LOCAL_STAGE_DIR y luego unificamos.

print("\nIniciando renderizado modular de los 10 bloques...")
segment_files = []
concat_list_path = os.path.join(LOCAL_STAGE_DIR, "concat_list.txt")

with open(concat_list_path, "w", encoding="utf-8") as f_concat:
    for b in BLOCKS:
        bg_file = os.path.join(FONDOS_DIR, b["bg"])
        avatar_file = os.path.join(AVATAR_DIR, b["avatar"])
        seg_out = os.path.join(LOCAL_STAGE_DIR, f"seg_{b['id']:02d}.mp4")
        dur = b["real_duration"]
        
        # Si el segmento ya existe y tiene tamaño válido (> 500 KB), reutilizarlo
        if os.path.exists(seg_out) and os.path.getsize(seg_out) > 500000:
            print(f"  [OK] Bloque {b['id']:02d} ya renderizado ({os.path.getsize(seg_out)} bytes). Reutilizando.")
            f_concat.write(f"file '{seg_out.replace(os.sep, '/')}'\n")
            segment_files.append(seg_out)
            continue

        # Copiar imagen local para acelerar ffmpeg
        local_bg = os.path.join(LOCAL_STAGE_DIR, f"bg_{b['id']:02d}.jpg")
        local_av = os.path.join(LOCAL_STAGE_DIR, f"av_{b['id']:02d}.png")
        shutil.copy2(bg_file, local_bg)
        shutil.copy2(avatar_file, local_av)
        
        cmd_seg = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{dur:.3f}", "-i", local_bg,
            "-loop", "1", "-t", f"{dur:.3f}", "-i", local_av,
            "-filter_complex", "[1:v]scale=-1:780,format=rgba[av];[0:v][av]overlay=W-w-40:H-h:format=auto",
            "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "30",
            seg_out
        ]
        
        t0 = time.time()
        print(f"  [*] Renderizando Bloque {b['id']:02d} ({dur:.2f}s) con avatar {b['avatar']}...")
        r_seg = subprocess.run(cmd_seg, capture_output=True, text=True)
        if r_seg.returncode != 0:
            print(f"[ERROR] Falló render del bloque {b['id']}:", r_seg.stderr[-600:])
            sys.exit(1)
        print(f"      [OK] Bloque {b['id']:02d} listo en {time.time()-t0:.2f}s")
        
        f_concat.write(f"file '{seg_out.replace(os.sep, '/')}'\n")
        segment_files.append(seg_out)

# Concatenar todos los segmentos de video
video_concat_temp = os.path.join(LOCAL_STAGE_DIR, "video_concat_temp.mp4")
print("\nConcatenando pistas de video con concat demuxer...")
cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list_path,
    "-c", "copy",
    video_concat_temp
]
r_cat = subprocess.run(cmd_concat, capture_output=True, text=True)
if r_cat.returncode != 0:
    print("[ERROR] Falló concatenación de video:", r_cat.stderr[-600:])
    sys.exit(1)

# Mux final de video concatenado + audio maestro canónico
local_final_mp4 = os.path.join(LOCAL_STAGE_DIR, OUT_NAME)
print("\nMuxing final con audio canónico Guiahoy (48 kHz / AAC / -14 LUFS)...")
cmd_mux = [
    "ffmpeg", "-y",
    "-i", video_concat_temp,
    "-i", AUDIO_PATH,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-t", f"{REAL_AUDIO_DURATION:.3f}",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    local_final_mp4
]
r_mux = subprocess.run(cmd_mux, capture_output=True, text=True)
if r_mux.returncode != 0:
    print("[ERROR] Falló mux final de audio y video:", r_mux.stderr[-600:])
    sys.exit(1)

# -------------------------------------------------------------
# 7. Copias Seguras a Google Drive, Bóveda Final y Artefacto
# -------------------------------------------------------------
print("\nCopiando video final a destinos oficiales...")
print("  -> Destino Producción:", OUT_FINAL_PATH)
shutil.copy2(local_final_mp4, OUT_FINAL_PATH)

print("  -> Destino Vault Final:", VAULT_FINAL_PATH)
shutil.copy2(local_final_mp4, VAULT_FINAL_PATH)

print("  -> Destino Artefacto:", ART_FINAL_PATH)
shutil.copy2(local_final_mp4, ART_FINAL_PATH)

# Calcular SHA-256
h = hashlib.sha256()
with open(OUT_FINAL_PATH, "rb") as f_hash:
    for chunk in iter(lambda: f_hash.read(65536), b""):
        h.update(chunk)
SHA256_HASH = h.hexdigest()
FILE_SIZE = os.path.getsize(OUT_FINAL_PATH)

print(f"\n[OK] Video maestro guardado exitosamente.")
print(f"Tamaño: {FILE_SIZE} bytes ({FILE_SIZE/(1024*1024):.2f} MB)")
print(f"SHA-256: {SHA256_HASH}")

# -------------------------------------------------------------
# 8. Registro de Manifiesto en Qdrant (http://localhost:6333)
# -------------------------------------------------------------
print("\nRegistrando manifiesto de render en Qdrant Vector Engine...")
try:
    point_id = "c1a5e001-0000-5000-8000-202611250001"
    manifest_payload = {
        "title": "Clase 01 MIT - El Molde Reproducible (GuíaHoy)",
        "file_name": OUT_NAME,
        "gdrive_path": OUT_FINAL_PATH,
        "vault_path": VAULT_FINAL_PATH,
        "srt_path": SRT_FINAL_PATH,
        "sha256": SHA256_HASH,
        "audio_master": AUDIO_PATH,
        "duration_seconds": REAL_AUDIO_DURATION,
        "resolution": "1920x1080",
        "fps": 30,
        "blocks_count": 10,
        "status": "APPROVED_MASTER_CLASE_01_MIT",
        "timestamp": datetime.now().isoformat()
    }
    
    # Dummy 768d vector (unit normalized)
    vector_768 = [0.036] * 768
    
    req_body = json.dumps({
        "points": [
            {
                "id": point_id,
                "vector": vector_768,
                "payload": manifest_payload
            }
        ]
    }).encode("utf-8")
    
    q_url = "http://localhost:6333/collections/canon_video_hbos_r768/points?wait=true"
    req_q = urllib.request.Request(q_url, data=req_body, headers={"Content-Type": "application/json"}, method="PUT")
    with urllib.request.urlopen(req_q, timeout=5) as q_resp:
        if q_resp.status in (200, 201):
            print(f"  [OK] Registrado en 'canon_video_hbos_r768' con ID {point_id}")
        else:
            print(f"  [!] Qdrant status code: {q_resp.status}")
except Exception as e:
    print(f"  [!] Advertencia Qdrant (continuando sin bloqueo): {e}")

# -------------------------------------------------------------
# 9. Apertura Automática (RULE_AUTO_LAUNCH_01)
# -------------------------------------------------------------
print("\nEjecutando apertura automática del archivo MP4...")
try:
    os.startfile(OUT_FINAL_PATH)
    print(f"[OK] Lanzador del sistema activado sobre: {OUT_FINAL_PATH}")
except Exception as e:
    print(f"[!] Advertencia al lanzar reproductor: {e}")

print("\n==========================================================")
print("             ENSAMBLE FINALIZADO CON ÉXITO                ")
print("==========================================================")
