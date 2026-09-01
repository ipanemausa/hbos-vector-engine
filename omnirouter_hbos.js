import express from "express";
import cors from "cors";
import { createHash } from "crypto";
import vectorEngine from "./vector_engine.js";

const app = express();
app.use(cors());
app.use(express.json());

const VECTOR_SIZE  = 384;
const GEMINI_URL   = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${process.env.GEMINI_API_KEY}";
const QDRANT_URL   = process.env.QDRANT_URL;
const QDRANT_KEY   = process.env.QDRANT_API_KEY;
const COLLECTION   = "casos_uso_hbos";

const modelos = [
  { nombre: "deepseek_v4",     proveedor: "deepseek",           estado: "activo", prioridad: 1 },
  { nombre: "qwen_3.8",        proveedor: "alibaba",            estado: "activo", prioridad: 2 },
  { nombre: "gemini_flash",    proveedor: "google_antigravity", estado: "activo", prioridad: 3 },
  { nombre: "perplexity",      proveedor: "perplexity",         estado: "activo", prioridad: 4 },
  { nombre: "openrouter_llama",proveedor: "openrouter",         estado: "activo", prioridad: 5 },
  { nombre: "groq_llama",      proveedor: "groq",               estado: "activo", prioridad: 6 }
];

async function embedGemini(texto) {
  if (!process.env.GEMINI_API_KEY) throw new Error("GEMINI_API_KEY no configurada en Vercel Secrets");
  const headers = { "Content-Type": "application/json" };
  
  const body = {
    model: "models/text-embedding-004",
    content: { parts: [{ text: texto }] },
    outputDimensionality: VECTOR_SIZE
  };

  const res = await fetch(GEMINI_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(6000)
  });

  if (!res.ok) throw new Error(`Gemini API ${res.status}`: ``);

  const data = await res.json();
  const vector = data.embedding?.values;
  
  if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
    throw new Error(`Gemini vector inesperado: dims=``);
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
  const url = ```/collections/``/points/search`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "api-key": QDRANT_KEY },
    body: JSON.stringify({ vector, limit: topK, with_payload: true }),
    signal: AbortSignal.timeout(6000)
  });
  if (!res.ok) throw new Error(`Qdrant ``: ``);
  const data = await res.json();
  return data.result ?? [];
}

app.get("/", (req, res) => {
  res.json({
    status: "OmniRouter HBOS activo",
    casos_totales: 45,
    protocolo: "R384",
    embedder: "text-embedding-004 via Gemini API",
    vector_db: "Qdrant Cloud",
    endpoints: ["/v1/buscar", "/v1/qdrant/collections", "/v1/combos/best_free_plus"],
    costo: 0
  });
});

app.post("/v1/buscar", async (req, res) => {
  const { query, top_k = 5 } = req.body ?? {};

  if (!query || typeof query !== "string" || query.trim() === "") {
    return res.status(400).json({
      error: "query_requerida",
      mensaje: "El campo 'query' es obligatorio y debe ser texto no vacío."
    });
  }

  if (!QDRANT_URL || !QDRANT_KEY) {
    return res.status(503).json({
      error: "credenciales_faltantes",
      mensaje: "QDRANT_URL o QDRANT_API_KEY no están en Vercel Secrets."
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
    console.warn("[HBOS] Gemini API falló, usando fallback:", err.message);
  }

  try {
    const resultados = await qdrantSearch(vector, Math.min(Number(top_k) || 5, 20));
    return res.json({
      query,
      fuente_embedding,
      vector_dims: vector.length,
      top_k: resultados.length,
      resultados: resultados.map(r => ({
        id:      r.id,
        score:   r.score,
        payload: r.payload
      }))
    });
  } catch (qdErr) {
    const msg = qdErr.message || "";
    const code = msg.includes("403") ? 403 : msg.includes("ENOTFOUND") ? 502 : 500;
    return res.status(code).json({
      error:   "qdrant_error",
      codigo:  code,
      detalle: msg
    });
  }
});

app.get("/v1/qdrant/collections", async (req, res) => {
  try {
    const conexion = await vectorEngine.checkConnection();
    if (!conexion.ok) {
      return res.status(502).json({
        evento: "conexion_qdrant", estado: "FALLIDO",
        error_code: conexion.error, detalle: conexion.detail,
        timestamp: new Date().toISOString()
      });
    }
    const coleccion = await vectorEngine.checkCollection();
    res.json({
      evento: "conexion_qdrant", estado: "OK",
      collections: conexion.collections, total: conexion.count,
      coleccion_principal: coleccion, protocolo: "R384",
      timestamp: new Date().toISOString()
    });
  } catch (e) {
    res.status(500).json({ evento: "conexion_qdrant", estado: "ERROR", detalle: e.message, timestamp: new Date().toISOString() });
  }
});

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
      res.json({ method: "sendMessage", chat_id: req.body?.message?.chat?.id, text: "HBOS está en línea" });
    } else {
      res.json({ status: "recibido" });
    }
  } catch (e) {
    res.status(500).json({ status: "error", detalle: e.message });
  }
});

export default app;