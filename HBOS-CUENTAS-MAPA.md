# HBOS · MAPA DE CUENTAS E IDENTIDAD SOBERANA

**Fecha de Generación:** 2026-09-27  
**Operación:** HBOS-SEC-HARDEN-v1  
**Soberanía:** HBOS-Diamantino / Ipanema Marketing  

---

## 1. Topología de Cuentas

| Parámetro | Cuenta A (Madre / Sombrilla / Keychain) | Cuenta B (Técnica / Fallback Núcleo) |
| :--- | :--- | :--- |
| **Email Canónico** | `ipanemamarketingusa@gmail.com` | `hbos@gmail.com` / `hbos.ecosystem@gmail.com` |
| **Rol en Ecosistema** | **Sombrilla Operativa**: Monetización, RRSS, Google Workspace, Infraestructura Cloud, Gestor de Contraseñas / Keychain | **Núcleo Técnico**: Fallback para telemetría técnica y repositorios específicos de cómputo |
| **Autenticación Biométrica** | Windows Hello (Sensor Synaptics WBDI) + FIDO2 / Passkeys | Vinculada / Enrolada a la sombrilla |
| **2FA / Segundo Factor** | Activado (Llaves de seguridad + Biometría) | Configurado para contingencia |
| **Almacenamiento Cloud** | Plan Google One / Workspace (55TB) | Repositorio satelital |

---

## 2. Servicios Vinculados a `ipanemamarketingusa@gmail.com`

- **YouTube Studio:** `@ipanemamarketingusa` (Canal Oficial HBOS-Diamantino)
- **Kiro AI:** Sesión iniciada con Google OAuth (`https://app.kiro.dev`)
- **FreeLLMAPI:** Daemon soberano local (:3001) y launcher biométrico
- **Google Workspace / Drive:** Almacenamiento máster de audiovisuales, avatares y modelos
- **Bitwarden:** Bóveda segura local desplegada para migración de contraseñas desde Google Keychain

---

## 3. Estado de Seguridad del Sistema Operativo (Windows)

- **Windows Hello Biometrics:** Enrolado y verificado (Sensor Synaptics UWP WBDI, UserConsentVerifier = True).
- **Firewall de Windows:** Activo al 100% en todos los perfiles (Domain, Private, Public).
- **BitLocker (C:):** Desactivado / Off (Recomendación: evaluar cifrado con TPM en siguiente fase).
- **Gestor de Contraseñas:** Bitwarden instalado y listo para sincronización de bóveda.
- **Windows Update:** Al día (solo actualización rutinaria de firmas Defender KB2267602).

---

## 4. Instrucción de Enlace para Archer (Cloud VM)

> **Acción para Guillermo:**
> Envía este resumen del MAPA a **Archer** en la VM de la nube para que lo replique y persista en **Qdrant Cloud** bajo la colección `hbos_rules` y mantenga la topología unificada sin desajustes.
