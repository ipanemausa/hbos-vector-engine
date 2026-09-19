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

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

payload_op97 = {
    "operation_id": 97,
    "tarea": "FASE 1 — INVESTIGACIÓN EN GITHUB DE FREELLMAPI",
    "timestamp": "2026-09-19T14:17:00Z",
    "repositorio": {
        "url": "https://github.com/tashfeenahmed/freellmapi",
        "homepage": "https://freellmapi.co",
        "licencia": "MIT",
        "estrellas": 27312,
        "forks": 3731,
        "contribuidores": 80,
        "lenguaje": "TypeScript",
        "open_issues_count": 34,
        "top_issues": [
            "#1270: Desktop: Update available for untagged commits that have no installer",
            "#1262: Reliability: per-endpoint TTFB-aware retry budget",
            "#1261: Feature: observed capability scoring — learn tool/vision support from live traffic",
            "#1254: Reliability: endpoint-level health state machine",
            "#1234: Feature: model_health_status table — per-model per-key persistent pass/fail tracking"
        ]
    },
    "capacidades": {
        "total_proveedores": 34,
        "total_endpoints_modelos": 635,
        "desglose": "584 chat, 41 embeddings, 7 transcripcion, 3 rerankers",
        "tts_gratis": ["CosyVoice2 (via SiliconFlow)", "Custom OpenAI-compatible TTS endpoints"],
        "video_gratis": ["Pollinations", "HuggingFace (fal queue)"],
        "imagen_gratis": ["FLUX.1-schnell (SiliconFlow/Pollinations)"],
        "modelos_texto_destacados": ["Gemini 2.5", "Qwen 2.5 / Qwen 3", "DeepSeek V3 / R1 / V4", "Mistral", "Llama 3.3"]
    },
    "privacidad_y_seguridad": {
        "cifrado_keys": "AES-256-GCM local en SQLite, descifrado solo en memoria",
        "almacenamiento_prompts": "Servidor central nunca ve prompts ni keys (zero-knowledge local proxy)",
        "gdpr": "Self-hosted localmente sin telemetria central PII",
        "terminos": "MIT License, exclusivamente para experimentacion personal y prototipado"
    },
    "compatibilidad": {
        "mcp_oficial": True,
        "mcp_endpoint": "/mcp",
        "openai_compatible": True,
        "superficies_adicionales": ["Anthropic /v1/messages", "Gemini /v1beta", "Ollama emulation"],
        "integracion_antigravity": True,
        "metodos_integracion": ["Proxy OpenAI base_url", "MCP server nativo", "Inferencia via scripts"]
    },
    "estado": "COMPLETADO"
}

vec_97 = generate_embedding("Fase 1 operacion 97 Investigacion FreeLLMAPI GitHub Tashfeen Ahmed MIT Capacidades TTS Privacidad MCP", dim=384)

client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=97,
            vector=vec_97,
            payload=payload_op97
        )
    ]
)
print("[OK] operation_id = 97 registrado exitosamente en registro_ecosistema de Qdrant.")
