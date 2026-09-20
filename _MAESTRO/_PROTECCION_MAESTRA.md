# _PROTECCION_MAESTRA.md — Seguridad Soberana, Clave Propia y HBOS VAULT
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 223 | **Canon:** FAM@-T v1.1 | **Nivel:** Soberanía Criptográfica Grado Militar

---

## 1. Misión de la Capa de Protección Propia
Erradicar de forma permanente la exposición de credenciales privadas externas en código fuente, repositorios Git, trazas de depuración o terminales de usuario.

---

## 2. La Clave Soberana HBOS (`hbos-sec-...`)
- **Estructura del Token:** `Bearer hbos-sec-0199...` (Prefijo institucional `hbos-sec-` seguido de 64 caracteres hexadecimales generados con entropía criptográfica segura).
- **Validación Interna:** El gateway unificado intercepta la cabecera `Authorization: Bearer <token>`, valida el hash SHA-256 frente al registro de claves autorizadas en SQLite protegida y asocia la petición al `operation_id` en curso.
- **Aislamiento Absoluto:** Ningún agente ni cliente externo interactúa jamás con claves de OpenAI, Google, Groq, Cerebras o Anthropic. Todos los clientes consumen el endpoint interno mediante la clave soberana.

---

## 3. HBOS VAULT (Cifrado AES-256-GCM)
- **Cifrado en Reposo:** Todas las API keys de terceros se custodian en `freeapi.db` y `.env.local` cifradas bajo **AES-256-GCM** con vector de inicialización (IV) único de 96 bits por cada credencial.
- **Descifrado Efímero en RAM (L-27):** La credencial externa solo se descifra en memoria volátil en el instante previo a transmitir los paquetes de red HTTPS al proveedor.
- **Destrucción Inmediata:** Tras recibir la respuesta HTTP, el búfer de memoria es sobreescrito con ceros (zeroed-out) inmediatamente.
- **Auditoría Inmutable:** Cada uso queda sellado en la colección `boveda_secretos` y `registro_ecosistema` en Qdrant Cloud.