"""Generate 10-block choreography JSON via live FreeLLMAPI router (zero hardcoded secrets)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

TIEMPOS_PATH = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\02_voz_guiahoy_voxcpm\tiempos.json"
)
OUT_JSON = Path(
    r"G:\My Drive\Guiahoy_Produccion\2026-11-25\equipo_agentes_v2_piloto\colab_3d_kit\v2_coreografia_10_bloques.json"
)

CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "openai/gpt-oss-120b",
    "command-a-03-2025",
    "glm-4.5-flash",
]


def call_freellmapi(model: str, prompt: str, key: str, base_url: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def extract_json_object(raw: str) -> dict:
    txt = raw.strip()
    if txt.startswith("```"):
        txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start = txt.find("{")
    end = txt.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("No JSON object found in FreeLLMAPI response")
    return json.loads(txt[start : end + 1])


def main() -> None:
    key = os.environ.get("FREELLMAPI_KEY") or Path("config/freellmapi-key.txt").read_text().strip()
    base_url = os.environ.get("FREELLMAPI_URL") or "http://127.0.0.1:3001"
    tiempos = json.loads(TIEMPOS_PATH.read_text(encoding="utf-8"))
    bloques_src = "\n".join(
        f"{b['block_id']} ({b['start_sec']}s-{b['end_sec']}s): {b['title']}"
        for b in tiempos["bloques"]
    )
    prompt = (
        "Eres el director escénico de Guía Hoy (Guillermo Alonso Hoyos, Rionegro, Antioquia).\n"
        "Tienes 5 poses oficiales de cuerpo entero transparentes con sonrisa natural:\n"
        "- 01_bienvenida\n- 02_senala_derecha\n- 03_pensativo_menton\n- 04_enfasis_tecnico\n- 05_saludo_cierre\n\n"
        f"Bloques reales del audio (414.28s):\n{bloques_src}\n\n"
        "Devuelve ÚNICAMENTE un JSON válido con la clave 'bloques' (lista exacta de 10 objetos). "
        "Cada objeto debe tener:\n"
        "- block_id (int 1..10)\n"
        "- pose_id (uno de los 5 anteriores)\n"
        "- ubicacion_pantalla ('izquierda' o 'derecha', dejando 90% del fondo 3D despejado)\n"
        "- gesto_humano (instrucción breve de manos/cabeza/respiración para animación neuronal)\n"
        "- subtitulo_lower_third (máximo 65 caracteres, claro y directo)"
    )

    errors = []
    for model in CANDIDATE_MODELS:
        try:
            raw = call_freellmapi(model, prompt, key, base_url)
            parsed = extract_json_object(raw)
            bloques = parsed.get("bloques", [])
            if len(bloques) != 10:
                raise ValueError(f"Expected 10 blocks, got {len(bloques)}")
            parsed["_meta"] = {"provider": "FreeLLMAPI", "model": model, "status": "PASS"}
            OUT_JSON.write_text(
                json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"PASS: choreography generated via FreeLLMAPI ({model}) -> {OUT_JSON}")
            return
        except Exception as exc:
            errors.append(f"{model}: {exc}")

    raise RuntimeError("BLOCKED: All FreeLLMAPI models failed: " + " | ".join(errors))


if __name__ == "__main__":
    main()
