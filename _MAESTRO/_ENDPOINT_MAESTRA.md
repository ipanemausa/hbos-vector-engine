# _ENDPOINT_MAESTRA.md — Especificación de Arquitectura de Gateway Unificado
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Arquitectura:** HBOS-Unified-Gateway v1.0

---

## 1. Arquitectura de Gateway HBOS Unificado
El gateway unificado de HBOS proporciona un punto de entrada único que encapsula:
1. **Modelos Locales Soberanos:** Ollama (`localhost:11434`), LM Studio (`localhost:1234`), Jan AI.
2. **Modelos Router FreeLLMAPI:** Los 235 a 630+ modelos multiruta en `localhost:3001`.
3. **Modelos API Directa de Alta Disponibilidad:** Google Gemini Cloud Node y Groq Cloud Direct.

```
                   ┌────────────────────────────────────────────────────────┐
                   │               CLIENTE / AGENTE HBOS                   │
                   └───────────────────────────┬────────────────────────────┘
                                               │ HTTP / OpenAI Spec
                                               ▼
                   ┌────────────────────────────────────────────────────────┐
                   │           HBOS-UNIFIED-GATEWAY (Puerto 3001)           │
                   ├───────────────────────────┬────────────────────────────┤
                   │  Router de Prioridad      │  Gestor de Límites Cuotas  │
                   │  Fallback Transparente    │  Auditoría Telemetría      │
                   └───────┬───────────────────┼────────────────────┬───────┘
                           │                   │                    │
            ┌──────────────▼─────┐   ┌─────────▼──────────┐  ┌──────▼──────────────┐
            │   MODELOS LOCALES  │   │  FREELLMAPI ROUTER │  │  APIS DIRECTAS NUBE │
            │ (Ollama:11434, Jan)│   │ (235-630+ Modelos) │  │  (Gemini / Groq)    │
            └────────────────────┘   └────────────────────┘  └─────────────────────┘
```

---

## 2. Contrato de Interfaz OpenAI-Compatible
- **Endpoint Base:** `http://127.0.0.1:3001/v1`
- **Listado de Modelos:** `GET /v1/models` (Devuelve metadatos enriquecidos: proveedor, cuotas, context_window).
- **Inferencia de Texto y Agentes:** `POST /v1/chat/completions` (Soporte para tools, vision, streaming y JSON mode).
- **Embeddings:** `POST /v1/embeddings` (Redirigido a `gemini-embedding-001` o modelo local).