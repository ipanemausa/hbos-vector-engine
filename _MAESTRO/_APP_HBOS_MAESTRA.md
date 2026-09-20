# DIRECTIVA MAESTRA: ARQUITECTURA DE LA APP HBOS-DIAMANTINO
## Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
### Subproyecto: Investigación de Organización Tipo Muse ➔ App HBOS
### Instancia de Registro: operation_id = 221 · Sellado en Qdrant Cloud · Vigente desde op=221

---

### 1. ANÁLISIS DE REFERENCIA TIPO MUSE (10 DIMENSIONES CANÓNICAS)
1. **Organización de Archivos:** Muse organiza por "tableros" (boards) espaciales jerárquicos donde cada elemento es una tarjeta anidada que contiene texto, imagen, audio o sub-tableros sin estructura rígida de carpetas.
2. **Jerarquía Espacial:** Jerarquía fractal bidimensional (zoom-in / zoom-out). Un sub-tablero es tanto un nodo contenedor como un objeto visual arrastrable.
3. **Diseño de Botones y Acciones:** Minimalismo contextual. No hay barras de herramientas permanentes saturadas; las acciones surgen al interactuar con la tarjeta (menú radial o contextual superior flotante).
4. **Modelo de Datos:** Grafo de nodos con coordenadas espaciales `(x, y, scale, z-index)` y tipos de contenido polimórficos vinculados por aristas semánticas implícitas.
5. **Diseño Visual:** Estética cálida, texturada, de cuaderno digital y lienzos monocromáticos de alta legibilidad, evitando bordes duros y saturación estridente.
6. **Navegación:** Navegación por paneo infinito y zoom continuo con minimapa contextual y breadcrumb dinámico en la parte superior izquierda.
7. **Gestión de Estado:** Arquitectura local-first ultrarrápida respaldada por base de datos SQLite/CRDTs locales con sincronización asíncrona encriptada punto a punto.
8. **Búsqueda y Acceso Rápido:** Command palette (`Cmd+K`) con búsqueda difusa (fuzzy search) indexada sobre todo el contenido textual y visual.
9. **Colaboración y Soberanía:** Enfoque centrado en la mente individual y colaboración asíncrona mediante snapshots portables.
10. **API e Integración:** Exportación estandarizada en JSON / Markdown / SVG sin encierros propietarios.

---

### 2. SÍNTESIS D ADOPTADA: LA APP CANÓNICA HBOS-DIAMANTINO
La Síntesis D integra la fluidez espacial de Muse con el rigor de gobierno homeostático R768 de HBOS:

#### A. Árbol de Organización de Archivos y Módulos
```text
hbos-app/
├── core/                        # Núcleo de gobierno homeostático UNBE
│   ├── engine/                  # Inferencia, orquestador de agentes y modelos
│   ├── memory/                  # Conectores Qdrant Cloud (17 colecciones)
│   └── redundancy/              # Watchdog triple redundancia física
├── canvas/                      # Lienzo infinito interactivo tipo Muse
│   ├── workspace/               # Tableros espaciales anidados por Episodio
│   ├── nodes/                   # Tarjetas polimórficas (Prompt, Guion, Voz, Video, Metadatos)
│   └── viewport/                # Paneo, zoom continuo y minimapa biocuántico
├── studio/                      # Factoría multimedia Diamantino
│   ├── audio/                   # Masterizador EBU R128 (-14 LUFS) y CosyVoice2
│   ├── video/                   # Pipeline Wan 2.1 descentralizado y ensamble FFmpeg
│   └── responsive/              # Generador multiformato (16:9, 9:16, 1:1, 4:5)
└── shared/                      # Sistema de diseño y tokens visuales
    ├── tokens/                  # Paleta biocuántica, tipografía Outfit e iconos
    └── components/              # Botones contextuales, Command Palette @ y modales
```

#### B. Modelo de Datos Canónico
```typescript
interface HBOSCanvasNode {
  id: string;                    // UUID canónico
  operation_id: number;          // Trazabilidad inmutable R768
  type: 'episode' | 'prompt' | 'voiceover' | 'video_clip' | 'pattern' | 'metric';
  position: { x: number; y: number; scale: number; zIndex: number };
  content: {
    title: string;
    payload: any;                // Texto, audio wav, video mp4, embedding 384d
    sha256: string;              // Hash inmutable de contenido
  };
  relations: string[];           // IDs de nodos dependientes (DAG topológico)
  metadata: {
    provider: string;            // 'gemini' | 'groq' | 'freellmapi' | 'unbe'
    token_usage: number;
    timestamp: string;
  };
}
```

#### C. Sistema de Diseño Visual y Experiencia de Usuario
- **Paleta Biocuántica Diamantino:** Fondo Obsidian Oscuro (`#0a0b0e`), Superficies Glassmorphism (`rgba(18, 22, 34, 0.85)`), Acento Neón Diamantino (`#00f0ff`), Alertas Ámbar Resiliencia (`#ffaa00`).
- **Tipografía:** *Outfit* para títulos e interfaces de alto impacto, *JetBrains Mono* para metrología y telemetría de tokens.
- **Acciones y Botones:** Barra flotante minimalista inferior para acciones globales (`Nuevo Episodio`, `Generar Master`, `Verificar UNBE`), y menús contextuales en nodos con acciones primarias y secundarias.
- **Búsqueda Universal:** Command Palette inteligente invocada con `@` o `Ctrl+K` para saltar a cualquier nodo, colección de Qdrant o script del sistema en $< 50	ext{ms}$.

---

### 3. PLAN DE IMPLEMENTACIÓN EN HBOS (4 FASES MEDIBLES)
- **Fase 1 (Cimiento de Datos y Espacio):** Creación del esquema `HBOSCanvasNode` y sincronización con las colecciones `diamantino_apps` y `registro_ecosistema` en Qdrant (op=222).
- **Fase 2 (Motor de Lienzo Espacial):** Implementación del viewport infinito con soporte de zoom, arrastre y renderizado de tarjetas en Vanilla JS + HTML5 Canvas (op=223).
- **Fase 3 (Integración de Factoría Multimedia):** Vinculación de los scripts de producción (`build_voiceover_master.py`, `step_fase5_video_v3.py`, FFmpeg) como acciones ejecutables desde los nodos (op=224).
- **Fase 4 (Sellado Soberano y Telemetría):** Enlace completo con el daemon FreeLLMAPI :3001, monitoreo en tiempo real de cuotas y verificación formal §1.0 (op=225).
