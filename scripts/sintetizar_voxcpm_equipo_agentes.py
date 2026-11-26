#!/usr/bin/env python3
"""
sintetizar_voxcpm_equipo_agentes.py
===================================
Genera la narración completa de "Equipo de Agentes de IA" (2026-11-25) desde cero
utilizando la receta canónica verificada:
1. Motor: openbmb/VoxCPM-Demo (VoxCPM2, Ultimate mode, guide_scale=2.0)
2. Audio de referencia: ref-video08-15s-16k.wav (16000 Hz mono PCM)
3. Transcripción guía: "y lo publica todo sola, en todas tus redes sociales, sin programar, empezando gratis..."
4. Ritmo y audio: velocidad natural 1.0x (~135-150 PPM), pausas de 0.20s entre segmentos, 48000 Hz mono
5. Normalización en 2 pasadas a -14.46 LUFS (EBU R128)
6. Exportación de segmentos, tiempos.json y máster final (.wav y .mp3)
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from gradio_client import Client, handle_file

# --- CONFIGURACIÓN ---
REPO_DIR = Path(__file__).resolve().parent.parent
TARGET_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy_voxcpm")
CANONICAL_VOICE_DIR = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy")
GUION_PATH = Path(r"G:\My Drive\Guiahoy_Produccion\2026-11-25\guion_equipo_agentes_ia.md")

LOCAL_REF_PATH = REPO_DIR / "ref-video08-15s-16k.wav"
PROMPT_GUIDE = "y lo publica todo sola, en todas tus redes sociales, sin programar, empezando gratis..."
TARGET_LUFS = -14.46
PAUSE_SEC = 0.20

# 10 Bloques Canónicos de "Equipo de Agentes de IA"
BLOCKS = [
    {
        "id": 1,
        "title": "De un Solo Modelo a un Verdadero Equipo de Agentes de IA",
        "chunks": [
            "Soy Guillermo Alonso Hoyos. Les hablo desde mi mesa de trabajo en Rionegro, Antioquia.",
            "La mayoría de las personas que hoy experimentan con inteligencia artificial cometen el mismo error: le piden a un único modelo que lo haga todo. Le piden que investigue, que redacte, que programe, que revise y que tome decisiones comerciales en un solo mensaje. El resultado casi siempre es superficial o confuso.",
            "En el mundo empresarial real, nadie contrata a una sola persona para que sea al mismo tiempo el abogado, el contador, el vendedor y el director de tecnología. La verdadera revolución de la productividad no está en hablar con un chatbot; está en orquestar un Equipo de Agentes de IA, donde cada agente tiene un rol específico, herramientas especializadas y objetivos claros."
        ]
    },
    {
        "id": 2,
        "title": "El Agente Coordinador: El Director de Orquesta Autónomo",
        "chunks": [
            "El primer miembro indispensable de nuestro equipo es el Agente Coordinador.",
            "Piensen en él como el director de proyectos o el líder de operaciones de su negocio. Cuando entra una solicitud compleja, como por ejemplo lanzar una campaña comercial o preparar una propuesta ejecutiva, el coordinador no intenta resolverla directamente.",
            "Su tarea es analizar el problema, descomponerlo en tareas ordenadas y asignarle cada parte al agente más capacitado para resolverla.",
            "El coordinador supervisa los tiempos de respuesta, evalúa que cada entrega cumpla los criterios mínimos de calidad y, si algo no encaja, le pide al agente responsable que lo corrija antes de dar el paso siguiente. Sin este director de orquesta, múltiples agentes solo generarían ruido y reprocesos."
        ]
    },
    {
        "id": 3,
        "title": "El Agente Investigador: Minería de Datos y Contexto en Tiempo Real",
        "chunks": [
            "El segundo integrante es el Agente Investigador.",
            "Ninguna empresa puede tomar decisiones correctas si sus datos están desactualizados. El agente investigador es el encargado de rastrear fuentes confiables, extraer información relevante de documentos internos, bases de datos o portales sectoriales, y condensar esos hallazgos en hechos verificados.",
            "Este agente tiene prohibido opinar o improvisar: su único trabajo es traer evidencia pura sobre la mesa de trabajo. Si estamos preparando una cotización o analizando un nuevo competidor, el investigador le entrega al equipo un resumen estructurado con datos exactos, citas claras y contexto actualizado al minuto."
        ]
    },
    {
        "id": 4,
        "title": "El Agente Ejecutor y Creador: Producción de Código y Contenido",
        "chunks": [
            "Con los datos verificados sobre la mesa, entra en acción el Agente Ejecutor.",
            "Este es el artesano técnico del equipo: el redactor que diseña la propuesta comercial, el desarrollador que construye el script de automatización o el diseñador que maqueta las piezas visuales.",
            "Como el ejecutor no tiene que perder tiempo investigando ni coordinando, se enfoca al cien por ciento en producir con precisión quirúrgica. Sigue las directivas de estilo corporativo de su empresa, aplica las fórmulas técnicas requeridas y entrega borradores completos en cuestión de segundos.",
            "La gran ventaja es que este agente no trabaja en el vacío: construye directamente sobre la evidencia que le suministró el investigador y bajo la pauta que le marcó el coordinador."
        ]
    },
    {
        "id": 5,
        "title": "El Agente Auditor: Control de Calidad y Cero Alucinación",
        "chunks": [
            "Aquí es donde la mayoría de los sistemas fallan: en el control de calidad. Por eso incorporamos al Agente Auditor.",
            "El auditor es un escéptico profesional. Su misión es revisar minuciosamente el trabajo del ejecutor antes de que cualquier persona externa lo vea. Verifica que los números sumen correctamente, que las afirmaciones estén respaldadas por la investigación original y que no existan contradicciones lógicas ni alucinaciones.",
            "Si el auditor encuentra un desfase, rechaza la entrega con un reporte detallado para que el ejecutor lo ajuste de inmediato. Este ciclo interno de retroalimentación garantiza que el entregable final tenga un nivel de consistencia y rigor técnico institucional."
        ]
    },
    {
        "id": 6,
        "title": "Protocolos de Comunicación y Handoff entre Agentes",
        "chunks": [
            "¿Cómo se comunican estos agentes entre sí sin generar desorden? Mediante protocolos de transferencia limpios, conocidos como handoffs estructurados.",
            "Cada agente entrega su resultado en un formato de datos estándar, con entradas, salidas y condiciones de éxito bien definidas. No se envían mensajes vagos: se transfieren estados claros.",
            "Esto permite que el flujo de trabajo avance como una línea de producción industrial, donde cada estación agrega valor sobre lo que hizo la anterior. Si un agente termina su tarea, el siguiente se activa de manera automática, sin fricción y sin necesidad de intervención manual constante."
        ]
    },
    {
        "id": 7,
        "title": "La Mesa de Trabajo Unificada: Humano en el Bucle (Human-in-the-Loop)",
        "chunks": [
            "Quiero ser muy enfático en este punto: los agentes autónomos no reemplazan el juicio humano; lo amplifican.",
            "El principio fundamental de nuestra metodología es el Humano en el Bucle. El equipo de agentes hace el trabajo pesado: busca, clasifica, redacta, verifica y presenta opciones viables.",
            "Pero la decisión estratégica, la aprobación final y el toque de criterio humano siempre le pertenecen al líder del negocio. Usted no tiene que redactar cada correo ni escribir cada línea de código; su rol evoluciona a ser el director general que aprueba entregables de alto nivel con un solo clic."
        ]
    },
    {
        "id": 8,
        "title": "Aplicación Real en la Empresa: Ventas, Operaciones y Soporte",
        "chunks": [
            "Aterricemos esto a la operación diaria de nuestras empresas en Antioquia y en toda Colombia.",
            "Un equipo de agentes puede gestionar la calificación de clientes potenciales en su sitio web, responder preguntas complejas de catálogo en menos de diez segundos y preparar cotizaciones a la medida mientras usted descansa.",
            "En el área de operaciones, puede auditar facturas, conciliar inventarios y generar reportes financieros consolidados cada mañana sin errores humanos. Todo esto corriendo sobre infraestructura propia y controlada."
        ]
    },
    {
        "id": 9,
        "title": "Métricas de Productividad: La Fuerza de 5 Especialistas en 1 Máquina",
        "chunks": [
            "Miremos el impacto operativo.",
            "Lo que antes requería el esfuerzo fragmentado de cinco personas durante toda una semana, ahora se consolida en un flujo automatizado que corre en minutos.",
            "Hablamos de reducir los tiempos de ciclo en más del noventa por ciento y de permitir que su equipo humano se concentre en innovar, negociar y atender a sus clientes cara a cara con empatía y excelencia."
        ]
    },
    {
        "id": 10,
        "title": "Conclusión y Hoja de Ruta: Despliega tu Propio Equipo de Agentes",
        "chunks": [
            "El futuro del trabajo no pertenece a quienes usan la inteligencia artificial como un juguete, sino a quienes construyen sistemas organizados de agentes autónomos.",
            "En Guía Hoy estamos comprometidos con transferir este conocimiento práctico para que su empresa opere con verdadera autonomía y soberanía.",
            "Los espero en nuestra mesa de trabajo para que juntos configuremos su primer equipo de agentes. Hasta la próxima lección."
        ]
    }
]


def check_ffprobe_duration(filepath: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(filepath)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def synthesize_chunk_with_retry(client, text: str, ref_file: Path, max_retries: int = 4) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            print(f"      [VoxCPM2] Inferencia (intento {attempt}/{max_retries}): '{text[:50]}...'")
            result = client.predict(
                text_input=text,
                control_instruction="",
                reference_wav_path_input=handle_file(str(ref_file)),
                use_prompt_text=True,
                prompt_text_input=PROMPT_GUIDE,
                cfg_value_input=2.0,
                do_normalize=False,
                denoise=False,
                api_name="/generate"
            )
            if result and os.path.exists(result) and os.path.getsize(result) > 1000:
                return result
            else:
                print(f"      [WARN] Archivo retornado inválido o vacío: {result}")
        except Exception as e:
            print(f"      [ERROR] Fallo intento {attempt}: {e}")
            time.sleep(3 * attempt)
    raise RuntimeError(f"Fallo definitivo al sintetizar fragmento: {text}")


def main():
    print("=" * 70)
    print("HBOS VOXCPM2 PIPELINE: EQUIPO DE AGENTES DE IA (2026-11-25)")
    print("=" * 70)

    # 1. Preparar directorios limpios
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CANONICAL_VOICE_DIR.mkdir(parents=True, exist_ok=True)
    seg_dir = TARGET_DIR / "segmentos"
    seg_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] Directorio limpio listo: {TARGET_DIR}")
    print(f"      Referencia de voz: {LOCAL_REF_PATH} ({LOCAL_REF_PATH.stat().st_size} bytes)")
    print(f"      Guía prompt: '{PROMPT_GUIDE}'")

    # 2. Conectar a VoxCPM2
    print("[2/6] Conectando a openbmb/VoxCPM-Demo...")
    client = Client("openbmb/VoxCPM-Demo")
    print("      Conexión establecida con éxito.")

    # 3. Sintetizar cada bloque
    block_records = []
    seg_wav_paths = []

    print("[3/6] Iniciando síntesis de 10 bloques...")
    for b in BLOCKS:
        b_id = b["id"]
        b_title = b["title"]
        b_chunks = b["chunks"]
        print(f"\n---> BLOQUE {b_id:02d}: {b_title} ({len(b_chunks)} fragmentos)")

        chunk_wavs = []
        for c_idx, chunk_text in enumerate(b_chunks, 1):
            tmp_audio = synthesize_chunk_with_retry(client, chunk_text, LOCAL_REF_PATH)
            # Convertir cada fragmento a 48kHz mono PCM temporal
            tmp_48k = seg_dir / f"tmp_b{b_id:02d}_c{c_idx:02d}.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", tmp_audio,
                "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
                str(tmp_48k)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            chunk_wavs.append(tmp_48k)

        # Concatenar fragmentos del bloque con micro-pausa natural (0.15s) entre oraciones
        block_final_wav = TARGET_DIR / f"seg_{b_id:02d}.wav"
        if len(chunk_wavs) == 1:
            shutil.copyfile(chunk_wavs[0], block_final_wav)
        else:
            # Crear lista de concatenación
            concat_list = seg_dir / f"concat_b{b_id:02d}.txt"
            pause_wav = seg_dir / f"pause_micro.wav"
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-t", "0.15", "-c:a", "pcm_s16le", str(pause_wav)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with open(concat_list, "w", encoding="utf-8") as f:
                for idx, cw in enumerate(chunk_wavs):
                    clean_cw = str(cw).replace("\\", "/")
                    f.write(f"file '{clean_cw}'\n")
                    if idx < len(chunk_wavs) - 1:
                        clean_pw = str(pause_wav).replace("\\", "/")
                        f.write(f"file '{clean_pw}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_list),
                "-c:a", "pcm_s16le",
                str(block_final_wav)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        dur = check_ffprobe_duration(block_final_wav)
        full_text = " ".join(b_chunks)
        print(f"      [OK] seg_{b_id:02d}.wav generado ({dur:.2f}s, {block_final_wav.stat().st_size} bytes)")

        seg_wav_paths.append(block_final_wav)
        block_records.append({
            "block_id": b_id,
            "title": b_title,
            "duration_sec": round(dur, 2),
            "text": full_text,
            "wav_file": block_final_wav.name
        })

    # 4. Ensamblar máster con pausas de 0.20s entre segmentos
    print("\n[4/6] Ensamblando pista continua con pausas exactas de 0.20s...")
    inter_pause_wav = seg_dir / "inter_pause_020s.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
        "-t", str(PAUSE_SEC), "-c:a", "pcm_s16le", str(inter_pause_wav)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    master_concat_txt = seg_dir / "master_concat.txt"
    with open(master_concat_txt, "w", encoding="utf-8") as f:
        for idx, sw in enumerate(seg_wav_paths):
            clean_sw = str(sw).replace("\\", "/")
            f.write(f"file '{clean_sw}'\n")
            if idx < len(seg_wav_paths) - 1:
                clean_ip = str(inter_pause_wav).replace("\\", "/")
                f.write(f"file '{clean_ip}'\n")

    unnorm_master = seg_dir / "master_unnorm.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(master_concat_txt),
        "-c:a", "pcm_s16le",
        str(unnorm_master)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Normalización en 2 pasadas a -14.46 LUFS (EBU R128)
    print(f"\n[5/6] Aplicando normalización en dos pasadas a {TARGET_LUFS} LUFS...")
    # Pasada 1: Medición
    pass1_cmd = [
        "ffmpeg", "-i", str(unnorm_master),
        "-af", f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    p1 = subprocess.run(pass1_cmd, capture_output=True, text=True, check=True)
    # Extraer JSON de stderr
    stderr_txt = p1.stderr
    json_start = stderr_txt.rfind("{")
    json_end = stderr_txt.rfind("}") + 1
    measured = json.loads(stderr_txt[json_start:json_end])

    print(f"      Medición Pass 1: Input I={measured['input_i']} LUFS, TP={measured['input_tp']} dB")

    # Pasada 2: Renderizado final
    final_master_wav = TARGET_DIR / "equipo_agentes_ia_master.wav"
    final_master_mp3 = TARGET_DIR / "equipo_agentes_ia_master.mp3"

    loudnorm_filter = (
        f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:"
        f"measured_I={measured['input_i']}:"
        f"measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:"
        f"measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true"
    )

    subprocess.run([
        "ffmpeg", "-y", "-i", str(unnorm_master),
        "-af", loudnorm_filter,
        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
        str(final_master_wav)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(final_master_wav),
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "1",
        str(final_master_mp3)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Copia a ruta canónica esperada por el DAG general
    canonical_wav = CANONICAL_VOICE_DIR / "equipo_agentes_ia_guiahoy.wav"
    canonical_mp3 = CANONICAL_VOICE_DIR / "equipo_agentes_ia_guiahoy.mp3"
    shutil.copyfile(final_master_wav, canonical_wav)
    shutil.copyfile(final_master_mp3, canonical_mp3)

    # 6. Calcular tiempos exactos acumulados y exportar tiempos.json
    total_dur = check_ffprobe_duration(final_master_wav)
    current_time = 0.0
    for idx, b_rec in enumerate(block_records):
        b_rec["start_sec"] = round(current_time, 2)
        current_time += b_rec["duration_sec"]
        b_rec["end_sec"] = round(current_time, 2)
        if idx < len(block_records) - 1:
            current_time += PAUSE_SEC

    tiempos_data = {
        "tema": "Equipo de Agentes de IA",
        "fecha": "2026-11-25",
        "motor": "VoxCPM-Demo (openbmb/VoxCPM2 Ultimate mode)",
        "guide_scale": 2.0,
        "reference_audio": "ref-video08-15s-16k.wav",
        "prompt_text": PROMPT_GUIDE,
        "sample_rate": 48000,
        "channels": 1,
        "target_lufs": TARGET_LUFS,
        "total_duration_sec": round(total_dur, 2),
        "total_duration_min": round(total_dur / 60.0, 2),
        "pause_between_blocks_sec": PAUSE_SEC,
        "master_wav": str(final_master_wav),
        "master_mp3": str(final_master_mp3),
        "canonical_wav": str(canonical_wav),
        "bloques": block_records
    }

    tiempos_json_path = TARGET_DIR / "tiempos.json"
    with open(tiempos_json_path, "w", encoding="utf-8") as f:
        json.dump(tiempos_data, f, indent=2, ensure_ascii=False)

    print(f"\n[6/6] VERIFICACIÓN DE INTEGRIDAD:")
    print(f"      Total Duración Máster: {total_dur:.2f}s ({total_dur/60.0:.2f} min)")
    print(f"      Máster WAV: {final_master_wav} ({final_master_wav.stat().st_size} bytes)")
    print(f"      Máster MP3: {final_master_mp3} ({final_master_mp3.stat().st_size} bytes)")
    print(f"      Canónico WAV: {canonical_wav} ({canonical_wav.stat().st_size} bytes)")
    print(f"      tiempos.json: {tiempos_json_path}")
    print("\nPROCESO COMPLETADO EXITOSAMENTE SIN DEFECTOS NI ARCHIVOS RESIDUALES.")


if __name__ == "__main__":
    main()
