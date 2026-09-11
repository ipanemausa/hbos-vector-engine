import express from "express";
import cors from "cors";
import { createHash } from "crypto";
import vectorEngine from "./vector_engine.js";
import openclawOrchestrator from "./openclaw-orchestrator.js";

const app = express();
app.use(cors());
app.use(express.json());

const VECTOR_SIZE = 384;
const GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key=" + (process.env.GEMINI_API_KEY || "");
const QDRANT_URL = process.env.QDRANT_URL;
const QDRANT_KEY = process.env.QDRANT_API_KEY;
const COLLECTION = "casos_uso_hbos";

const modelos = [
  { nombre: "deepseek_v4",      proveedor: "deepseek",           estado: "activo", prioridad: 1 },
  { nombre: "qwen_3.8",         proveedor: "alibaba",            estado: "activo", prioridad: 2 },
  { nombre: "gemini_flash",     proveedor: "google_antigravity", estado: "activo", prioridad: 3 },
  { nombre: "perplexity",       proveedor: "perplexity",         estado: "activo", prioridad: 4 },
  { nombre: "openrouter_llama", proveedor: "openrouter",         estado: "activo", prioridad: 5 },
  { nombre: "groq_llama",       proveedor: "groq",               estado: "activo", prioridad: 6 }
];

async function embedGemini(texto) {
  if (!process.env.GEMINI_API_KEY) throw new Error("GEMINI_API_KEY no configurada en Vercel Secrets");
  const headers = { "Content-Type": "application/json" };
  const body = {
    model: "models/gemini-embedding-2",
    content: { parts: [{ text: texto }] },
    outputDimensionality: VECTOR_SIZE
  };

  const res = await fetch(GEMINI_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(6000)
  });

  if (!res.ok) throw new Error("Gemini API " + res.status + ": " + (await res.text()));

  const data = await res.json();
  const vector = data.embedding?.values;
  if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
    throw new Error("Gemini vector inesperado: dims=" + (vector ? vector.length : 0));
  }
  return vector;
}

function embedFallback(texto) {
  const seed = createHash("sha256").update(texto).digest();
  const vector = [];
  for (let i = 0; i < VECTOR_SIZE; i++) {
    const byte = seed[i % seed.length];
    vector.push((byte / 255) * 2 - 1);
  }
  return vector;
}

async function qdrantSearch(vector, topK) {
  const url = QDRANT_URL + "/collections/" + COLLECTION + "/points/search";
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "api-key": QDRANT_KEY },
    body: JSON.stringify({ vector, limit: topK, with_payload: true }),
    signal: AbortSignal.timeout(6000)
  });
  if (!res.ok) throw new Error("Qdrant " + res.status + ": " + (await res.text()));
  const data = await res.json();
  return data.result ?? [];
}

// ── ENDPOINTS PRINCIPALES ─────────────────────────────────────────────
app.get("/", (req, res) => {
  res.json({
    status: "OmniRouter HBOS activo",
    arquitectura: "Blueprint 5 Capas (HBOS v4.0)",
    orquestador: "OpenClaw Layer 2 Orchestrator",
    casos_totales: 45,
    protocolo: "R768 / R384",
    embedder: "gemini-embedding-2 via Gemini API",
    vector_db: "Qdrant Cloud",
    endpoints: [
      "/v1/health",
      "/v1/buscar",
      "/v1/openclaw/status",
      "/v1/openclaw/cpm",
      "/v1/openclaw/orchestrate",
      "/v1/ecosistema/trazabilidad",
      "/v1/ecosistema/registrar",
      "/v1/qdrant/collections",
      "/v1/combos/best_free_plus"
    ],
    costo: 0
  });
});

// Búsqueda Semántica Vectorial
app.post("/v1/buscar", async (req, res) => {
  const { query, top_k = 5 } = req.body ?? {};

  if (!query || typeof query !== "string" || query.trim() === "") {
    return res.status(400).json({
      error: "query_requerida",
      mensaje: "El campo 'query' es obligatorio y debe ser texto no vacio."
    });
  }

  if (!QDRANT_URL || !QDRANT_KEY) {
    return res.status(503).json({
      error: "credenciales_faltantes",
      mensaje: "QDRANT_URL o QDRANT_API_KEY no estan en Vercel Secrets."
    });
  }

  let vector;
  let fuente_embedding;

  try {
    vector = await embedGemini(query.trim());
    fuente_embedding = "gemini";
  } catch (err) {
    vector = embedFallback(query.trim());
    fuente_embedding = "fallback_sha256";
    console.warn("[HBOS] Gemini API fallo, usando fallback:", err.message);
  }

  try {
    const resultados = await qdrantSearch(vector, Math.min(Number(top_k) || 5, 20));
    return res.json({
      query,
      fuente_embedding,
      vector_dims: vector.length,
      top_k: resultados.length,
      resultados: resultados.map(r => ({
        id: r.id,
        score: r.score,
        payload: r.payload
      }))
    });
  } catch (qdErr) {
    const msg = qdErr.message || "";
    const code = msg.includes("403") ? 403 : msg.includes("ENOTFOUND") ? 502 : 500;
    return res.status(code).json({
      error: "qdrant_error",
      codigo: code,
      detalle: msg
    });
  }
});

// ── ENDPOINTS DE ESPECIALISTAS Y PATRONES v14.0 (GPU CLOUD + 9 ESPECIALISTAS)
app.get("/v1/openclaw/especialistas", (req, res) => {
  res.json({
    total: 9,
    principio: "Un solo agente no es especialista en todo. La maestria esta en la orquestacion.",
    especialistas: [
      { id: 1, rol: "Investigador de Nicho y Tendencias", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["VidIQ GPT", "Google Trends", "Antigravity"], output: "{ temas: [], viralidad_score: 0-10 }" },
      { id: 2, rol: "Director de Historia y Cumplimiento de YouTube", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["NotebookLM", "Antigravity Gemini", "LTX Studio"], output: "{ estructura_narrativa, compliance_youtube, seo_multimodal }" },
      { id: 3, rol: "Escritor de Guiones y Estructuras", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["Harpa AI", "Antigravity Gemini", "LTX Studio"], output: "{ titulo, escenas: [], duracion_estimada }" },
      { id: 4, rol: "Narrador y Clonador de Voz", destino: "GPU_CLOUD", proveedor: "Fal.ai", herramientas: ["ElevenLabs", "NotebookLM", "Google TTS"], output: "{ audio_url, duracion_segundos, emocion_detectada }" },
      { id: 5, rol: "Animador y Generador de Clips", destino: "GPU_CLOUD", proveedor: "Fal.ai", herramientas: ["Vidu IA", "Bedo", "Runway", "Pika"], output: "{ clips: [{ escena, url, duracion }] }" },
      { id: 6, rol: "Editor y Post-Producción", destino: "GPU_CLOUD", proveedor: "CapCut_IA", herramientas: ["CapCut AI Studio", "DaVinci API"], output: "{ video_url, duracion_total, formatos_disponibles }" },
      { id: 7, rol: "Publicador y Distribuidor", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["Make.com", "Buffer", "Hootsuite"], output: "{ publicado: true, plataformas: [], metricas: {} }" },
      { id: 8, rol: "Community Manager y Engagement", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["Make.com", "Buffer", "Antigravity Gemini"], output: "{ comentarios_respondidos, engagement_generado, oportunidades_contenido }" },
      { id: 9, rol: "Analista de Métricas y Mejora Continua", destino: "CPU_CLOUD", proveedor: "Vercel", herramientas: ["YouTube Analytics API", "Qdrant Cloud", "Antigravity Gemini"], output: "{ video_id, metricas, analisis, recomendaciones }" }
    ]
  });
});

app.get("/v1/openclaw/patrones", (req, res) => {
  res.json({
    patrones: [
      { id: "PIPELINE", tipo: "Secuencial", regla: "Cada especialista espera el output del anterior" },
      { id: "FAN_OUT_FAN_IN", tipo: "Paralelo + Agregación", regla: "Lanza subtareas independientes y agrega resultados" },
      { id: "ROUTING", tipo: "Enrutamiento por Tipo", regla: "Clasifica según categoría de macro-tarea" },
      { id: "ORCHESTRATOR_WORKER", tipo: "Decisión Dinámica", regla: "Analiza y asigna orden y agentes dinámicamente" }
    ]
  });
});

app.post("/v1/openclaw/orquestar", async (req, res) => {
  try {
    const resultado = await openclawOrchestrator.orquestarEspecialistas(req.body);
    res.json(resultado);
  } catch (e) {
    res.status(500).json({ error: "orchestration_v14_failed", detalle: e.message });
  }
});

// ── ENDPOINTS ARBITRAJE 0 COSTO & HITL v14.0 ──────────────────────────
app.get("/v1/openclaw/arbitraje", (req, res) => {
  res.json({
    principio: "No estamos inventando. Estamos adquiriendo tecnicas probadas y gratuitas.",
    costo_total: "$0.00",
    arbitraje_herramientas: [
      { especialista: "Investigador", herramientas: "VidIQ GPT + Google Trends", plan: "Free", fail_strategy: "MAXIMO_ESFUERZO", destino: "CPU_CLOUD" },
      { especialista: "Director de Historia", herramientas: "NotebookLM + Antigravity Gemini + LTX Studio", plan: "Free / 100% YouTube Compliant", fail_strategy: "FALLO_RAPIDO", destino: "CPU_CLOUD" },
      { especialista: "Escritor", herramientas: "Harpa AI + Antigravity Gemini", plan: "Free Tier", fail_strategy: "FALLO_RAPIDO", destino: "CPU_CLOUD" },
      { especialista: "Narrador", herramientas: "ElevenLabs + NotebookLM", plan: "Free Tier (Caracteres/Mes)", fail_strategy: "FALLO_RAPIDO", destino: "GPU_CLOUD" },
      { especialista: "Animador", herramientas: "Vidu IA + Bedo + Runway/Pika", plan: "Free Tiers", fail_strategy: "MAXIMO_ESFUERZO", destino: "GPU_CLOUD" },
      { especialista: "Editor", herramientas: "CapCut Web Creador IA", plan: "100% Free", fail_strategy: "FALLO_RAPIDO", destino: "GPU_CLOUD" },
      { especialista: "Publicador", herramientas: "Make.com (1000 ops) + Buffer", plan: "Free Tier", hitl: "OBLIGATORIO", destino: "CPU_CLOUD" },
      { especialista: "Community Manager", herramientas: "Make.com (Free) + Buffer (Free) + Gemini", plan: "Free Tier", fail_strategy: "MAXIMO_ESFUERZO", destino: "CPU_CLOUD" },
      { especialista: "Analista de Métricas", herramientas: "YouTube Analytics API + Qdrant Cloud + Gemini", plan: "Free Tier", fail_strategy: "MAXIMO_ESFUERZO", destino: "CPU_CLOUD" }
    ]
  });
});

app.get("/v1/openclaw/alibaba-status", (req, res) => {
  res.json({
    proveedor: "Alibaba Model Studio",
    region: "Singapur",
    free_quota: {
      video: "10-50 segundos por modelo",
      tts: "110,000 caracteres",
      llm: "1,000,000 tokens",
      validez: "90 días desde activación"
    },
    modelos: {
      video_t2v: "wan2.7-t2v-2026-06-12",
      video_i2v: "wan2.7-i2v-2026-04-25",
      video_r2v: "wan2.7-r2v-2026-06-12",
      tts: "qwen3-tts-flash",
      llm: "qwen3-max"
    },
    status: "READY",
    regla: "0 costo con free quota 90 días",
    timestamp: new Date().toISOString()
  });
});

app.get("/v1/openclaw/gpu-status", (req, res) => {
  res.json({
    principio: "Todo cálculo pesado (GPU, vectorización, renderizado) vive en GPU Cloud.",
    proveedor_primario: "Alibaba Model Studio (Singapur)",
    proveedores: {
      alibaba_model_studio: { status: "READY", rol: "PRIMARIO", free_quota: "90 días", especialistas: ["narrador", "animador", "editor"] },
      fal_ai: { status: "READY", rol: "SECUNDARIO_RESPALDO", especialistas: ["narrador", "animador"] },
      google_colab: { status: "READY", rol: "TERCIARIO_RESPALDO", free_tier: "T4", especialistas: ["pruebas", "render"] }
    },
    especialistas_gpu: 3,
    especialistas_cpu: 6,
    total_especialistas: 9,
    regla: "Antigravity es consola. GPU Cloud es motor.",
    timestamp: new Date().toISOString()
  });
});

app.get("/v1/openclaw/gpu-arbitrage", (req, res) => {
  res.json({
    principio: "0 costo siempre. Si un proveedor agota, se cambia a otro.",
    proveedor_primario: "Alibaba Model Studio (Free Quota 90 días)",
    proveedores: {
      alibaba_model_studio: { status: "READY", rol: "PRIMARIO", free_quota: "90 dias", especialistas: ["narrador", "animador", "editor"] },
      fal_ai: { status: "READY", rol: "SECUNDARIO_RESPALDO", free_tier: true, especialistas: ["narrador", "animador"] },
      google_colab: { status: "READY", rol: "TERCIARIO_RESPALDO", free_tier: "T4", especialistas: ["pruebas"] }
    },
    regla_arbitraje: [
      "Alibaba Model Studio → Fal.ai → Google Colab",
      "Si todos agotados → DETENER y reportar"
    ],
    costo_total: "$0.00",
    timestamp: new Date().toISOString()
  });
});

app.post("/v1/openclaw/hitl/aprobar", (req, res) => {
  const { task_id, aprobador } = req.body ?? {};
  if (!task_id) {
    return res.status(400).json({ error: "task_id_requerido" });
  }
  const resultado = openclawOrchestrator.aprobarHITL(task_id, aprobador);
  res.json(resultado);
});

app.get("/v1/openclaw/status", (req, res) => {
  res.json(openclawOrchestrator.getStatus());
});

app.get("/v1/openclaw/metricas", async (req, res) => {
  const videoId = req.query.video_id || "hbos_master_render_2026";
  const resultado = await openclawOrchestrator.getMetricas(videoId);
  res.json(resultado);
});

app.get("/v1/openclaw/community", async (req, res) => {
  const resultado = await openclawOrchestrator.getCommunity();
  res.json(resultado);
});

app.get("/v1/openclaw/cpm", (req, res) => {
  res.json(openclawOrchestrator.evaluateCPM());
});

app.post("/v1/openclaw/orchestrate", async (req, res) => {
  try {
    const resultado = await openclawOrchestrator.orchestrate(req.body);
    res.json(resultado);
  } catch (e) {
    res.status(500).json({ error: "orchestration_failed", detalle: e.message });
  }
});

// ── ENDPOINTS TRAZABILIDAD QDRANT CLOUD (CAPA 4) ───────────────────────
app.get("/v1/ecosistema/trazabilidad", async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 100);
  const data = await vectorEngine.getTrazabilidad(limit);
  res.json(data);
});

app.post("/v1/ecosistema/registrar", async (req, res) => {
  const { evento, payload, operation_id } = req.body ?? {};
  if (!evento) {
    return res.status(400).json({ error: "evento_requerido" });
  }
  const resultado = await vectorEngine.registrarTrazabilidad(evento, payload || {}, operation_id);
  res.json(resultado);
});

// ── ENDPOINT INFO COLECCION ──────────────────────────────────────────
app.get("/v1/qdrant/info/:name", async (req, res) => {
  try {
    const client = vectorEngine.getClient();
    const info = await client.getCollection(req.params.name);
    res.json(info);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ── ENDPOINT COLECCIONES QDRANT ───────────────────────────────────────
app.get("/v1/qdrant/collections", async (req, res) => {
  try {
    const conexion = await vectorEngine.checkConnection();
    if (!conexion.ok) {
      return res.status(502).json({
        evento: "conexion_qdrant",
        estado: "FALLIDO",
        error_code: conexion.error,
        detalle: conexion.detail,
        timestamp: new Date().toISOString()
      });
    }
    const coleccion = await vectorEngine.checkCollection();
    res.json({
      evento: "conexion_qdrant",
      estado: "OK",
      collections: conexion.collections,
      total: conexion.count,
      coleccion_principal: coleccion,
      protocolo: "R768/R384",
      timestamp: new Date().toISOString()
    });
  } catch (e) {
    res.status(500).json({ evento: "conexion_qdrant", estado: "ERROR", detalle: e.message, timestamp: new Date().toISOString() });
  }
});

// ── ENDPOINTS COMPLEMENTARIOS DE CASOS DE USO ─────────────────────────
app.get("/v1/combos/best_free_plus", (req, res) => {
  res.json({ nombre: "best_free_plus", jerarquia: modelos, estado: "activo", costo: 0 });
});

app.post("/v1/arbitrator/failover", (req, res) => {
  const { modelo } = req.body;
  const idx = modelos.findIndex(m => m.nombre === modelo);
  if (idx !== -1) modelos[idx].estado = "fallido";
  const siguiente = modelos.find(m => m.estado === "activo");
  res.json({ failover: modelo, siguiente, costo: 0 });
});

app.post("/v1/casos/28-modo-estudio", (req, res) => {
  const { tema } = req.body;
  res.json({ caso: 28, nombre: "modo-estudio", modelo: "deepseek_v4", tema, costo: 0 });
});

app.post("/v1/casos/20-auditar-web", (req, res) => {
  const { url } = req.body;
  res.json({ caso: 20, nombre: "auditar-web", plugin: "antigravity", url, costo: 0 });
});

app.post("/v1/casos/43-animar-historias", (req, res) => {
  const { guion } = req.body;
  res.json({ caso: 43, nombre: "animar-historias", plugin: "google_flow", guion, costo: 0 });
});

app.post("/webhook/telegram", async (req, res) => {
  try {
    const texto = req.body?.message?.text || "";
    if (texto === "/start") {
      res.json({ method: "sendMessage", chat_id: req.body?.message?.chat?.id, text: "HBOS esta en linea" });
    } else {
      res.json({ status: "recibido" });
    }
  } catch (e) {
    res.status(500).json({ status: "error", detalle: e.message });
  }
});

// ── ENDPOINT HEALTH CHECK & CRON WORKER 24/7 ──────────────────────────
app.get(["/v1/health", "/api/health", "/health"], (req, res) => {
  res.json({
    status: "HEALTHY",
    service: "HBOS OmniRouter Worker 24/7",
    timestamp: new Date().toISOString(),
    cron: "VERCEL_CRON_ACTIVE",
    schedule: "0 0 * * *",
    protocolo: "R768/R384",
    uptime: process.uptime(),
    vector_db: "Qdrant Cloud",
    orchestrator: openclawOrchestrator.getStatus().estado
  });
});

export default app;
