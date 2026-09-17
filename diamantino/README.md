# UNIVERSO DIAMANTINO — REPOSITORIO CANÓNICO Y REGLAS DE PRODUCCIÓN

Bienvenido a la carpeta canónica de **Universo Diamantino**, producción cinematográfica animada del ecosistema soberano **HBOS**.

---

## 🏛️ REGLA FUNDAMENTAL DE MEMORIA Y ALMACENAMIENTO
1. **NUNCA acumular multimedia pesada en el PC ni en Git**:
   - Todo archivo pesado (`.mp4`, `.wav`, `.png`, `.mp3`) se genera temporalmente, se sube a Google Drive (`G:\My Drive\HBOS-Diamantino\`), se verifica 1:1 y se borra inmediatamente del disco local.
   - En Git únicamente se versionan scripts, esquemas, prompts, guiones y metadatos JSON.
2. **Streaming en Producción**:
   - Los masters oficiales para consumo web se despliegan directamente a Vercel Edge (`https://hbos-vector-engine.vercel.app/media/diamantino/ep01.mp4`).

---

## 📁 ESTRUCTURA DEL PROYECTO

```text
diamantino/
├── MANIFEST.json                   # Índice general del proyecto (leído por todos los agentes)
├── README.md                       # Guía maestra humana
├── ep01/                           # Episodio 01: "La Tabla Periódica es una Mentira"
│   ├── context.json                # Estado, IDs y trazabilidad de Ep01
│   ├── storyboard.json             # Estructura narrativa de 6 planos (90s)
│   ├── guion/voz_off.txt           # Locución completa de los 6 planos
│   ├── prompts/
│   │   ├── music_prompt.txt        # Prompt orquestal BGM
│   │   └── i2v_prompt.txt          # Prompts de animación Wan 2.1
│   └── REFERENCIA_DRIVE.md         # Enlace al archivo íntegro en Google Drive
├── ep02/                           # Episodio 02: "El Agente: Lo Que Huang Realmente Dijo"
│   ├── context.json                # Estado de producción y personajes
│   ├── guion/voz_off.txt           # Guion de 5 minutos en 4 bloques
│   ├── prompts/
│   │   ├── personajes.md           # Ficha de los 7 personajes de gemas
│   │   └── i2v_prompt.txt          # Guía de animación para Wan 2.1
│   └── assets/                     # Directorio temporal de ensamblaje local
└── _shared/                        # Guía de estilo y coherencia transversal
    ├── personajes.md               # Universo completo de gemas
    ├── paleta_colores.json         # Códigos hex y tokens cromáticos
    └── estilo_visual.md            # Directrices de render Pixar/DreamWorks 3D
```

---

## 🚀 TRAZABILIDAD EN QDRANT CLOUD
- **Episodio 01**: `operation_id = 34` (Colección: `registro_ecosistema`)
- **Episodio 02**: `operation_id = 35` (En producción)
