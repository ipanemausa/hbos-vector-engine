# _ROUTING_MAESTRA.md — Estrategia de Enrutamiento Inteligente y Failover
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 13:10 | **Prioridad:** P0

---

## 1. Principio de Enrutamiento de FreeLLMAPI
El enrutamiento no es estático ni aleatorio; se rige por una matriz multi-dimensional:
1. **Costo:** Preferencia absoluta por tiers 100% gratuitos ($0.00 / 1M tokens).
2. **Capacidades Requeridas:** Verificación previa de banderas `supports_tools` y `supports_vision` según la petición.
3. **Métrica de Calidad / Velocidad:** Calificación por `intelligence_rank` (1 a 100) y `speed_rank` (1 a 100).
4. **Estado de Cuota:** Verificación en memoria del estado de cooldown antes de emitir la llamada HTTP.

---

## 2. Cadena de Fallback Canónica (Fallback Chain)
En la base de datos `freeapi.db`, existen 295 reglas de prioridad activas.
Cuando un modelo solicitado falla:
- **Paso 1:** Interceptación del código de retorno (429, 500, 502, 503, 504 o Timeout).
- **Paso 2:** Registro del evento en `request_attempts` y actualización de `rate_limit_cooldowns`.
- **Paso 3:** Selección del siguiente modelo en `fallback_config` con igual o superior `intelligence_rank`.
- **Paso 4:** Reintento transparente en menos de 350 ms.

---

## 3. Adopción en el Ecosistema HBOS
El orquestador de HBOS (`_HBOS_ORCHESTRATOR.md`) adopta este protocolo con la siguiente cascada de agentes:
1. **Nivel Primario (Velocidad / Herramientas):** `llama-3.3-70b-versatile` (Groq via FreeLLMAPI) / `gemma-4-26b-a4b-it` (Google Gemini API).
2. **Nivel Secundario (Razonamiento / Contexto Extendido):** `deepseek-chat` / `qwen-2.5-coder-32b` (HuggingFace/Cloudflare via FreeLLMAPI).
3. **Nivel de Respaldo Soberano:** Inferencia local privada vía Ollama (`llama3:latest` o `mistral:latest` en `http://localhost:11434`).