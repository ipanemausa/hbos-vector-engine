# _FREELMAPI_FIX_MAESTRA.md — Daemon FreeLLMAPI Soberano y Conexión MCP
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 228 | **Fecha:** 2026-09-20 | **Puerto:** 3001 | **Estado:** OPERATIONAL · VERIFICADO  
> **Marco Canónico:** FAM@-T · LLMAPI ⊕ R768 · DAG · H_ALT · NO-REGRESIÓN (v1.1) · §D (Arquitectura Desacoplada)

---

## 1. Diagnóstico y Causa Raíz
- **Incidente:** El servidor MCP `hbos-freellmapi` reportaba `fetch failed` al invocar `list_models` o `chat`.
- **Causa:** El binario desktop Electron de FreeLLMAPI (`FreeLLMAPI.exe` en `G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app`) no se encontraba activo como daemon permanente en segundo plano en el puerto `3001`.
- **Solución Canónica:** Se configuró y levantó el daemon `start_freellmapi_daemon.py` como soporte desatendido permanente en el puerto 3001, coexistiendo de forma desacoplada con el HBOS Gateway en el puerto 3002.

---

## 2. Verificación Empírica
- **Puerto:** `127.0.0.1:3001` (TCP Listen Activo).
- **Endpoint:** `GET http://127.0.0.1:3001/v1/models`.
- **Modelos Disponibles:** 235 modelos expuestos a costo marginal cero ($0/mes).
- **MCP Bridge:** Herramienta `list_models` de `hbos-freellmapi` probada y respondiendo con catálogo completo de modelos (Auto, Fusion, Gemini, DeepSeek, Claude, Mistral, OpenAI).

---

## 3. Arquitectura Desacoplada (§D)
- **Capa 1 (Agente):** Invocación transparente de herramientas MCP sin dependencias cruzadas.
- **Capa 2 (Gateway):** Gateway :3002 enruta peticiones hacia FreeLLMAPI :3001 como proveedor primario de costo cero con fallback automático hacia Ollama :11434 y Google Cloud.
