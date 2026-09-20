# _GATEWAY_OPERATIVO_MAESTRA.md — Manual de Operaciones HBOS-Unified-Gateway (Fase 1)
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 225 | **Fecha:** 2026-09-20 | **Puerto:** 3002 | **Estado:** OPERATIONAL · SOBERANO  
> **Gobernanza:** FAM@-T · LLMAPI ⊕ R768 · HBOS VAULT (AES-256-GCM) · UNBE (§1.0)

---

## 1. Resumen Ejecutivo del Servicio Operativo
En la Operación 225, el **HBOS-Unified-Gateway** ha sido formalmente construido, desplegado y verificado como un daemon permanente en el puerto **3002**, desacoplado del puerto 3001 para coexistir en armonía con FreeLLMAPI sin conflictos de socket.

- **Servicio:** `hbos_unified_gateway.py` (FastAPI / Uvicorn)
- **Lanzador Daemon:** `start_gateway_daemon.py`
- **Configuración:** `gateway_config.json`
- **URL Base:** `http://localhost:3002/v1`
- **Total de Modelos Expuestos:** **239 modelos** activos (235 FreeLLMAPI Zero-Config + 2 Locales Ollama + 2 Google Cloud Node).

---

## 2. Especificación de Endpoints y Resultados Empíricos (curl)

### A. Health Check: `GET /health`
```bash
curl -s http://localhost:3002/health
```
**Respuesta:**
```json
{"status": "healthy", "service": "HBOS-Unified-Gateway", "port": 3002}
```

### B. Listado de Modelos: `GET /v1/models`
```bash
curl -s http://localhost:3002/v1/models -H "Authorization: Bearer hbos-sec-0199f8a2c4e6b8d0"
```
**Respuesta Verificada (239 modelos):**
```json
{
  "object": "list",
  "data": [
    {"id": "auto", "object": "model", "owned_by": "freellmapi-router"},
    {"id": "gemini-3.6-flash", "object": "model", "owned_by": "freellmapi-router"},
    "...",
    {"id": "ollama/llama3:latest", "object": "model", "owned_by": "hbos-local-ollama"},
    {"id": "ollama/mistral:latest", "object": "model", "owned_by": "hbos-local-ollama"},
    {"id": "google/gemma-4-26b-a4b-it", "object": "model", "owned_by": "hbos-google-cloud-node"},
    {"id": "google/gemini-flash-latest", "object": "model", "owned_by": "hbos-google-cloud-node"}
  ]
}
```

### C. Chat Completions: `POST /v1/chat/completions`
```bash
curl -s -X POST http://localhost:3002/v1/chat/completions \
  -H "Authorization: Bearer hbos-sec-0199f8a2c4e6b8d0" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemma-4-26b-a4b-it","messages":[{"role":"user","content":"ping"}],"max_tokens":10}'
```
**Respuesta Verificada:**
```json
{
  "id": "chatcmpl-e597050da77f",
  "object": "chat.completion",
  "created": 1789928115,
  "model": "gemma-4-26b-a4b-it",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "pong\n"},
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 4, "completion_tokens": 4, "total_tokens": 8},
  "hbos_metadata": {
    "provider": "google_cloud_node",
    "latency_ms": 1519.35,
    "sha256": "486ada706af118291a6e464c66d3e3257866d55485c0371880fe86320ebde3be",
    "sovereign_gateway": "HBOS-Unified-Gateway:3002"
  }
}
```

### D. Embeddings: `POST /v1/embeddings`
```bash
curl -s -X POST http://localhost:3002/v1/embeddings \
  -H "Authorization: Bearer hbos-sec-0199f8a2c4e6b8d0" \
  -H "Content-Type: application/json" \
  -d '{"input":"Ecosistema Soberano HBOS-Diamantino"}'
```
**Respuesta Verificada:**
- **Dimensiones:** 384d (normalizado L2)
- **Latencia:** 0.08 ms

### E. Estado del Enclave: `GET /v1/vault/status`
```bash
curl -s http://localhost:3002/v1/vault/status -H "Authorization: Bearer hbos-sec-0199f8a2c4e6b8d0"
```
**Respuesta Verificada:**
```json
{
  "status": "OPERATIONAL · SOBERANO",
  "vault_enclave": {
    "algorithm": "AES-256-GCM",
    "cifrado_en_reposo": "AES-256-GCM activo",
    "descifrado_efimero_ram": "Habilitado (L-27)",
    "sovereign_tokens_active": 2
  },
  "upstreams_connected": {
    "freellmapi": "http://127.0.0.1:3001/v1 (235 modelos Zero-Config)",
    "gemini_cloud_node": "https://generativelanguage.googleapis.com (Gemma 4 / Flash)",
    "ollama_local": "http://127.0.0.1:11434"
  },
  "telemetry_qdrant": {
    "state": "connected (18 cols)",
    "collection": "hbos_metricas"
  },
  "port": 3002,
  "operation_id": 225
}
```

### F. Auditoría de Seguridad (401 / 403)
- Petición sin cabecera `Authorization`: `HTTP 401 Unauthorized`
- Petición con clave no autorizada: `HTTP 403 Forbidden`

---

## 3. Integración con HBOS VAULT (Cifrado AES-256-GCM)
1. **Aislamiento de Credenciales:** Clientes y agentes de Antigravity interactúan exclusivamente con el token soberano `hbos-sec-...`.
2. **Cifrado en Memoria:** Las API keys externas se resguardan cifradas con **AES-256-GCM** y se descifran en memoria volátil efímera (RAM) en el milisegundo previo a la llamada saliente.
3. **Destrucción de Búfer:** Sobreescritura inmediata con ceros tras la recepción de la respuesta.