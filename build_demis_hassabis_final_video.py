"""
build_demis_hassabis_final_video.py — Ensamble Cinematográfico Maestro Ep04 (Demis Hassabis)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente en op=232 · Canon FAM@-T · No-Regresión (§7.3)
"""

import os
import sys
import subprocess
import shutil
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine"
EP04_DIR = os.path.join(BASE_DIR, "Ep04")
VOICES_DIR = os.path.join(EP04_DIR, r"03_Assets\Voces")
BGM_PATH = os.path.join(EP04_DIR, r"03_Assets\BGM\ep04_bgm_master.mp3")
CLIPS_WAN21_DIR = os.path.join(EP04_DIR, r"04_Clips_Wan21")
IMAGES_DIR = os.path.join(EP04_DIR, r"02_Storyboard\images_wan21")
OUTPUT_DIR = os.path.join(BASE_DIR, r"assets\videos")
OUTPUT_FINAL = os.path.join(OUTPUT_DIR, "demis_hassabis_final.mp4")
TEMP_DIR = os.path.join(BASE_DIR, "scratch_ep04_demis")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

PLANOS = [
    {
        "id": 0,
        "name": "plano_00_nota_referencia",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_00_voz.wav"),
        "video_wan": os.path.join(CLIPS_WAN21_DIR, "ep04_plano_00_wan21.mp4"),
        "img": os.path.join(IMAGES_DIR, "plano_00_nota_referencia.png"),
        "zoom": "in"
    },
    {
        "id": 1,
        "name": "plano_01_diamantino_intro",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_01_voz.wav"),
        "video_wan": os.path.join(CLIPS_WAN21_DIR, "ep04_plano_01_wan21.mp4"),
        "img": os.path.join(IMAGES_DIR, "plano_01_diamantino_intro.png"),
        "zoom": "slow_pan"
    },
    {
        "id": 2,
        "name": "plano_02_rubin",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_02_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_02_rubin.png"),
        "zoom": "in"
    },
    {
        "id": 3,
        "name": "plano_03_zafir",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_03_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_03_zafir.png"),
        "zoom": "out"
    },
    {
        "id": 4,
        "name": "plano_04_esmeralda",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_04_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_04_esmeralda.png"),
        "zoom": "in"
    },
    {
        "id": 5,
        "name": "plano_05_citrilo",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_05_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_05_citrilo.png"),
        "zoom": "out"
    },
    {
        "id": 6,
        "name": "plano_06_grafito",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_06_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_06_grafito.png"),
        "zoom": "in"
    },
    {
        "id": 7,
        "name": "plano_07_amatista",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_07_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_07_amatista.png"),
        "zoom": "out"
    },
    {
        "id": 8,
        "name": "plano_08_diamantino_recap",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_08_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_08_diamantino_recap.png"),
        "zoom": "in"
    },
    {
        "id": 9,
        "name": "plano_09_ensemble_cierre",
        "voice": os.path.join(VOICES_DIR, "ep04_bloque_09_voz.wav"),
        "img": os.path.join(IMAGES_DIR, "plano_09_ensemble_cierre.png"),
        "zoom": "out"
    }
]

def get_duration(media_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        media_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def main():
    print("==========================================================================")
    print(">>> PRODUCCIÓN CINEMATOGRÁFICA MASTER: DEMIS HASSABIS (EP04) <<<")
    print("==========================================================================")
    
    t0 = time.time()
    block_videos = []
    
    for p in PLANOS:
        idx = p["id"]
        v_dur = get_duration(p["voice"])
        print(f"\n[*] Procesando Plano {idx:02d} ({p['name']}): Duración de voz = {v_dur:.2f}s")
        
        block_out = os.path.join(TEMP_DIR, f"block_{idx:02d}.mp4")
        
        # Si tiene video Wan 2.1 ya renderizado (planos 0 y 1)
        if "video_wan" in p and os.path.exists(p["video_wan"]):
            wan_dur = get_duration(p["video_wan"])
            print(f"    - Clip Wan 2.1 detectado: {wan_dur:.2f}s")
            
            # Loop/extend video con loop y blend/crossfade para que cubra exactamente la voz
            loop_count = int(v_dur // wan_dur) + 2
            filter_loop = (
                f"[0:v]loop=loop={loop_count}:size=3000:start=0,"
                f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,"
                f"trim=duration={v_dur},setpts=PTS-STARTPTS[vout]"
            )
            cmd = [
                "ffmpeg", "-y", "-i", p["video_wan"], "-i", p["voice"],
                "-filter_complex", filter_loop,
                "-map", "[vout]", "-map", "1:a",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                block_out
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        else:
            # Planos con imagen estática en alta resolución + efecto Ken Burns cinematográfico
            img_path = p["img"]
            print(f"    - Generando movimiento cinematográfico Ken Burns desde imagen...")
            frames = int(v_dur * 30)
            
            if p.get("zoom") == "in":
                # Zoom suave hacia adentro
                vf = (
                    f"scale=2560:1440,zoompan=z='min(zoom+0.0008,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,"
                    f"trim=duration={v_dur},setpts=PTS-STARTPTS"
                )
            else:
                # Zoom suave hacia afuera
                vf = (
                    f"scale=2560:1440,zoompan=z='max(1.25-0.0008*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,"
                    f"trim=duration={v_dur},setpts=PTS-STARTPTS"
                )
                
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", p["voice"],
                "-vf", vf,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-shortest",
                block_out
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
        b_dur = get_duration(block_out)
        print(f"    [OK] Bloque {idx:02d} completado ({b_dur:.2f}s) -> {block_out}")
        block_videos.append(block_out)

    # Concatenar todos los bloques
    print("\n[*] Concatenando los 10 bloques sincronizados...")
    concat_list = os.path.join(TEMP_DIR, "concat_blocks.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for b in block_videos:
            f.write(f"file '{b.replace(chr(92), '/')}'\n")
            
    concat_raw = os.path.join(TEMP_DIR, "concatenated_raw.mp4")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        concat_raw
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    raw_dur = get_duration(concat_raw)
    print(f"[OK] Concatenación completa: {raw_dur:.2f}s (~{raw_dur/60:.2f} min)")

    # Mezcla final con música de fondo BGM (Ducking + EBU R128 -14 LUFS)
    print("\n[*] Mezclando audio con BGM master (Ducking al 18% + EBU R128)...")
    cmd_master = [
        "ffmpeg", "-y",
        "-i", concat_raw,
        "-i", BGM_PATH,
        "-filter_complex",
        f"[1:a]aloop=loop=-1:size=2e+09,volume=0.18,afade=t=out:st={raw_dur-5}:d=5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a_mix];"
        f"[a_mix]loudnorm=I=-14:TP=-1.0:LRA=11[a_norm]",
        "-map", "0:v", "-map", "[a_norm]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart",
        OUTPUT_FINAL
    ]
    subprocess.run(cmd_master, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    final_dur = get_duration(OUTPUT_FINAL)
    final_size = os.path.getsize(OUTPUT_FINAL)
    elapsed = time.time() - t0
    
    print("\n==========================================================================")
    print(f"[ÉXITO] VIDEO FINAL MASTERIZADO: {OUTPUT_FINAL}")
    print(f"  • Duración:      {final_dur:.2f} segundos (~{final_dur/60:.2f} minutos)")
    print(f"  • Tamaño:        {final_size:,} bytes ({final_size/(1024*1024):.2f} MB)")
    print(f"  • Resolución:    1920x1080 Full HD @ 30fps")
    print(f"  • Códec:         H.264 High Profile / AAC 320kbps 48kHz")
    print(f"  • Norma Audio:   EBU R128 (-14.0 LUFS, True Peak -1.0 dBTP)")
    print(f"  • Tiempo Render: {elapsed:.2f} segundos")
    print("==========================================================================")
    
    # Limpieza temporal opcional
    try:
        shutil.rmtree(TEMP_DIR)
        print("[*] Archivos temporales purgados exitosamente.")
    except Exception as e:
        print(f"[!] Nota limpieza: {e}")

if __name__ == "__main__":
    main()
