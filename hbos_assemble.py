import subprocess
import os
import sys

CLIPS = [
    {
        "id": 1,
        "img": "assets/diamantino/generated/DIAMANTINO_ATOMO_01.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_01.wav",
        "out": "assets/diamantino/clips/ep01_plano_01.mp4",
        "zoom": "min(zoom+0.00035,1.18)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)"
    },
    {
        "id": 2,
        "img": "assets/diamantino/generated/DIAMANTINO_PARTICULAS_02.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_02.wav",
        "out": "assets/diamantino/clips/ep01_plano_02.mp4",
        "zoom": "min(zoom+0.00032,1.16)",
        "x": "iw/2-(iw/zoom/2)+sin(on/25)*35",
        "y": "ih/2-(ih/zoom/2)"
    },
    {
        "id": 3,
        "img": "assets/diamantino/generated/DIAMANTINO_ENERGIA_03.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_03.wav",
        "out": "assets/diamantino/clips/ep01_plano_03.mp4",
        "zoom": "min(zoom+0.00045,1.22)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)"
    },
    {
        "id": 4,
        "img": "assets/diamantino/generated/DIAMANTINO_CARBONO_02.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_04.wav",
        "out": "assets/diamantino/clips/ep01_plano_04.mp4",
        "zoom": "min(zoom+0.00035,1.16)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)-(on/450)*35"
    },
    {
        "id": 5,
        "img": "assets/diamantino/generated/DIAMANTINO_TRANSISTOR_01.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_05.wav",
        "out": "assets/diamantino/clips/ep01_plano_05.mp4",
        "zoom": "min(zoom+0.00045,1.24)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)"
    },
    {
        "id": 6,
        "img": "assets/diamantino/generated/DIAMANTINO_NUCLEO_01.png",
        "aud": "assets/diamantino/audio/ep01_voz_plano_06.wav",
        "out": "assets/diamantino/clips/ep01_plano_06.mp4",
        "zoom": "max(1.22-0.00045*on,1.0)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)"
    }
]

def render_clip(clip):
    print(f"[*] Procesando Plano {clip['id']} -> {clip['out']}...")
    filter_str = (
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=15:3,eq=brightness=-0.12[bg_blur];"
        f"[fg_in]zoompan=z='{clip['zoom']}':x='{clip['x']}':y='{clip['y']}':d=450:s=1080x1080:fps=30[fg_zoomed];"
        f"[bg_blur][fg_zoomed]overlay=(W-w)/2:(H-h)/2[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", clip["img"],
        "-i", clip["aud"],
        "-filter_complex", filter_str,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-t", "15.0",
        "-shortest",
        clip["out"]
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error en clip {clip['id']}: {res.stderr}")
        return False
    else:
        sz = os.path.getsize(clip["out"]) / (1024 * 1024)
        print(f"[OK] Plano {clip['id']} generado: {sz:.2f} MB")
        return True

def main():
    os.makedirs("assets/diamantino/clips", exist_ok=True)
    for c in CLIPS:
        render_clip(c)

if __name__ == "__main__":
    main()
