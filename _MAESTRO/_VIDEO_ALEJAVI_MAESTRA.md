# _VIDEO_ALEJAVI_MAESTRA.md — Integración Canónica Video ALEJAVI
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Fecha:** 2026-09-20 | **Fuente:** https://youtu.be/7Oez8kmknOA  
> **Referencia Video:** ALEJAVI (17 sep 2026, 102,380 visualizaciones) | **Estado:** CURADO · COMPLETO · AUDITADO

---

## 1. Resumen Ejecutivo y Ficha Técnica
- **Video:** https://youtu.be/7Oez8kmknOA
- **Título de la emisión:** FreeLLMAPI: Router Universal de Inteligencia Artificial Gratuito, Agentes, Logging y Modelos Privados
- **Canal:** ALEJAVI (Modo Experto)
- **Fecha de publicación:** 17 de septiembre de 2026
- **Visualizaciones:** 102,380
- **Herramienta central:** FreeLLMAPI v0.11.0 (creada por Tashfeen Ahmed, Neu Software LLC)
- **Objetivo de integración HBOS:** Adoptar la arquitectura completa de router multimodelo, failover en cascada, auditoría horaria y soporte de agentes en UNBE.

---

## 2. Desglose Estructurado por Timestamps y Conceptos Operativos

### [00:00 - 05:12] Introducción y Problemática de Fragmentación de LLMs
- **Concepto:** Dispersión de cuotas gratuitas entre más de 30 proveedores (Groq, HuggingFace, Cloudflare, Google, Cerebras, Mistral, etc.).
- **Solución expuesta:** FreeLLMAPI como proxy único OpenAI-compatible que centraliza llaves y unifica las cuotas sin tarjeta de crédito.
- **Impacto HBOS:** Evita reconfigurar el software al agotarse un proveedor; el endpoint `http://127.0.0.1:3001/v1` actúa como pasarela transparente.

### [05:13 - 13:09] Instalación, Autenticación y Catálogo en Vivo
- **Concepto:** Distribución como aplicación de escritorio Electron y motor de base de datos local SQLite (`freeapi.db`).
- **Llave Unificada:** Generación automática de Bearer token `freellmapi-...` que da acceso instantáneo a todos los modelos habilitados.
- **Sincronización:** Catálogo vivo sincronizado mensualmente con el repositorio oficial (`https://freellmapi.co/`).

### [13:10 - 14:40] Estrategia de Enrutamiento (Routing Strategy)
- **Concepto:** Selección inteligente de modelos según `intelligence_rank`, `speed_rank` y tamaño de contexto.
- **Mecánica de Fallback:** Si un proveedor responde con error (HTTP 429 cuota excedida, 500 error interno, 503 sobrecarga), el router transfiere la consulta automáticamente al siguiente modelo de la tabla `fallback_config`.
- **Adopción HBOS:** Incorporación al orquestador `_HBOS_ORCHESTRATOR.md` de la lista de prioridad de fallbacks.

### [14:41 - 20:34] Agente de Inteligencia Artificial (AI Agent)
- **Concepto:** Exposición estándar compatible con OpenAI de herramientas (`supports_tools`) y visión multimodal (`supports_vision`).
- **Perfiles de Cliente:** Creación de `profiles` para segregar agentes de programación, agentes creativos y agentes de análisis de datos.
- **Adopción HBOS:** Vinculación directa con los 4 MCP servers del ecosistema diamantino.

### [20:35 - 23:38] Análisis, Telemetría y Registro (Analysis & Logging)
- **Concepto:** Tablas dedicadas en SQLite (`requests`, `request_hourly`, `request_attempts`, `server_logs`, `rate_limit_usage`).
- **Métricas registradas:** Latencia en ms, input tokens, output tokens, estado HTTP, proveedor utilizado y marca temporal.
- **Adopción HBOS:** Ingestión directa de estas métricas al vector store Qdrant (`hbos_metricas`).

### [23:39 - 25:08] Modelos Locales Privados (Private Local Models)
- **Concepto:** Emulación de Ollama y adición de endpoints privados locales (`localhost:11434`, LM Studio, Jan AI).
- **Soberanía HBOS:** Permite que tareas de máxima confidencialidad se resuelvan en local y tareas pesadas en nube sin modificar la API de llamada.

### [25:09 - 27:30] DeepSeek Harness
- **Concepto:** Harness de optimización para DeepSeek-R1 / V3 / V4_V5, aplicando gestión de tokens de razonamiento (`<think>...</think>`), clamping de temperatura y mitigación de repetición.
- **Adopción HBOS:** Integración con el MCP `openweight-models-hub`.

### [27:31 - 28:26] Aplicación Móvil (Mobile App)
- **Concepto:** Interfaz web adaptable PWA servida en LAN o mediante túneles seguros (Cloudflare Zero Trust / Tailscale).
- **Adopción HBOS:** Compatibilidad nativa con la interfaz diseñada en el Subproyecto App HBOS (Op 221).

### [28:27 - 29:15] Operación Continua 24/7 vía VPS
- **Concepto:** Despliegue del router en servidor virtual privado (VPS Linux) con `systemd`, PM2 o Docker, garantizando disponibilidad ininterrumpida.
- **Adopción HBOS:** El nodo de coordinación UNBE o un droplet de respaldo puede hospedar FreeLLMAPI permanentemente.

### [29:16 - 32:45] Ajustes Avanzados y Conclusiones
- **Concepto:** Ajustes de caché de respuestas (`response_cache`), idempotencia (`idempotency_claims`), y parámetros de cooldown de cuotas (`rate_limit_cooldowns`).