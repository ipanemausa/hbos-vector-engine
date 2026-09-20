# _MODELOS_LOCALES_MAESTRA.md — Modelos Privados Locales y Coexistencia Híbrida
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 23:39

---

## 1. Soporte de Modelos Locales en FreeLLMAPI
- **Plataforma `ollama`:** En `freeapi.db`, la plataforma Ollama está integrada nativamente (6 modelos registrados en BD local).
- **Ajuste `ollama_emulation`:** Permite conmutar la recepción de llamadas bajo el formato de Ollama (`/api/generate`, `/api/chat`) redirigiéndolas internamente al catálogo.
- **Conexión a Ollama Local:** Endpoint configurable a `http://127.0.0.1:11434`.

---

## 2. Coexistencia Soberana en HBOS
El ecosistema diamantino opera bajo una arquitectura híbrida de soberanía estricta:
- **Datos Críticos / Secretos / Personales:** Dirigidos al motor local (Ollama / Jan AI / LM Studio) con 0 filtración de datos fuera del hardware.
- **Cálculo Creativo / Razonamiento Masivo:** Dirigido a través de FreeLLMAPI a modelos de alto parámetro (70B, 120B, Gemini 2.5/Flash, DeepSeek R1).