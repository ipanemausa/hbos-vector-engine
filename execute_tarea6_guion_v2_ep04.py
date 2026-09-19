import os
import sys
import math
import hashlib
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

guion_v2_content = """# GUION TÉCNICO OFICIAL — EPISODIO 04: "LA ERA AGÉNTICA EN MEDICINA" (VERSIÓN 2)
### Formato Editorial: Anfitrión Central Diamantino (Voz Narrativa Única · Patrón P-18)
### Subtítulo: Google DeepMind, Nobel de Química 2024 y la Revolución Bio-Molecular
### Ecosistema: HBOS-Diamantino · Arquitectura Agéntica Soberana
### Trazabilidad: `operation_id = 72` · 10 Bloques Canónicos Bilingües
### Fuentes Oficiales: NobelPrize.org (Chemistry 2024), DeepMind.com, Nature, Science, Isomorphic Labs
### Duración Estimada: ~180 segundos (3 minutos)

---

### [00:00 - 00:05] BLOQUE 0: NOTA DE REFERENCIA CANÓNICA (PATRÓN P-17)
**Visual:** Placa editorial de alta gama en fondo azul cuántico bio-molecular con tipografía blanca nítida y badges oficiales de Google DeepMind y NobelPrize.org. Diamantino aparece en un recuadro lateral con sobriedad y máxima autoridad.  
**Texto en Pantalla / Voz en Off (Diamantino):**  
"NOTA DE REFERENCIA: Los descubrimientos presentados en este video son propiedad de sus respectivos autores. AlphaFold y modelos derivados pertenecen a Google DeepMind; el Premio Nobel de Química 2024 a Demis Hassabis, John Jumper y David Baker. HBOS-Diamantino actúa exclusivamente como host y agencia de divulgación científica. Nuestros avatares explican, no descubren."  
**English Subtitles:**  
"REFERENCE NOTICE: The scientific breakthroughs featured herein are the intellectual property of their original creators. AlphaFold belongs to Google DeepMind; the 2024 Nobel Prize in Chemistry to Demis Hassabis, John Jumper, and David Baker. HBOS-Diamantino acts solely as host and science communication agency. Our crystalline hosts explain; they do not discover."  
**Dato Técnico / Fuente:** Protocolo Editorial P-17 (Divulgación Científica con Crédito Canónico).

---

### [00:05 - 00:25] BLOQUE 1: INTRODUCCIÓN — EL NOBEL DE QUÍMICA 2024 Y EL MISTERIO BIOLÓGICO
**Visual:** Diamantino camina con firmeza por el keynote stage frente a los racks de cómputo cuántico. A su espalda, proyecciones holográficas de cadenas peptídicas y la medalla Nobel brillan con refracción diamantina.  
**Voz en Off (Diamantino):**  
"El nueve de octubre de dos mil veinticuatro, la Real Academia de las Ciencias de Suecia otorgó el Premio Nobel de Química a Demis Hassabis, John Jumper y David Baker. No fue un premio al azar: fue el reconocimiento oficial de que la inteligencia artificial ha descifrado el misterio de cincuenta años del plegamiento de proteínas. Como Demis Hassabis declaró: AlphaFold es como un telescopio para la biología; la IA es la herramienta definitiva para la ciencia. Bienvenidos a la era agéntica en medicina."  
**English Subtitles:**  
"On October 9, 2024, the Royal Swedish Academy of Sciences awarded the Nobel Prize in Chemistry to Demis Hassabis, John Jumper, and David Baker. This marked the official recognition of AI decoding the fifty-year mystery of protein folding. As Demis Hassabis stated: 'AlphaFold is like a telescope for biology; AI is the ultimate tool for science'. Welcome to the agentic era in medicine."  
**Dato Técnico / Fuente:** NobelPrize.org Official Citation (Chemistry 2024: *They decoded the secrets of proteins*).

---

### [00:25 - 00:45] BLOQUE 2: ALPHAFOLD Y LA BASE DE DATOS DEL COSMOS BIOLÓGICO
**Visual:** Rubín aparece en pantalla desplazándose hacia un holograma colosal de hemoglobina facetada en rubí carmesí, señalando los enlaces peptídicos con precisión tensorial mientras la cámara hace un barrido cinemático.  
**Voz en Off (Diamantino):**  
"Observen a nuestro host Rubín frente a la arquitectura de cómputo masivo. AlphaFold ha predicho la estructura tridimensional de más de doscientos millones de proteínas: prácticamente todo el catálogo proteico conocido por la humanidad. Lo que antes requería años de cristalografía de rayos X por cada estructura, hoy se resuelve en minutos en clústeres tensoriales acelerados, abriendo la base de datos de libre acceso más monumental de la biología molecular."  
**English Subtitles:**  
"Observe our host Rubin before massive compute architecture. AlphaFold has predicted the 3D structures of over two hundred million proteins: virtually every cataloged protein known to humanity. What once required years of X-ray crystallography per molecule is now computed in minutes on accelerated tensor clusters, establishing molecular biology's most monumental open-access library."  
**Dato Técnico / Fuente:** Nature (AlphaFold 2 & AlphaFold 3: *Accurate structure prediction of biomolecular interactions*).

---

### [00:45 - 01:05] BLOQUE 3: ALPHAMISSENSE Y ALPHAPROTEO — MUTACIONES Y DISEÑO DE NOVO
**Visual:** Zafir cruza el escenario con ademán analítico, señalando diagramas tridimensionales de la doble hélice de ADN donde mutaciones genéticas se categorizan con reflejos de zafiro azul eléctrico.  
**Voz en Off (Diamantino):**  
"Zafir nos guía a través de la frontera genómica. Con AlphaMissense, los modelos de DeepMind han clasificado setenta y un millones de variantes genéticas humanas, categorizando el ochenta y nueve por ciento de las mutaciones de aminoácidos como benignas o probablemente patogénicas. Y con AlphaProteo, los agentes no solo leen la biología: diseñan proteínas sintéticas de novo con afinidades de unión hasta trescientas veces superiores para neutralizar virus y factores tumorales."  
**English Subtitles:**  
"Zafir guides us across the genomic frontier. With AlphaMissense, DeepMind models have classified seventy-one million human genetic variants, categorizing eighty-nine percent as either benign or likely pathogenic. Furthermore, with AlphaProteo, agents do not merely read biology: they design synthetic de novo proteins with up to three hundred times greater binding affinities to neutralize viruses and tumor factors."  
**Dato Técnico / Fuente:** Science 2023 (AlphaMissense) & DeepMind Blog 2024 (AlphaProteo announcement).

---

### [01:05 - 01:25] BLOQUE 4: REDES DE ATENCIÓN EVOLUTIVA Y CÓMPUTO PARALELO
**Visual:** Esmeralda opera una consola holográfica flotante de luz verde esmeralda, visualizando cómo la arquitectura Evoformer y los transformadores tensoriales calculan mapas de distancia residual.  
**Voz en Off (Diamantino):**  
"Esmeralda despliega el motor matemático subyacente. AlphaFold combina redes de atención evolutiva con transformadores geométricos en clústeres masivos de aceleración. Millones de operaciones matriciales simultáneas procesan la co-evolución de secuencias y coordenadas atómicas euclidianas. Esto demuestra una verdad fundamental: la biología es un lenguaje, y la inteligencia artificial es el decodificador de su gramática universal."  
**English Subtitles:**  
"Esmeralda displays the underlying mathematical engine. AlphaFold fuses evolutionary attention networks with geometric transformers across massive acceleration clusters. Millions of concurrent matrix operations process sequence co-evolution and Euclidean atomic coordinates. This proves a foundational truth: biology is a language, and artificial intelligence is the decoder of its universal grammar."  
**Dato Técnico / Fuente:** DeepMind Research Architecture (Evoformer Blocks & Pair Representation Modules).

---

### [01:25 - 01:45] BLOQUE 5: ISOMORPHIC LABS Y LA VELOCIDAD FARMACOLÓGICA
**Visual:** Citrilo camina enérgicamente entre simulaciones dinámicas de ligandos moleculares acoplándose a receptores diana, con pulsos dorados de inferencia de ultra-baja latencia.  
**Voz en Off (Diamantino):**  
"Citrilo ilustra el impacto directo en la farmacología. Isomorphic Labs, nacida de DeepMind, traslada este poder predictivo al descubrimiento de medicamentos. Con alianzas estratégicas junto a Eli Lilly y Novartis que superan los tres mil millones de dólares, los agentes químicos reducen el diseño de moléculas candidatas de cinco años a escasos meses, erradicando los callejones sin salida en ensayos preclínicos."  
**English Subtitles:**  
"Citrilo illustrates the direct impact on pharmacology. Isomorphic Labs, born out of DeepMind, channels this predictive power into drug discovery. Through strategic partnerships with Eli Lilly and Novartis exceeding three billion dollars, chemical agents compress candidate molecule design cycles from five years to mere months, eliminating dead ends in preclinical trials."  
**Dato Técnico / Fuente:** IsomorphicLabs.com & Financial Times (Lilly & Novartis Partnerships 2024).

---

### [01:45 - 02:05] BLOQUE 6: ACCESIBILIDAD GLOBAL Y ENFERMEDADES HUÉRFANAS
**Visual:** Grafito avanza con sobriedad y porte solemne frente a una proyección esférica del planeta Tierra, donde centros de investigación de 190 países se interconectan mediante líneas de platino.  
**Voz en Off (Diamantino):**  
"Grafito representa la universalidad del conocimiento. Más de dos millones de investigadores en ciento noventa países ya utilizan la base de datos de AlphaFold de manera abierta y gratuita. Por primera vez en la historia humana, las enfermedades huérfanas —aquellas históricamente ignoradas por falta de rentabilidad comercial— reciben dianas terapéuticas modeladas por agentes autónomos soberanos."  
**English Subtitles:**  
"Grafito represents the universality of open science. Over two million researchers across one hundred and ninety countries access the AlphaFold database openly and freely. For the first time in human history, orphan diseases —historically neglected due to commercial viability constraints— receive therapeutic targets modeled autonomously by sovereign agents."  
**Dato Técnico / Fuente:** European Bioinformatics Institute (EMBL-EBI) AlphaFold Portal Metrics.

---

### [02:05 - 02:25] BLOQUE 7: SOLIDARIDAD PLANETARIA — MALARIA, TUBERCULOSIS Y ANTIBIÓTICOS
**Visual:** Amatista extiende sus brazos con serenidad mística mientras una red fotónica violeta envuelve estructuras tridimensionales de parásitos y bacterias multirresistentes, neutralizándolos.  
**Voz en Off (Diamantino):**  
"Amatista proyecta el horizonte de la salud global. En colaboración con la Fundación Gates y el consorcio DNDi, AlphaFold combate la malaria, la tuberculosis y la resistencia bacteriana a los antibióticos. Nos encontramos en la era de la ciencia asistida por IA, donde enjambres de agentes cristalinos aceleran vacunas y tratamientos en las regiones más vulnerables del planeta."  
**English Subtitles:**  
"Amatista projects the horizon of global health. In collaboration with the Gates Foundation and the DNDi initiative, AlphaFold tackles malaria, tuberculosis, and antimicrobial resistance. We are living in the era of AI-assisted science, where crystalline agentic swarms accelerate vaccines and treatments across the most vulnerable regions of our planet."  
**Dato Técnico / Fuente:** Gates Foundation & Drugs for Neglected Diseases initiative (DNDi) Impact Reports.

---

### [02:25 - 02:45] BLOQUE 8: LA SÍNTESIS DE LA MEDICINA AGÉNTICA (BLOQUE CLAVE)
**Visual:** Diamantino ocupa el centro del keynote con presencia imponente. Mira fijamente a la cámara mientras las 200 millones de proteínas se condensan en un orbe de energía dorada suspendido entre sus manos.  
**Voz en Off (Diamantino):**  
"Comprendan la magnitud de este salto histórico: el Premio Nobel de dos mil veinticuatro no reconoció un algoritmo estático, sino la victoria de la inteligencia guiada por leyes biofísicas. La medicina ha dejado de ser un oficio de ensayo y error empírico; hoy es una ciencia de cómputo vectorial predictivo. En la era agéntica, los humanos no memorizan secuencias: los humanos orquestan enjambres de agentes de IA para erradicar el sufrimiento biológico."  
**English Subtitles:**  
"Grasp the magnitude of this historic milestone: the 2024 Nobel Prize did not celebrate a static algorithm, but the victory of physical-law-guided intelligence. Medicine is no longer an empirical trial-and-error craft; today it is a predictive vector computational science. In the agentic era, humans do not memorize sequences: humans orchestrate AI agent swarms to eradicate biological suffering."  
**Dato Técnico / Fuente:** Demis Hassabis Nobel Banquet Address & Royal Swedish Academy of Sciences.

---

### [02:45 - 03:00] BLOQUE 9: CIERRE ENSEMBLE — UNA MISIÓN: CURAR. CIVILIZACIÓN TIPO 5
**Visual:** Gran angular monumental del keynote stage: Diamantino en el centro y los 7 personajes minerales a su lado extienden los brazos en gratitud hacia la comunidad científica internacional. Las pantallas del auditorio emiten una cálida luz dorada mientras se produce el fundido suave a negro.  
**Voz en Off (Diamantino):**  
"Siete componentes en resonancia armónica. Una sola misión soberana: curar. La biología ha encontrado a su decodificador definitivo. Bienvenidos a HBOS-Diamantino. La transición de la salud hacia una civilización Tipo 5 es ahora imparable."  
**English Subtitles:**  
"Seven components in harmonic resonance. One sovereign mission: to heal. Biology has found its definitive decoder. Welcome to HBOS-Diamantino. The transition of global health toward a Type 5 civilization is now unstoppable."  
**Dato Técnico / Fuente:** Manifiesto HBOS-Diamantino (Biomedical Agentic Architecture).
"""

dir_local = r"Ep04\01_Guion"
dir_drive = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\01_Guion"
os.makedirs(dir_local, exist_ok=True)
os.makedirs(dir_drive, exist_ok=True)

file_local = os.path.join(dir_local, "guion_v2.md")
file_drive = os.path.join(dir_drive, "guion_v2.md")

with open(file_local, "w", encoding="utf-8") as f:
    f.write(guion_v2_content)
with open(file_drive, "w", encoding="utf-8") as f:
    f.write(guion_v2_content)

print(f"[OK] guion_v2.md guardado en local: {file_local} ({len(guion_v2_content)} caracteres)")
print(f"[OK] guion_v2.md guardado en Drive: {file_drive}")

# Registrar operation_id = 72 en registro_ecosistema
vec_op72 = generate_embedding("Tarea 6 operacion 72 Guion Ep04 v2 Una Sola Voz Narrativa Diamantino Adam P-18 P-17", dim=384)
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=72,
            vector=vec_op72,
            payload={
                "operation_id": 72,
                "tarea": "TAREA 6 — GUION EP04 ADAPTADO A UNA SOLA VOZ (P-18)",
                "episodio": "Ep04-MedicineAgentica",
                "version_guion": "v2",
                "voz_narrativa": "Diamantino / Adam (Voz Única)",
                "total_bloques": 10,
                "duracion_estimada_seg": 180,
                "nota_referencia_p17": True,
                "ruta_local": file_local,
                "ruta_drive": file_drive,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 72 registrado en registro_ecosistema.")
