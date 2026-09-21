# _DAILY_START_MAESTRA.md — Manual Operativo de Arranque Diario Soberano en Segundos
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ CANON OPERATIVO DIARIO  
> **Comando Único de Arranque:** `python hbos_daily_start.py`

---

## 1. El Nuevo Paradigma de Arranque
A partir de la operación 232, queda formalmente abolido el inicio de sesión artesanal o fragmentado.

### Modo de Uso:
Al abrir la terminal o iniciar la jornada de trabajo creativo, el operador o agente ejecuta un único comando:
```powershell
python hbos_daily_start.py
```

### Comportamiento Determinista:
1. **Inspección de FreeLLMAPI (:3001):** Si el daemon está apagado, lo levanta automáticamente en background y valida sus 235 modelos.
2. **Inspección de Gateway (:3002):** Si el servidor FastAPI está apagado, lo inicia en background.
3. **Inspección de Qdrant Cloud:** Verifica la conectividad y latencia de las 20 colecciones vectoriales.
4. **Inspección de Triple Redundancia:** Comprueba la presencia física de réplicas en Local, Drive y Backup.
5. **Tiempo de Respuesta Garantizado:** Menos de 1 segundo en estado estacionario (0.51s medido en producción).

---

## 2. Enlaces Operativos Activos Post-Arranque
Una vez completado el script, quedan disponibles de inmediato en el navegador:
* **Dashboard 360:** `http://localhost:3002/dashboard`
* **Marketplace Soberano:** `http://localhost:3002/marketplace`
* **GEV Frontend:** `http://localhost:4173`
* **FreeLLMAPI Catalog:** `http://localhost:3001/v1/models`
