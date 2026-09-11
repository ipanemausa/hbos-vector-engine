/**
 * SEED RECURSOS HBOS — QDRANT CLOUD (R384)
 * DAG R768 v17.0
 * Registra Voz (9), Avatares (59), Modelos (15), Servicios (12)
 */

import crypto from "crypto";

const QDRANT_URL = process.env.QDRANT_URL || "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io";
const QDRANT_API_KEY = process.env.QDRANT_API_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoyMTAzNTY3NDE0LCJzdWJqZWN0IjoiYXBpLWtleTozYmE3YTQ3ZC1hN2QzLTRmMDktOWY2Ny0xY2RmODAzYjlmNGYifQ.QDvkb89UU_j72W3auMM6O_hg39EMsiSP0CF7ojT4c-s";
const COLLECTION = "recursos_hbos";

// Generador de vector determinista R384 normalizado
function generarVector384(texto) {
  const hash = crypto.createHash("sha256").update(texto).digest();
  const vector = new Array(384);
  for (let i = 0; i < 384; i++) {
    const byte = hash[i % hash.length];
    const offset = Math.sin(i * 0.123 + byte) * 0.5;
    vector[i] = offset;
  }
  // Normalizar norma L2
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0)) || 1;
  return vector.map(v => Number((v / norm).toFixed(6)));
}

const timestamp = new Date().toISOString();

// ── 1. RECURSOS DE VOZ (9 Archivos) ──────────────────────────────────
const RECURSOS_VOZ = [
  {
    id: 101,
    tipo: "VOZ",
    nombre: "GUILLERMO_SOVEREIGN_AUTHENTIC_VOICE_48K.wav",
    ruta: "assets/voice/GUILLERMO_SOVEREIGN_AUTHENTIC_VOICE_48K.wav",
    formato: "WAV",
    tamaño: 73259662,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Master Maestro Soberano 48kHz / 16-bit PCM Estéreo (381.56s) sin compresión"
  },
  {
    id: 102,
    tipo: "VOZ",
    nombre: "guillermo_voice_studio_master_48k.wav",
    ruta: "assets/voice/guillermo_voice_studio_master_48k.wav",
    formato: "WAV",
    tamaño: 2924122,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Studio Master 48kHz WAV locución de referencia"
  },
  {
    id: 103,
    tipo: "VOZ",
    nombre: "guillermo_voice_studio_master_48k.aac",
    ruta: "assets/voice/guillermo_voice_studio_master_48k.aac",
    formato: "AAC",
    tamaño: 487378,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Studio Master comprimido AAC para streaming web rápido"
  },
  {
    id: 104,
    tipo: "VOZ",
    nombre: "guillermo_voice_real_master.aac",
    ruta: "assets/voice/guillermo_voice_real_master.aac",
    formato: "AAC",
    tamaño: 487378,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Voz real de producción utilizada en Media Vault"
  },
  {
    id: 105,
    tipo: "VOZ",
    nombre: "guillermo_voice_tiktok_raw.mp3",
    ruta: "assets/voice/guillermo_voice_tiktok_raw.mp3",
    formato: "MP3",
    tamaño: 243715,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Muestra original de captura directa móvil"
  },
  {
    id: 106,
    tipo: "VOZ",
    nombre: "GUILLERMO_HOYOS_HBOS_HISTORIA_CANONICA_REF_2026.mp3",
    ruta: "assets/voice/GUILLERMO_HOYOS_HBOS_HISTORIA_CANONICA_REF_2026.mp3",
    formato: "MP3",
    tamaño: 2312612,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Referencia de tono y cadencia para historia canónica"
  },
  {
    id: 107,
    tipo: "VOZ",
    nombre: "GUILLERMO_REAL_VOICE_3MIN_SUMMARY.mp3",
    ruta: "assets/voice/GUILLERMO_REAL_VOICE_3MIN_SUMMARY.mp3",
    formato: "MP3",
    tamaño: 1962780,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Resumen de voz auténtica para videos de formato medio (3 min)"
  },
  {
    id: 108,
    tipo: "VOZ",
    nombre: "GUILLERMO_EXPRESSIVE_VOICE_MASTER_48K.mp3",
    ruta: "assets/voice/GUILLERMO_EXPRESSIVE_VOICE_MASTER_48K.mp3",
    formato: "MP3",
    tamaño: 949229,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Master vocal optimizado con modulación expresiva para retención YouTube 2026"
  },
  {
    id: 109,
    tipo: "VOZ",
    nombre: "real_guillermo_voice.mp3",
    ruta: "assets/voice/real_guillermo_voice.mp3",
    formato: "MP3",
    tamaño: 239901,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Cápsula de voz real para previsualizaciones en cliente frontend"
  }
];

// ── 2. RECURSOS DE AVATAR (59 Elementos: 5 base + 50 slots + 4 videos) ─
const RECURSOS_AVATARES_BASE = [
  {
    id: 201,
    tipo: "AVATAR",
    nombre: "guillermo_studio_mic.png",
    ruta: "assets/avatars/base/guillermo_studio_mic.png",
    formato: "PNG",
    tamaño: 1403012,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Avatar base estudio con micrófono frontal, alta resolución"
  },
  {
    id: 202,
    tipo: "AVATAR",
    nombre: "avatar_transparent_hbos.png",
    ruta: "assets/avatars/base/avatar_transparent_hbos.png",
    formato: "PNG",
    tamaño: 1040783,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Avatar con recorte alfa transparente e insignia oficial HB.OS"
  },
  {
    id: 203,
    tipo: "AVATAR",
    nombre: "avatar_pro.png",
    ruta: "assets/avatars/base/avatar_pro.png",
    formato: "PNG",
    tamaño: 1313360,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Fotografía maestra profesional de estudio sin fondo"
  },
  {
    id: 204,
    tipo: "AVATAR",
    nombre: "studio_mic.png",
    ruta: "assets/avatars/base/studio_mic.png",
    formato: "PNG",
    tamaño: 1403012,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Retrato en posición de podcasting y locución técnica"
  },
  {
    id: 205,
    tipo: "AVATAR",
    nombre: "desk_mic.png",
    ruta: "assets/avatars/base/desk_mic.png",
    formato: "PNG",
    tamaño: 1462058,
    proveedor: "Guillermo_Hoyos",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Retrato sentado frente a escritorio de control ejecutivo"
  }
];

// 50 Slots temáticos
const RECURSOS_AVATARES_SLOTS = [];
const CATEGORIAS_MAP = (i) => {
  if (i <= 10) return { cat: "Ejecutivo", desc: "Business formal, escritorio cristal, boardroom" };
  if (i <= 20) return { cat: "Tech", desc: "Casual tech, hoodie HB.OS, bomber, laboratorio software" };
  if (i <= 40) return { cat: "Podcast", desc: "Taller de precisión, whiteboard, explicación activa" };
  return { cat: "Futurista", desc: "Sovereign AI cósmico, matriz R768, traje insignia gala" };
};

for (let i = 1; i <= 50; i++) {
  const num = String(i).padStart(2, "0");
  const meta = CATEGORIAS_MAP(i);
  RECURSOS_AVATARES_SLOTS.push({
    id: 210 + i,
    tipo: "AVATAR",
    nombre: `guillermo_avatar_slot_${num}.jpg`,
    ruta: `assets/avatars/slots/guillermo_avatar_slot_${num}.jpg`,
    formato: "JPG",
    tamaño: 285000,
    proveedor: "Flow_Engine_Nanobanana",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: `Slot #${num} [Categoría: ${meta.cat}]: ${meta.desc}`
  });
}

// 4 Videos de Avatares
const RECURSOS_AVATARES_VIDEOS = [
  {
    id: 281,
    tipo: "AVATAR",
    nombre: "hbos_avatar_animated_test.mp4",
    ruta: "assets/avatars/videos/hbos_avatar_animated_test.mp4",
    formato: "MP4",
    tamaño: 993743,
    proveedor: "HBOS_Video_Pipeline",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Prueba técnica de lipsync y animación de avatar en HBOS"
  },
  {
    id: 282,
    tipo: "AVATAR",
    nombre: "Dialogue_Two_Guillermo_Avatars_Flow_1080p.mp4",
    ruta: "assets/avatars/videos/Dialogue_Two_Guillermo_Avatars_Flow_1080p.mp4",
    formato: "MP4",
    tamaño: 1821390,
    proveedor: "Flow_Engine",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Dúo sincronizado de dos avatares de Guillermo en 1080p"
  },
  {
    id: 283,
    tipo: "AVATAR",
    nombre: "Masterclass_Flow_Avatares_Guillermo_1080p.mp4",
    ruta: "assets/avatars/videos/Masterclass_Flow_Avatares_Guillermo_1080p.mp4",
    formato: "MP4",
    tamaño: 4215900,
    proveedor: "Flow_Engine",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Masterclass completa de demostración con avatares activos"
  },
  {
    id: 284,
    tipo: "AVATAR",
    nombre: "avatar_base.mp4",
    ruta: "assets/avatars/videos/avatar_base.mp4",
    formato: "MP4",
    tamaño: 884120,
    proveedor: "HBOS_Video_Pipeline",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Loop base neutro de avatar para interpolación y síntesis"
  }
];

// ── 3. RECURSOS DE MODELOS DE IA (15 Modelos) ────────────────────────
const RECURSOS_MODELOS = [
  // Alibaba Model Studio (5)
  {
    id: 301,
    tipo: "MODELO",
    nombre: "wan2.7-t2v-2026-06-12",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_VIDEO_T2V",
    tamaño: 0,
    proveedor: "Alibaba_Model_Studio",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Generación Text-to-Video fotorrealista (90 días free quota)",
    especialistas: ["animador"]
  },
  {
    id: 302,
    tipo: "MODELO",
    nombre: "wan2.7-i2v-2026-04-25",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_VIDEO_I2V",
    tamaño: 0,
    proveedor: "Alibaba_Model_Studio",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Animación de fotos estáticas Image-to-Video de avatares (90 días free quota)",
    especialistas: ["animador"]
  },
  {
    id: 303,
    tipo: "MODELO",
    nombre: "wan2.7-r2v-2026-06-12",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_VIDEO_R2V",
    tamaño: 0,
    proveedor: "Alibaba_Model_Studio",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Reference-to-Video para consistencia biológica del rostro (90 días free quota)",
    especialistas: ["animador"]
  },
  {
    id: 304,
    tipo: "MODELO",
    nombre: "qwen3-tts-flash",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_AUDIO_TTS",
    tamaño: 0,
    proveedor: "Alibaba_Model_Studio",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Síntesis de voz expresiva ultra-rápida (110k caracteres free)",
    especialistas: ["narrador"]
  },
  {
    id: 305,
    tipo: "MODELO",
    nombre: "qwen3-max",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_LLM",
    tamaño: 0,
    proveedor: "Alibaba_Model_Studio",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "LLM de razonamiento avanzado y dirección de escena (1M tokens free)",
    especialistas: ["director_historia", "escritor"]
  },
  // Fal.ai (3)
  {
    id: 306,
    tipo: "MODELO",
    nombre: "vidu-video-generator",
    ruta: "https://fal.ai",
    formato: "API_VIDEO",
    tamaño: 0,
    proveedor: "Fal.ai",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Generación de video por difusión Vidu en capa gratuita",
    especialistas: ["animador"]
  },
  {
    id: 307,
    tipo: "MODELO",
    nombre: "bedo-video-fast",
    ruta: "https://fal.ai",
    formato: "API_VIDEO",
    tamaño: 0,
    proveedor: "Fal.ai",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Renderizado rápido de clips B-roll en Fal.ai",
    especialistas: ["animador"]
  },
  {
    id: 308,
    tipo: "MODELO",
    nombre: "runway-pika-fallback",
    ruta: "https://fal.ai",
    formato: "API_VIDEO",
    tamaño: 0,
    proveedor: "Fal.ai",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Modelos de relevo secundario para clips dinámicos",
    especialistas: ["animador"]
  },
  // LLMs (7)
  {
    id: 309,
    tipo: "MODELO",
    nombre: "gemini-2.5-pro",
    ruta: "https://generativelanguage.googleapis.com",
    formato: "API_LLM",
    tamaño: 0,
    proveedor: "Google",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Razonamiento multimodal y embeddings vectoriales (Free tier)",
    especialistas: ["director_historia", "investigador"]
  },
  {
    id: 310,
    tipo: "MODELO",
    nombre: "deepseek-r1",
    ruta: "https://openrouter.ai / local",
    formato: "API_LLM_REASONER",
    tamaño: 0,
    proveedor: "DeepSeek",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Cadena de pensamiento estricta y lógica deductiva",
    especialistas: ["director_historia", "analista_metricas"]
  },
  {
    id: 311,
    tipo: "MODELO",
    nombre: "groq-llama-3.3-70b",
    ruta: "https://api.groq.com",
    formato: "API_LLM_LPU",
    tamaño: 0,
    proveedor: "Groq",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Generación de texto a velocidad de hardware 500+ tokens/s (Free)",
    especialistas: ["escritor", "community_manager"]
  },
  {
    id: 312,
    tipo: "MODELO",
    nombre: "openrouter-unified",
    ruta: "https://openrouter.ai",
    formato: "API_ROUTER",
    tamaño: 0,
    proveedor: "OpenRouter",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Enrutador multi-modelo de respaldo universal",
    especialistas: ["investigador", "escritor"]
  },
  {
    id: 313,
    tipo: "MODELO",
    nombre: "mistral-large-codestral",
    ruta: "https://api.mistral.ai",
    formato: "API_LLM",
    tamaño: 0,
    proveedor: "Mistral",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Validación estricta de código, esquemas y formateo JSON",
    especialistas: ["director_historia"]
  },
  {
    id: 314,
    tipo: "MODELO",
    nombre: "qwen-2.5-coder",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "API_LLM",
    tamaño: 0,
    proveedor: "Alibaba_Cloud",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Especialista en lógica matemática y pipelines de ejecución",
    especialistas: ["analista_metricas"]
  },
  {
    id: 315,
    tipo: "MODELO",
    nombre: "elevenlabs-voice-clone",
    ruta: "https://api.elevenlabs.io",
    formato: "API_VOICE_CLONE",
    tamaño: 0,
    proveedor: "ElevenLabs",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Clonación biométrica con 10,000 caracteres mensuales gratuitos",
    especialistas: ["narrador"]
  }
];

// ── 4. RECURSOS DE SERVICIOS Y HERRAMIENTAS (12 Elementos) ───────────
const RECURSOS_SERVICIOS = [
  // 9 Servicios Activos ($0.00)
  {
    id: 401,
    tipo: "SERVICIO",
    nombre: "Vercel",
    ruta: "https://hbos-vector-engine.vercel.app",
    formato: "CLOUD_SERVERLESS",
    tamaño: 0,
    proveedor: "Vercel",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "CPU Cloud y Gateway de APIs serverless sin costo de infraestructura"
  },
  {
    id: 402,
    tipo: "SERVICIO",
    nombre: "Qdrant Cloud",
    ruta: "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io",
    formato: "VECTOR_DB",
    tamaño: 0,
    proveedor: "Qdrant",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Memoria inmutable, 5 colecciones activas, 1GB cluster gratuito perpetuo"
  },
  {
    id: 403,
    tipo: "SERVICIO",
    nombre: "Alibaba Model Studio",
    ruta: "https://dashscope-intl.aliyuncs.com",
    formato: "GPU_CLOUD_PRIMARIO",
    tamaño: 0,
    proveedor: "Alibaba_Cloud",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Proveedor GPU primario, cuota gratuita 90 días en región Singapur"
  },
  {
    id: 404,
    tipo: "SERVICIO",
    nombre: "Fal.ai",
    ruta: "https://fal.ai",
    formato: "GPU_CLOUD_RESPALDO",
    tamaño: 0,
    proveedor: "Fal.ai",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Proveedor GPU de respaldo secundario con créditos gratuitos iniciales"
  },
  {
    id: 405,
    tipo: "SERVICIO",
    nombre: "Google Colab",
    ruta: "https://colab.research.google.com",
    formato: "GPU_CLOUD_TERCIARIO",
    tamaño: 0,
    proveedor: "Google",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Proveedor GPU terciario para renderizado y pruebas pesadas (T4 Free)"
  },
  {
    id: 406,
    tipo: "SERVICIO",
    nombre: "ElevenLabs",
    ruta: "https://elevenlabs.io",
    formato: "VOZ_SINTETICA",
    tamaño: 0,
    proveedor: "ElevenLabs",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Motor de voz con cuota mensual gratuita de caracteres"
  },
  {
    id: 407,
    tipo: "SERVICIO",
    nombre: "Make.com",
    ruta: "https://make.com",
    formato: "AUTOMATIZACION_WEBHOOKS",
    tamaño: 0,
    proveedor: "Make",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "1,000 operaciones mensuales gratuitas para publicación y redes"
  },
  {
    id: 408,
    tipo: "SERVICIO",
    nombre: "Buffer",
    ruta: "https://buffer.com",
    formato: "SOCIAL_SYNC",
    tamaño: 0,
    proveedor: "Buffer",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "3 canales sociales conectados en tier gratuito (YouTube, TikTok, IG)"
  },
  {
    id: 409,
    tipo: "HERRAMIENTA",
    nombre: "CapCut Web IA",
    ruta: "https://www.capcut.com",
    formato: "EDITOR_VIDEO_RENDER",
    tamaño: 0,
    proveedor: "ByteDance",
    costo: "$0.00",
    disponible: true,
    ultima_verificacion: timestamp,
    notas: "Editor de video en la nube 100% gratuito con subtitulación automática"
  },
  // 3 Servicios Descartados (De Pago)
  {
    id: 410,
    tipo: "SERVICIO",
    nombre: "HeyGen",
    ruta: "https://heygen.com",
    formato: "AVATAR_SAAS_PAID",
    tamaño: 0,
    proveedor: "HeyGen",
    costo: "DE_PAGO ($29-$89/mes)",
    disponible: false,
    ultima_verificacion: timestamp,
    notas: "DESCARTADO: Violación de la regla de oro de 0 costo. Requiere tarjeta y pago recurrente.",
    razon_descarte: "Plan comercial de suscripción obligatoria en USD."
  },
  {
    id: 411,
    tipo: "SERVICIO",
    nombre: "D-ID",
    ruta: "https://d-id.com",
    formato: "AVATAR_SAAS_PAID",
    tamaño: 0,
    proveedor: "D-ID",
    costo: "DE_PAGO (créditos/min)",
    disponible: false,
    ultima_verificacion: timestamp,
    notas: "DESCARTADO: Modelo de cobro por crédito y duración. Sustituido por Wan 2.7 I2V a costo cero.",
    razon_descarte: "Tarificación por minuto de renderizado."
  },
  {
    id: 412,
    tipo: "SERVICIO",
    nombre: "Oracle Cloud Infrastructure",
    ruta: "https://cloud.oracle.com",
    formato: "CLOUD_VM_PAID",
    tamaño: 0,
    proveedor: "Oracle",
    costo: "REQUIERE_TARJETA",
    disponible: false,
    ultima_verificacion: timestamp,
    notas: "DESCARTADO: Requiere tarjeta de crédito bancaria para verificación de cuenta.",
    razon_descarte: "Fricción de tarjeta de crédito obligatoria."
  }
];

// ── EJECUCIÓN PRINCIPAL ──────────────────────────────────────────────
async function main() {
  console.log("=== INICIANDO SEEDING DE RECURSOS HBOS EN QDRANT CLOUD ===");
  
  const todosLosRecursos = [
    ...RECURSOS_VOZ,
    ...RECURSOS_AVATARES_BASE,
    ...RECURSOS_AVATARES_SLOTS,
    ...RECURSOS_AVATARES_VIDEOS,
    ...RECURSOS_MODELOS,
    ...RECURSOS_SERVICIOS
  ];

  console.log(`Total recursos a indexar: ${todosLosRecursos.length}`);
  console.log(`- Voz: ${RECURSOS_VOZ.length}`);
  console.log(`- Avatares: ${RECURSOS_AVATARES_BASE.length + RECURSOS_AVATARES_SLOTS.length + RECURSOS_AVATARES_VIDEOS.length}`);
  console.log(`- Modelos: ${RECURSOS_MODELOS.length}`);
  console.log(`- Servicios y Herramientas: ${RECURSOS_SERVICIOS.length}`);

  const points = todosLosRecursos.map(r => ({
    id: r.id,
    vector: generarVector384(r.nombre + " " + r.tipo + " " + (r.notas || "")),
    payload: r
  }));

  // Enviar en lotes de 25
  const batchSize = 25;
  for (let i = 0; i < points.length; i += batchSize) {
    const chunk = points.slice(i, i + batchSize);
    const resp = await fetch(`${QDRANT_URL}/collections/${COLLECTION}/points?wait=true`, {
      method: "PUT",
      headers: {
        "api-key": QDRANT_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ points: chunk })
    });
    const resData = await resp.json();
    console.log(`Lote ${Math.floor(i / batchSize) + 1}/${Math.ceil(points.length / batchSize)}: Status = ${resData.status || "ok"}`);
  }

  // Verificar cantidad total
  const countResp = await fetch(`${QDRANT_URL}/collections/${COLLECTION}/points/count`, {
    method: "POST",
    headers: { "api-key": QDRANT_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ exact: true })
  });
  const countData = await countResp.json();
  console.log("=== SEEDING COMPLETADO CON ÉXITO ===");
  console.log(`Total puntos en '${COLLECTION}': ${countData.result?.count}`);
}

main().catch(err => {
  console.error("Error en seeding:", err);
  process.exit(1);
});
