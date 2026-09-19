# HBOS ORCHESTRATOR — AGENTE ORQUESTADOR DE MODELOS Y PROVEEDORES
### Ecosistema: HBOS-Diamantino · Vector Engine
### Tipo: Agente Interno · Categoría: Orquestación y Arbitraje
### Trazabilidad: operation_id = 148 | Estado: Pendiente

---

## 1. DESCRIPCIÓN
HBOS ORCHESTRATOR es el cerebro de asignación y despacho de inferencia del ecosistema. Evalúa la tarea solicitada, consulta la matriz de casos de uso y la salud de cuotas en tiempo real, decidiendo si canalizar el prompt hacia FreeLLMAPI, Gemini, Groq, Ollama o proveedores dedicados.

## 2. FUNCIONES
- Selección de proveedor óptimo por criterios de Calidad, Velocidad o Privacidad (P-26).
- Gestión del failover dinámico en cascada ante respuestas HTTP 429 o 5xx (P-29).
- Orquestación del Modo Fusión multi-modelo con síntesis mediante modelo juez.
- Control de perfiles de compresión de contexto R768 para solicitudes densas.

## 3. CÓMO USARLO
```python
# Consulta y decisión automática de proveedor
proveedor = orquestador.decidir_proveedor(
    tarea="Generacion de Guion Cientifico Ep05",
    criterio="calidad_maxima",
    tokens_estimados=3500
)
print(f"Proveedor seleccionado: {proveedor.nombre} (Modo: {proveedor.modo})")
```

## 4. DEPENDENCIAS
- Qdrant Cloud (colecciones `diamantino_patrones`, `diamantino_casos_uso`, `registro_ecosistema`).
- API Gateways (FreeLLMAPI, Google AI Studio, Groq Cloud).

## 5. ESTADO
- **Estado Actual:** Pendiente de despliegue operacional tras auditoría de cuotas.
