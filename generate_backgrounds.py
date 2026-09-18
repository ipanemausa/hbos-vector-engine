import os
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')

DRIVE_BASE = Path(r"G:\My Drive\HBOS-Diamantino")
LOCAL_BASE = Path(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine")
ARTIFACTS_DIR = Path(r"C:\Users\ipane\.gemini\antigravity-ide\brain\d81d4d69-f81d-4539-a5cd-9d522623d434")

# Mapeo de backgrounds generados por episodio
BACKGROUND_CATALOG = {
    "Ep02": {
        "dir_name": "Ep02-Los7Chips",
        "tema": "Los 7 Chips de Vera Rubin",
        "personaje": "Diamantino",
        "raw_img": ARTIFACTS_DIR / "ep02_bg_datacenter_1789759427874.jpg",
        "color_accent": "#00F0FF"
    },
    "Ep03": {
        "dir_name": "Ep03-RedesFotonicasCuanticas",
        "tema": "Redes Fotónicas Cuánticas y Spectrum-X",
        "personaje": "Amatista",
        "raw_img": ARTIFACTS_DIR / "ep03_bg_photonics_1789759439862.jpg",
        "color_accent": "#BD00FF"
    }
}

def process_and_save_background(ep_code):
    data = BACKGROUND_CATALOG.get(ep_code)
    if not data:
        raise ValueError(f"Episodio desconocido: {ep_code}")

    raw_path = data["raw_img"]
    if not raw_path.exists():
        raise FileNotFoundError(f"Archivo fuente de background no encontrado: {raw_path}")

    # Carpetas destino en Drive y Local
    dest_dirs = [
        DRIVE_BASE / data["dir_name"] / "02_Storyboard" / "backgrounds",
        LOCAL_BASE / data["dir_name"] / "02_Storyboard" / "backgrounds"
    ]
    for d in dest_dirs:
        d.mkdir(parents=True, exist_ok=True)

    print(f"[*] Procesando Background para {ep_code}: {data['tema']}...")
    img = Image.open(raw_path).convert("RGB")
    img_1080p = img.resize((1920, 1080), Image.Resampling.LANCZOS)

    # Versión con bokeh/blur suave para planos de diálogo
    img_bokeh = img_1080p.filter(ImageFilter.GaussianBlur(radius=8))

    outputs = []
    for d in dest_dirs:
        p_master = d / "bg_tematico_1080p.png"
        p_bokeh = d / "bg_tematico_bokeh_1080p.png"
        img_1080p.save(p_master, format="PNG", optimize=True)
        img_bokeh.save(p_bokeh, format="PNG", optimize=True)
        outputs.append((p_master, p_bokeh))

    print(f"[OK] {ep_code} Backgrounds guardados exitosamente:")
    print(f"     Master: {dest_dirs[0] / 'bg_tematico_1080p.png'} ({dest_dirs[0].stat().st_size if (dest_dirs[0] / 'bg_tematico_1080p.png').exists() else 0} bytes)")
    print(f"     Bokeh:  {dest_dirs[0] / 'bg_tematico_bokeh_1080p.png'}")
    return outputs

if __name__ == "__main__":
    for ep in ["Ep02", "Ep03"]:
        process_and_save_background(ep)
