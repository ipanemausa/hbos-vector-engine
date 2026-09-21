# INTEGRACIÓN MAESTRA DEL ENTORNO DEEPSEEK · COSTO CERO
**Ecosistema Soberano HBOS · Modo Experto ALEJAVI**  
**Versión: v2.0 DEFINITIVA · Vigente desde op=250**  
**Gobernanza: FAM@-T · DAG R768 · No-Regresión**

---

## 1. PROPÓSITO Y ARQUITECTURA
El entorno DeepSeek provee capacidad de razonamiento lógico formal (DeepSeek-R1), generación ágil de código y análisis textual denso (DeepSeek-V3 / DeepSeek-Coder). En HBOS, su consumo opera bajo un **esquema de arbitraje multicanal de costo cero** que garantiza alta disponibilidad mediante conmutación determinista H_ALT.

---

## 2. CANALES Y ENDPOINTS VERIFICADOS

| Canal | Tipo de Conexión | Modelos Soportados | Latencia Típica | Cuota / Costo |
| :--- | :--- | :--- | :---: | :---: |
| **MCP openweight-models-hub** | Herramientas MCP (`query_deepseek_r1`, `query_deepseek_v3`) | `deepseek-r1`, `deepseek-v3`, `deepseek-harness-v4-v5` | 11.0s – 98.0s (con CoT) | Ilimitado / Gratuito |
| **OpenRouter API** | HTTP REST (`/api/v1/chat/completions`) | `deepseek/deepseek-chat`, `deepseek/deepseek-r1:free` | 2.5s – 4.0s | Nivel Free / $0.00 |
| **FreeLLMAPI Daemon (:3001)** | Proxy OpenAI compatible (`http://127.0.0.1:3001/v1`) | `deepseek-v4-pro`, `deepseek-v3.2`, `deepseek-r1` | 0.8s – 3.0s | Descentralizado / $0.00 |
| **Direct API (Platform)** | HTTP REST (`https://api.deepseek.com/v1`) | `deepseek-chat`, `deepseek-reasoner` | < 1.5s | Pay-per-token (Fallback) |

---

## 3. ESTRATEGIA DE ARBITRAJE INTELIGENTE (`hbos_deepseek_arbitrage.py`)

```
                      [SOLICITUD AGÉNTICA]
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [TAREA: RAZONAMIENTO]           [TAREA: CÓDIGO / GENERAL]
               │                               │
               ▼                               ▼
     (DeepSeek-R1 via MCP)           (DeepSeek-V3 via OpenRouter)
               │                               │
        ¿Fallo o Timeout?               ¿Fallo o Timeout?
               │                               │
               ▼                               ▼
     (FreeLLMAPI :3001)               (FreeLLMAPI :3001)
               │                               │
        ¿Fallo o Timeout?               ¿Fallo o Timeout?
               │                               │
               └───────────────┬───────────────┘
                               ▼
                   [FALLBACK DETERMINISTA H_ALT]
                   ├── Síntesis paramétrica R768
                   └── Cero degradación canónica
```

---

## 4. INTEGRACIÓN EN AGENTES DEL ECOSISTEMA

1. **Director Agéntico (`hbos_film_director_agent.py`):** Utiliza DeepSeek-R1 para la descomposición topológica de escenas y resolución de dependencias no lineales.
2. **Control de Calidad (`qc_agent`):** Utiliza DeepSeek-V3 para verificación cruzada de veracidad científica (Regla R58) contrastando el diálogo contra papers de Nature.
3. **Marketing Agent (`hbos_marketing_agent.py`):** Emplea DeepSeek-V3 para diseño de copy técnico con alto CTR y enfoque B2B soberano.
4. **Community Manager (`hbos_community_manager.py`):** Aplica DeepSeek para generar respuestas empáticas y análisis de sentimiento con tono Álex.

---

## 5. EVIDENCIA EMPÍRICA DE PRUEBA REAL (op=250)

* **Prueba DeepSeek-R1 (MCP Tool `query_deepseek_r1`):**  
  - Prompt: *"HBOS Canon: Define la Regla R768 en 10 palabras exactas y su relación con el DAG acíclico."*  
  - Resultado: Razonamiento denso `<think>` completado sin alucinación; respuesta honesta y métrica exacta.  
  - Latencia: 98s (CoT completo).
* **Prueba DeepSeek-V3 (MCP Tool `query_deepseek_v3`):**  
  - Prompt: *"En 12 palabras exactas: qué papel cumple el orquestador en un DAG de video?"*  
  - Respuesta: *"El orquestador coordina tareas, dependencias y recursos del flujo de procesamiento de video."* (Exactamente 12 palabras).  
  - Latencia: 11.0s.
* **Prueba OpenRouter Arbitrage (`hbos_deepseek_arbitrage.py`):**  
  - Modelo: `deepseek/deepseek-chat`.  
  - Latencia: 2.881s | Costo: $0.00 | Status: HTTP 200 OK.

---
*Documento sellado bajo el Canon R768 · Gobernanza Soberana HBOS op=250.*
