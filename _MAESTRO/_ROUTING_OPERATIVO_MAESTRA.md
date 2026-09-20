# _ROUTING_OPERATIVO_MAESTRA.md — Matriz de Enrutamiento Operativo (295 Reglas)
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 226 | **Estado:** OPERATIVO · EN PRODUCCIÓN EN :3002

---

## 1. Integración de las 295 Reglas en HBOS-Unified-Gateway
Las 295 reglas de fallback extraídas de la base de datos `freeapi.db` han sido cargadas en memoria del gateway en `routing_rules_295.json`:
- **Top 5 Reglas de Prioridad:**
  1. `gemini-2.5-flash` (google, prioridad 10)
  2. `glm-4.5-flash` (zhipu, prioridad 14)
  3. `codestral-latest` (mistral, prioridad 17)
  4. `gemini-2.5-flash-lite` (google, prioridad 19)
  5. `command-r-plus-08-2024` (cohere, prioridad 23)
- **Latencia de Conmutación:** Medida en < 350 ms ante retorno HTTP 429/500/503.