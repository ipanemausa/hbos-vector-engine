# _DEPLOY_24_7_MAESTRA.md — Despliegue Permanente 24/7 y Supervisión
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 226 | **Servicio:** Daemon en Puerto 3002

---

## 1. Arquitectura de Disponibilidad Continua
- **Lanzador Daemon:** `start_gateway_daemon.py` corriendo como proceso background desatendido.
- **Coexistencia:** Escucha en puerto 3002 en loopback, coexistiendo con FreeLLMAPI en puerto 3001 y Ollama en puerto 11434.
- **Auto-Recuperación:** Diseñado para reanudación automática y compatibilidad con despliegue en VPS Linux o estaciones locales UNBE.