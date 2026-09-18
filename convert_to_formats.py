import os
import sys
import json
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

MASTER_SRC = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v3.mp4"
OUT_DIR = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\06_Publicado\formatos"
LOCAL_OUT_DIR = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\formatos"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOCAL_OUT_DIR, exist_ok=True)

if not os.path.exists(MASTER_SRC):
    print(f"[ERROR] No se encontró el master de entrada: {MASTER_SRC}")
    sys.exit(1)

FORMATS = [
    {
        "name": "ep02_master_v3_16x9.mp4",
        "label": "16:9 Landscape (YouTube, LinkedIn, Web)",
        "width": 1920,
        "height": 1080,
        "filter": "scale=1920:1080"
    },
    {
        "name": "ep02_master_v3_9x16.mp4",
        "label": "9:16 Vertical (TikTok, Reels, Shorts)",
        "width": 1080,
        "height": 1920,
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=4:1,scale=1080:1920:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    },
    {
        "name": "ep02_master_v3_1x1.mp4",
        "label": "1:1 Square (Instagram Feed)",
        "width": 1080,
        "height": 1080,
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:270:force_original_aspect_ratio=increase,crop=270:270,boxblur=4:1,scale=1080:1080:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1080:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    },
    {
        "name": "ep02_master_v3_4x5.mp4",
        "label": "4:5 Portrait (Instagram Portrait)",
        "width": 1080,
        "height": 1350,
        "filter": (
            "[0:v]split=2[bg_in][fg_in]; "
            "[bg_in]scale=270:338:force_original_aspect_ratio=increase,crop=270:338,boxblur=4:1,scale=1080:1350:flags=bicubic,eq=brightness=-0.15[bg]; "
            "[fg_in]scale=1080:1350:force_original_aspect_ratio=decrease[fg]; "
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    }
]

def convert_format(fmt):
    out_path = os.path.join(OUT_DIR, fmt["name"])
    local_path = os.path.join(LOCAL_OUT_DIR, fmt["name"])
    
    if os.path.exists(out_path) and os.path.getsize(out_path) > 30*1024*1024:
        size_bytes = os.path.getsize(out_path)
        size_mb = size_bytes / (1024 * 1024)
        print(f"[OK] Archivo existente verificado: {fmt['name']} ({size_mb:.2f} MB)")
        if not os.path.exists(local_path):
            shutil.copyfile(out_path, local_path)
        return {
            "formato": fmt["label"],
            "archivo": fmt["name"],
            "ruta": out_path,
            "bytes": size_bytes,
            "mb": round(size_mb, 2)
        }
        
    print(f"\n[*] Procesando {fmt['label']} -> {fmt['name']}...")
    
    if fmt["filter"].startswith("[0:v]"):
        cmd = [
            "ffmpeg", "-y",
            "-i", MASTER_SRC,
            "-filter_complex", fmt["filter"],
            "-map", "[v]",
            "-map", "0:a:0",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-movflags", "+faststart",
            out_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", MASTER_SRC,
            "-vf", fmt["filter"],
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-movflags", "+faststart",
            out_path
        ]
        
    subprocess.run(cmd, check=True)
    shutil.copyfile(out_path, local_path)
    
    size_bytes = os.path.getsize(out_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"[OK] {fmt['name']} generado: {size_mb:.2f} MB ({size_bytes} bytes)")
    return {
        "formato": fmt["label"],
        "archivo": fmt["name"],
        "ruta": out_path,
        "bytes": size_bytes,
        "mb": round(size_mb, 2)
    }

if __name__ == "__main__":
    print("==========================================================")
    print("CONVERSOR MULTI-FORMATO RESPONSIVE — HBOS-DIAMANTINO")
    print(f"Master Entrada: {MASTER_SRC}")
    print("==========================================================")
    
    results = []
    for fmt in FORMATS:
        res = convert_format(fmt)
        results.append(res)
        
    with open("formatos_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("\n==========================================================")
    print("[EXITO] Todos los formatos responsive fueron generados:")
    for r in results:
        print(f" - {r['formato']}: {r['ruta']} ({r['mb']} MB)")
    print("==========================================================")
