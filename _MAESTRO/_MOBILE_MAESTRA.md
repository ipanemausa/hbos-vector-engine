# _MOBILE_MAESTRA.md — Arquitectura de Acceso Móvil
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 27:31

---

## 1. Modalidades de Acceso Móvil
1. **Web App / PWA Local en LAN:** Acceso a través de la IP local (`http://192.168.x.x:3001`) con diseño responsivo optimizado para pantallas táctiles.
2. **Túnel Cifrado Seguro:** Despliegue mediante Cloudflare Tunnel (`cloudflared`) o Tailscale VPN con autenticación mTLS y token Bearer.

---

## 2. Sinergia con el Subproyecto App HBOS (Op 221)
La interfaz móvil diseñada en Op 221 (`_MAESTRO/_APP_HBOS_MAESTRA.md`) se enlaza directamente con el router de FreeLLMAPI, permitiendo la visualización en tiempo real del estado de los 235 modelos, cuotas de tokens y ejecución agéntica desde cualquier dispositivo smartphone o tablet.