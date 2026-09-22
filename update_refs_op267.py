# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
refs = [
    BASE / "_HBOS_REFERENCIAS.md",
    BASE / "_MAESTRO" / "_HBOS_REFERENCIAS.md",
    BASE / "backup_hbos" / "_MAESTRO" / "_HBOS_REFERENCIAS.md"
]

seccion = f"""

---

## Completar Todas las APIs en FreeLLMAPI (op=267, {datetime.now().isoformat()})

- **Operación:** Recuperación de Groq (clave activa HTTP 200), GitHub Models e integración de 10 plataformas en `api_keys`.
- **Plataformas Activas (10):** `openrouter`, `modelscope`, `google`, `huggingface`, `ollama`, `kilo`, `ovh`, `llm7`, `groq`, `github`.
- **Inferencia Verificada:** Groq activo con `openai/gpt-oss-20b` (HTTP 200), Google `gemini-2.5-flash` (HTTP 200), OpenRouter activo.
- **Multimodalidad:** ElevenLabs validado con 21 voces (operativo en `step_fase2_voice.py`), Fal.ai auditado (vía Hugging Face router).
- **Puertos:** FreeLLMAPI `:3001` (247 modelos activos) ⊕ HBOS-Unified-Gateway `:3002`.
- **UNBE:** §1.0 CUMPLE AL 100%. Qdrant actualizado al rango 45 a 267.
"""

for p in refs:
    if p.parent.exists():
        mode = "a" if p.exists() else "w"
        with open(p, mode, encoding="utf-8") as f:
            f.write(seccion)
        print(f"[OK] Actualizado {p}")
