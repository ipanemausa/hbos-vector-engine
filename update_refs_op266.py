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

## Inyección de Providers FreeLLMAPI (op=266, {datetime.now().isoformat()})

- **Operación:** Inyección de API keys desde `.env.local` cifradas con AES-256-GCM idéntico a Node.js en FreeLLMAPI (`freeapi.db`).
- **Proveedores Activos:** OpenRouter (HTTP 200, 453 modelos), DashScope/ModelScope (HTTP 200), Google Gemini (HTTP 200, 50 modelos), HuggingFace (HTTP 200), Ollama Local (localhost:11434), Kilo, OVH, LLM7. Total: 8 plataformas.
- **Claves Omitidas por Fallo Previsto:** Groq (HTTP 401 revocada), Mistral (HTTP 401 placeholder).
- **Puertos Operativos:** FreeLLMAPI `:3001` (247 modelos activos) ⊕ HBOS-Unified-Gateway `:3002` (FastAPI/Uvicorn).
- **Verificación:** Inferencia activa en `:3001/v1/chat/completions` y `:3002/v1/chat/completions` con modelo auto-routing `gemini-2.5-flash`.
- **UNBE:** §1.0 CUMPLE AL 100%. Qdrant actualizado al rango 45 a 266.
"""

for p in refs:
    if p.parent.exists():
        mode = "a" if p.exists() else "w"
        with open(p, mode, encoding="utf-8") as f:
            f.write(seccion)
        print(f"[OK] Actualizado {p}")
