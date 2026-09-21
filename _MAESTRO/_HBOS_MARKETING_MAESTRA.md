# _HBOS_MARKETING_MAESTRA.md — Google Workspace 5TB, Email e Infraestructura Comercial
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 230 | **Fecha:** 2026-09-20 | **Estado:** 📋 PLAN CONCRETO DE ACTIVACIÓN CONSOLIDADO  
> **Email Base:** `ipanemamarketingusa@gmail.com` | **Tier Requerido:** Google Workspace Business Standard

---

## 1. Estado Actual y Diagnóstico Empírico
* **Cuenta Gmail Base:** `ipanemamarketingusa@gmail.com` activa y documentada.
* **Google Drive MCP:** Conexión validada y funcional vía protocolo MCP `gdrive`.
* **Capacidad Objetivo:** 5 TB de almacenamiento en la nube compartido (pooled storage) para alojar másters 4K/8K, renders de Wan 2.1 y backups del ecosistema.

---

## 2. Guía Paso a Paso de Activación Comercial

### Paso 1 · Acceso al Portal de Workspace
* Navegar a `https://workspace.google.com/pricing.html` o `admin.google.com`.
* Iniciar sesión con `ipanemamarketingusa@gmail.com`.

### Paso 2 · Selección de Plan Empresarial
* Seleccionar el plan **Business Standard**:
  * Costo: **$12.00 USD / mes** (facturación flexible) o $10.80 USD/mes (facturación anual).
  * Incluye: 5 TB de almacenamiento por usuario en Google Drive, reuniones de hasta 150 participantes con grabación y correo electrónico con dominio personalizado.

### Paso 3 · Configuración de Dominio y Seguridad SMTP
* Vincular dominio corporativo (ej. `ipanemamarketing.com` o subdominio `hbos.ai`).
* Configurar registros DNS: MX, SPF (`v=spf1 include:_spf.google.com ~all`) y DKIM para asegurar 100% de entregabilidad y evitar spam.
* Habilitar Verificación en Dos Pasos (2FA) y generar **Contraseña de Aplicación** (App Password) de 16 caracteres para que `hbos_unified_gateway.py` pueda enviar correos transaccionales automáticamente.

### Paso 4 · Gobernanza y Asignación
* **Responsable Asignado:** Titular comercial ALEJAVI.
* **Presupuesto Mensual:** $12.00 USD.
* **Fecha Estimada de Ejecución:** Ciclo mensual 2026-10-01.
