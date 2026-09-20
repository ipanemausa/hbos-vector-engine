# _AGENTE_APRENDIZ_MAESTRA.md — Especificación del Agente Aprendiz Homeostático
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 224 | **Canon:** FAM@-T v1.1 | **Vector Store:** `hbos_orquestacion_historica`

---

## 1. Misión y Funcionamiento del Agente Aprendiz
El Agente Aprendiz es el proceso autónomo que monitoriza la colección `hbos_orquestacion_historica` en Qdrant Cloud.
- **Análisis de Similitud Coseno:** Cuando una nueva tarea ingresa, el aprendiz localiza las $k=5$ operaciones más cercanas en $\mathbb{R}^{384}$.
- **Detección de Patrones de Degradación:** Si detecta que un proveedor presenta latencias crecientes o fallas repetidas (429/500), calcula un vector de penalización y propone la re-priorización de la cadena de fallbacks.
- **Cumplimiento de No-Regresión (§7.3):** Ningún ajuste se aplica a menos que la simulación vectorial demuestre un incremento estricto en la puntuación ponderada M1–M7.