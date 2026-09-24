# HBOS · ANCLA ACTUAL · op=313
op=313
commit_previo=590599a
fecha=2026-09-24
hora=16:57
estado=operativo · E auditado · Qdrant cierre redundante · Kiro diagnosticado

## QDRANT (cierre redundante 2026-09-24)
modo=embebido en FreeLLMAPI
puerto_6333=cerrado (esperado, NO es KO)
acceso=via FreeLLMAPI
estado=operativo

## KIRO (diagnostico 2026-09-24 op=313)
id=20
platform=kiro
label=Kiro AI (Claude 3.7 / Opus)
bridge=http://127.0.0.1:3005/v1
enabled=0
status_db=healthy (cosmetico)
puerto_3005=cerrado
last_checked_at=None
decision=PENDIENTE A/B (reactivar / limpiar)
nota=proveedor #11 de 11 registrados (9 activos + 2 deshabilitados)

## PROVEEDORES (11 totales)
total=11
activos=9
deshabilitados=2 (modelscope invalido + kiro apagado)

## PENDIENTE E · PREMIUM SIN PAGAR PREMIUM
estado=auditado
providers_activos=9
modelos_total=316
profiles=10
fallback_total=316
ruta=free tiers top-tier + fallback + perfiles
recomendacion=GoogleAIStudio + Groq + Cerebras (2-3 primero)

## DAG
orden=D -> A -> B -> C -> E -> cierre canonico
D=validar perfil aprendizaje
A=vectorizacion real
B=Ep05
C=HuggingFace + Kiro
E=premium sin pagar premium

## SISTEMA
portable=si
hook=activo
factorizacion=universal (APP+R798 · FASE->CAPA->DAG->COMPLETO)
backup=local + drive + git
redundancia=triple
