"""Build the 1-click $0 Google Colab T4 notebook for v2 full-body humanized avatar."""

from __future__ import annotations

import json
from pathlib import Path

NB_PATH = Path(
    r"G:\My Drive\Colab Notebooks\HBOS_Avatar_3D_Humano_V2_ColabT4.ipynb"
)


def md_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.splitlines()],
    }


def code_cell(code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.splitlines()],
    }


def main() -> None:
    cells = [
        md_cell(
            "# Guía Hoy v2 — Avatar Humanizado en Tiempo Real ($0 Costo · Colab T4 GPU)\n\n"
            "**Objetivo:** generar la animación humana real de Guillermo (cabeza, parpadeo, "
            "expresión, sonrisa natural y labios) sobre fondo Chroma `#00B140` usando GPU gratuita "
            "**Tesla T4** sin tarjeta ni suscripciones, y guardarla directo en tu Google Drive.\n\n"
            "**Pasos al abrir:** `Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU T4` → `Ejecutar todas`."
        ),
        code_cell(
            "# @title 1. Verificar GPU T4 gratuita y montar Google Drive\n"
            "import os, subprocess, sys\n"
            "from pathlib import Path\n"
            "\n"
            "!nvidia-smi\n"
            "from google.colab import drive\n"
            "drive.mount('/content/drive')\n"
            "\n"
            "KIT_DIR = Path('/content/drive/MyDrive/Guiahoy_Produccion/2026-11-25/equipo_agentes_v2_piloto/colab_3d_kit')\n"
            "OUT_DIR = Path('/content/drive/MyDrive/Guiahoy_Produccion/2026-11-25/equipo_agentes_v2_piloto/colab_3d_out')\n"
            "OUT_DIR.mkdir(parents=True, exist_ok=True)\n"
            "\n"
            "AUDIO_10S = KIT_DIR / 'piloto_10s_16k.wav'\n"
            "AUDIO_5S  = KIT_DIR / 'piloto_5s_16k.wav'\n"
            "IMG_UPPER = KIT_DIR / 'chroma_upper_01.png'\n"
            "IMG_FULL  = KIT_DIR / 'chroma_full_01.png'\n"
            "\n"
            "for p in [AUDIO_10S, AUDIO_5S, IMG_UPPER, IMG_FULL]:\n"
            "    assert p.exists(), f'FALTA ARCHIVO EN DRIVE: {p}'\n"
            "    print('OK:', p.name, f'{p.stat().st_size:,} bytes')\n"
        ),
        code_cell(
            "# @title 2. Motor Principal T4 (~1-2 min): Ditto-TalkingHead (PyTorch Nativo, compatible con T4)\n"
            "%cd /content\n"
            "!git lfs install\n"
            "!git clone -q https://github.com/antgroup/ditto-talkinghead.git /content/ditto-talkinghead || true\n"
            "%cd /content/ditto-talkinghead\n"
            "\n"
            "# Dependencias ligeras compatibles con T4 + PyTorch (sin requerir Ampere TensorRT)\n"
            "!pip install -q librosa tqdm filetype imageio opencv_python_headless scikit-image cython imageio-ffmpeg colored mediapipe transformers\n"
            "\n"
            "# Descargar pesos PyTorch + Config desde Hugging Face (solo lectura pública, sin token)\n"
            "!git clone -q https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints || true\n"
            "\n"
            "OUT_DITTO = str(OUT_DIR / 'guillermo_ditto_10s_chroma.mp4')\n"
            "!python inference.py \\\n"
            "  --data_root ./checkpoints/ditto_pytorch \\\n"
            "  --cfg_pkl ./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl \\\n"
            "  --audio_path \"{AUDIO_10S}\" \\\n"
            "  --source_path \"{IMG_UPPER}\" \\\n"
            "  --output_path \"{OUT_DITTO}\"\n"
            "\n"
            "assert Path(OUT_DITTO).exists(), 'Ditto no generó salida'\n"
            "print('PASS Ditto guardado en Drive:', OUT_DITTO, f'{Path(OUT_DITTO).stat().st_size:,} bytes')\n"
        ),
        code_cell(
            "# @title 3. (Opcional) Motor de Brazos y Manos: EchoMimicV2 clip 5s en T4 FP16\n"
            "# Nota: Si quieres probar movimiento completo de manos/brazos además de cabeza/rostro,\n"
            "# ejecuta esta celda (usa infer_acc.py optimizado para 15GB VRAM en clip corto de 5s).\n"
            "import torch, gc, yaml\n"
            "torch.cuda.empty_cache(); gc.collect()\n"
            "\n"
            "%cd /content\n"
            "!git clone -q https://github.com/antgroup/echomimic_v2.git /content/echomimic_v2 || true\n"
            "%cd /content/echomimic_v2\n"
            "!pip install -q -r requirements.txt\n"
            "!pip install -q --no-deps facenet_pytorch==2.6.0\n"
            "!git clone -q https://huggingface.co/BadToBest/EchoMimicV2 pretrained_weights || true\n"
            "\n"
            "cfg_path = Path('./configs/prompts/infer_acc.yaml')\n"
            "doc = yaml.safe_load(cfg_path.read_text())\n"
            "doc['test_cases'] = {'guillermo_01': [str(IMG_UPPER), str(AUDIO_5S)]}\n"
            "cfg_path.write_text(yaml.safe_dump(doc))\n"
            "\n"
            "!python infer_acc.py --config ./configs/prompts/infer_acc.yaml\n"
            "print('Revisa la carpeta ./output y copia el MP4 final a:', OUT_DIR)\n"
        ),
        code_cell(
            "# @title 4. Auditoría rápida con ffprobe y Previsualización en Colab\n"
            "from IPython.display import Video, display\n"
            "\n"
            "outs = sorted(OUT_DIR.glob('*.mp4'))\n"
            "assert outs, 'No se encontraron MP4 en colab_3d_out'\n"
            "for mp4 in outs:\n"
            "    print('=== AUDIT:', mp4.name, f'{mp4.stat().st_size:,} bytes ===')\n"
            "    !ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 \"{mp4}\"\n"
            "display(Video(str(outs[0]), embed=True, width=420))\n"
        ),
    ]

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10"},
            "accelerator": "GPU",
        },
        "cells": cells,
    }
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    NB_PATH.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: notebook created at {NB_PATH}")


if __name__ == "__main__":
    main()
