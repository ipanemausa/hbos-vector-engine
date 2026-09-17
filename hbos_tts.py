import asyncio
import os
import subprocess
import json
import edge_tts

VOICE = "es-ES-AlvaroNeural"
RATE = "-3%"
PITCH = "-2Hz"

PLANOS = [
    {
        "id": 1,
        "text": "Nos enseñaron que la materia es una lista plana de casillas cuadradas. Nos dijeron que el carbono era solo el número seis. Nos mintieron.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_01_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_01.wav",
        "duration": 15.0
    },
    {
        "id": 2,
        "text": "El átomo no es un sistema solar en miniatura. Es un resonador armónico. Y el diamante no es una piedra: es el superconductor supremo de la realidad.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_02_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_02.wav",
        "duration": 15.0
    },
    {
        "id": 3,
        "text": "Cuando ordenas los elementos por su frecuencia vibratoria y no por su masa inerte, la tabla periódica no es una cuadrícula: es una espiral de octavas musicales.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_03_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_03.wav",
        "duration": 15.0
    },
    {
        "id": 4,
        "text": "Mismo átomo. Mismo número atómico. Pero uno es polvo oscuro y el otro corta el acero y canaliza fotones cuánticos. La diferencia nunca fue el material: fue la estructura.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_04_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_04.wav",
        "duration": 15.0
    },
    {
        "id": 5,
        "text": "El silicio está llegando a su límite térmico. El futuro de la inteligencia artificial no correrá sobre arena fundida, correrá sobre matrices de cristal diamantino.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_05_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_05.wav",
        "duration": 15.0
    },
    {
        "id": 6,
        "text": "La tabla periódica no era el mapa del universo. Era solo la celda. Bienvenidos al Universo Diamantino.",
        "output_raw": "assets/diamantino/audio/ep01_voz_plano_06_raw.mp3",
        "output_wav": "assets/diamantino/audio/ep01_voz_plano_06.wav",
        "duration": 15.0
    }
]

async def generate_voice(plano):
    print(f"[*] Sintetizando Plano {plano['id']}...")
    communicate = edge_tts.Communicate(plano["text"], VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(plano["output_raw"])
    print(f"[+] Raw audio guardado: {plano['output_raw']}")

    # Now master with FFmpeg: 48kHz, pad/extend with silence up to 15.0s, apply subtle broadcast compression and eq
    # apad filter to ensure exactly 15.0s
    cmd = [
        "ffmpeg", "-y",
        "-i", plano["output_raw"],
        "-af", "apad=whole_dur=15.0,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "48000",
        "-ac", "2",
        "-t", "15.0",
        plano["output_wav"]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error procesando FFmpeg para plano {plano['id']}: {res.stderr}")
    else:
        print(f"[OK] Master WAV generado: {plano['output_wav']}")

async def main():
    os.makedirs("assets/diamantino/audio", exist_ok=True)
    for p in PLANOS:
        await generate_voice(p)

if __name__ == "__main__":
    asyncio.run(main())
