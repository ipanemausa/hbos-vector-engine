# INTEGRACIÓN DE DEEPSEEK HARNESS CON FREELMAPI EN HBOS-DIAMANTINO
### Sello: HBOS-Diamantino · Vector Engine
### Trazabilidad: `operation_id = 156` | Directiva Canónica ALEJAVI
### Rol Sugerido: Proveedor Especializado de Razonamiento y Modelos Abiertos

---

## 1. ¿QUÉ ES DEEPSEEK HARNESS?
**DeepSeek Harness** es el entorno de orquestación, evaluación e inferencia estructurada diseñado para maximizar el rendimiento de la familia de modelos de pesos abiertos de DeepSeek (V3, R1, Coder, V4/V5) y el ecosistema de IA abierta (Qwen, ModelScope, Zhipu).
Actúa como arnés de ejecución capaz de canalizar prompts de razonamiento paso a paso (*chain-of-thought*), generación de código y benchmarks comparativos en entornos de desarrollo avanzados.

---

## 2. CÓMO SE INTEGRA CON FREELMAPI
FreeLLMAPI agrega y consolida múltiples plataformas gratuitas que sirven modelos DeepSeek y modelos abiertos de origen internacional y chino:
- **SiliconFlow:** Sirve inferencia de modelos DeepSeek y CosyVoice2.
- **ModelScope (Alibaba):** Acceso a familias Qwen, DeepSeek y GLM.
- **OpenRouter & HuggingFace:** Rutas `:free` para DeepSeek-R1 y DeepSeek-V3.

### Arquitectura de Enlace:
$$\mathbf{DeepSeek\text{ Harness (Arnés de Razonamiento)}} \longleftrightarrow \mathbf{FreeLLMAPI\text{ (Gateway Failover)}} \longleftrightarrow \mathbf{HBOS\text{ Ecosistema}}$$

1. **Protocolo Unificado:** DeepSeek Harness se enlaza al puerto local de FreeLLMAPI (`http://localhost:3001/v1`) como cliente OpenAI-compatible o a través de la herramienta MCP `query_deepseek_harness_v4_v5`.
2. **Arbitraje y Redundancia:** Las consultas de razonamiento pesado (que requieren alta ventana de contexto) se distribuyen entre los proveedores que tengan cuota disponible, evitando el bloqueo por HTTP 429.
3. **Preservación de Tokens de Razonamiento:** FreeLLMAPI soporta la extracción del campo `reasoning_content` en respuestas de DeepSeek-R1 para auditorías técnicas transparentes.

---

## 3. MODELOS DISPONIBLES EN LA INTEGRACIÓN

| Modelo | Especialidad | Parámetros / Arquitectura | Uso Principal en HBOS |
|---|---|---|---|
| **DeepSeek V3** | Inferencia General y Chat | 671B MoE (37B activos) | Redacción de guiones bilingües y análisis de tendencias. |
| **DeepSeek R1** | Razonamiento Matemático y Lógico | 671B con CoT puro | Auditoría científica P-15 y resolución de problemas de pipeline. |
| **DeepSeek Coder** | Programación y Refactorización | 33B / 236B MoE | Construcción de scripts Python, Playwright y FFmpeg. |
| **Familia Qwen 2.5 / 3** | Formateo Estricto JSON | 72B denso / MoE | Generación de metadatos, storyboards y payloads de Qdrant. |
| **GLM-4 / GLM-5** | Conocimiento Enciclopédico | Arquitectura Zhipu | Cruce de fuentes primarias y papers científicos. |

---

## 4. CASOS DE USO ESPECÍFICOS EN HBOS

1. **Razonamiento Complejo (Ep04/Ep05):**
   - Análisis de papers de biología computacional (AlphaFold, bioinformática cuántica).
   - DeepSeek R1 genera la explicación técnica detallada sin metáforas, lista para ser traducida al formato de los *Anchors* de Diamantino.
2. **Programación y Automatización:**
   - Generación de scripts para el Agente Navegador (`map_app.py` / `navigate_app.py`) y filtrado complejo de audio EBU R128.
3. **Auditoría y Verificación de Datos (P-15):**
   - Comparación cruzada de afirmaciones del guion frente a hechos científicos verificados antes de proceder a la síntesis vocal o renderizado.
4. **Respaldo Soberano Offline:**
   - Compatibilidad directa con Ollama Local (`query_local_ollama`) para ejecutar pesos DeepSeek R1 cuantizados localmente si la conexión externa cae.

---

## 5. RECOMENDACIÓN ESTRATÉGICA
Adoptar **DeepSeek Harness** como el **Proveedor de Razonamiento Primario** en el catálogo de HBOS:
- Permite sustituir APIs comerciales costosas por inferencia de nivel frontera a coste \$0.00 mediante la agregación de FreeLLMAPI.
- Habilita capacidades analíticas de nivel doctoral para la divulgación científica rigurosa y sin apropiación intelectual.
