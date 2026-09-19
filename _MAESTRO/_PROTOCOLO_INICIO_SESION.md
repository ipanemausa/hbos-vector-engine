# PROTOCOLO DE INICIO DE SESIÓN — HBOS-DIAMANTINO
### Ecosistema: HBOS (Experto ALEJAVI) · Vector Engine
### Trazabilidad: `operation_id = 164` | Directiva Canónica ALEJAVI
### Patrón Asociado: P-53 · Lección: L-39

---

## 1. ¿QUÉ ES EL PROTOCOLO DE INICIO DE SESIÓN?
Es el procedimiento operativo estándar y obligatorio que todo agente (o par humano-IA en Antigravity IDE) debe ejecutar al arrancar una jornada de trabajo o reabrir una conversación.
Su propósito es **erradicar por completo la amnesia entre sesiones**, eliminando la necesidad de reconstruir contexto manualmente y garantizando que el trabajo se reanude de forma instantánea y sin fricción.

---

## 2. ¿CUÁNDO SE EJECUTA?
- **Al abrir una nueva ventana o sesión en Antigravity IDE.**
- **Tras un reinicio de contexto o cambio de modelo LLM.**
- **Al iniciar la jornada diaria de producción.**

---

## 3. PASOS DE EJECUCIÓN (PIPELINE DE 5 PASOS)

```
[Paso 1: Ejecutar hbos_estado.py]
               │ (Consulta instantánea < 1 seg)
               ▼
[Paso 2: Reportar Estado al Operador]
               │ (Resumen ejecutivo estructurado)
               ▼
[Paso 3: Identificar Pendientes Críticos]
               │ (Cuellos de botella y cuotas)
               ▼
[Paso 4: Proponer Próximos Pasos Priorizados]
               │ (Roadmap inmediato de acción)
               ▼
[Paso 5: Esperar Aprobación del Operador]
               │ (Cero improvisación)
```

### Detalle de los Pasos:

### Paso 1: Ejecutar `hbos_estado.py`
El agente ejecuta en la terminal local:
```bash
python hbos_estado.py
```
Este comando consulta Qdrant Cloud (`hbos_estado` ID=1) y devuelve en menos de 1 segundo la fotografía exacta del ecosistema.

### Paso 2: Reportar Estado al Operador
El agente sintetiza el reporte en 4 bloques claros:
1. **Balance de Episodios:** Estado de Ep02, Ep03 y Ep04.
2. **Gobernanza Activa:** Rango de patrones (P-01 a P-54) y lecciones (L-01 a L-40).
3. **Salud de Cuotas:** Estado de ElevenLabs, DashScope, Gemini y FreeLLMAPI.
4. **Hitos Recientes:** Últimas operaciones consolidadas.

### Paso 3: Identificar Pendientes
Extraer directamente del payload los pendientes abiertos (ej. renderizado de planos Wan 2.1, generación de voces o masterización sonora).

### Paso 4: Proponer Próximos Pasos
Ofrecer al operador 2 o 3 opciones concretas de avance inmediato, señalando la recomendada según disponibilidad de recursos.

### Paso 5: Esperar Aprobación
El agente se detiene y espera la confirmación explícita del operador (*"Procede"*, *"Ejecuta opción 1"*) antes de tocar código o lanzar pipelines.

---

## 4. EJEMPLO DE SALIDA DEL PROTOCOLO EN CHAT

```markdown
### 🌅 Inicio de Sesión HBOS-Diamantino (2026-09-19)
- **Estado General:** OPERATIVO
- **Episodios:** Ep02 y Ep03 concluidos en responsive; Ep04 preproducción al 100%.
- **Cuotas:** ElevenLabs y DashScope agotadas; Gemini 100% activo; FreeLLMAPI portable listo en Sandbox.
- **Pendientes:** Renderizado planos 02-09 Ep04 y síntesis vocal de bloques.

**Próximos Pasos Propuestos:**
1. (Recomendado) Iniciar pruebas de voz con CosyVoice2 vía FreeLLMAPI en Sandbox.
2. Ensamblar pista musical BGM con nota de referencia de Ep04.

¿Por cuál avanzamos, Guillermo?
```

---

## 5. INTEGRACIÓN EN ANTIGRAVITY IDE
- **Regla Inviolable:** Queda prohibido iniciar una sesión preguntando *"¿en qué estábamos ayer?"* o solicitando al usuario que explique el proyecto.
- **Persistencia Garantizada:** El estado reside en Qdrant Cloud y no depende de la ventana de contexto efímera del chat.
