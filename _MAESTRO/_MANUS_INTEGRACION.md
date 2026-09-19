# INTEGRACIÓN DE MANUS AI CON FREELMAPI EN HBOS-DIAMANTINO
### Sello: HBOS-Diamantino · Vector Engine
### Trazabilidad: `operation_id = 155` | Directiva Canónica ALEJAVI
### Rol Sugerido: Motor Ejecutivo de HBOS AUTOMATOR

---

## 1. ¿QUÉ ES MANUS AI?
**Manus AI** es un agente autónomo de propósito general de última generación, diseñado para ejecutar flujos de trabajo multi-paso desatendidos. A diferencia de los LLMs conversacionales reactivos, Manus opera con autonomía completa:
- Descompone una meta compleja en tareas atómicas estructuradas.
- Navega la web, analiza documentos densos y ejecuta código en entornos aislados.
- Auto-corrige errores de ejecución en tiempo real mediante bucles de introspección.
- Entrega productos técnicos acabados (código, reportes, datos estructurados, assets).

---

## 2. CÓMO SE INTEGRA CON FREELMAPI
La limitación tradicional de Manus y los agentes multi-paso es el **costo acumulado de tokens**: un flujo complejo puede consumir millones de tokens en llamadas recursivas de planificación y verificación.

### La Sinergia Soberana:
$$\mathbf{Manus\text{ (Autonomía de Acción)}} + \mathbf{FreeLLMAPI\text{ (Inferencia Gratuita Ilimitada)}} = \mathbf{AUTOMATIZACIÓN\text{ TOTAL A COSTE \$0.00}}$$

1. **Conexión OpenAI-Compatible:**
   - En la configuración de proveedor de Manus, se define la URL base hacia el router local de FreeLLMAPI:
     ```yaml
     api_base: "http://localhost:3001/v1"
     api_key: "freellmapi-soberano-hbos"
     model: "auto:coding" # o "fusion" para razonamiento profundo
     ```
2. **Failover Dinámico y Rotación de Tasa:**
   - Cuando Manus genera un alto volumen de llamadas y un proveedor upstream agota su cuota de rate-limit (429), FreeLLMAPI conmuta de forma transparente al siguiente modelo de la cadena sin interrumpir el plan de Manus.
3. **Compresión de Contexto Automática:**
   - La deduplicación y compactación de contexto de FreeLLMAPI reduce hasta un 40% la huella de memoria en ejecuciones prolongadas de Manus.

---

## 3. CASOS DE USO ESPECÍFICOS EN EL ECOSISTEMA HBOS

| Caso de Uso | Función de Manus | Proveedor FreeLLMAPI Sugerido |
|---|---|---|
| **Investigación Científica (P-15)** | Rastreo de papers oficiales en Nature, ArXiv y PubMed para validar avances biológicos del Ep04/Ep05. | `gemini-2.5-flash` / `deepseek-v3` |
| **Generación de Storyboards** | Desglose de 10 bloques con asignación cinemática de planos y timings precisos. | `auto:reasoning` (Modo Fusión) |
| **Auditoría de Veracidad y Créditos (P-17)** | Verificación cruzada de afirmaciones del guion frente a fuentes primarias. | `fusion` multi-modelo |
| **Inspección de Assets y Redundancia** | Verificación recursiva de integridad de bytes en Drive y backup local. | Scripts locales vía sandbox |

---

## 4. RECOMENDACIÓN ESTRATÉGICA: MANUS COMO HBOS AUTOMATOR
Se recomienda designar a Manus como el **motor de ejecución de fondo de HBOS AUTOMATOR** (Agente Interno ID=6):
- El **Agente Orquestador (HBOS ORCHESTRATOR)** recibe la orden de Guillermo y genera la directiva.
- **Manus** asume el rol de ejecutor desatendido, coordinando la compilación, llamada de APIs y pruebas intermedias.
- El operador recupera el 90% de su tiempo diario, dedicándose exclusivamente a la aprobación final y dirección creativa.
