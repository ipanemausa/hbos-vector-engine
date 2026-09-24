# HBOS · ANCLA ACTUAL · 92426Tarde
op=305
commit_previo=e1ab470
fecha=2026-09-24
hora=15:28
estado=operativo
fuente_verdad=SQLite freeapi.db + Git

## REGLA DE FACTORIZACION (universal, sin excepcion)
factorizacion=PROTOCOLO DE ENTRADA OBLIGATORIO
  forma=PROMPT -> FASE -> CAPA -> CONDICIONAL -> COMPLETO
  mecanismo=Python en archivo temporal | sin comillas anidadas | sin here-strings rotos
  excepcion=ninguna
  razon=PowerShell no factoriza | FreeLLMAPI factoriza pero pierdes control
  aplica_a=TODO input, sin importar longitud ni origen

## INTEGRACION GOOGLE AI
integrado=Google AI aprendizaje acompanado (patron emulado, no dependencia)
perfil_aprendizaje=creado
nodo_qdrant=documentado
documento=hbos_conocimiento/google_ai_aprendizaje_24sep2026.md

## SISTEMA
portable=si (hbos-init.ps1 detecta raiz desde cualquier punto)
backup=local (C:\Users\ipane\hbos-backups) + drive (G:\My Drive\HBOS) + git
redundancia=triple

## PENDIENTES
pendiente=vectorizacion real en Qdrant Cloud + Ep05
