# _AJUSTES_MAESTRA.md — Configuración Avanzada y Parámetros del Sistema
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 29:16

---

## 1. Ajustes Avanzados en Base de Datos (`settings`)
Valores auditados en el entorno activo:
- `embeddings_default_family`: `gemini-embedding-001`
- `unified_api_key`: `freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037`
- `active_profile_id`: `1`
- `ollama_emulation`: `off` (recomendado conmutar a `on` para compatibilidad transparente con clientes CLI de Ollama)
- `enable_mcp`: `0` (conmutable a `1` para exponer catálogo como servidor MCP directo)
- `catalog_applied_tier`: `monthly`
- `catalog_applied_version`: `2026.09.20`

---

## 2. Parámetros de Resiliencia Canónicos para HBOS
- **Response Cache:** Habilitar caché local en memoria para consultas idénticas de validación vectorial.
- **Idempotency Claims:** Prevención de doble ejecución en transacciones agénticas críticas.
- **Rate Limit Cooldown:** Cooldown exponencial (inicial 60s, máximo 3600s) tras recibir HTTP 429 de cualquier proveedor.