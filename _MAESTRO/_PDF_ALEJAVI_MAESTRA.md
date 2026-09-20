# _PDF_ALEJAVI_MAESTRA.md — Documentación Técnica del PDF ALEJAVI
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Fecha:** 2026-09-20 | **Regla de Oro:** §16.5 (Veracidad Estricta)

---

## 1. Declaración Formal de Estado de Localización
- **Estado del Archivo Físico (.pdf):** **NO LOCALIZADO EN REPOSITORIO LOCAL NI EN GOOGLE DRIVE**.
- **Acción Canónica adoptada:** De acuerdo con la Regla de Oro §16.5 (*"NO inventar. Si no se encuentra un dato, declararlo 'no verificado'"*), se declara formalmente que el archivo binario PDF suministrado por ALEJAVI queda pendiente de adjunto directo por el usuario.
- **Fuente Técnica Primaria Verificada:** Documentación técnica viva y base de datos de la versión oficial **FreeLLMAPI v0.11.0** instalada en `G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app` y telemetría de catálogo extraída directamente de `https://freellmapi.co/es/`.

---

## 2. Contenido Técnico Correlacionado con el Manual de FreeLLMAPI
1. **Definición del Sistema:**
   - Proxy inverso compatible con OpenAI v1 (`/v1/chat/completions`, `/v1/models`, `/v1/embeddings`).
   - Gestión multi-proveedor sin custodia de claves en servidores externos (auto-alojado en local o VPS).
2. **Estructura de Cuotas y Límites:**
   - Seguimiento por ventana de tiempo: RPM (Requests por minuto), RPD (Requests por día), TPM (Tokens por minuto), TPD (Tokens por día).
   - Cooldown automático: Al detectar error de cuota (HTTP 429), se activa un periodo de gracia en la tabla `rate_limit_cooldowns` sin interrumpir la experiencia del usuario, enrutando las peticiones a un modelo análogo.
3. **Catálogo de 34 Proveedores:**
   - Proveedores con modelos libres sin tarjeta: Groq, Cloudflare Workers AI, HuggingFace Inference API, Cohere, Google Gemini API, OpenRouter (modelos `:free`), Sambanova, Cerebras, GitHub Models, Zhipu, Kilo, ModelScope, etc.