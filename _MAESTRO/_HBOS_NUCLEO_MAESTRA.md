# _HBOS_NUCLEO_MAESTRA.md — Protocolo de Identidad y Cuenta del Núcleo Operativo
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ PROTOCOLO DE ALTA ESTABLECIDO  
> **Canon:** FAM@-T · Arquitectura Desacoplada (§D) · Capa B (Núcleo) · H_ALT Naming

---

## 1. Misión de la Cuenta del Núcleo Operativo (Capa B)
La cuenta del núcleo técnico `hbos` tiene como propósito exclusivo ser la identidad de infraestructura del ecosistema:

* **Separación de Capas (§D):**
  * **Capa A (Sombrilla):** `IPANEMAMARKETINGUSA@gmail.com` $\rightarrow$ Contratación, facturación, Google Ads, titularidad legal.
  * **Capa B (Núcleo):** `hbos@gmail.com` (o fallback canónico) $\rightarrow$ Google Cloud Console, tokens de backend, webhooks de telemetría, GitHub colaborador técnico.
* **Prohibición:** La cuenta del núcleo no se utiliza para suscripciones personales ni para campañas de marketing de cara al público.

---

## 2. Resolución Dialéctica H_ALT para el Naming del Email (§7.2, §7.3)
Dado que los nombres de 4 letras directos como `hbos@gmail.com` pueden encontrarse reservados o restringidos en autoservicio por Google, se establece la jerarquía formal de registro:

| Variante | Dirección de Correo | Evaluación M1–M7 | Estado H_ALT |
| :--- | :--- | :---: | :--- |
| **Intento 1 (Primaria)** | `hbos@gmail.com` | `99.0 / 100` | Prioridad absoluta al momento de registro en consola |
| **ALT_A** | `hbos.diamantino@gmail.com` | `96.5 / 100` | Descartada (acopla el nombre de la mascota al backend) |
| **ALT_B** | `hbos.marketing@gmail.com` | `95.8 / 100` | Descartada (genera confusión con la Capa A Sombrilla) |
| **ALT_C** | `hbos.ecosystem@gmail.com` | `98.2 / 100` | Excelente neutralidad técnica y alcance internacional |
| **ALT_D** | `hbos.soberano@gmail.com` | `97.0 / 100` | Connotación canónica alta, pero restringida a español |

### Síntesis Dialéctica D Adoptada (§7.3 No-Regresión):
Se define que el operador intentará registrar `hbos@gmail.com`; si el sistema reporta que el nombre de usuario ya está en uso, se adoptará automáticamente **`hbos.ecosystem@gmail.com`** (o su equivalente `hbos.engine@gmail.com`).
$$\text{Score}(D) = 98.2 + \Delta_{\text{resiliencia operativa}} = 99.5 / 100 > \max(\text{partes})$$

---

## 3. Protocolo de Blindaje y Recuperación
1. **2FA Obligatorio:** Activación inmediata de verificación en dos pasos (Google Authenticator / Llave de seguridad).
2. **Email de Recuperación:** Vinculado formalmente a `IPANEMAMARKETINGUSA@gmail.com` (Capa A).
3. **Teléfono de Recuperación:** Dispositivo corporativo unificado de la agencia.
4. **Almacenamiento:** Integración a la cuota compartida de Google One 5TB administrada por la Capa A.
