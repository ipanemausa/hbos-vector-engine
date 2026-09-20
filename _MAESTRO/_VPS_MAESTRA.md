# _VPS_MAESTRA.md — Despliegue 24/7 en VPS y Resiliencia en Nube
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 222 | **Timestamp Video:** 28:27

---

## 1. Estrategia de Operación Ininterrumpida 24/7
- **Entorno VPS:** Instancia virtualizada Linux (Ubuntu LTS / Debian) con reverse proxy NGINX y certificados TLS automáticos (Let's Encrypt).
- **Gestión de Proceso Daemon:** Servicio `systemd` o contenedor Docker con reinicio automático (`restart: always`).

---

## 2. Compatibilidad con el Nodo de Coordinación UNBE
El despliegue 24/7 en VPS actúa como nodo satélite de UNBE:
- Permite que las tareas automatizadas nocturnas (`_TAREAS_AUTOMATICAS.md`) ejecuten consultas a modelos LLM sin requerir que la estación de trabajo local esté encendida.
- La base de datos SQLite sincroniza periódicamente snapshots cifrados con Google Drive y Qdrant Cloud.