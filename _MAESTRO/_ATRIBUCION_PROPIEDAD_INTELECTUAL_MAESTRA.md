# REGLA R73 · ATRIBUCIÓN DE PROPIEDAD INTELECTUAL Y VERACIDAD INSTITUCIONAL
**Ecosistema Soberano HBOS · Modo Experto ALEJAVI**  
**Vigente desde op=249 · Canon Audiovisual y Científico Soberano**

---

## 1. PRINCIPIO FUNDAMENTAL (REGLA R73)
Toda pieza audiovisual, gráfica, técnica o documental generada en el ecosistema HBOS debe contener **atribución explícita, permanente y verificable** de la propiedad intelectual, autoría original, instituciones de investigación y premios o reconocimientos asociados al tema abordado.

Queda estrictamente prohibida la producción o publicación de contenido técnico sin la debida mención a los científicos, laboratorios, papers o instituciones originarias.

---

## 2. REQUISITOS OBLIGATORIOS POR FASE DE VIDEO

### A. Fase 0 · Identificación Canónica
En la etapa de vectorización e investigación inicial, el orquestador (`hbos_film_director_agent`) debe extraer obligatoriamente:
- **Autor(es) Principal(es):** Nombres completos de los investigadores o inventores (ej. *Sir Demis Hassabis*, *John Jumper*, *David Baker*).
- **Institución / Laboratorio:** Entidad creadora o depositaria (ej. *Google DeepMind*, *University of Washington*, *EMBL-EBI*).
- **Premio / Reconocimiento:** Si aplica (ej. *Premio Nobel de Química 2024*).
- **Paper / Fuente Científica R58:** DOI, URL oficial o publicación de referencia (ej. *Nature 2024 / AlphaFold 3*).

### B. Fase 3B & Fase 4 · Capa Gráfica Permanente (Lower Third Legal)
- Se incorpora como **Capa 3 independiente** en el compositor multicapa de FFmpeg.
- **Ubicación:** Tercio inferior izquierdo o banner contextual no invasivo pero 100% legible (tipografía sin serif, contraste garantizado, tamaño $\ge 22\text{pt}$ a 1080p).
- **Presencia:**
  - **Intro:** Tarjeta completa de apertura y presentación del tema.
  - **Desarrollo:** Cinta o identificador permanente discreto.
  - **Cierre:** Placa formal de agradecimiento y cita de fuentes canónicas.

### C. Fase 5 · Control de Calidad (QC)
El agente de control de calidad (`qc_agent`) debe verificar la existencia del campo de atribución mediante inspección de metadatos o análisis OCR/gráfico:
- ¿Autor presente? $\rightarrow$ Requisito crítico (`FAIL` aborta el DAG si está ausente).
- ¿Institución presente? $\rightarrow$ Requisito crítico.
- ¿Premio presente? $\rightarrow$ Mandatorio si el guion lo menciona.

### D. Fase 7 · Distribución Multiplataforma
- Todas las descripciones en YouTube, LinkedIn, X, Instagram y Telegram deben incluir en sus primeras 3 líneas la atribución canónica completa y el enlace directo al paper o repositorio original.

---

## 3. APLICACIÓN EN CASO EMBLEMÁTICO · DEMIS HASSABIS & DEEPMIND
- **Autor:** Sir Demis Hassabis & John Jumper.
- **Institución:** Google DeepMind / Isomorphic Labs.
- **Hito:** AlphaFold 2 & AlphaFold 3 (Predicción de estructuras biomoleculares).
- **Premio:** Premio Nobel de Química 2024.
- **Rótulo Canónico:**  
  `[INVESTIGACIÓN]: Demis Hassabis & John Jumper · Google DeepMind`  
  `[RECONOCIMIENTO]: Premio Nobel de Química 2024 · AlphaFold / Nature`

---
*Documento sellado bajo el Canon R768 · Gobernanza Soberana HBOS op=249.*
