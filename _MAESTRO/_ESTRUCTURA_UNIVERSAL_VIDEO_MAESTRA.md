# REGLA R67 · ESTRUCTURA UNIVERSAL DE PRODUCCIÓN AUDIOVISUAL
**Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
**Vigente desde op=245 · Válido para cualquier dominio o formato de contenido**

---

## 1. PRINCIPIO RECTOR Y ALCANCE UNIVERSAL (R67)
Toda producción audiovisual generada en el ecosistema HBOS —ya sea sobre descubrimientos científicos, noticias de frontera, revisiones de software, tutoriales técnicos o análisis geopolíticos— obedece a una **arquitectura universal de cinco capas desacopladas y cinco fases temporales inmutables**.

El objetivo es eliminar la improvisación artesanal, garantizar coherencia visual/narrativa de grado broadcast e independizar el motor de producción del tema específico abordado.

---

## 2. ARQUITECTURA UNIVERSAL DE ROLES Y ELEMENTOS

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CANAL MAESTRO: HBOS                           │
├────────────────────────────────────────────────────────────────────────┤
│  CAPA 4 · HUMANO SOBERANO       │ Álex (ALEJAVI) · Presencia / Firma    │
│  CAPA 3 · DIRECTOR / ANCHOR     │ Diamantino · Conductor Principal     │
│  CAPA 2 · ANCHORS ESPECIALISTAS │ Anchors Temáticos (Salud, Farma, etc)│
│  CAPA 1 · CANVAS DE CONTENIDO   │ Backgrounds Dinámicos · Citas R58    │
│  CAPA 0 · AUDIO MASTER          │ Voiceover (-14 LUFS) + BGM (-22 LUFS)│
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Especificación de Roles
1. **CANAL: HBOS**
   - Marco institucional soberano, identidad criptográfica y línea gráfica broadcast.
2. **DIRECTOR & ANCHOR PRINCIPAL: Diamantino**
   - Entidad inteligente central; conduce la narrativa, modula los cambios de fase, presenta las tesis rectoras e interactúa con el canvas y la audiencia.
3. **ANCHORS TEMÁTICOS: Especialistas Modulares**
   - Personajes secundarios activados según la ontología del episodio:
     - *Anchor Salud / Bio:* Genomas, proteómica, medicina personalizada.
     - *Anchor Farma / Química:* Descubrimiento de fármacos, síntesis, bio-reactores.
     - *Anchor Algorítmico / Cuántico:* Arquitecturas LLM, transformers, computación cuántica.
     - *Anchor Legal / Soberano:* Gobernanza de datos, licencias y normativas.
4. **HUMANO SOBERANO: Álex (ALEJAVI)**
   - Director y titular biométrico; valida tesis de fondo, ancla la empatía comunitaria y supervisa la frontera exterior.
5. **CONTENIDO DINÁMICO: Backgrounds y Storyboard Cinético**
   - Gráficos 3D, simulaciones, esquemas moleculares y citas textuales auditadas bajo R58.

---

## 3. LAS CINCO FASES TEMPORALES INMUTABLES

Todo guion, timeline y renderizado se estructura en cinco fases obligatorias:

| Fase | Denominación Canónica | Función Narrativa | Anchors Activos |
|---|---|---|---|
| **Fase 1** | **Intro** | Planteamiento del problema, tesis central y contextualización de frontera. | Diamantino (⊕ Álex en episodios insignia) |
| **Fase 2** | **Desarrollo I** | Fundamentos empíricos, antecedentes históricos o estado del arte. | Diamantino + Anchor Especialista A |
| **Fase 3** | **Desarrollo II** | El quiebre disruptivo, mecanismo de innovación y demostración cuantitativa. | Diamantino + Anchor Especialista A/B |
| **Fase 4** | **Aplicación / Análisis** | Casos de uso prácticos en la industria, impacto real y validación en mercado. | Diamantino + Anchor Especialista B |
| **Fase 5** | **Cierre Soberano** | Síntesis epistemológica, llamado a la comunidad e integración HBOS. | Diamantino ⊕ Álex |

---

## 4. MATRIZ DE INTEGRACIÓN CON REGLAS PREVIAS

- **R58 (Veracidad Total):** En cada fase se proyecta en lower third la fuente oficial, fecha y cita verificada (cero alucinación).
- **R59 (Aislamiento Total):** Todos los assets de cada video residen exclusivamente en `assets/videos/<id_video>/` sin contaminación cruzada.
- **R61 (Roles Desacoplados):** Jerarquía estricta entre capas visuales (Diamantino, Secundarios, Background, Álex).
- **R62 (Anchors Vivos):** Movimiento humanizado con oscilación armónica continua (420 micro-movimientos por ciclo: respiración, micro-sacadas oculares, balanceo craneal).
- **R67 (Estructura Universal):** El motor (`hbos_anchor_vivo.py`) consume las fases serializadas en JSON para cualquier tema sin reescribir la lógica base.

---

## 5. PLANTILLA UNIVERSAL DE MANIFIESTO DE FASE (`fase_template.json`)

```json
{
  "fase_id": 1,
  "nombre": "Intro: [Título Universal]",
  "canal": "HBOS",
  "anchor_principal": "Diamantino",
  "anchor_secundario": null,
  "presentador_humano": "Alex",
  "background_tema": "[Canvas Visual Dinámico]",
  "fuente_r58": "[Fuente Oficial Verificada con URL y Fecha]",
  "dialogo": "[Texto del locutor con sincronía de audio]",
  "duracion_segundos": 45.0,
  "movimientos_humanizados": {
    "pasos_interpolacion": 420,
    "respiracion_hz": 0.25,
    "gestos": "apertura_y_enfasis"
  }
}
```
