# PROMPT DE INICIO — HBOS SOVEREIGN AI v7.1
# SECUENCIA OBLIGATORIA: LIMPIAR CACHÉ → CARGAR HBOS → VERIFICAR → EJECUTAR

## PASO 1: LIMPIAR CACHÉ
npm cache clean --force
Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "C:\Users\ipane\.gemini\antigravity-ide\brain\*" -ErrorAction SilentlyContinue

## PASO 2: CARGAR WORKSPACE HBOS
File > Open Workspace...
C:\Users\ipane\hbos-deploy\hbos-vector-engine\hbos-vector-engine.code-workspace

## PASO 3: VERIFICAR WORKSPACE
pwd → C:\Users\ipane\hbos-deploy\hbos-vector-engine
git remote -v → ipanemausa/hbos-vector-engine
git status → On branch main, nothing to commit

## PASO 4: PRE-FLIGHT CHECK
curl https://hbos-vector-engine.vercel.app/v1/health → 200 OK
curl https://hbos-vector-engine.vercel.app/v1/qdrant/collections → 5 colecciones

## PASO 5: REPORTAR
"SECUENCIA DE INICIO: OK" o "SECUENCIA DE INICIO: FALLIDO [razón]"

## REGLA DE ORO
"SI LA CACHÉ NO ESTÁ LIMPIA, O HBOS NO ESTÁ CARGADO, NO SE EJECUTA NINGUNA TAREA."
