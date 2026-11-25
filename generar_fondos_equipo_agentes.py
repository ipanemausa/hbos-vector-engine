"""
HBOS · GENERADOR DE FONDOS 16:9 DEDICADOS A 'EQUIPO DE AGENTES DE IA'
Destino: G:\\My Drive\\Guiahoy_Produccion\\2026-11-25\\fondos_16x9\\bg_01.jpg a bg_10.jpg
Sin referencias a Clase 01 MIT, Make ni RAG 768D.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"G:\My Drive\Guiahoy_Produccion\2026-11-25\fondos_16x9"
os.makedirs(OUT_DIR, exist_ok=True)

BLOCKS_DATA = [
    {
        "id": 1,
        "file": "bg_01.jpg",
        "title": "MÓDULO 01: EQUIPOS DE AGENTES DE IA",
        "subtitle": "De un Modelo Aislado a una Fuerza de Trabajo Especializada",
        "points": [
            "Superando el límite del chatbot: especialización funcional por roles",
            "Estructura colaborativa: división clara de tareas y responsabilidades",
            "Multiplicador de capacidad operativa para profesionales y empresas"
        ]
    },
    {
        "id": 2,
        "file": "bg_02.jpg",
        "title": "MÓDULO 02: EL AGENTE COORDINADOR",
        "subtitle": "El Director de Orquesta y Enrutador Autónomo",
        "points": [
            "Descomposición de solicitudes complejas en flujos de tareas ordenadas",
            "Asignación inteligente al agente más capacitado para cada paso",
            "Supervisión estricta de plazos, consistencia y criterios de éxito"
        ]
    },
    {
        "id": 3,
        "file": "bg_03.jpg",
        "title": "MÓDULO 03: EL AGENTE INVESTIGADOR",
        "subtitle": "Minería de Datos, Citas Exactas y Contexto en Tiempo Real",
        "points": [
            "Rastreo metódico de fuentes documentales, inventarios y mercado",
            "Extracción de hechos puros y evidencia verificada sin improvisación",
            "Entrega de contexto estructurado para toma de decisiones ejecutivas"
        ]
    },
    {
        "id": 4,
        "file": "bg_04.jpg",
        "title": "MÓDULO 04: EL AGENTE EJECUTOR Y CREADOR",
        "subtitle": "Producción Precisa de Código, Contenidos y Propuestas",
        "points": [
            "Construcción técnica enfocada sobre la evidencia suministrada",
            "Aplicación estricta de manuales corporativos y fórmulas del negocio",
            "Generación ágil de borradores completos y entregables listos"
        ]
    },
    {
        "id": 5,
        "file": "bg_05.jpg",
        "title": "MÓDULO 05: EL AGENTE AUDITOR",
        "subtitle": "Control de Calidad Riguroso y Verificación Cero Alucinación",
        "points": [
            "Revisión escéptica e independiente antes de cualquier publicación",
            "Validación de coherencia matemática, lógica y respaldo documental",
            "Ciclos de retroalimentación interna para garantizar rigor institucional"
        ]
    },
    {
        "id": 6,
        "file": "bg_06.jpg",
        "title": "MÓDULO 06: PROTOCOLOS DE COMUNICACIÓN",
        "subtitle": "Handoffs Estructurados y Líneas de Producción Digital",
        "points": [
            "Transferencia estándar de estados, entradas y condiciones de salida",
            "Activación automática por etapas sin desorden ni mensajes vagos",
            "Flujos continuos de extremo a extremo con alta trazabilidad técnica"
        ]
    },
    {
        "id": 7,
        "file": "bg_07.jpg",
        "title": "MÓDULO 07: HUMANO EN EL BUCLE (HUMAN-IN-THE-LOOP)",
        "subtitle": "La Supervisión Estratégica que Potencia el Juicio del Líder",
        "points": [
            "Los agentes procesan el volumen; el humano toma la decisión crítica",
            "Evolución del rol operativo a director general del sistema",
            "Aprobación ejecutiva de alto nivel con un solo clic de confirmación"
        ]
    },
    {
        "id": 8,
        "file": "bg_08.jpg",
        "title": "MÓDULO 08: APLICACIÓN REAL EN LA EMPRESA",
        "subtitle": "Ventas B2B, Operaciones y Soporte Continuo",
        "points": [
            "Calificación comercial instantánea y cotizaciones a la medida (< 10s)",
            "Auditoría de operaciones, facturas y conciliación de inventario",
            "Atención autónoma sin interrupciones sobre infraestructura propia"
        ]
    },
    {
        "id": 9,
        "file": "bg_09.jpg",
        "title": "MÓDULO 09: MÉTRICAS DE PRODUCTIVIDAD",
        "subtitle": "La Fuerza de 5 Especialistas Coordinados en un Solo Flujo",
        "points": [
            "Reducción superior al 90% en tiempos de ciclo y entrega de proyectos",
            "Recuperación de más de 120 horas de trabajo mensual para el equipo",
            "Liberación de tiempo humano para innovación, negociación y empatía"
        ]
    },
    {
        "id": 10,
        "file": "bg_10.jpg",
        "title": "MÓDULO 10: CONCLUSIÓN Y HOJA DE RUTA",
        "subtitle": "Puesta en Marcha Práctica · Guillermo Alonso Hoyos",
        "points": [
            "Construcción paso a paso de tu propio equipo de agentes autónomos",
            "Tecnología aplicada con soberanía y sin rentas tecnológicas abusivas",
            "Mesa de trabajo práctica en vivo con Guía Hoy"
        ]
    }
]

def get_font(size, bold=False):
    fonts = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

f_head = get_font(30, bold=True)
f_title = get_font(34, bold=True)
f_sub = get_font(20, bold=False)
f_card_t = get_font(18, bold=True)
f_card_d = get_font(15, bold=False)
f_badge = get_font(14, bold=True)

print("Iniciando generación de los 10 fondos futuristas en:", OUT_DIR)

for b in BLOCKS_DATA:
    out_file = os.path.join(OUT_DIR, b["file"])
    img = Image.new("RGB", (1920, 1080), (6, 11, 22))
    d = ImageDraw.Draw(img)

    # 1. Grid tecnológico sutil
    for y in range(0, 1080, 40):
        d.line([(0, y), (1920, y)], fill=(12, 20, 38), width=1)
    for x in range(0, 1920, 40):
        d.line([(x, 0), (x, 1080)], fill=(12, 20, 38), width=1)

    # 2. Resplandor superior y líneas guía
    d.line([(0, 2), (1920, 2)], fill=(56, 189, 248), width=3)

    # 3. Banner Header Superior
    d.rounded_rectangle([60, 45, 1160, 120], radius=14, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    d.ellipse([85, 74, 99, 88], fill=(52, 211, 153))
    d.text((115, 66), "EQUIPO DE AGENTES DE IA · GUÍA HOY", fill=(255, 255, 255), font=f_head)

    # Badge de Bloque
    d.rounded_rectangle([860, 64, 1135, 100], radius=8, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    d.text((880, 72), f"BLOQUE {b['id']:02d} / 10", fill=(56, 189, 248), font=f_badge)

    # 4. Contenedor Principal (Anti-oclusión: 2/3 izquierdos para reservar derecha al avatar)
    d.rounded_rectangle([60, 140, 1160, 840], radius=18, fill=(11, 17, 33), outline=(30, 41, 59), width=2)

    # 5. Título y Subtítulo Temático
    d.text((95, 175), b["title"], fill=(248, 250, 252), font=f_title)
    d.text((95, 225), b["subtitle"], fill=(56, 189, 248), font=f_sub)
    d.line([(95, 265), (1125, 265)], fill=(51, 65, 85), width=2)

    # 6. Tarjetas de Pilares y Contenido
    card_colors = [(56, 189, 248), (52, 211, 153), (192, 132, 252)]
    for i, pt in enumerate(b["points"]):
        y0 = 295 + i * 155
        y1 = y0 + 130
        c = card_colors[i % len(card_colors)]
        d.rounded_rectangle([95, y0, 1125, y1], radius=14, fill=(19, 27, 46), outline=c, width=1)
        # Indicador visual
        d.ellipse([125, y0 + 35, 145, y0 + 55], fill=c)
        d.text((165, y0 + 25), f"Pilar {i+1}", fill=c, font=f_card_t)
        d.text((165, y0 + 58), pt, fill=(226, 232, 240), font=f_card_d)

    # 7. Barra Inferior de Telemetría
    d.rounded_rectangle([60, 860, 1160, 930], radius=12, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    d.text((95, 882), "Arquitectura Multi-Agente · Colaboración Especializada · Guillermo Alonso Hoyos · Guía Hoy 2026", fill=(148, 163, 184), font=f_badge)

    img.save(out_file, quality=95)
    print(f"  [+] Regenerado: {b['file']} ({b['title']})")

print("Todos los 10 fondos de 'Equipo de Agentes de IA' se han regenerado exitosamente.")
