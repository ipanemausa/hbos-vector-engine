# _GATEWAY_FASE1_MAESTRA.md — Especificación de HBOS-Unified-Gateway (Fase 1)
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 224 | **Puerto:** 3001 | **Seguridad:** HBOS VAULT (AES-256-GCM)

---

## 1. Definición del Gateway
`HBOS-Unified-Gateway` es el punto de conmutación único del ecosistema:
- **URL Base:** `http://127.0.0.1:3001/v1`
- **Autenticación Soberana:** Cabecera obligatoria `Authorization: Bearer hbos-sec-...`
- **Enrutamiento Inteligente:** Dirige peticiones según tipo de tarea hacia modelos locales privados (Ollama en `:11434`), catálogo multi-proveedor (FreeLLMAPI con 235 modelos Zero-Config) o APIs directas de Google y Groq.

---

## 2. Endpoints Implementados en Fase 1
- `GET /v1/models`: Listado integral de modelos con capacidades (`supports_tools`, `supports_vision`) y límites de tasa.
- `POST /v1/chat/completions`: Inferencia de texto y ejecución de agentes con streaming y failover transparente.
- `POST /v1/embeddings`: Generación de vectores de 384 dimensiones.
- `GET /v1/vault/status`: Auditoría de cuotas en memoria RAM y estado de los proveedores externos.