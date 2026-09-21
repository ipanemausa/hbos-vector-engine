# _ALERTAS_MAESTRA.md — Protocolo de Umbrales y Notificación Silenciosa
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ VIGENTE  
> **Principio:** Notificación exclusiva ante fallo crítico · Silencio absoluto ante éxito operativo

---

## 1. Umbrales de Detección y Severidad

| Nivel de Alerta | Componente / Evento | Condición de Disparo | Acción Inmediata del Watchdog | Notificación |
| :--- | :--- | :--- | :--- | :--- |
| **CRÍTICA** | **FreeLLMAPI (:3001)** | Puerto cerrado > 5 min tras intento de reinicio | Reintento forzado de spawn `FreeLLMAPI.exe` | Log crítico + alerta en dashboard |
| **CRÍTICA** | **Gateway (:3002)** | Inaccesible > 5 min | Relanzamiento desacoplado con uvicorn | Log crítico + alerta en dashboard |
| **CRÍTICA** | **Triple Redundancia** | Discrepancia SHA256 no recuperable | Ejecución inmediata de `hbos_repair.py` | Commit automático de auto-reparación |
| **MEDIA** | **Qdrant Cloud** | Latencia de consulta > 2.0 segundos | Reintento con backoff exponencial (3x) | Registro en `hbos_metricas` |
| **INFORMATIVA** | **Git Sync** | Commits locales no pusheados | Ejecución de `git push origin main` | Registro en `hbos_commit_auto.py` |

---

## 2. Política de Silencio Positivo (Quiet Success)
* Si todos los subsistemas responden dentro de los parámetros nominales, los procesos en background no emiten mensajes redundantes a la consola.
* La telemetría se visualiza pasivamente en el dashboard `http://localhost:3002/dashboard`.
