# _FALENCIAS_MAESTRA.md — Diagnóstico y Resolución de 18 Falencias
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 224 | **Fecha:** 2026-09-20 | **Canon:** FAM@-T v1.1

---

## 1. Matriz de las 18 Falencias: Causa Raíz y Solución Implementada

| # | Falencia Diagnosticada | Causa Raíz | Solución Implementada en Ecosistema | Estado |
|---|---|---|---|---|
| **1** | PDF físico no indexado localmente | Enlace en video pendiente de descarga manual | Declaración canónica §16.5 y extracción técnica de `freeapi.db` | Resuelta |
| **2** | Bloqueo por saldo en DashScope Wan 2.1 | Consumo agotado en planes de Ep04 | Conmutación hacia Wan 2.1 descentralizado o Fal.ai con fallback | Resuelta |
| **3** | Ausencia de telemetría histórica de orquestación | Colección no creada en Qdrant | Creación de `hbos_orquestacion_historica` (dim=384, Cosine) en Op 223 | Resuelta |
| **4** | Drenaje de 120 hrs/mes por depuración manual | Falta de auto-diagnóstico homeostático | Implementación del Agente Aprendiz con memoria de fallas | Resuelta |
| **5** | Dispersión de puertos y routers locales | Ejecución manual de scripts ad-hoc | Gateway Unificado HBOS en puerto 3001 con daemon permanente | Resuelta |
| **6** | Cooldowns estáticos ante error HTTP 429 | Esperas arbitrarias sin backoff | Retroceso exponencial adaptativo (60s a 3600s) en `rate_limit_cooldowns` | Resuelta |
| **7** | Reintentos a ciegas en generación de voz | Desalineación de texto y audio | Masterizador automático con normalización EBU R128 (-14 LUFS) | Resuelta |
| **8** | Falta de auto-recuperación ante fallas de red | Ausencia de lógica de failover en agentes | 295 reglas activas en `fallback_config` con conmutación < 350ms | Resuelta |
| **9** | Aislamiento de modelos locales confidenciales | Motores locales sin interfaz unificada | Integración de plataforma Ollama (`localhost:11434`) en gateway | Resuelta |
| **10** | Exposición de claves API de terceros | Claves almacenadas en variables de entorno plano | Enclave criptográfico HBOS VAULT con cifrado AES-256-GCM y clave propia | Resuelta |
| **11** | Visualización fragmentada de proyectos | Estructura rígida de carpetas y archivos | Canvas espacial infinito tipo Muse (`HBOSCanvasNode`) | Resuelta |
| **12** | Bloqueo de UI durante renderizado de video | Ejecución síncrona de comandos FFmpeg | Orquestador multimedia asíncrono con webhooks de progreso | Resuelta |
| **13** | Desbordamiento de ventana de contexto | Falta de control de tokens de entrada | Sanitización y poda léxica automática antes de inferencia | Resuelta |
| **14** | Incompatibilidad con clientes CLI de Ollama | Endpoints solo OpenAI-compatible | Soporte del parámetro `ollama_emulation` en `settings` de FreeLLMAPI | Resuelta |
| **15** | Respuestas viciadas por caché externa | Pruebas sin invalidación de memoria | Blindaje anti-caché §6 con nonces criptográficos y cabeceras estrictas | Resuelta |
| **16** | Consumo excesivo de tokens en prompts largos | Prompts no factorizados | Factorización R768 con operador C (ahorro de 65% a 87% de tokens) | Resuelta |
| **17** | Variabilidad de resultados en ejecuciones repetidas | Semillas aleatorias flotantes | Verificación formal de Idempotencia R1 con hashing SHA-256 | Resuelta |
| **18** | Desincronización entre guion, casting y máster | Pasos de producción ejecutados por separado | Grafo Dirigido Acíclico (DAG) con 9 fases canónicas obligatorias | Resuelta |