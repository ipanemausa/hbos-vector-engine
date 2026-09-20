# _MUSE_HBOS_MAESTRA.md — Canvas Espacial Infinito y Experiencia Visual Muse
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 223 | **Canon:** FAM@-T v1.1 | **Capa:** Visual & UX Espacial

---

## 1. Filosofía Espacial de Muse Aplicada a HBOS
La interfaz espacial rompe con la rigidez de las carpetas y los listados tradicionales:
1. **Lienzo Infinito Multiescala:** Paneo continuo bidimensional con zoom semántico (desde vista galáctica del ecosistema completo hasta inspección a nivel de línea de código en tarjetas anidadas).
2. **Nodos Polimórficos (`HBOSCanvasNode`):** Cada entidad del proyecto (Episodio, Guion, Voz, Video Clip, Métrica, Nódulo de Orquestación) se renderiza como una tarjeta espacial interactiva con coordenadas `(x, y, scale, zIndex)`.
3. **Command Palette Universal (`@` / `Ctrl+K`):** Menú flotante de acceso instantáneo con búsqueda difusa (fuzzy search) de latencia menor a 50 ms.
4. **Navegación Gestual:** Soporte para gestos multitáctiles, trackpad y rueda de ratón con inercia física suave.
5. **Arquitectura Local-First:** El estado visual y espacial se guarda en SQLite/IndexedDB local de forma inmediata, sincronizándose asíncronamente con Google Drive y Qdrant Cloud.

---

## 2. Definición Canónica del Modelo de Datos `HBOSCanvasNode`
```typescript
interface HBOSCanvasNode {
  id: string;                    // Identificador único UUID v4
  operation_id: number;          // Trazabilidad inmutable R768
  type: 'episode' | 'prompt' | 'voiceover' | 'video_clip' | 'pattern' | 'metric' | 'orchestrator_node';
  position: {
    x: number;
    y: number;
    scale: number;
    zIndex: number;
  };
  content: {
    title: string;
    payload: any;                // Texto markdown, buffer de audio, URL de video, embedding
    sha256: string;              // Verificación criptográfica de integridad
  };
  relations: string[];           // Aristas dirigidas del DAG hacia nodos dependientes
  metadata: {
    provider: string;            // 'ollama' | 'freellmapi' | 'gemini' | 'groq'
    tokens: number;
    latency_ms: number;
    timestamp: string;
  };
}
```

---

## 3. Integración con la Factoría Multimedia Diamantino
Desde cualquier nodo de video o voz en el lienzo de Muse, el usuario o agente puede ejecutar directamente los scripts de renderizado (`step_fase5_video_v3.py`, `build_voiceover_master.py`), visualizando el progreso en tiempo real sobre la propia tarjeta.