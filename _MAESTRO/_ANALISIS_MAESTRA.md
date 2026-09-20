# _ANALISIS_MAESTRA.md — Métricas, Telemetría y Exportación a Qdrant
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 20:35

---

## 1. Esquema de Telemetría en FreeLLMAPI
En `freeapi.db`, las métricas de uso se almacenan con granularidad de microsegundo:
- `requests`: id, timestamp, model_id, provider, input_tokens, output_tokens, latency_ms, status_code.
- `request_hourly`: agregación horaria para detección de cuellos de botella y picos de tráfico.
- `rate_limit_usage`: consumo acumulado frente a las cuotas máximas de cada plataforma.

---

## 2. Pipeline de Sincronización con `hbos_metricas`
Para cumplir con la gobernanza y auditoría del canon FAM@-T:
1. **Extracción:** Script de fondo o hook periódico que lee los registros de `requests` con status finalizado.
2. **Transformación:** Normalización a vector de telemetría de 384 dimensiones que incorpora latencia, tasa de compresión y costo marginal ($0.0).
3. **Carga Inmutable en Qdrant:** Inserción en la colección `hbos_metricas` vinculando cada consulta con su correspondiente `operation_id`.