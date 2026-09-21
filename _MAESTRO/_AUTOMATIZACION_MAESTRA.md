# _AUTOMATIZACION_MAESTRA.md — Integración OAuth y Publicación Multicanal
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 230 | **Fecha:** 2026-09-20 | **Estado:** 📋 ROADMAP OAUTH PASO A PASO CONSOLIDADO  
> **Google Drive OAuth:** ✅ ACTIVO (Protocolo MCP gdrive) | **Redes Sociales:** Registro de Developer Apps

---

## 1. Estado Actual de Conectores OAuth
* **Google Drive OAuth:** ✅ Completamente operativo y verificado en la Capa 5 de persistencia mediante MCP `gdrive`.
* **APIs de Redes Sociales:** Mapeadas con permisos mínimos necesarios (Least Privilege) para evitar sobre-exposición de credenciales.

---

## 2. Guía de Creación de Aplicaciones de Desarrollador

### 1. YouTube Data API v3 (Google Cloud Console)
* **Portal:** `console.cloud.google.com`.
* **Proyecto:** `HBOS-Sovereign-Marketing`.
* **Habilitar API:** Buscar y habilitar *YouTube Data API v3*.
* **Credenciales:** Crear credencial tipo *OAuth 2.0 Client ID* (Aplicación web).
* **Scopes Requeridos:** `https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube.readonly`.
* **Almacenamiento:** Client ID y Client Secret cifrados en HBOS Vault (`AES-256-GCM`).

### 2. Meta for Developers (Instagram Graph API & Facebook Pages)
* **Portal:** `developers.facebook.com`.
* **Tipo de App:** Negocios (Business).
* **Productos:** Agregar *Instagram Graph API* y *Webhooks*.
* **Permisos Requeridos:** `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
* **Generación de Token:** Generar Token de Acceso de Usuario del Sistema (Larga duración / Never Expire).

### 3. TikTok for Developers
* **Portal:** `developers.tiktok.com`.
* **App:** Crear App bajo categoría *Content Posting API*.
* **Permisos:** `video.upload`, `video.publish`.

### 4. LinkedIn Developer Portal
* **Portal:** `linkedin.com/developers`.
* **Productos Asociados:** *Share on LinkedIn* y *Sign In with LinkedIn using OpenID Connect*.
* **Permisos:** `w_member_social`, `r_liteprofile`.

### 5. X Developer Portal (Twitter API v2)
* **Portal:** `developer.x.com`.
* **Tier:** Free Tier (Suficiente para publicación de tweets automatizados mediante endpoint `POST /2/tweets`).
* **Permisos de la App:** Read and Write.
* **Tokens:** API Key, API Key Secret, OAuth 2.0 Client ID y Secret.
