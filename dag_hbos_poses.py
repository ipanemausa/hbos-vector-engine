#!/usr/bin/env python3
"""
DAG HBOS Poses: Generación de 200 poses vectorizadas 768D + RAG por fases
Para ejecutar en Antigravity: python dag_hbos_poses.py --fase [1-5]
"""

import os, sys, json, base64, subprocess
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
import argparse

# Configurar encoding seguro para consola Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cargar credenciales de entorno (.env.local)
from dotenv import load_dotenv
load_dotenv('.env.local')

# === CONFIGURACIÓN SOBERANA (100% CÓMPUTO EN LA NUBE) ===
class Config:
    # Qdrant Cloud (GCP)
    QDRANT_URL = os.getenv("QDRANT_URL", "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_ID = "hbos_poses_768"
    VECTOR_SIZE = 768
    
    # Generador Creativo en la Nube (Cloud APIs: Fal.ai / Replicate / DashScope)
    # REGLA DE ORO HBOS: CERO cómputo creativo pesado en hardware local
    CLOUD_IMAGE_PROVIDER = "fal_or_replicate"
    FAL_API_KEY = os.getenv("FAL_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # RAG
    EMBEDDING_MODEL = "all-mpnet-base-v2"  # 768D
    TOP_K_CONTEXT = 5
    
    # FFmpeg (operaciones ligeras de recorte/colorkey en CPU)
    FFMPEG_BIN = "ffmpeg"
    
    # Output
    OUTPUT_DIR = "hbos_poses_output"
    CHROMA_COLOR = "0x00FF00"

# === INICIALIZAR COMPONENTES ===
print("🔥 Inicializando componentes...")

# Modelo de embeddings 768D
embedder = SentenceTransformer(Config.EMBEDDING_MODEL)
print(f"✅ Embeddings 768D cargados: {Config.EMBEDDING_MODEL}")

# Conectar Qdrant (Cloud preferente)
if Config.QDRANT_API_KEY:
    qdrant = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
    print("✅ Conectado a Qdrant Cloud (GCP)")
else:
    qdrant = QdrantClient(host="localhost", port=6333)
    print("⚠️ Conectando a Qdrant local")

# Crear colección si no existe
collections = qdrant.get_collections().collections
if Config.COLLECTION_ID not in [c.name for c in collections]:
    qdrant.create_collection(
        collection_name=Config.COLLECTION_ID,
        vectors_config=models.VectorParams(
            size=Config.VECTOR_SIZE,
            distance=models.Distance.COSINE
        )
    )
    print(f"✅ Colección {Config.COLLECTION_ID} creada (768D)")
else:
    print(f"✅ Colección {Config.COLLECTION_ID} existe")

# === BASE DE CONOCIMIENTOS (RAG) ===
KNOWLEDGE_BASE = {
    "identidad": """
    IDENTIDAD BLOQUEADA - Guillermo:
    - 1.87m, complexión delgada/atlética, hombros anchos rectos, erguido
    - Cara: gafas, pelo corto gris, sonrisa sutil labios cerrados (dientes apenas visibles)
    - Piel: bronceado moderado natural en cara, más profundo en cuello/brazos/manos (nada rosáceo)
    - Ropa: camiseta negra con logo amarillo pequeño HB.OS, jean, zapatos negros, muñecas sin reloj
    - Postura: cuerpo erguido, cuello liso sin arrugas exageradas, sin papada colgante, sin huecos en mejillas
    - Textura: piel natural como fotografía genuina, marcas de edad sutiles
    """,
    
    "patron_movimientos": """
    PATRÓN DE MOVIMIENTOS:
    - Brazos: rotación total (palma arriba, abajo, dorso, frente, lado, girada)
    - Simetría obligatoria: cada gesto existe en versión derecha e izquierda
    - Piernas: peso izquierda, peso derecha, pies juntos, postura amplia, paso medio
    - Torso: erguido, adelante, atrás, izquierda, derecha
    - Cabeza: arriba, abajo, izquierda, derecha, inclinación lateral
    - Giros: 180° = perfiles y tres-cuartos; 360° = rotación del cuerpo (torno)
    - Movimientos acoplados: brazos con cintura/torso, cambios de peso con cadera compensando
    """,
    
    "limites_anatomicos": """
    LÍMITES ANATÓMICOS:
    - Cabeza sobre dorso quieto: 70-90° por lado, máximo
    - 180° hacia un lado = imposible
    - Barrido total izq→der ≈ 140-180° (la suma, no por lado)
    - Regla: cabeza sola ≤ ~80°; más allá, el torso acompaña
    """,
    
    "protocolo_produccion": """
    PROTOCOLO DE PRODUCCIÓN:
    - Fondo croma verde puro #00FF00 en prompt → ffmpeg colorkey → PNG transparente
    - Encuadre consistente: cuerpo entero centrado, pies abajo, cabeza arriba, misma escala
    - Catálogo en poses-catalogo.md (pose → archivo → combinación del patrón → estado)
    - Contact sheet por lote + revisión visual; cero piezas defectuosos al usuario
    """,
    
    "caminos_aprobados": """
    CAMINOS APROBADOS:
    - (a) stills con identidad bloqueada → interpolación (ffmpeg minterpolate)
    - (b) primer/último frame (2-3 imágenes → animación; Wan 2.2 la trae nativa)
    - (c) modelos guiados por pose (MimicMotion: 1 imagen + secuencia de poses)
    - (d) modelos guiados por audio (HunyuanVideo-Avatar: 1 imagen + voz)
    - (e) Kling tier gratis para clips sutiles (~6/día)
    DESCARTADO: image-to-video directo desde un still (desfigura)
    """,
    
    "estilo_visual": """
    ESTILO VISUAL:
    - Fotografía realista, 8k, iluminación de studio
    --ar 16:9 --v 6 --style raw
    - Textura de piel natural como fotografía genuina
    - Sin barriga, sin papada, sin huecos en mejillas
    - Hombros anchos rectos y nivelados (más anchos que el torso, nunca caídos)
    """
}

# === VECTORIZAR Y CARGAR RAG ===
def inicializar_rag():
    """Cargar conocimiento en Qdrant 768D"""
    print("🧠 Vectorizando base de conocimientos...")
    
    puntos = []
    id_counter = 0
    
    for categoria, texto in KNOWLEDGE_BASE.items():
        # Dividir en chunks si es muy largo
        chunks = [texto] if len(texto) < 1000 else [texto[i:i+1000] for i in range(0, len(texto), 1000)]
        
        for chunk in chunks:
            vector = embedder.encode([chunk])[0].tolist()
            payload = {
                "categoria": categoria,
                "texto": chunk,
                "timestamp": "2024-10-12"
            }
            
            puntos.append(models.PointStruct(
                id=id_counter,
                vector=vector,
                payload=payload
            ))
            id_counter += 1
    
    # Upsert en Qdrant
    qdrant.upsert(
        collection_name=Config.COLLECTION_ID,
        points=puntos
    )
    print(f"✅ {len(puntos)} fragmentos vectorizados (768D) cargados en Qdrant")

def retrieve_context(query: str, categoria: str = None, top_k: int = Config.TOP_K_CONTEXT) -> str:
    """Recuperar contexto relevante usando RAG 768D"""
    query_vector = embedder.encode([query])[0].tolist()
    
    # Filtro por categoría si se especifica
    query_filter = None
    if categoria:
        query_filter = models.Filter(
            must=[models.FieldCondition(
                key="categoria",
                keyword=models.KeywordValue(value=categoria)
            )]
        )
    
    search_result = qdrant.search(
        collection_name=Config.COLLECTION_ID,
        query_vector=query_vector,
        limit=top_k,
        query_filter=query_filter
    )
    
    contextos = []
    for hit in search_result:
        contextos.append(f"[{hit.payload['categoria']}] {hit.payload['texto']}")
    
    return "\n---\n".join(contextos)

# === DEFINICIÓN DE FASES (200 poses en 5 lotes de 40) ===
FASES = {
    1: {
        "nombre": "BRAZOS - Rotaciones Básicas",
        "lotes": 5,
        "poses_por_lote": 8,
        "prompt_template": """
        [REFERENCE: Guillermo v6-0]
        {contexto}
        Pose: {pose_descripción}
        Background: pure chroma green #00FF00
        Photorealistic, 8k, studio lighting, --ar 16:9 --v 6 --style raw
        """,
        "poses": [
            # Lote 1: Brazos basicos
            "Brazos en cruz T, palmas abajo, dedos extendidos",
            "Brazos en cruz T, palmas arriba, dedos extendidos",
            "Brazos laterales, palmas frente, codos ligeramente flexionados",
            "Brazos laterales, palmas lado, pulgares arriba",
            # Lote 2: Rotaciones avanzadas
            "Brazo derecho abajo, palma hacia atrás (vista dorsal), izquierdo relajado",
            "Brazo derecho adelante, palma rotada 90° hacia adentro, izquierdo espejo",
            "Ambos brazos adelante, palmas enfrentadas, ángulo 45°",
            "Brazo derecho apuntando derecha, torso rotado derecha; izquierdo apuntando izquierda, torso rotado izquierda",
            # Lote 3: Simetría y acoplamiento
            "Brazo derecho palma arriba, izquierdo palma abajo, simétrico",
            "Brazo derecho palma frente, izquierdo palma dorso, simétrico",
            "Ambos brazos en cruz, palmas giradas 45°, torsos neutros",
            "Brazos acoplados: derecho con torso derecha, izquierdo con torso izquierda",
            # Lote 4: Gestos complejos
            "Brazo derecho cruzado pecho, palma lado; izquierdo extendido, palma arriba",
            "Ambos brazos en cruz, palmas rotadas lentamente",
            "Brazo derecho gesto 'stop', palma frente; izquierdo relajado",
            "Ambos brazos hacia abajo, palmas hacia atrás, torsos adelantados",
            # Lote 5: Variaciones dinámicas
            "Brazo derecho en movimiento, palma arriba; izquierdo estático",
            "Ambos brazos en cruz, palmas alternando",
            "Brazo derecho palma arriba, izquierdo palma lado, torso ligeramente rotado",
            "Brazos en cruz, palmas hacia el observador, torsos erguidos"
        ]
    },
    
    2: {
        "nombre": "PIERNAS Y PESO",
        "lotes": 5,
        "poses_por_lote": 8,
        "poses": [
            # Lote 1: Pesos básicos
            "Peso en pierna izquierda, derecha ligeramente flexionada adelante, torso erguido",
            "Peso en pierna derecha, izquierda ligeramente flexionada adelante, torso erguido",
            "Pies juntos, torso erguido, brazos relajados",
            "Postura amplia: pies separados, rodillas ligeramente flexionadas, torso centrado",
            # Lote 2: Pasos y equilibrio
            "Paso medio: pie derecho adelante, pie izquierdo atrás, brazos balanceándose",
            "Paso medio: pie izquierdo adelante, pie derecho atrás, brazos balanceándose",
            "Peso izquierda, derecha cruzada delante, torso ligeramente rotado",
            "Peso derecha, izquierda cruzada delante, torso ligeramente rotado",
            # Lote 3: Posiciones dinámicas
            "Un pie en el aire, peso en el otro, torso erguido",
            "Ambos pies juntos, un talón elevado, torso erguido",
            "Postura amplia, un pie girado hacia afuera, torso centrado",
            "Paso medio, brazos en cruz, torso erguido",
            # Lote 4: Cambios de lado
            "Peso izquierda, torso hacia la derecha, brazos balanceándose",
            "Peso derecha, torso hacia la izquierda, brazos balanceándose",
            "Pies juntos, torso rotado 45° a la derecha",
            "Pies juntos, torso rotado 45° a la izquierda",
            # Lote 5: Combinaciones
            "Peso izquierda, brazo derecho adelante, torso erguido",
            "Peso derecha, brazo izquierdo adelante, torso erguido",
            "Postura amplia, brazos en cruz, torso erguido",
            "Paso medio, brazos en cruz, torso rotado 45°"
        ]
    },
    
    3: {
        "nombre": "TORSO Y CABEZA",
        "lotes": 5,
        "poses_por_lote": 8,
        "poses": [
            # Lote 1: Inclinaciones básicas
            "Cabeza arriba 15°, mirando al techo, torso erguido",
            "Cabeza abajo 15°, mirando al suelo, torso erguido",
            "Cabeza inclinada izquierda 10°, hombros nivelados, torso erguido",
            "Cabeza inclinada derecha 10°, hombros nivelados, torso erguido",
            # Lote 2: Giros simples
            "Cabeza rotada 45° derecha, torso erguido",
            "Cabeza rotada 45° izquierda, torso erguido",
            "Cabeza rotada 90° derecha, torso erguido",
            "Cabeza rotada 90° izquierda, torso erguido",
            # Lote 3: Giros encadenados
            "Cabeza 45° derecha, torso 15° derecha, hombros alineados",
            "Cabeza 45° izquierda, torso 15° izquierda, hombros alineados",
            "Cabeza 90° derecha, torso 45° derecha, hombros alineados",
            "Cabeza 90° izquierda, torso 45° izquierda, hombros alineados",
            # Lote 4: Movimientos acoplados
            "Cabeza arriba, torso adelante, brazos balanceándose",
            "Cabeza abajo, torso atrás, brazos balanceándose",
            "Cabeza izquierda, torso derecha, brazos en cruz",
            "Cabeza derecha, torso izquierda, brazos en cruz",
            # Lote 5: Combinaciones complejas
            "Cabeza arriba 10°, torso rotado 30° derecha, brazos en cruz",
            "Cabeza abajo 10°, torso rotado 30° izquierda, brazos en cruz",
            "Cabeza inclinada 5° izquierda, torso adelante, brazos relajados",
            "Cabeza al frente, torso atrás, brazos extendidos"
        ]
    },
    
    4: {
        "nombre": "GIROS COMPLETOS Y CADENA",
        "lotes": 5,
        "poses_por_lote": 8,
        "poses": [
            # Lote 1: Tres-cuartos
            "Tres-cuartos derecho: torso 45° derecha, cabeza al frente",
            "Tres-cuartos izquierdo: torso 45° izquierda, cabeza al frente",
            "Tres-cuartos derecho, cabeza rotada 30°",
            "Tres-cuartos izquierdo, cabeza rotada 30°",
            # Lote 2: Perfiles
            "Perfil derecho: torso 90° derecha, cabeza al frente",
            "Perfil izquierdo: torso 90° izquierda, cabeza al frente",
            "Perfil derecho, cabeza rotada 45°",
            "Perfil izquierdo, cabeza rotada 45°",
            # Lote 3: Cadena encadenada (15° por eslabón)
            "Cadena: torso 15° derecha, cabeza 15° derecha",
            "Cadena: torso 30° derecha, cabeza 30° derecha",
            "Cadena: torso 45° derecha, cabeza 45° derecha",
            "Cadena: torso 60° derecha, cabeza 60° derecha",
            # Lote 4: Rotación del cuerpo (torno)
            "Torno 90° derecha, cabeza acompañando",
            "Torno 180° (perfil), cabeza acompañando",
            "Torno 270° (tres-cuartos izquierdo), cabeza acompañando",
            "Torno 360° (volver al frente), cabeza acompañando",
            # Lote 5: Movimientos acoplados
            "Torno 90° derecha, brazo derecho adelante, izquierdo atrás",
            "Torno 180°, brazos en cruz, cabeza al frente",
            "Torno 270°, brazo izquierdo adelante, derecho atrás",
            "Torno completo, brazos balanceándose, cabeza moviéndose"
        ]
    },
    
    5: {
        "nombre": "POSES ESPECIALES Y COMPLEJAS",
        "lotes": 5,
        "poses_por_lote": 8,
        "poses": [
            # Lote 1: Gestos con las manos
            "Mano derecha en puño, brazo flexionado, izquierdo relajado",
            "Ambos brazos en cruz, dedos extendidos y separados",
            "Mano derecha tocando la cabeza, izquierdo en cruz",
            "Ambos brazos hacia abajo, palmas abajo, dedos juntos",
            # Lote 2: Expresiones corporales
            "Torso erguido, brazos en cruz, cabeza sonriendo",
            "Torso adelante, brazos relajados, cabeza mirando abajo",
            "Torso atrás, brazos extendidos, cabeza mirando arriba",
            "Torso rotado, brazos en cruz, cabeza inclinada",
            # Lote 3: Poses dinámicas
            "Brazo derecho en movimiento, palma arriba; izquierdo estático",
            "Ambos brazos en cruz, palmas alternando",
            "Brazo derecho palma arriba, izquierdo palma lado, torso ligeramente rotado",
            "Brazos en cruz, palmas hacia el observador, torsos erguidos",
            # Lote 4: Combinaciones extremas
            "Cabeza 90° derecha, torso 45° derecha, brazo derecho adelante",
            "Cabeza 90° izquierda, torso 45° izquierda, brazo izquierdo adelante",
            "Torno 180°, brazos en cruz, cabeza rotada 45°",
            "Torno 360°, brazos balanceándose, cabeza moviéndose",
            # Lote 5: Verificación de límites
            "Cabeza sola 80° (límite), torso quieto",
            "Cabeza 100° con torso 20° (acompañando)",
            "Barrido total 140° (cabeza 70° + torso 70°)",
            "Barrido total 180° (cabeza 90° + torso 90°)"
        ]
    }
}

# === GENERADOR DE IMÁGENES ===
def generate_image(prompt: str, output_path: str, lote: int, pose_num: int) -> bool:
    """Generar imagen usando Stable Diffusion WebUI API"""
    full_prompt = f"{prompt}, high quality, 8k, detailed"
    negative_prompt = "deformed, blurry, bad anatomy, extra limbs, poorly drawn hands, missing fingers, watermark, signature, text, logo, chroma green background"
    
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "steps": Config.SD_STEPS,
        "cfg_scale": Config.SD_CFG_SCALE,
        "width": Config.SD_WIDTH,
        "height": Config.SD_HEIGHT,
        "sampler_index": Config.SD_SAMPLER,
        "seed": -1,  # Aleatorio
        "batch_size": 1,
        "n_iter": 1
    }
    
    try:
        print(f"🎨 Generando {output_path}...")
        response = requests.post(Config.SD_API_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if 'images' in result and len(result['images']) > 0:
                image_base64 = result['images'][0]
                image_data = base64.b64decode(image_base64)
                
                os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
                filepath = os.path.join(Config.OUTPUT_DIR, output_path)
                
                with open(filepath, "wb") as f:
                    f.write(image_data)
                
                print(f"✅ {output_path} guardado")
                return True
            else:
                print(f"❌ Error: Sin imágenes en respuesta")
                return False
        else:
            print(f"❌ Error API: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generando {output_path}: {e}")
        return False

# === POST-PROCESAMIENTO FFMPEG ===
def process_pose(input_path: str, output_path: str, lote: int, pose_num: int) -> bool:
    """Aplicar colorkey y convertir a PNG transparente"""
    input_file = os.path.join(Config.OUTPUT_DIR, input_path)
    output_file = os.path.join(Config.OUTPUT_DIR, output_path)
    
    cmd = [
        Config.FFMPEG_BIN, "-y",
        "-i", input_file,
        "-vf", f"colorkey={Config.CHROMA_COLOR}:0.1:0.1",
        "-c:v", "png",
        output_file
    ]
    
    try:
        print(f"🔧 Procesando {input_path} → {output_path}")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ {output_path} procesado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error procesando {input_path}: {e.stderr.decode()}")
        return False

def generate_contact_sheet(lote: int, poses_count: int) -> bool:
    """Generar contact sheet para un lote"""
    # Buscar todos los PNG transparentes del lote
    input_files = []
    for i in range(1, poses_count + 1):
        filename = f"lote{lote}_pose{i}_transparente.png"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            input_files.append(filepath)
    
    if not input_files:
        print(f"❌ No hay imágenes para el contact sheet del lote {lote}")
        return False
    
    # Construir comando ffmpeg
    cmd = [Config.FFMPEG_BIN, "-y"]
    for f in input_files:
        cmd.extend(["-i", f])
    
    # Filtro complex para grid 4x2 (8 poses)
    filter_parts = []
    for i in range(len(input_files)):
        filter_parts.append(f"[{i}:v]drawtext=text='Pose {i+1}':fontcolor=white:fontsize=24:x=10:y=10[v{i}]")
    
    # Stack horizontal (4 por fila)
    row1 = "".join([f"[v{i}]" for i in range(min(4, len(input_files)))])
    row2 = "".join([f"[v{i}]" for i in range(4, min(8, len(input_files)))])
    
    filter_parts.append(f"{row1}hstack=inputs={min(4, len(input_files))}[row1]")
    if len(input_files) > 4:
        filter_parts.append(f"{row2}hstack=inputs={len(input_files)-4}[row2]")
        filter_parts.append("[row1][row2]vstack=inputs=2[final]")
        final_tag = "[final]"
    else:
        final_tag = "[row1]"
    
    filter_complex = ";".join(filter_parts)
    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", final_tag])
    cmd.extend(["-c:v", "png"])
    
    output_file = os.path.join(Config.OUTPUT_DIR, f"lote{lote}_contact_sheet.png")
    cmd.append(output_file)
    
    try:
        print(f"📊 Generando contact sheet lote {lote}...")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Contact sheet guardado: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generando contact sheet: {e.stderr.decode()}")
        return False

# === FLUJO PRINCIPAL ===
def ejecutar_fase(fase_num: int):
    """Ejecutar una fase completa"""
    if fase_num not in FASES:
        print(f"❌ Fase {fase_num} no encontrada. Disponibles: {list(FASES.keys())}")
        return
    
    fase = FASES[fase_num]
    print(f"\n{'='*60}")
    print(f"🚀 INICIANDO FASE {fase_num}: {fase['nombre']}")
    print(f"{'='*60}")
    
    # Recuperar contexto RAG
    contexto = retrieve_context(fase["nombre"], categoria="patron_movimientos")
    print(f"Contexto RAG recuperado: {len(contexto)} caracteres")
    
    total_poses = len(fase["poses"])
    poses_exitosas = 0
    
    for i, pose_desc in enumerate(fase["poses"], 1):
        lote = (i - 1) // 8 + 1
        pose_num = (i - 1) % 8 + 1
        
        # Generar prompt
        prompt = fase["prompt_template"].format(
            contexto=contexto,
            pose_descripción=pose_desc
        )
        
        # Generar imagen
        raw_filename = f"lote{lote}_pose{pose_num}_raw.png"
        if generate_image(prompt, raw_filename, lote, pose_num):
            # Procesar con FFmpeg
            transparent_filename = f"lote{lote}_pose{pose_num}_transparente.png"
            if process_pose(raw_filename, transparent_filename, lote, pose_num):
                poses_exitosas += 1
                print(f"✅ Pose {i}/{total_poses} completada")
            else:
                print(f"❌ Error procesando pose {i}")
        else:
            print(f"❌ Error generando pose {i}")
    
    # Generar contact sheet por lote
    for lote in range(1, fase["lotes"] + 1):
        generate_contact_sheet(lote, 8)
    
    print(f"\n✅ Fase {fase_num} completada: {poses_exitosas}/{total_poses} poses exitosas")

# === ANIMACIÓN FINAL ===
def generar_animacion_completa():
    """Generar animación con todas las poses"""
    print("\n🎬 Generando animación final...")
    
    # Buscar todos los PNG transparentes
    todos_los_archivos = []
    for root, dirs, files in os.walk(Config.OUTPUT_DIR):
        for file in files:
            if file.endswith("_transparente.png"):
                todos_los_archivos.append(os.path.join(root, file))
    
    if not todos_los_archivos:
        print("❌ No hay imágenes para animar")
        return
    
    # Ordenar por lote y pose
    try:
        todos_los_archivos.sort(key=lambda x: int(x.split("lote")[1].split("_pose")[0]) * 100 + int(x.split("_pose")[1].split("_")[0]))
    except Exception:
        todos_los_archivos.sort()
    
    # Comando ffmpeg para interpolación
    cmd = [
        Config.FFMPEG_BIN, "-y",
        "-framerate", "1",
        "-i", "lote%d_pose%d_transparente.png",
        "-vf", "minterpolate=fps=24:mode=average",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "hbos_poses_animacion.mp4"
    ]
    
    print("✅ Pipeline configurado para interpolación: hbos_poses_animacion.mp4")

# === MAIN ===
def main():
    parser = argparse.ArgumentParser(description="DAG HBOS Poses - Generación de 200 poses vectorizadas")
    parser.add_argument("--fase", type=int, choices=[1,2,3,4,5], help="Fase a ejecutar (1-5)")
    parser.add_argument("--todo", action="store_true", help="Ejecutar todas las fases")
    parser.add_argument("--animacion", action="store_true", help="Generar animación final")
    
    args = parser.parse_args()
    
    # Inicializar RAG
    inicializar_rag()
    
    if args.todo:
        for fase_num in range(1, 6):
            ejecutar_fase(fase_num)
        if args.animacion:
            generar_animacion_completa()
    elif args.fase:
        ejecutar_fase(args.fase)
        if args.animacion:
            generar_animacion_completa()
    else:
        print("Uso: python dag_hbos_poses.py --fase [1-5] | --todo")
        print("Ejemplos:")
        print("  python dag_hbos_poses.py --fase 1")
        print("  python dag_hbos_poses.py --todo --animacion")

if __name__ == "__main__":
    main()
