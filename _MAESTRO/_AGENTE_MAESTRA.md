# _AGENTE_MAESTRA.md — Integración Agéntica y Tool Calling
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 14:41

---

## 1. Exposición del Agente en FreeLLMAPI
FreeLLMAPI expone una interfaz OpenAI completa que permite la ejecución de agentes autónomos:
- **Tool Calling (Function Calling):** Permite pasar el parámetro `tools` con esquema JSON. El router filtra exclusivamente aquellos modelos que posean `supports_tools = 1` en su catálogo.
- **Perfiles Agénticos (`client_profiles`):** Configuración de system prompts persistentes, límites de tokens y aislamiento de contexto.

---

## 2. Interacción con el Orquestador HBOS
El orquestador de agentes HBOS interactúa directamente con el endpoint local de FreeLLMAPI:
- **Protocolo de Llamada:**
  - `POST http://127.0.0.1:3001/v1/chat/completions`
  - `Authorization: Bearer freellmapi-...`
- **Integración con MCP Servers:** Los 4 MCP servers del ecosistema (`diamantini-imagenes`, `gdrive`, `hbos-diamantino`, `hbos-freellmapi`) proveen las herramientas que los modelos enrutados invocan de manera autónoma.