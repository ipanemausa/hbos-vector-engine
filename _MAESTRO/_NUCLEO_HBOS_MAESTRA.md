# _NUCLEO_HBOS_MAESTRA.md — Capa B: Identidad Operativa del Núcleo Técnico
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ PLAN DE ALTA Y CONFIGURACIÓN  
> **Canon:** Arquitectura Desacoplada (§D) · Capa B (Núcleo Operativo)

---

## 1. Definición y Alcance de la Capa B
La **Capa B (Núcleo)** es la identidad tecnológica aislada destinada a la operación interna y los servicios de backend:

* **Cuenta Principal:** `hbos@gmail.com`
  * *Alternativa de alta en caso de no disponibilidad en registro:* `hbos.soberano@gmail.com` o `hbos.engine@gmail.com`.
* **Naturaleza:** Cuenta puramente técnica para gobernanza de APIs, webhooks y monitoreo.
* **Funciones Exclusivas:**
  1. **Consolas de Desarrollador:** Google Cloud Platform (habilitación de APIs Drive, YouTube Data v3, Gemini Developer).
  2. **Recepción de Telemetría:** Alertas automatizadas emitidas por `hbos_watchdog.py` y reportes de fallo crítico.
  3. **Registro de Servicios MCP:** Enlace con servidores MCP desacoplados y credenciales OAuth de backend.
  4. **Colaboración GitHub:** Invitación como colaborador técnico con permisos de despliegue en repositorios.

---

## 2. Protocolo de Vinculación con Capa A (§D)
Para garantizar recuperación y gobernanza sin acoplamiento:
1. **Email de Recuperación:** Obligatoriamente configurado hacia `IPANEMAMARKETINGUSA@gmail.com` (Capa A).
2. **Teléfono de Recuperación:** Mismo dispositivo corporativo centralizado bajo la sombrilla.
3. **Google One Storage:** No contrata plan individual; recibe invitación de almacenamiento compartido (Familia / Grupo) desde la Capa A.
