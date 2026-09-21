# _AUTOMATIZACION_MAESTRA.md - Arquitectura de Integracion OAuth y Dev Apps
> **Ecosistema Soberano HBOS-Diamantino . Modo Experto ALEJAVI**
> **Operacion:** 235 | **Canon:** FAM@-T v1.3 | **Capa:** D (§16.4)

---

## 1. Topologia de APIs Oficiales y Registro de Aplicaciones

| API / Consola | Scopes Requeridos | Destino de Credenciales |
|---|---|---|
| **Google Cloud (YouTube Data v3)** | youtube.upload, youtube.readonly | Vault HBOS (AES-256-GCM) |
| **Meta Developers (Instagram Graph)** | instagram_content_publish, pages_manage_posts | Vault HBOS (AES-256-GCM) |
| **TikTok for Developers** | video.upload, video.publish | Vault HBOS (AES-256-GCM) |
| **LinkedIn Developer Portal** | w_member_social, r_liteprofile | Vault HBOS (AES-256-GCM) |
| **X Developer Portal** | tweet.read, tweet.write | Vault HBOS (AES-256-GCM) |

---

## 2. Protocolo de Aislamiento de Secretos
- Las credenciales nunca se exponen en repositorios publicos ni variables sin cifrar.
- hbos_social_manager.py consume los tokens directamente del almacenamiento seguro cifrado.
