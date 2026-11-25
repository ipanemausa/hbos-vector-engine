"""
HBOS ENGINE · ENSAMBLADOR CLASE 01 MIT (V1 LIMPIO · NUEVO PROYECTO)
Script: ensamblar_clase01_mit_v1.py
Salida: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\guiahoy_clase01_mit_10min_v1.mp4

DIRECTIVAS DEL PROYECTO NUEVO:
1. Audio de voz nuevo y exclusivo:
   Ruta por defecto: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\02_voz_guiahoy\\clase01_mit_10min_guiahoy_v1.wav
   Si el archivo no existe, el script SE DETIENE DE INMEDIATO con código 2 e instrucciones explícitas.
   PROHIBIDO caer en pistas viejas o de temas anteriores.
2. 10 fondos 16:9 (bg_01.jpg a bg_10.jpg) en G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\fondos_16x9\\
3. 10 poses transparentes del avatar Guillermo en G:\\My Drive\\Avatar Guillermo - transparencias\\
   con scale=-1:780,format=rgba y overlay=W-w-40:H-h:format=auto.
4. Cálculo con ffprobe de la duración real del audio WAV y sincronización matemática de los 10 bloques.
5. Generación de subtítulos .srt y manifiesto JSON con hash SHA-256.
6. Copia final a Bóveda (03_MEDIA_VAULT_FINAL) y apertura automática.
"""

import os
import sys
import json
import time
import shutil
import hashlib
import argparse
import urllib.request
import subprocess
from datetime import datetime

# -------------------------------------------------------------
# 1. Configuración de Rutas
# -------------------------------------------------------------
PROD_DATE_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-25"
VOZ_DIR = os.path.join(PROD_DATE_DIR, "02_voz_guiahoy")
FONDOS_DIR = os.path.join(PROD_DATE_DIR, "fondos_16x9")
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"
LOCAL_STAGE_DIR = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\stage_2026_11_23\studio_vivo_final\mit_10min_v1_stage"

DEFAULT_VOICE_WAV = os.path.join(VOZ_DIR, "clase01_mit_10min_guiahoy_v1.wav")

OUT_NAME = "guiahoy_clase01_mit_10min_v1.mp4"
SRT_NAME = "guiahoy_clase01_mit_10min_v1.srt"
MANIFEST_NAME = "guiahoy_clase01_mit_10min_v1_manifest.json"

OUT_FINAL_PATH = os.path.join(PROD_DATE_DIR, OUT_NAME)
SRT_FINAL_PATH = os.path.join(PROD_DATE_DIR, SRT_NAME)
MANIFEST_FINAL_PATH = os.path.join(PROD_DATE_DIR, MANIFEST_NAME)
VAULT_FINAL_PATH = os.path.join(VAULT_DIR, OUT_NAME)

# -------------------------------------------------------------
# 2. Configuración de los 10 Bloques del Guion
# -------------------------------------------------------------
BLOCKS_CONFIG = [
    {
        "id": 1,
        "bg": "bg_01.jpg",
        "avatar": "avatar-pose-t-arms-open-narrower.png",
        "nom_start": 0.0,
        "nom_end": 55.0,
        "title": "MÓDULO 01: EL MOLDE REPRODUCIBLE",
        "subtitle": "Soberanía Tecnológica MIT & Ecosistema HBOS 2026"
    },
    {
        "id": 2,
        "bg": "bg_02.jpg",
        "avatar": "avatar-pose-t-calm-both.png",
        "nom_start": 55.0,
        "nom_end": 130.0,
        "title": "MÓDULO 02: COSTO CERO & INFRAESTRUCTURA",
        "subtitle": "Ahorro Radical para PYMEs y Universidades en Colombia"
    },
    {
        "id": 3,
        "bg": "bg_03.jpg",
        "avatar": "avatar-pose-t-chin-stroke-L.png",
        "nom_start": 130.0,
        "nom_end": 195.0,
        "title": "MÓDULO 03: MOTOR VECTORIAL RAG 768D",
        "subtitle": "Indexación Segregada con Cero Alucinación"
    },
    {
        "id": 4,
        "bg": "bg_04.jpg",
        "avatar": "avatar-pose-t-arms-open-palms-up.png",
        "nom_start": 195.0,
        "nom_end": 285.0,
        "title": "MÓDULO 04: AGENTES AUTÓNOMOS Y WORKFORCE",
        "subtitle": "Orquestación Multimodal y Calificación B2B Inmediata"
    },
    {
        "id": 5,
        "bg": "bg_05.jpg",
        "avatar": "avatar-pose-t-chin-stroke-R.png",
        "nom_start": 285.0,
        "nom_end": 355.0,
        "title": "MÓDULO 05: PIPELINE REA & INGENIERÍA INVERSA",
        "subtitle": "Extracción Autónoma de Patrones y Topologías de Código"
    },
    {
        "id": 6,
        "bg": "bg_06.jpg",
        "avatar": "avatar-pose-t-arms-open-wider.png",
        "nom_start": 355.0,
        "nom_end": 425.0,
        "title": "MÓDULO 06: MULTI-PLATAFORMA AUTÓNOMO",
        "subtitle": "Distribución Simultánea a Redes Sociales sin Programar"
    },
    {
        "id": 7,
        "bg": "bg_07.jpg",
        "avatar": "avatar-pose-t-calm-both.png",
        "nom_start": 425.0,
        "nom_end": 485.0,
        "title": "MÓDULO 07: AUDITORÍA CRIPTOGRÁFICA SHA-256",
        "subtitle": "Registro Inmutable y Certificación de Entregables"
    },
    {
        "id": 8,
        "bg": "bg_08.jpg",
        "avatar": "avatar-pose-t-arms-open-palms-front.png",
        "nom_start": 485.0,
        "nom_end": 535.0,
        "title": "MÓDULO 08: IMPACTO REAL EN ANTIOQUIA",
        "subtitle": "Transferencia de Conocimiento a PYMEs y Universidades"
    },
    {
        "id": 9,
        "bg": "bg_09.jpg",
        "avatar": "avatar-pose-t-both-thumbs-up.png",
        "nom_start": 535.0,
        "nom_end": 570.0,
        "title": "MÓDULO 09: MÉTRICAS Y RETORNO OPERATIVO",
        "subtitle": "-98.6% Tiempo de Ciclo y Margen Operativo +38.4%"
    },
    {
        "id": 10,
        "bg": "bg_10.jpg",
        "avatar": "avatar-pose-t-beckon-R.png",
        "nom_start": 570.0,
        "nom_end": 600.0,
        "title": "MÓDULO 10: CONCLUSIÓN & HOJA DE RUTA",
        "subtitle": "Mesa de Trabajo en Vivo · Guillermo Alonso Hoyos"
    }
]

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def is_qdrant_online():
    try:
        with urllib.request.urlopen("http://localhost:6333/collections", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

# -------------------------------------------------------------
# 3. Función Principal
# -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Ensamblador HBOS Clase 01 MIT V1")
    parser.add_argument("--voice-wav", default=DEFAULT_VOICE_WAV, help="Ruta obligatoria al audio WAV de voz")
    parser.add_argument("--dry-run", action="store_true", help="Audita activos y genera SRT/manifiesto sin lanzar ffmpeg")
    args = parser.parse_args()

    voice_wav_path = os.path.abspath(args.voice_wav)

    print("==========================================================")
    print("   HBOS ENGINE · ENSAMBLADOR CLASE 01 MIT V1 (PROYECTO NUEVO)")
    print("==========================================================")

    # 1. CONTROL ESTRICTO DE PISTA DE AUDIO
    print("\n[PASO 1/6] Auditoría Estricta de la Pista de Voz...")
    print(f"  Ruta esperada: {voice_wav_path}")

    if not os.path.isfile(voice_wav_path):
        os.makedirs(os.path.dirname(voice_wav_path), exist_ok=True)
        print("\n" + "=" * 72)
        print("[BLOQUEADO] PISTA DE VOZ NO ENCONTRADA")
        print("El proyecto nuevo exige una pista de voz validada antes de compilar.")
        print("No se encontró el archivo en la ruta esperada:")
        print(f"  -> {voice_wav_path}")
        print("\nInstrucciones para continuar:")
        print("1. Coloca tu archivo de voz grabado/clonado (.wav a 48 kHz / -14 LUFS) en:")
        print(f"   '{voice_wav_path}'")
        print("2. O ejecuta el script indicando la ruta directa de tu audio con:")
        print(f"   python .\\ensamblar_clase01_mit_v1.py --voice-wav \"<RUTA_DEL_AUDIO.wav>\"")
        print("=" * 72 + "\n")
        sys.exit(2)

    print(f"  [OK] Audio verificado: {os.path.basename(voice_wav_path)} ({os.path.getsize(voice_wav_path)} bytes)")

    # 2. MEDICIÓN REAL CON FFPROBE
    print("\n[PASO 2/6] Medición de duración real con ffprobe...")
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        voice_wav_path
    ]
    try:
        r_probe = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        real_duration = float(r_probe.stdout.strip())
    except Exception as e:
        print(f"[ERROR] Error al ejecutar ffprobe sobre el audio: {e}")
        sys.exit(1)

    print(f"  [OK] Duración exacta: {real_duration:.2f}s ({real_duration/60:.2f} min)")

    # Sincronización proporcional de los 10 bloques
    nominal_total = 600.0
    time_factor = real_duration / nominal_total

    blocks = []
    accum = 0.0
    for b in BLOCKS_CONFIG:
        d_nom = b["nom_end"] - b["nom_start"]
        d_real = d_nom * time_factor
        s_real = accum
        e_real = accum + d_real
        accum = e_real
        b_c = dict(b)
        b_c["real_start"] = s_real
        b_c["real_end"] = e_real
        b_c["real_duration"] = d_real
        blocks.append(b_c)
    blocks[-1]["real_end"] = real_duration
    blocks[-1]["real_duration"] = real_duration - blocks[-1]["real_start"]

    # 3. VERIFICACIÓN DE FONDOS 16:9 Y AVATARES TRANSPARENTES
    print("\n[PASO 3/6] Verificación de Fondos 16:9 y Poses Transparentes...")
    for b in blocks:
        bg_p = os.path.join(FONDOS_DIR, b["bg"])
        av_p = os.path.join(AVATAR_DIR, b["avatar"])
        if not os.path.isfile(bg_p):
            print(f"[ERROR] Falta fondo requerido: {bg_p}")
            sys.exit(1)
        if not os.path.isfile(av_p):
            print(f"[ERROR] Falta pose de avatar requerida: {av_p}")
            sys.exit(1)
        print(f"  [OK] Bloque {b['id']:02d}: {b['bg']} + {b['avatar']} ({b['real_duration']:.2f}s)")

    # 4. GENERACIÓN DE SUBTÍTULOS .SRT SINCRONIZADOS
    print(f"\n[PASO 4/6] Generando subtítulos sincronizados en: {SRT_FINAL_PATH}...")
    os.makedirs(os.path.dirname(SRT_FINAL_PATH), exist_ok=True)
    with open(SRT_FINAL_PATH, "w", encoding="utf-8") as f_srt:
        for b in blocks:
            f_srt.write(f"{b['id']}\n")
            f_srt.write(f"{format_srt_time(b['real_start'])} --> {format_srt_time(b['real_end'])}\n")
            f_srt.write(f"{b['title']} - {b['subtitle']}\n\n")
    print("  [OK] Subtítulos .srt generados.")

    if args.dry_run:
        print("\n[MODO DRY-RUN] Validación técnica completada con éxito. Cero llamadas pesadas de ffmpeg.")
        return

    # 5. RENDERIZADO MODULAR Y CONCATENACIÓN CON FFMPEG
    print("\n[PASO 5/6] Renderizado Modular de Video (1920x1080 @ 30fps)...")
    os.makedirs(LOCAL_STAGE_DIR, exist_ok=True)
    concat_list_path = os.path.join(LOCAL_STAGE_DIR, "concat_list_v1.txt")
    segment_files = []

    with open(concat_list_path, "w", encoding="utf-8") as f_concat:
        for b in blocks:
            bg_file = os.path.join(FONDOS_DIR, b["bg"])
            avatar_file = os.path.join(AVATAR_DIR, b["avatar"])
            seg_out = os.path.join(LOCAL_STAGE_DIR, f"seg_v1_{b['id']:02d}.mp4")
            dur = b["real_duration"]

            # Si ya existe con tamaño coherente (> 500 KB), reutilizarlo
            if os.path.exists(seg_out) and os.path.getsize(seg_out) > 500000:
                print(f"  [CACHE OK] Bloque {b['id']:02d} ya renderizado ({os.path.getsize(seg_out)} bytes).")
                f_concat.write(f"file '{seg_out.replace(os.sep, '/')}'\n")
                segment_files.append(seg_out)
                continue

            loc_bg = os.path.join(LOCAL_STAGE_DIR, f"bg_v1_{b['id']:02d}.jpg")
            loc_av = os.path.join(LOCAL_STAGE_DIR, f"av_v1_{b['id']:02d}.png")
            shutil.copy2(bg_file, loc_bg)
            shutil.copy2(avatar_file, loc_av)

            cmd_seg = [
                "ffmpeg", "-y",
                "-loop", "1", "-t", f"{dur:.3f}", "-i", loc_bg,
                "-loop", "1", "-t", f"{dur:.3f}", "-i", loc_av,
                "-filter_complex", "[1:v]scale=-1:780,format=rgba[av];[0:v][av]overlay=W-w-40:H-h:format=auto",
                "-t", f"{dur:.3f}",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "30",
                seg_out
            ]

            t0 = time.time()
            print(f"  [*] Codificando Bloque {b['id']:02d} ({dur:.2f}s)...")
            r_s = subprocess.run(cmd_seg, capture_output=True, text=True)
            if r_s.returncode != 0:
                print(f"[ERROR] Error al renderizar bloque {b['id']}:", r_s.stderr[-600:])
                sys.exit(1)
            print(f"      [OK] Bloque {b['id']:02d} renderizado en {time.time()-t0:.2f}s")

            f_concat.write(f"file '{seg_out.replace(os.sep, '/')}'\n")
            segment_files.append(seg_out)

    # Concatenar video
    concat_temp = os.path.join(LOCAL_STAGE_DIR, "video_concat_v1.mp4")
    print("\nConcatenando pistas de video con concat demuxer...")
    cmd_cat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", concat_temp]
    subprocess.run(cmd_cat, capture_output=True, text=True, check=True)

    # Mux final de video concatenado + pista de audio exclusiva
    local_final = os.path.join(LOCAL_STAGE_DIR, OUT_NAME)
    print("\nMuxing final con audio de voz exclusivo...")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", concat_temp,
        "-i", voice_wav_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", f"{real_duration:.3f}",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        local_final
    ]
    subprocess.run(cmd_mux, capture_output=True, text=True, check=True)

    # Copias a producción y bóveda final
    print(f"\nCopiando video final a Producción: {OUT_FINAL_PATH}...")
    shutil.copy2(local_final, OUT_FINAL_PATH)
    
    print(f"Copiando video final a Bóveda Final: {VAULT_FINAL_PATH}...")
    shutil.copy2(local_final, VAULT_FINAL_PATH)

    # 6. MANIFIESTO CRIPTOGRÁFICO SHA-256 E INDEXACIÓN
    print("\n[PASO 6/6] Generación de Manifiesto Criptográfico e Indexación...")
    h = hashlib.sha256()
    with open(OUT_FINAL_PATH, "rb") as f_h:
        for chunk in iter(lambda: f_h.read(65536), b""):
            h.update(chunk)
    sha256_hash = h.hexdigest()
    file_size = os.path.getsize(OUT_FINAL_PATH)

    manifest_data = {
        "title": "Clase 01 MIT V1 - El Molde Reproducible (GuíaHoy)",
        "file_name": OUT_NAME,
        "production_path": OUT_FINAL_PATH,
        "vault_path": VAULT_FINAL_PATH,
        "srt_path": SRT_FINAL_PATH,
        "voice_wav_path": voice_wav_path,
        "sha256": sha256_hash,
        "file_size_bytes": file_size,
        "duration_seconds": real_duration,
        "resolution": "1920x1080",
        "fps": 30,
        "blocks_count": 10,
        "status": "APPROVED_MASTER_CLASE_01_MIT_V1",
        "timestamp": datetime.now().isoformat()
    }

    with open(MANIFEST_FINAL_PATH, "w", encoding="utf-8") as f_man:
        json.dump(manifest_data, f_man, indent=2, ensure_ascii=False)
    print(f"  [OK] Manifiesto guardado en: {MANIFEST_FINAL_PATH}")

    # Registro en Qdrant
    if is_qdrant_online():
        try:
            point_id = "c1a5e003-0000-5000-8000-202611250003"
            vector_768 = [0.036] * 768
            body = json.dumps({
                "points": [
                    {
                        "id": point_id,
                        "vector": vector_768,
                        "payload": manifest_data
                    }
                ]
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:6333/collections/canon_video_hbos_r768/points?wait=true",
                data=body,
                headers={"Content-Type": "application/json"},
                method="PUT"
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status in (200, 201):
                    print(f"  [OK] Indexado en Qdrant ('canon_video_hbos_r768', ID: {point_id})")
        except Exception as e:
            print(f"  [!] Qdrant aviso: {e}")

    # Auto-Launch
    try:
        os.startfile(OUT_FINAL_PATH)
        print(f"[OK] Lanzador automático activado: {OUT_FINAL_PATH}")
    except Exception as e:
        print(f"[!] Aviso al lanzar reproductor: {e}")

    print("\n==========================================================")
    print("             ENSAMBLE V1 FINALIZADO CON ÉXITO             ")
    print("==========================================================")
    print(f"Ruta Final: {OUT_FINAL_PATH}")
    print(f"SHA-256:    {sha256_hash}")
    print(f"Tamaño:     {file_size} bytes ({file_size/(1024*1024):.2f} MB)")
    print(f"Subtítulos: {SRT_FINAL_PATH}")
    print(f"Manifiesto: {MANIFEST_FINAL_PATH}")

if __name__ == "__main__":
    main()
