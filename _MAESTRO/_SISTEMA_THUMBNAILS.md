# SISTEMA DE THUMBNAILS PROFESIONALES — HBOS-DIAMANTINO
### Directiva Maestra de Composición Visual, Tipografía y Formatos Multired
### Ecosistema: HBOS-Diamantino · Trazabilidad: `operation_id = 65` · Patrón: `P-11`

---

## 1. FORMATOS Y RESOLUCIONES DE SALIDA

Cada episodio producido en la fábrica audiovisual debe generar de forma obligatoria 3 thumbnails optimizados por plataforma:

| Formato | Relación de Aspecto | Resolución | Plataformas Principales | Propósito |
| :--- | :---: | :---: | :--- | :--- |
| **Horizontal (Landscape)** | `16:9` | **1280 × 720 px** | YouTube, LinkedIn Web, Sitio Web, Twitter/X | Portada principal y miniatura de video tradicional. |
| **Vertical (Portrait)** | `9:16` | **1080 × 1920 px** | YouTube Shorts, Instagram Reels, TikTok | Portada estática para formato vertical y stories. |
| **Cuadrado (Square)** | `1:1` | **1080 × 1080 px** | Instagram Feed, LinkedIn Feed, Discord, Comunidades | Carátula para feeds sociales y previews cuadradas. |

---

## 2. REGLAS DE COMPOSICIÓN Y DISEÑO

### A. Estructura Tríptica de Elementos
1. **Fondo Temático (Background):** Escenario de supercomputación del episodio con efecto bokeh/blur suave o profundidad de campo cinematográfica.
2. **Personaje Mineral (Host / Especialista):** Render nítido del personaje en plano medio o primer plano, ubicado estratégicamente (a la derecha en 16:9, centrado/inferior en 9:16 y 1:1) con iluminación de borde (rim-light) del color de su gema.
3. **Titular Tipográfico de Alto Contraste:** Texto masivo, sin serifa, legible en pantallas móviles a escala miniatura.
4. **Micro-Badge Técnico:** Etiqueta flotante con el chip, hardware o estándar clave (ej. `VERA RUBIN`, `SPECTRUM-X`, `NVLINK 6`).

### B. Regla de Texto (Máximo 4-5 Palabras)
- El titular **NUNCA debe exceder 4 o 5 palabras**.
- Debe sintetizar el núcleo de valor tecnológico del episodio.
- Ejemplos canónicos:
  * Ep01: `"LA RED CRISTALINA"`
  * Ep02: `"7 CHIPS DE NVIDIA"`
  * Ep03: `"1.6 Tbps FOTÓNICOS"`
  * Ep04: `"RTX SPARK EN PC"`

### C. Tipografía y Estilo
- **Familia:** Sans-serif bold de impacto (Impact, Segoe UI Black, Arial Bold).
- **Tratamiento:** Letras mayúsculas (ALL CAPS), trazo blanco puro con sombra proyectada difusa y resplandor sutil (glow) o gradiente oscuro inferior para garantizar 100% de legibilidad contra cualquier fondo.

### D. Paleta de Color por Personaje Protagonista
- **Diamantino:** Azul Diamante / Cian Luminoso (`#00F0FF`, `#0A84FF`)
- **Amatista:** Violeta Neón / Púrpura Fotónico (`#BD00FF`, `#D946EF`)
- **Rubín:** Rojo Rubí / Carmesí Cuántico (`#FF0055`, `#EF4444`)
- **Esmeralda:** Verde Esmeralda / Neón Tensor (`#00FF88`, `#10B981`)
- **Zafir:** Azul Cobalto / Zafiro Profundo (`#0051FF`, `#3B82F6`)
- **Citrilo:** Ámbar / Dorado Eléctrico (`#FFB700`, `#F59E0B`)
- **Grafito:** Gris Carbón / Plata Metálica (`#94A3B8`, `#E2E8F0`)

---

## 3. ESPECIFICACIÓN DE ALMACENAMIENTO

Los archivos se guardan obligatoriamente bajo la estructura de distribución canónica:
```text
<Episodio>/
└── 06_Publicado/
    └── thumbnails/
        ├── epXX_thumb_16x9.png   (1280x720)
        ├── epXX_thumb_9x16.png   (1080x1920)
        └── epXX_thumb_1x1.png    (1080x1080)
```
