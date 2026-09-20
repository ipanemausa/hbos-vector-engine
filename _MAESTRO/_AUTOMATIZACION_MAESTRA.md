# _AUTOMATIZACION_MAESTRA.md — Orquestación de APIs y Automatización sin Fricción
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 228 | **Fecha:** 2026-09-20 | **Versión:** v1.2 Profundizada | **Estado:** OPERATIVO · VAULT INTEGRADO  
> **Principio Rector:** Autonomía 24/7 sin intervención manual en expiración de tokens

---

## 1. Matriz de Conectividad OAuth2 y APIs

| Servicio | API / Endpoint | Función Automatizada | Mecanismo de Renovación |
| :--- | :--- | :--- | :--- |
| **YouTube** | YouTube Data API v3 | Subida autónoma de videos y Shorts con metadatos y thumbnails | Refresh Token persistido en VAULT |
| **Instagram / FB** | Graph API v19.0 | Publicación programada de reels y carruseles | Long-lived User Token (60 días auto-renovable) |
| **TikTok** | TikTok Content Posting API | Envío de clips verticales renderizados por Diamantino | OAuth2 PKCE con webhook de refresco |
| **LinkedIn** | Community Management API | Publicación de artículos técnicos y resúmenes ejecutivos | Access token renovado cada 60 días |
| **X / Twitter** | Twitter API v2 | Hilos automatizados con enlaces al video y timestamps | OAuth 1.0a / OAuth 2.0 App-only Bearer |
| **Gmail** | Google Workspace Gmail API | Dispersión de newsletters y confirmación de descargas | Service Account con Delegación de Dominio |
| **Google Drive** | Drive API v3 | Sincronización inmutable de réplicas en nube | Service Account con permisos de escritura |

---

## 2. Watchdog de Tokens bajo HBOS VAULT (§D)
- El Gateway :3002 incorpora un hilo de supervisión periódica que audita los tiempos de expiración (`exp`) de cada token.
- Si un token se encuentra a menos de 48 horas de caducar, el gateway ejecuta la rutina de intercambio con el endpoint de autenticación de Google/Meta sin detener los servicios en producción.
