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
- **Trazabilidad:** Cada intento y resultado de verificacion se registra de forma inmutable en auth_ui_audit.json.
- **Integracion con el DAG:** Cualquier accion que requiera confirmacion de soberania (credenciales, metodos de pago, publicaciones sensibles) es delegada a HBOSAuthUI.authorize(scope, mensaje).

---

## 3. Regla R37 · Windows Hello Una Sola Vez por Proceso
Para evitar interrupciones redundantes al operador:
1. **Token Cache con TTL:** La primera autorización exitosa para un `scope` determinado emite un token criptográfico UUID v4 con validez de **30 minutos** (`timeout_minutes=30`).
2. **Hit de Caché Transparente (`[CACHE_HIT]`):** Mientras el token esté vigente dentro del scope, Antigravity ejecuta todas las acciones subsecuentes de manera continua sin volver a desplegar el diálogo de Windows Hello.
3. **Re-autenticación Condicional:** Solo si el token expira o si se cambia a un scope diferente de alta seguridad se solicita nuevamente la huella dactilar.
4. **Invalidación Segura:** Capacidad de invalidar scopes puntuales o purgar la caché completa al finalizar el proceso (`auth.invalidate()`).
