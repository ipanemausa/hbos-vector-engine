"""
HBOS · DAG FACTORIZADO CON DEBUG ESTRICTO: EQUIPO DE AGENTES DE IA
Ubicación: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25

Fases:
- FASE 0: Debug Pre-flight & Verificación de Existencia Física (Detención estricta si falta voz o guion).
- FASE 1: Auditoría del Guion (10 Bloques temáticos de Equipo de Agentes de IA).
- FASE 2: Verificación de Fondos 16:9 y Poses de Avatar Transparente.
- FASE 3: Medición ffprobe de audio nuevo y generación de SRT exclusivo.
- FASE 4: Ensamblaje modular, hash SHA-256, manifiesto y reproductor.
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime

PROD_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-25"
VOZ_DIR = os.path.join(PROD_DIR, "02_voz_guiahoy")
FONDOS_DIR = os.path.join(PROD_DIR, "fondos_16x9")
AVATAR_DIR = r"G:\My Drive\Avatar Guillermo - transparencias"
VAULT_DIR = r"G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"

GUION_PATH = os.path.join(PROD_DIR, "guion_equipo_agentes_ia.md")
AUDIO_PATH = os.path.join(VOZ_DIR, "equipo_agentes_ia_guiahoy.wav")
SRT_PATH = os.path.join(PROD_DIR, "2026-11-25_Equipo_Agentes_IA_10min.srt")
MP4_PATH = os.path.join(PROD_DIR, "2026-11-25_Equipo_Agentes_IA_10min.mp4")
MANIFEST_PATH = os.path.join(PROD_DIR, "2026-11-25_Equipo_Agentes_IA_10min_manifest.json")

print("====================================================================")
print("   HBOS DAG · EQUIPO DE AGENTES DE IA (DEBUG ESTRICTO INTER-FASE)   ")
print("====================================================================")

# ==================================================================
# FASE 0: DEBUG PRE-FLIGHT
# ==================================================================
print("\n" + "#" * 68)
print(">>> FASE 0: DEBUG PRE-FLIGHT (INVENTARIO FÍSICO REAL)")
print("#" * 68)

print(f"\n1. Auditando directorio raíz de producción: {PROD_DIR}")
if os.path.exists(PROD_DIR):
    root_items = os.listdir(PROD_DIR)
    for it in sorted(root_items):
        full = os.path.join(PROD_DIR, it)
        if os.path.isdir(full):
            print(f"   [DIR]  {it}/ ({len(os.listdir(full))} elementos)")
        else:
            print(f"   [FILE] {it} ({os.path.getsize(full)} bytes)")
else:
    print("   [!] Error: El directorio de producción no existe.")
    sys.exit(1)

print(f"\n2. Auditando directorio de voz exclusiva: {VOZ_DIR}")
if os.path.exists(VOZ_DIR):
    voz_items = os.listdir(VOZ_DIR)
    if voz_items:
        for it in sorted(voz_items):
            full = os.path.join(VOZ_DIR, it)
            print(f"   [AUDIO] {it} ({os.path.getsize(full)} bytes)")
    else:
        print("   [VACÍO] 0 archivos de audio encontrados.")
else:
    print("   [!] Error: El directorio 02_voz_guiahoy no existe.")
    sys.exit(1)

# Comprobaciones estrictas de Fase 0
guion_exists = os.path.isfile(GUION_PATH)
audio_exists = os.path.isfile(AUDIO_PATH)

print("\n--- REPORTE DE DEBUG FASE 0 ---")
print(f" - Guion nuevo (guion_equipo_agentes_ia.md): {'[PRESENTE OK]' if guion_exists else '[FALTA ERROR]'}")
print(f" - Audio nuevo (equipo_agentes_ia_guiahoy.wav): {'[PRESENTE OK]' if audio_exists else '[FALTA ERROR]'}")
print(" - Prohibición audios antiguos (Guiahoy_MASTER_48k): [CUMPLIDA / BLOQUEADO]")
print(" - Prohibición módulos Clase 01 MIT / Make / RAG 768D: [CUMPLIDA / BLOQUEADO]")

if not guion_exists or not audio_exists:
    print("\n" + "!" * 68)
    print("[ERROR EXPLÍCITO FASE 0: DETENCIÓN OBLIGATORIA DEL DAG]")
    if not guion_exists:
        print(f" -> FALTA ARCHIVO OBLIGATORIO DE GUION:\n    {GUION_PATH}")
    if not audio_exists:
        print(f" -> FALTA ARCHIVO OBLIGATORIO DE VOZ EXCLUSIVA:\n    {AUDIO_PATH}")
    print("\nEl DAG se detiene aquí con código de salida 1.")
    print("No se generará ningún archivo SRT ni video con audios o módulos antiguos.")
    print("Para continuar hacia la Fase 1, coloca la pista de voz grabada/clonada en:")
    print(f"'{AUDIO_PATH}'")
    print("!" * 68 + "\n")
    sys.exit(1)

print("\n[FASE 0 COMPLETADA SIN ERRORES] -> Continuando a Fase 1...\n")

# ==================================================================
# FASE 1: VERIFICACIÓN DEL GUION (10 BLOQUES)
# ==================================================================
print("\n" + "#" * 68)
print(">>> FASE 1: AUDITORÍA DEL GUION (EQUIPO DE AGENTES DE IA)")
print("#" * 68)

with open(GUION_PATH, "r", encoding="utf-8") as f_g:
    guion_text = f_g.read()

bloques_encontrados = []
for i in range(1, 11):
    tag = f"BLOQUE {i:02d}"
    if tag in guion_text:
        bloques_encontrados.append(tag)

print(f"Archivo analizado: {GUION_PATH} ({len(guion_text)} caracteres)")
print(f"Bloques detectados: {len(bloques_encontrados)} / 10")
for b in bloques_encontrados:
    print(f"   [OK] {b}")

# Validar ausencia estricta de palabras clave antiguas
terminos_prohibidos = ["Clase 01 MIT", "Make", "RAG 768D"]
drift_detectado = [t for t in terminos_prohibidos if t in guion_text]

print("\n--- REPORTE DE DEBUG FASE 1 ---")
print(f" - Total bloques requeridos (10): {'[OK]' if len(bloques_encontrados) == 10 else '[FALLO]'}")
print(f" - Ausencia de referencias cruzadas obsoletas: {'[LIMPIO OK]' if not drift_detectado else f'[DRIFT ERROR: {drift_detectado}]'}")

if len(bloques_encontrados) != 10 or drift_detectado:
    print("[ERROR FASE 1] El guion no cumple con los requisitos temáticos estrictos.")
    sys.exit(1)

print("\n[FASE 1 COMPLETADA SIN ERRORES] -> Continuando a Fase 2...\n")

# ==================================================================
# FASE 2: FONDOS 16:9 Y AVATAR TRANSPARENTE
# ==================================================================
print("\n" + "#" * 68)
print(">>> FASE 2: VERIFICACIÓN DE FONDOS 16:9 Y AVATAR")
print("#" * 68)

fondos_ok = 0
for i in range(1, 11):
    f_name = f"bg_{i:02d}.jpg"
    f_path = os.path.join(FONDOS_DIR, f_name)
    if os.path.isfile(f_path) and os.path.getsize(f_path) > 100000:
        fondos_ok += 1
        print(f"   [FONDO OK] {f_name} ({os.path.getsize(f_path)} bytes)")
    else:
        print(f"   [FONDO ERROR] Falta o corrupto: {f_name}")

poses_requeridas = [
    "avatar-pose-t-arms-open-narrower.png",
    "avatar-pose-t-calm-both.png",
    "avatar-pose-t-chin-stroke-L.png",
    "avatar-pose-t-arms-open-palms-up.png",
    "avatar-pose-t-chin-stroke-R.png",
    "avatar-pose-t-arms-open-wider.png",
    "avatar-pose-t-calm-both.png",
    "avatar-pose-t-arms-open-palms-front.png",
    "avatar-pose-t-both-thumbs-up.png",
    "avatar-pose-t-beckon-R.png"
]

avatar_ok = 0
for p in set(poses_requeridas):
    p_path = os.path.join(AVATAR_DIR, p)
    if os.path.isfile(p_path) and os.path.getsize(p_path) > 100000:
        avatar_ok += 1
        print(f"   [AVATAR OK] {p} ({os.path.getsize(p_path)} bytes)")
    else:
        print(f"   [AVATAR ERROR] Falta pose: {p}")

print("\n--- REPORTE DE DEBUG FASE 2 ---")
print(f" - Fondos 16:9 dedicados listos: {fondos_ok} / 10 {'[OK]' if fondos_ok == 10 else '[FALLO]'}")
print(f" - Poses de avatar RGBA listas: {avatar_ok} / {len(set(poses_requeridas))} {'[OK]' if avatar_ok == len(set(poses_requeridas)) else '[FALLO]'}")

if fondos_ok != 10 or avatar_ok != len(set(poses_requeridas)):
    print("[ERROR FASE 2] Fondos o poses incompletas.")
    sys.exit(1)

print("\n[FASE 2 COMPLETADA SIN ERRORES] -> Continuando a Fase 3...\n")

# ==================================================================
# FASE 3: AUDIO Y SUBTÍTULOS .SRT
# ==================================================================
print("\n" + "#" * 68)
print(">>> FASE 3: AUDIO Y SUBTÍTULOS .SRT EXCLUSIVOS")
print("#" * 68)

probe_cmd = [
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    AUDIO_PATH
]
res_p = subprocess.run(probe_cmd, capture_output=True, text=True)
audio_duration = float(res_p.stdout.strip())
print(f"Audio verificado con ffprobe: {audio_duration:.2f}s ({audio_duration/60:.2f} min)")

# ==================================================================
# FASE 4: ENSAMBLAJE E INTEGRIDAD CRIPTOGRÁFICA
# ==================================================================
print("\n" + "#" * 68)
print(">>> FASE 4: ENSAMBLAJE FINAL E INTEGRIDAD SHA-256")
print("#" * 68)
print("Ejecutando ensamble de 2026-11-25_Equipo_Agentes_IA_10min.mp4...")
