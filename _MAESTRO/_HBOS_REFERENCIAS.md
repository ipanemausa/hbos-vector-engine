

---

## Blindaje Daemon FreeLLMAPI (op=262, 2026-09-22T14:12:34.637959)

- **Tarea programada:** `HBOS-FreeLLMAPI-Daemon` · trigger at log on · restart 3x/1min · RunLevel Highest / User Namespace
- **Script daemon:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\start_freellmapi_daemon.py`
- **Chequeo ruidoso:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\hbos_verify_unbe.py` · falla con exit 1 si :3001 o :6333 caídos
- **Watchdog:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\hbos_watchdog.py` (opcional, ver bloque en blindaje)
- **Puertos:** FreeLLMAPI :3001 · Qdrant :6333
- **Verificación:** `Get-ScheduledTask -TaskName "HBOS-FreeLLMAPI-Daemon"` + `Get-NetTCPConnection -LocalPort 3001`


---

## Inyección de Providers FreeLLMAPI (op=266, 2026-09-22T18:00:38.787958)

- **Operación:** Inyección de API keys desde `.env.local` cifradas con AES-256-GCM idéntico a Node.js en FreeLLMAPI (`freeapi.db`).
- **Proveedores Activos:** OpenRouter (HTTP 200, 453 modelos), DashScope/ModelScope (HTTP 200), Google Gemini (HTTP 200, 50 modelos), HuggingFace (HTTP 200), Ollama Local (localhost:11434), Kilo, OVH, LLM7. Total: 8 plataformas.
- **Claves Omitidas por Fallo Previsto:** Groq (HTTP 401 revocada), Mistral (HTTP 401 placeholder).
- **Puertos Operativos:** FreeLLMAPI `:3001` (247 modelos activos) ⊕ HBOS-Unified-Gateway `:3002` (FastAPI/Uvicorn).
- **Verificación:** Inferencia activa en `:3001/v1/chat/completions` y `:3002/v1/chat/completions` con modelo auto-routing `gemini-2.5-flash`.
- **UNBE:** §1.0 CUMPLE AL 100%. Qdrant actualizado al rango 45 a 266.
