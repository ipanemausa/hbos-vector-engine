import json
import os

fases = [
    {
        "fase_id": 1,
        "nombre": "Intro: El Arquitecto de DeepMind",
        "anchor_principal": "Diamantino",
        "anchor_secundario": None,
        "presentador_humano": "Alex (Supervisión)",
        "background_tema": "Redes Neuronales y Cómputo Cuántico",
        "fuente_r58": "Google DeepMind About (deepmind.google/about) · Nobel Chemistry 2024",
        "dialogo": "Saludos, arquitectos del futuro. Hoy desentrañamos el hito que redefinió la frontera entre computación y biología molecular: la trayectoria de Sir Demis Hassabis y Google DeepMind.",
        "duracion_segundos": 45.0,
        "movimientos_humanizados": {
            "respiracion_frecuencia_hz": 0.25,
            "micro_inclinacion_cabeza": "dinamica_suave_3_grados",
            "parpadeo_intervalo_s": [2.8, 4.2],
            "gestos_manos": "apertura_bienvenida_y_enfasis_frontal",
            "vector_mirada": "directo_a_camara_con_foco_activo",
            "pasos_interpolacion": 420
        },
        "interaccion_background": {
            "evento_inicio": "pulso_sinaptico_central",
            "evento_destacado": "aparicion_holograma_demis_deepmind",
            "zoom_canvas": 1.05
        }
    },
    {
        "fase_id": 2,
        "nombre": "Genomas: El Enigma del Plegamiento",
        "anchor_principal": "Diamantino",
        "anchor_secundario": "Anchor_Salud",
        "presentador_humano": None,
        "background_tema": "Doble Hélice de ADN y Cadenas Polipeptídicas",
        "fuente_r58": "Nature 596, 583–589 (2021) · CASP14 Structural Biology Milestone",
        "dialogo": "Durante cincuenta años, el enigma del plegamiento de proteínas desafió a los mayores centros del planeta. El código genético dictaba la secuencia, pero inferir la estructura 3D requería décadas.",
        "duracion_segundos": 55.0,
        "movimientos_humanizados": {
            "respiracion_frecuencia_hz": 0.28,
            "micro_inclinacion_cabeza": "giro_atento_hacia_anchor_salud_15_grados",
            "parpadeo_intervalo_s": [3.0, 4.5],
            "gestos_manos": "senalizacion_lateral_al_canvas_genomico",
            "vector_mirada": "alternada_camara_y_pantalla_adn",
            "pasos_interpolacion": 420
        },
        "interaccion_background": {
            "evento_inicio": "despliegue_helice_adn_3d",
            "evento_destacado": "simulacion_plegamiento_aminoacidos",
            "zoom_canvas": 1.15
        }
    },
    {
        "fase_id": 3,
        "nombre": "AlphaFold: Precisión Atómica y Open Science",
        "anchor_principal": "Diamantino",
        "anchor_secundario": "Anchor_Salud",
        "presentador_humano": None,
        "background_tema": "Red de Atención Espacial AlphaFold 2 y 3",
        "fuente_r58": "EMBL-EBI AlphaFold Database (alphafold.ebi.ac.uk) & Nature 630, 493–500 (2024)",
        "dialogo": "Con AlphaFold, DeepMind no solo resolvió el reto con precisión atómica, sino que liberó más de doscientos millones de estructuras tridimensionales para toda la humanidad.",
        "duracion_segundos": 50.0,
        "movimientos_humanizados": {
            "respiracion_frecuencia_hz": 0.26,
            "micro_inclinacion_cabeza": "asentimiento_rotundo_de_veracidad",
            "parpadeo_intervalo_s": [2.5, 3.8],
            "gestos_manos": "sintesis_palmar_expandida",
            "vector_mirada": "foco_en_metadatos_200m_estructuras",
            "pasos_interpolacion": 420
        },
        "interaccion_background": {
            "evento_inicio": "convergencia_de_gradientes_3d",
            "evento_destacado": "proyeccion_globo_terrestre_con_200M_proteinas",
            "zoom_canvas": 1.20
        }
    },
    {
        "fase_id": 4,
        "nombre": "Aplicaciones: Farma, Hospitales y Sostenibilidad",
        "anchor_principal": "Diamantino",
        "anchor_secundario": "Anchor_Farma",
        "presentador_humano": None,
        "background_tema": "Acoplamiento Molecular Ligando-Receptor y PETasa",
        "fuente_r58": "Isomorphic Labs Collaborations (Eli Lilly, Novartis) & Portsmouth University PETase",
        "dialogo": "A través de Isomorphic Labs y alianzas multimillonarias con Novartis y Eli Lilly, la predicción acelera fármacos y bio-enzimas para degradar plásticos en horas.",
        "duracion_segundos": 52.0,
        "movimientos_humanizados": {
            "respiracion_frecuencia_hz": 0.27,
            "micro_inclinacion_cabeza": "escucha_activa_y_ceder_turno_a_farma",
            "parpadeo_intervalo_s": [2.9, 4.1],
            "gestos_manos": "apuntamiento_precision_a_sitio_activo_enzima",
            "vector_mirada": "camara_con_microdesplazamientos_humanos",
            "pasos_interpolacion": 420
        },
        "interaccion_background": {
            "evento_inicio": "docking_molecular_en_tiempo_real",
            "evento_destacado": "descomposicion_molecular_polimero_pet",
            "zoom_canvas": 1.10
        }
    },
    {
        "fase_id": 5,
        "nombre": "Cierre y Soberanía HBOS",
        "anchor_principal": "Diamantino",
        "anchor_secundario": None,
        "presentador_humano": "Alex (Director Soberano)",
        "background_tema": "Grafo de Inferencia DAG HBOS-Diamantino",
        "fuente_r58": "Royal Swedish Academy Nobel 2024 & Arquitectura HBOS FAM@-T",
        "dialogo": "Demis Hassabis demostró que la inteligencia artificial es un telescopio para la ciencia fundamental. En HBOS-Diamantino, adoptamos este rigor para coordinar la nueva era cognitiva.",
        "duracion_segundos": 49.0,
        "movimientos_humanizados": {
            "respiracion_frecuencia_hz": 0.24,
            "micro_inclinacion_cabeza": "elevacion_inspiracional_frontal",
            "parpadeo_intervalo_s": [3.1, 4.4],
            "gestos_manos": "cierre_manos_juntas_agradecimiento_respetuoso",
            "vector_mirada": "directo_a_comunidad_y_camara",
            "pasos_interpolacion": 420
        },
        "interaccion_background": {
            "evento_inicio": "despliegue_constelacion_hbos_diamantino",
            "evento_destacado": "sello_inmutable_unbe_100_ok",
            "zoom_canvas": 1.00
        }
    }
]

out_dir = os.path.join("assets", "videos", "demis_hassabis_v2", "fases")
os.makedirs(out_dir, exist_ok=True)
for f in fases:
    f_id = f["fase_id"]
    path = os.path.join(out_dir, f"fase_{f_id}.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(f, fp, indent=2, ensure_ascii=False)
    print(f"Fase {f_id} guardada en {path}")
