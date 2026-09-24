# HBOS · ANCLA ACTUAL · op=310
op=310
commit_previo=326f794
fecha=2026-09-24
hora=16:42
estado=operativo · E auditado

## PENDIENTE E · PREMIUM SIN PAGAR PREMIUM
estado=auditado
top_tier_accesibles=3
providers_activos=9
providers_total=11
modelos_total=316
profiles=10
fallback_total=316
ruta=free tiers top-tier + fallback + perfiles
recomendacion=GoogleAIStudio + Groq + Cerebras (2-3 primero)
regla=anadir 2-3 · verificar · ampliar si funciona
no_hacer=anadir todos de golpe · romper cadenas actuales

## KIRO (descubrimiento 2026-09-24)
id=20
platform=kiro
label=Kiro AI (Claude 3.7 / Opus)
bridge=http://127.0.0.1:3005/v1
enabled=0
status_db=healthy (cosmetico)
puerto_3005=cerrado
decision=pendiente A/B

## DAG MANANA
orden=D -> A -> B -> C -> E -> cierre canonico
D=validar perfil aprendizaje
A=vectorizacion real
B=Ep05
C=HuggingFace + Kiro
E=premium sin pagar premium

## SISTEMA
portable=si
hook=activo
factorizacion=universal (APP+R768 · FASE->CAPA->DAG->COMPLETO)
backup=local + drive + git
redundancia=triple
