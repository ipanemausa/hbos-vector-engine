# _AUTORIZACION_UI_MAESTRA.md - Modulo de Autorizacion Biometrica Nativa en UI (R32)
> **Ecosistema Soberano HBOS-Diamantino . Modo Experto ALEJAVI**
> **Operacion:** 237 | **Canon:** FAM@-T v1.3 | **Regla:** R32 (Autorizacion en UI Nativa Sin Pestanas)

---

## 1. Filosofia de la Regla R32
Se erradica la dependencia de pestanas emergentes en el navegador externo:
- Antigravity no abre navegadores ni desvia la atencion del operador.
- Antigravity interactua directamente con la API nativa de Windows Hello a traves del modulo hbos_auth_ui.py.
- El subsistema UserConsentVerifier despliega el dialogo seguro del sistema operativo solicitando la confirmacion dactilar.

---

## 2. Verificacion de Disponibilidad de Windows Hello
- **UserConsentVerifierAvailability:** AVAILABLE (0) comprobado empiricamente en runtime de Python.
- **Trazabilidad:** Cada intento y resultado de verificacion se registra de forma inmutable en uth_ui_audit.json.
- **Integracion con el DAG:** Cualquier accion que requiera confirmacion de soberania (credenciales, metodos de pago, publicaciones sensibles) es delegada a HBOSAuthUI.authorize(mensaje).
