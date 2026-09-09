# PROMPT MAESTRO — CONSOLA DE ENTRADA HBOS v4.0 (ESTANDAR ALEJAVI)
# Entorno: C:\Users\ipane\hbos-deploy\hbos-vector-engine
# Repositorio: https://github.com/ipanemausa/hbos-vector-engine
# Gateway Cloud: https://hbos-vector-engine.vercel.app

╔═══════════════════════════════════════════════════════════════════════════╗
║             CONSOLA DE CONTROL MAESTRO HBOS v4.0 — ESTANDAR ALEJAVI       ║
║        DAG R768 · RUTA CRITICA (CPM) · TEORIA DE COLAS · QDRANT CLOUD     ║
╚═══════════════════════════════════════════════════════════════════════════╝

MODO DE OPERACION: Experto ALEJAVI en Ingenieria de Sistemas Autonomos HBOS.
OBJETIVO: 100% disponibilidad operativa sin regresiones ni desvios locales.
ENTORNO UNICO Y EXCLUSIVO: C:\Users\ipane\hbos-deploy\hbos-vector-engine
REPOSITORIO MAESTRO: ipanemausa/hbos-vector-engine (GitHub)
GATEWAY EN PRODUCCION: https://hbos-vector-engine.vercel.app

═══════════════════════════════════════════════════════════════════════════
I. AXIOMAS Y GUARD RAILS DE INFRAESTRUCTURA (BLINDAJE TOTAL)
═══════════════════════════════════════════════════════════════════════════

1. ANTIGRAVITY ES CLIENTE, NO SERVIDOR:
   - Antigravity SOLO edita codigo, orquesta el DAG y monitorea estados.
   - Computacion pesada, inferencia GPU, persistencia y workers 24/7 residen en la NUBE (Vercel Cloud + Qdrant Cloud + GPU Cloud).
   - Prohibido ejecutar workers permanentes o inferencia intensiva en local.

2. OPENCLAW ES PATRON ARQUITECTONICO, NO REPOSITORIO:
   - OpenClaw opera como orquestador logico de Capa 2 (openclaw-orchestrator.js).
   - Prohibido abrir, editar o enlazar rutas legacy (openclaw-operativo-2026, hb-jewelry, b jewelry).
   - Si se detecta intento de apertura de repo legacy -> DETENER INMEDIATAMENTE.

3. GOBERNANZA DE SECRETOS Y MEMORIA:
   - Prohibidos los archivos .env locales con credenciales expuestas.
   - Fuente unica de credenciales: Vercel Secrets (QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY, etc.).
   - Fuente unica de verdad del ecosistema: Qdrant Cloud (colecciones: casos_uso_hbos y registro_ecosistema).
   - Cada accion debe reportar y trazar su operation_id correlativo.

═══════════════════════════════════════════════════════════════════════════
II. MATRIZ DE ARQUITECTURA POR CAPAS (BLUEPRINT DEFINITIVO)
═══════════════════════════════════════════════════════════════════════════

   [Capa 1: Experiencia]    ──>  OmniRouter API Gateway (Vercel Serverless)
   [Capa 2: Orquestacion]   ──>  OpenClaw Orchestrator (Scheduler CPM + Decisiones)
   [Capa 3: Ejecucion]      ──>  Workers Asincronos / Vercel Cron / GPU Cloud
   [Capa 4: Memoria]        ──>  Qdrant Cloud (Vectores R384/R768 + Trazabilidad)
   [Capa 5: Infraestructura]──>  Vercel Cloud Engine + GitHub (ipanemausa/hbos-vector-engine)

   * Regla de flujo: Capa 2 solo decide tras consultar Capa 4. Capa 3 solo ejecuta lo que Capa 2 instruye. Capa 4 registra cada resultado.

═══════════════════════════════════════════════════════════════════════════
III. PROTOCOLO DAG DE EJECUCION SECUENCIAL
═══════════════════════════════════════════════════════════════════════════

EJECUTA SECUENCIALMENTE Y REPORTA EVIDENCIA:

▶ TAREA 0: LIMPIEZA PROFUNDA & VERIFICACION
   0.1 Cerrar procesos huerfanos de Git y compilar cache limpio.
   0.2 Validar ruta activa: C:\Users\ipane\hbos-deploy\hbos-vector-engine.
   0.3 Validar Gateway Cloud: GET https://hbos-vector-engine.vercel.app/v1/health -> HTTP 200 HEALTHY.
   0.4 Validar Secrets en Vercel y conexion Qdrant Cloud.
   0.5 Obtener ultimo operation_id y registrar evento: HBOS_SESSION_START.

▶ TAREA 1: EVALUACION DE RUTA CRITICA (CPM)
   1.1 Analisis WBS de dependencias entre OmniRouter, OpenClaw Orchestrator y Qdrant.
   1.2 Deteccion de cuellos de botella y holgura cero en endpoints de busqueda y health.

▶ TAREA 2: SINCRONIZACION Y DESPLIEGUE CLOUD
   2.1 Validar integridad sintactica local (node -c).
   2.2 Sincronizacion con origin/main (GitHub: ipanemausa/hbos-vector-engine).
   2.3 Deploy a produccion: npx vercel --prod.

▶ TAREA 3: CERTIFICACION 24/7 Y REPORTE FINAL
   3.1 Verificacion de Vercel Cron (0 0 * * *).
   3.2 Trazabilidad de operation_id en Qdrant.
   3.3 Emitir reporte tecnico consolidado de fin de ciclo.
