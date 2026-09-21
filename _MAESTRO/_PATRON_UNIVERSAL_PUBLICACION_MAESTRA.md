# REGLA R50 · PATRÓN UNIVERSAL DE PUBLICACIÓN HBOS-DIAMANTINO
**Soberanía Multiplataforma · 10 Canales · 6 Pasos Inmutables**

## 1. PRINCIPIO FUNDAMENTAL (R50)
Toda publicación dentro del Ecosistema Soberano HBOS-Diamantino debe seguir obligatoria y estrictamente el Patrón Universal de 6 Pasos.
- **PROHIBIDO** publicar sin preview funcional.
- **PROHIBIDO** publicar sin aprobación biométrica soberana (Windows Hello / HBOSAuthUI).
- **PROHIBIDO** abrir pestañas intrusivas en el navegador externo (R32).
- URLs capturadas y verificadas por red.
- Registro inmutable en UNBE (Qdrant Cloud) y Triple Redundancia física garantizada al 100%.

---

## 2. EL CICLO UNIVERSAL DE 6 PASOS

```
[1. prepare_content] ──> [2. upload_draft] ──> [3. open_preview]
                                                      │
[6. capture_url]    <── [5. publish]      <── [4. wait_biometric_auth]
```

1. **`prepare_content(content)`**: Normalización de metadatos, verificación criptográfica SHA-256 de assets audiovisuales y cálculo de hash de integridad.
2. **`upload_draft(platform, content)`**: Despliegue del material en modo borrador privado (`draft`) sin indexación pública previa.
3. **`open_preview(draft_url)`**: Generación de URL de previsualización interna en la UI/consola soberana para inspección de calidad antes de cualquier salida.
4. **`wait_biometric_auth(platform)`**: Consulta de autenticación biométrica mediante `HBOSAuthUI`. Aplica token caché con TTL de 30 minutos (R37/R42) bajo el scope unificado `publish_session_master`.
5. **`publish(platform, content)`**: Promoción formal de borrador a estado público verificado.
6. **`capture_url(platform, public_url)`**: Extracción y almacenamiento de la URL definitiva, timestamp y estatus auditado en `publish_pattern_log.json`.

---

## 3. LAS 10 REDES INTEGRADAS

| ID | Red / Plataforma | Formato / Pipeline | Alcance |
|---|---|---|---|
| 1 | **YouTube** | Long-form 1080p / Shorts | Global Video Search & SEO |
| 2 | **Instagram** | Reels / Carousels | Social Visual Engagement |
| 3 | **TikTok** | Vertical High-Retention | Algorithmic Discovery |
| 4 | **X (Twitter)** | Thread + Media Clip | Real-Time AI News & Tech Dialogue |
| 5 | **LinkedIn** | Professional Article & Video | B2B, Institutional & AI Enterprise |
| 6 | **Facebook** | Watch Page & Community Feed | Mass Reach & Evergreen Shares |
| 7 | **Threads** | Conversational Micro-updates | Meta Direct Ecosystem |
| 8 | **Telegram** | Sovereign Channel Broadcast | Direct Community Distribution |
| 9 | **Discord** | Guild Server Announcements | Developer & Creator Deep Discussions |
| 10 | **GitHub** | Releases & Release Notes | Open Source Audit & Code Traceability |

---

## 4. INTEGRACIÓN TÉCNICA
- **Módulo Motor**: [`hbos_publish_pattern.py`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/hbos_publish_pattern.py)
- **Registro Auditor**: [`publish_pattern_log.json`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/publish_pattern_log.json)
- **Seguridad**: Windows Hello Fingerprint Token Cache (TTL: 1800s).
