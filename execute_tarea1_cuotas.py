import os
import sys
import json
import time
import datetime
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

el_key = os.getenv("ELEVENLABS_API_KEY")
ds_key = os.getenv("DASHSCOPE_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

results = {
    "tarea": "TAREA 1 — VERIFICAR RENOVACIÓN DE CRÉDITOS",
    "operation_id": 89,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "fase1_elevenlabs": {},
    "fase2_dashscope": {},
    "fase3_gemini": {},
    "fase4_conclusion": {}
}

# --- FASE 1: ElevenLabs ---
try:
    headers_el = {"xi-api-key": el_key}
    r_el = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=headers_el, timeout=15)
    if r_el.status_code == 200:
        sub = r_el.json()
        char_count = sub.get("character_count", 0)
        char_limit = sub.get("character_limit", 0)
        next_reset_unix = sub.get("next_character_count_reset_unix", 0)
        days_to_reset = max(0, round((next_reset_unix - time.time()) / 86400, 1)) if next_reset_unix else None
        quota_available = char_count < char_limit
        results["fase1_elevenlabs"] = {
            "status_code": 200,
            "character_count": char_count,
            "character_limit": char_limit,
            "caracteres_disponibles": max(0, char_limit - char_count),
            "cuota_disponible": "SÍ" if quota_available else "NO",
            "next_reset_unix": next_reset_unix,
            "next_reset_date": datetime.datetime.fromtimestamp(next_reset_unix, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC') if next_reset_unix else "N/A",
            "dias_hasta_renovacion": days_to_reset
        }
    else:
        results["fase1_elevenlabs"] = {
            "status_code": r_el.status_code,
            "cuota_disponible": "NO",
            "error": r_el.text[:200]
        }
except Exception as e:
    results["fase1_elevenlabs"] = {"error": str(e), "cuota_disponible": "NO"}

# --- FASE 2: DashScope (Wan 2.1) ---
try:
    # Solicitud mínima a Wan 2.1
    url_ds = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    headers_ds = {
        "Authorization": f"Bearer {ds_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    # Payload de prueba mínima
    payload_ds = {
        "model": "wan2.1-i2v-turbo",
        "input": {
            "img_url": "https://img.alicdn.com/imgextra/i2/O1CN01f4V8aX1Z3O9xZ8X6d_!!6000000003138-2-tps-1024-1024.png",
            "prompt": "gentle subtle cinematic movement test"
        }
    }
    r_ds = requests.post(url_ds, headers=headers_ds, json=payload_ds, timeout=20)
    status_code = r_ds.status_code
    body_ds = r_ds.json() if "application/json" in r_ds.headers.get("Content-Type", "") else r_ds.text
    
    if status_code == 200:
        results["fase2_dashscope"] = {
            "status_code": 200,
            "cuota_disponible": "SÍ",
            "output": body_ds
        }
    else:
        code_err = ""
        msg_err = ""
        if isinstance(body_ds, dict):
            code_err = body_ds.get("code", "")
            msg_err = body_ds.get("message", "")
        results["fase2_dashscope"] = {
            "status_code": status_code,
            "cuota_disponible": "NO",
            "code": code_err,
            "message": msg_err,
            "raw": str(body_ds)[:250]
        }
except Exception as e:
    results["fase2_dashscope"] = {"error": str(e), "cuota_disponible": "NO"}

# --- FASE 3: Gemini ---
try:
    url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
    r_gem = requests.get(url_gemini, timeout=15)
    if r_gem.status_code == 200:
        data_gem = r_gem.json()
        models_list = [m.get("name", "").replace("models/", "") for m in data_gem.get("models", [])]
        results["fase3_gemini"] = {
            "status_code": 200,
            "cuota_disponible": "SÍ",
            "total_modelos": len(models_list),
            "modelos_principales": [m for m in models_list if "gemini" in m][:10]
        }
    else:
        results["fase3_gemini"] = {
            "status_code": r_gem.status_code,
            "cuota_disponible": "NO",
            "error": r_gem.text[:200]
        }
except Exception as e:
    results["fase3_gemini"] = {"error": str(e), "cuota_disponible": "NO"}

# --- FASE 4: Conclusión ---
el_ok = results["fase1_elevenlabs"].get("cuota_disponible") == "SÍ" and results["fase1_elevenlabs"].get("caracteres_disponibles", 0) > 1000
ds_ok = results["fase2_dashscope"].get("cuota_disponible") == "SÍ"
gem_ok = results["fase3_gemini"].get("cuota_disponible") == "SÍ"

can_produce_ep04 = "SÍ" if (el_ok and ds_ok) else "NO"

results["fase4_conclusion"] = {
    "elevenlabs_cuota_actual": f"{results['fase1_elevenlabs'].get('character_count')}/{results['fase1_elevenlabs'].get('character_limit')} (Disponibles: {results['fase1_elevenlabs'].get('caracteres_disponibles')})",
    "dashscope_cuota_actual": f"Status {results['fase2_dashscope'].get('status_code')} - {results['fase2_dashscope'].get('code', 'N/A')}",
    "gemini_cuota_actual": f"Status {results['fase3_gemini'].get('status_code')} ({results['fase3_gemini'].get('total_modelos')} modelos)",
    "se_puede_producir_ep04": can_produce_ep04,
    "motivo_bloqueo": "Falta de cuota en DashScope (Wan 2.1) y/o ElevenLabs" if can_produce_ep04 == "NO" else "Cuotas activas"
}

print(json.dumps(results, indent=2, ensure_ascii=False))
