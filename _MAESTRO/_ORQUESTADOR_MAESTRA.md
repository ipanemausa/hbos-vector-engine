# _ORQUESTADOR_MAESTRA.md — Orquestador Homeostático de Nódulos
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 223 | **Canon:** FAM@-T v1.1 | **Arquitectura:** DAG Desacoplado

---

## 1. Arquitectura de Desacoplamiento de Operadores
El Orquestador HBOS no es un script monolítico; está estructurado como un Grafo Dirigido Acíclico (DAG) donde cada operador canónico opera como un nódulo independiente e idempotente:
- **Operador $\mathcal{F}$ (Factorización Matemática Input $\to$ Output):** Proyecta la demanda de usuario en $\mathbb{R}^{384}$ sin procesamiento consecutivo lineal.
- **Operador $\mathcal{C}$ (Compresión Holística):** Condensa invariantes semánticas minimizando consumo de tokens.
- **Operador $\mathcal{H}$ (Hibridación Base LLMAPI $\oplus$ R768):** Fusión sinérgica entre el router universal y la memoria vectorial.
- **Operador $M \oplus P$ (Manus $\oplus$ Pipeline):** Sincronización entre el workflow agéntico global y la micro-secuencia operativa.
- **Operador $\text{FAM@-H}$ / $\text{FAM@-T}$:** Navegación en el entorno total de agentes, modelos y proveedores.

---

## 2. Tabla de Enrutamiento Dinámico y Rotación por Cuota
| Tipo de Tarea | Operador Requerido | Proveedor Primario | Fallback Secundario | Fallback Soberano |
|---|---|---|---|---|
| **Cálculo Creativo / Guion** | $M \oplus P$ | Google Gemini 2.5/Flash | Groq (Llama 3.3 70B) | Ollama (Llama 3 Local) |
| **Razonamiento Complejo** | $\mathcal{H}_{\text{DeepSeek}}$ | DeepSeek-R1 (HuggingFace) | Qwen 2.5 Coder 32B | LM Studio / Jan Local |
| **Extracción / Embeddings** | $\mathcal{F}_{768}$ | Gemini Embedding 001 | HuggingFace MiniLM | Qdrant Local Hash 384d |
| **Inferencia Crítica Privada** | $\mathcal{O}_{\text{Local}}$ | Ollama Local :11434 | Jan AI Local :1337 | Failover sin salida a red |

---

## 3. Trazabilidad Histórica en Qdrant
Cada ejecución orquestada genera un vector de telemetría de 384 dimensiones almacenado en la colección dedicada **`hbos_orquestacion_historica`**, vinculando:
- `operation_id`
- Nódulos invocados y orden topológico del DAG
- Latencias individuales por nódulo y latencia de pipeline compuesta
- Ahorro porcentual de tokens frente al baseline canónico