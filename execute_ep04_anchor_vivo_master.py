#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBOS · op=281 · Ep04 ANCHOR VIVO MASTER PIPELINE
==========================================================
Pipeline CORRECTO conforme al Ecosistema HBOS-Diamantino:
- Los anchors (Rubín, Zafir, Esmeralda, Citrilo, Grafito, Amatista, Diamantino)
  se ANIMAN con movimientos humanizados (R62 / AnchorVivoEngine):
    · Respiración armónica
    · Micro-inclinación craneal
    · Desplazamiento de hombros
    · Interacción con el background biocuántico
    · 420 pasos de movimiento por ciclo
- Las imágenes PNG del storyboard son la referencia visual de composición
- El audio es el voiceover masterizado por bloques + BGM -20dB
- Salida: Ep04/05_Master/ep04_master_v1.mp4 (1920x1080, H.264, 30fps)

Arquitectura del frame por plano:
  Layer 0: Background biocuántico (bg_ep04_biocuantico_1080p.png) animado con overlay de partículas
  Layer 1: Personaje PNG (plano_0N_*.png) animado con movimientos AnchorVivo R62
  Layer 2: Texto overlay (nombre del personaje, dato técnico) con fade in/out
  Layer 3: Lower third HBOS (barra inferior con logo)
"""

import os
import sys
import json
import math
import time
import wave
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────── PATHS ───────────────────
ROOT       = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine"
EP04       = os.path.join(ROOT, "Ep04")
IMAGES_DIR = os.path.join(EP04, "02_Storyboard", "images_wan21")
BG_DIR     = os.path.join(EP04, "02_Storyboard", "backgrounds")
VOICES_DIR = os.path.join(EP04, "03_Assets", "Voces")
BGM_FILE   = os.path.join(EP04, "03_Assets", "BGM", "ep04_bgm_master.mp3")
MASTER_DIR = os.path.join(EP04, "05_Master")
CLIPS_DIR  = os.path.join(EP04, "04_Clips_Wan21")
TEMP_DIR   = os.path.join(MASTER_DIR, "temp_anchor")

os.makedirs(MASTER_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

W, H = 1920, 1080
FPS  = 30

# ─────────────────── PASOS HUMANIZADOS (R62) ───────────────────
PASOS = 420

def get_anchor_pose(step, total, base_x, base_y, scale=1.0, desplazamiento="caminar_frontal_keynote"):
    """
    Calcula la pose humanizada del anchor en el paso dado.
    Implementa R62: respiración, micro-sacadas, inclinación craneal, desplazamiento.
    """
    t = (step % total) / float(total)
    
    # Respiración armónica (15 resp/min a 30fps)
    breath_y = math.sin(t * 2 * math.pi * 3.0) * 6.0  # pixels
    breath_scale = math.sin(t * 2 * math.pi * 3.0) * 0.008
    
    # Micro-inclinación craneal
    head_tilt = math.sin(t * 2 * math.pi * 1.5 + 0.4) * 2.5  # grados
    
    # Desplazamiento lateral de hombros
    shoulder_sway_x = math.cos(t * 2 * math.pi * 0.8) * 5.0  # pixels
    
    # Movimiento específico por tipo de desplazamiento P-16
    walk_x = 0.0
    walk_y = 0.0
    
    if desplazamiento == "caminar_frontal_keynote":
        # Caminar hacia cámara: ligero avance progresivo + balanceo
        progress = t * 0.04  # avance acumulado
        walk_x = math.sin(t * 2 * math.pi * 2.0) * 8.0  # balanceo al caminar
        walk_y = -progress * 15  # acercamiento a cámara (ligero zoom in)
        
    elif desplazamiento == "traslacion_lateral_racks":
        # Moverse lateralmente hacia el holograma
        walk_x = t * 40.0 - 20.0  # desplaza 40px total
        walk_y = math.sin(t * 2 * math.pi * 2.0) * 4.0  # rebote al caminar
        
    elif desplazamiento == "avance_analitico_frontal":
        walk_x = math.sin(t * 2 * math.pi * 1.5) * 6.0
        walk_y = math.sin(t * 2 * math.pi * 0.5) * -8.0  # ligero avance
        
    elif desplazamiento == "paso_firme_consola":
        walk_x = math.sin(t * 2 * math.pi * 2.5) * 5.0
        walk_y = -t * 10.0  # acercamiento firme a consola
        
    elif desplazamiento == "marcha_dinamica_diagonal":
        walk_x = t * 30.0  # desplazamiento diagonal
        walk_y = math.sin(t * 2 * math.pi * 2.0) * 6.0
        
    elif desplazamiento == "desplazamiento_sobrio_racks":
        walk_x = math.sin(t * 2 * math.pi * 0.7) * 12.0
        walk_y = 0  # sobrio, casi estático
        
    elif desplazamiento == "traslacion_serena_escenario":
        walk_x = math.sin(t * 2 * math.pi * 0.5) * 15.0  # muy suave
        walk_y = math.cos(t * 2 * math.pi * 0.4) * 5.0
        
    elif desplazamiento == "avance_central_monumental":
        walk_x = 0  # centrado
        walk_y = -t * 20.0  # avance monumental hacia cámara
        
    elif desplazamiento == "pose_ensemble_estatica_dinamica":
        walk_x = math.sin(t * 2 * math.pi * 0.3) * 8.0
        walk_y = math.cos(t * 2 * math.pi * 0.2) * 4.0
        
    elif desplazamiento == "placa_editorial_sobria":
        walk_x = 0
        walk_y = math.sin(t * 2 * math.pi * 0.5) * 3.0  # respiración mínima
    
    final_x = base_x + shoulder_sway_x + walk_x
    final_y = base_y - breath_y + walk_y
    final_scale = scale + breath_scale
    
    # Parpadeo (cada ~3 segundos a 30fps: cada 90 frames)
    is_blinking = (step % 90) in (0, 1, 2)
    
    return {
        "x": final_x,
        "y": final_y,
        "scale": max(0.7, min(1.3, final_scale)),
        "head_tilt": head_tilt,
        "is_blinking": is_blinking,
        "breath_y": breath_y,
    }


# ─────────────────── DEFINICIÓN DE PLANOS ───────────────────
PLANOS = [
    {
        "plano": 0,
        "personaje": "Diamantino (Editorial)",
        "tipo": "clip_real",  # usar clip WAN21 real
        "video": os.path.join(CLIPS_DIR, "ep04_plano_00_wan21.mp4"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_00_voz.wav"),
        "imagen": os.path.join(IMAGES_DIR, "plano_00_nota_referencia.png"),
        "desplazamiento": "placa_editorial_sobria",
        "texto_lower": "NOTA DE REFERENCIA EDITORIAL",
        "color_personaje": (220, 230, 255),
    },
    {
        "plano": 1,
        "personaje": "Diamantino",
        "tipo": "clip_real",
        "video": os.path.join(CLIPS_DIR, "ep04_plano_01_wan21.mp4"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_01_voz.wav"),
        "imagen": os.path.join(IMAGES_DIR, "plano_01_diamantino_intro.png"),
        "desplazamiento": "caminar_frontal_keynote",
        "texto_lower": "DIAMANTINO · Nobel de Química 2024 · AlphaFold",
        "color_personaje": (200, 230, 255),
    },
    {
        "plano": 2,
        "personaje": "Rubín",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_02_rubin.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_02_voz.wav"),
        "desplazamiento": "traslacion_lateral_racks",
        "texto_lower": "RUBÍN · AlphaFold: 200M+ estructuras proteicas",
        "color_personaje": (255, 80, 80),
        "anchor_pos": (800, 300),
    },
    {
        "plano": 3,
        "personaje": "Zafir",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_03_zafir.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_03_voz.wav"),
        "desplazamiento": "avance_analitico_frontal",
        "texto_lower": "ZAFIR · AlphaMissense: 71M variantes genéticas",
        "color_personaje": (80, 140, 255),
        "anchor_pos": (760, 280),
    },
    {
        "plano": 4,
        "personaje": "Esmeralda",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_04_esmeralda.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_04_voz.wav"),
        "desplazamiento": "paso_firme_consola",
        "texto_lower": "ESMERALDA · Evoformer · Gramática Universal de la Biología",
        "color_personaje": (60, 220, 120),
        "anchor_pos": (780, 270),
    },
    {
        "plano": 5,
        "personaje": "Citrilo",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_05_citrilo.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_05_voz.wav"),
        "desplazamiento": "marcha_dinamica_diagonal",
        "texto_lower": "CITRILO · Isomorphic Labs · $3B Lilly + Novartis",
        "color_personaje": (255, 200, 50),
        "anchor_pos": (750, 290),
    },
    {
        "plano": 6,
        "personaje": "Grafito",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_06_grafito.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_06_voz.wav"),
        "desplazamiento": "desplazamiento_sobrio_racks",
        "texto_lower": "GRAFITO · 2M+ investigadores · 190 países",
        "color_personaje": (180, 190, 200),
        "anchor_pos": (790, 260),
    },
    {
        "plano": 7,
        "personaje": "Amatista",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_07_amatista.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_07_voz.wav"),
        "desplazamiento": "traslacion_serena_escenario",
        "texto_lower": "AMATISTA · Malaria · Tuberculosis · Solidaridad Global",
        "color_personaje": (180, 80, 255),
        "anchor_pos": (770, 280),
    },
    {
        "plano": 8,
        "personaje": "Diamantino (Síntesis)",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_08_diamantino_recap.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_08_voz.wav"),
        "desplazamiento": "avance_central_monumental",
        "texto_lower": "DIAMANTINO · Era Agéntica en Medicina · Nobel 2024",
        "color_personaje": (200, 230, 255),
        "anchor_pos": (790, 260),
    },
    {
        "plano": 9,
        "personaje": "Ensemble Cierre",
        "tipo": "anchor_vivo",
        "imagen": os.path.join(IMAGES_DIR, "plano_09_ensemble_cierre.png"),
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_09_voz.wav"),
        "desplazamiento": "pose_ensemble_estatica_dinamica",
        "texto_lower": "HBOS-DIAMANTINO · Civilización Tipo 5 · Una misión: Curar",
        "color_personaje": (200, 220, 255),
        "anchor_pos": (800, 250),
    },
]


def get_voice_duration(wav_path):
    """Obtiene duración real de WAV."""
    with wave.open(wav_path, 'r') as w:
        return w.getnframes() / float(w.getframerate())


def make_lower_third(draw, text, color, width=1920, height=1080, alpha=200):
    """Dibuja el lower third de HBOS sobre el frame."""
    # Barra inferior
    bar_y = height - 90
    bar_h = 65
    draw.rectangle([0, bar_y, width, bar_y + bar_h], fill=(0, 0, 20, alpha))
    # Acento de color del personaje
    draw.rectangle([0, bar_y, 6, bar_y + bar_h], fill=color)
    # Texto HBOS
    draw.text((20, bar_y + 10), "HBOS-DIAMANTINO", fill=(0, 200, 255))
    draw.text((20, bar_y + 35), text, fill=(255, 255, 255))
    # Logo derecho
    draw.text((width - 260, bar_y + 20), "EP04 · MEDICINA AGÉNTICA", fill=(0, 200, 255))


def render_background_animated(bg_img, step, total, plano_id):
    """Anima el background biocuántico con partículas y pulsos de luz."""
    bg = bg_img.copy().convert("RGBA")
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    t = step / float(total)
    
    # Pulso de energía (ondas concéntricas desde el centro)
    cx, cy = W // 2, H // 2
    pulse_r = int((t * 300) % 250 + 50)
    alpha_pulse = max(0, 60 - int(t * 60))
    if alpha_pulse > 0:
        draw.ellipse([cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r],
                     outline=(0, 200, 255, alpha_pulse), width=2)
    
    # Partículas moleculares flotantes (posiciones basadas en step)
    for i in range(8):
        px = int((cx + math.cos(t * 2 * math.pi + i * 0.8) * (200 + i * 30)) % W)
        py = int((cy + math.sin(t * 2 * math.pi * 0.7 + i * 1.1) * (100 + i * 20)) % H)
        particle_alpha = int(80 + 40 * math.sin(t * 2 * math.pi * 2 + i))
        draw.ellipse([px-3, py-3, px+3, py+3], fill=(0, 255, 200, particle_alpha))
    
    # Líneas de conexión entre nodos (red molecular)
    nodes = [(350 + int(math.sin(t * 0.5 + i) * 20), 400 + int(math.cos(t * 0.3 + i) * 15)) 
             for i in range(6)]
    for i in range(len(nodes) - 1):
        line_alpha = int(40 + 20 * math.sin(t * 2 * math.pi + i))
        draw.line([nodes[i], nodes[i+1]], fill=(0, 200, 255, line_alpha), width=1)
    
    result = Image.alpha_composite(bg, overlay)
    return result.convert("RGB")


def render_anchor_frame_fast(plano, bg_base, persona_img, frame_idx, total_frames):
    """
    Renderiza un frame completo con persona_img pre-cargada:
    - Layer 0: Background biocuantico animado con particulas
    - Layer 1: Personaje PNG con 420 micro-movimientos AnchorVivo R62
    - Layer 2: Lower third HBOS con fade in/out
    """
    # Layer 0: Background animado
    frame = render_background_animated(bg_base, frame_idx, total_frames, plano["plano"])
    frame_rgba = frame.convert("RGBA")

    # Layer 1: Personaje con movimientos AnchorVivo R62
    orig_w, orig_h = persona_img.size

    # Posicion base del personaje
    base_x = plano.get("anchor_pos", (W // 2, H // 2))[0]
    base_y = plano.get("anchor_pos", (W // 2, H // 2))[1]

    # Calcular pose en este step
    step = int((frame_idx / max(total_frames - 1, 1)) * PASOS)
    pose = get_anchor_pose(step, PASOS, base_x, base_y, 1.0, plano["desplazamiento"])
    
    # Aplicar escala con respiración
    new_w = int(orig_w * pose["scale"])
    new_h = int(orig_h * pose["scale"])
    persona_scaled = persona_img.resize((new_w, new_h), Image.LANCZOS)
    
    # Aplicar inclinación de cabeza (rotación suave)
    if abs(pose["head_tilt"]) > 0.1:
        persona_scaled = persona_scaled.rotate(
            pose["head_tilt"], expand=False, 
            resample=Image.BICUBIC,
            center=(new_w // 2, new_h // 3)  # rotar desde la cabeza (tercio superior)
        )
    
    # Parpadeo: suavizar imagen ligeramente
    if pose["is_blinking"]:
        persona_scaled = persona_scaled.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Posicionar sobre el frame
    paste_x = int(pose["x"] - new_w // 2)
    paste_y = int(pose["y"] - new_h // 4)  # anclar desde el pecho del personaje
    paste_x = max(0, min(W - new_w, paste_x))
    paste_y = max(0, min(H - new_h, paste_y))
    
    frame_rgba.paste(persona_scaled, (paste_x, paste_y), persona_scaled)
    
    # Layer 2: Lower third con fade in/out
    result = frame_rgba.convert("RGB")
    draw_final = ImageDraw.Draw(result)
    
    # Fade in (primeros 0.5s = 15 frames) y fade out (últimos 0.5s)
    fade_frames = 15
    if frame_idx < fade_frames:
        alpha_lt = int(255 * (frame_idx / fade_frames))
    elif frame_idx > total_frames - fade_frames:
        alpha_lt = int(255 * ((total_frames - frame_idx) / fade_frames))
    else:
        alpha_lt = 255
    
    if alpha_lt > 10:
        make_lower_third(draw_final, plano["texto_lower"], plano["color_personaje"])
    
    return result


def generate_anchor_vivo_segment(plano, seg_out):
    """
    Genera un segmento de video con animacion AnchorVivo para un plano.
    Metodo: image2 JPG (estable, sin deadlock de pipe stdin).
    1. Renderiza frames PIL -> JPGs en disco (frames_dir)
    2. FFmpeg image2 -> H.264 sin audio
    3. Mux con audio de voz
    4. Limpia temporales
    """
    voice_path = plano["voice"]
    dur = get_voice_duration(voice_path)
    total_frames = int(dur * FPS)

    print(f"  [anchor_vivo] Plano {plano['plano']} ({plano['personaje']}): {dur:.1f}s, {total_frames} frames")

    # Cargar assets una sola vez
    bg_path = os.path.join(BG_DIR, "bg_ep04_biocuantico_1080p.png")
    if os.path.exists(bg_path):
        bg_base = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        bg_base = Image.new("RGBA", (W, H), (8, 12, 24, 255))
        draw_bg = ImageDraw.Draw(bg_base)
        for y in range(0, H, 80):
            draw_bg.line([(0, y), (W, y)], fill=(20, 35, 70, 60))
        for x in range(0, W, 80):
            draw_bg.line([(x, 0), (x, H)], fill=(20, 35, 70, 60))

    # Pre-cargar imagen del personaje
    persona_img = Image.open(plano["imagen"]).convert("RGBA")

    # Directorio de frames JPG temporales
    frames_dir = os.path.join(TEMP_DIR, f"frames_p{plano['plano']:02d}")
    os.makedirs(frames_dir, exist_ok=True)

    temp_video_noaudio = os.path.join(TEMP_DIR, f"seg_{plano['plano']:02d}_noaudio.mp4")

    # ── PASO 1: Renderizar frames a JPG ──
    reported = set()
    t_render = time.time()
    for fi in range(total_frames):
        frame = render_anchor_frame_fast(plano, bg_base, persona_img, fi, total_frames)
        frame.save(os.path.join(frames_dir, f"f{fi:05d}.jpg"), quality=92, optimize=False)
        pct = fi * 100 // total_frames
        if pct % 25 == 0 and pct not in reported:
            reported.add(pct)
            elapsed_r = time.time() - t_render
            eta = (elapsed_r / max(fi, 1)) * (total_frames - fi)
            print(f"    Plano {plano['plano']}: {pct}% ({fi}/{total_frames}) ETA:{eta:.0f}s")
    print(f"    Render completo en {time.time()-t_render:.1f}s")

    # ── PASO 2: FFmpeg image2 -> H.264 ──
    cmd_encode = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f%05d.jpg"),
        "-vf", f"scale={W}:{H}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video_noaudio
    ]
    r_enc = subprocess.run(cmd_encode, capture_output=True, text=True)
    if r_enc.returncode != 0:
        print(f"  [ERROR encode] Plano {plano['plano']}: {r_enc.stderr[-300:]}")
        return False

    # ── PASO 3: Mux con audio de voz ──
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", temp_video_noaudio,
        "-i", voice_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "aresample=44100",
        "-shortest",
        seg_out
    ]
    r_mux = subprocess.run(cmd_mux, capture_output=True, text=True)
    if r_mux.returncode != 0:
        print(f"  [ERROR mux] Plano {plano['plano']}: {r_mux.stderr[-300:]}")
        return False

    # ── PASO 4: Limpiar temporales ──
    shutil.rmtree(frames_dir, ignore_errors=True)
    if os.path.exists(temp_video_noaudio):
        os.remove(temp_video_noaudio)

    size_mb = os.path.getsize(seg_out) / 1024 / 1024
    print(f"  OK Plano {plano['plano']} -> {size_mb:.1f} MB")
    return True


def generate_clip_real_segment(plano, seg_out):
    """
    Para planos con clip WAN21 real (plano 00 y 01):
    extiende/loopea el clip para que coincida con la duración de la voz.
    """
    voice_path = plano["voice"]
    video_path = plano["video"]
    dur = get_voice_duration(voice_path)
    
    # Verificar duración del clip
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    clip_dur = float(probe.stdout.strip())
    loops = int(dur / clip_dur) + 2
    
    print(f"  [clip_real] Plano {plano['plano']} ({plano['personaje']}): clip={clip_dur:.1f}s, voz={dur:.1f}s, loops={loops}")
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(loops), "-i", video_path,
        "-i", voice_path,
        "-t", str(dur),
        "-filter_complex",
        (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080[vscaled];"
            f"[vscaled]drawtext=text='{plano['texto_lower']}':"
            "fontcolor=white:fontsize=28:x=20:y=h-80:alpha=0.9[vout]"
        ),
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "aresample=44100",
        "-shortest",
        seg_out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERROR] clip_real plano {plano['plano']}: {r.stderr[-300:]}")
        # Fallback sin drawtext
        cmd_simple = [
            "ffmpeg", "-y",
            "-stream_loop", str(loops), "-i", video_path,
            "-i", voice_path,
            "-t", str(dur),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-af", "aresample=44100",
            "-shortest",
            seg_out
        ]
        r2 = subprocess.run(cmd_simple, capture_output=True, text=True)
        if r2.returncode != 0:
            print(f"  [ERROR FATAL] plano {plano['plano']}: {r2.stderr[-200:]}")
            return False
    
    size_mb = os.path.getsize(seg_out) / 1024 / 1024
    print(f"  OK Plano {plano['plano']} -> {size_mb:.1f} MB")
    return True


# ─────────────────── PIPELINE PRINCIPAL ───────────────────
print("\n" + "="*70)
print("HBOS op=281 - Ep04 ANCHOR VIVO MASTER PIPELINE")
print("Anchors humanizados R62: respiracion + caminar + interaccion background")
print("="*70)

t_start = time.time()
seg_files = []
errors = []

total_dur = 0.0
for p in PLANOS:
    total_dur += get_voice_duration(p["voice"])

print(f"\n[EP04] Duracion total por voz: {total_dur:.1f}s ({total_dur/60:.1f} min)")
print(f"[EP04] Planos: {len(PLANOS)} ({sum(1 for p in PLANOS if p['tipo']=='clip_real')} clips reales + {sum(1 for p in PLANOS if p['tipo']=='anchor_vivo')} anchor vivo)\n")

for plano in PLANOS:
    seg_out = os.path.join(TEMP_DIR, f"seg_{plano['plano']:02d}.mp4")
    seg_files.append(seg_out)
    
    if os.path.exists(seg_out) and os.path.getsize(seg_out) > 200_000:
        print(f"  [skip] Plano {plano['plano']} ya existe ({os.path.getsize(seg_out)//1024}KB)")
        continue
    
    if plano["tipo"] == "clip_real":
        ok = generate_clip_real_segment(plano, seg_out)
    else:
        ok = generate_anchor_vivo_segment(plano, seg_out)
    
    if not ok:
        errors.append(plano["plano"])

if errors:
    print(f"\n!! Errores en planos: {errors}")

# Concat sin BGM
concat_file = os.path.join(TEMP_DIR, "concat_list.txt")
no_bgm_file = os.path.join(MASTER_DIR, "ep04_no_bgm.mp4")

available_segs = [f for f in seg_files if os.path.exists(f) and os.path.getsize(f) > 100_000]
print(f"\n[EP04] Concatenando {len(available_segs)}/{len(seg_files)} segmentos...")

with open(concat_file, "w") as f:
    for sf in available_segs:
        f.write(f"file '{sf.replace(chr(92), '/')}'\n")

concat_cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_file,
    "-c", "copy",
    no_bgm_file
]
r = subprocess.run(concat_cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(f"[ERROR concat]: {r.stderr[-400:]}")
else:
    print(f"OK Sin BGM: {no_bgm_file}")

# Mezclar BGM (-20dB con fade out)
OUTPUT = os.path.join(MASTER_DIR, "ep04_master_v1.mp4")
print(f"[EP04] Mezclando BGM a -20dB con fade out...")

bgm_cmd = [
    "ffmpeg", "-y",
    "-i", no_bgm_file,
    "-stream_loop", "-1", "-i", BGM_FILE,
    "-filter_complex",
    f"[1:a]volume=-20dB,aresample=44100[bgm];"
    "[0:a]aresample=44100[vo];"
    "[vo][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "320k",
    "-movflags", "+faststart",
    OUTPUT
]
r_bgm = subprocess.run(bgm_cmd, capture_output=True, text=True)
ok_final = (r_bgm.returncode == 0)

if not ok_final:
    print(f"[ERROR BGM mix]: {r_bgm.stderr[-400:]}")

elapsed = time.time() - t_start
print(f"\n{'='*70}")
print(f"PIPELINE COMPLETADO en {elapsed:.0f}s ({elapsed/60:.1f} min)")
if ok_final and os.path.exists(OUTPUT):
    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"OUTPUT: {OUTPUT}")
    print(f"TAMANO: {size_mb:.1f} MB")
    print(f"DURACION PLANIFICADA: {total_dur:.1f}s ({total_dur/60:.1f} min)")
else:
    print("ERROR: No se pudo generar el master final")
print("="*70)

# Actualizar estado produccion
estado_file = os.path.join(EP04, "estado_produccion_ep04.json")
with open(estado_file, "r", encoding="utf-8") as f:
    estado = json.load(f)
estado["master_v1"] = {
    "archivo": "ep04_master_v1.mp4",
    "duracion_seg": total_dur,
    "duracion_min": round(total_dur / 60, 2),
    "tecnica": "AnchorVivo R62 (420 micro-movimientos humanizados) + clips WAN21 reales",
    "estado": "GENERADO_OP281" if ok_final else "ERROR_OP281",
    "local": ok_final,
    "errores_planos": errors
}
estado["estado_general"] = "Master v1 AnchorVivo generado" if ok_final else "Error en generacion"
with open(estado_file, "w", encoding="utf-8") as f:
    json.dump(estado, f, indent=2, ensure_ascii=False)
print(f"OK Estado actualizado: {estado_file}")
