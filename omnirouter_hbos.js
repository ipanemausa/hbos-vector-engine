import express from "express";
import cors from "cors";
import vectorEngine from "./vector_engine.js";

const app = express();
app.use(cors());
app.use(express.json());

const modelos = [
  { nombre: "deepseek_v4",    proveedor: "deepseek",           estado: "activo", prioridad: 1 },
  { nombre: "qwen_3.8",       proveedor: "alibaba",            estado: "activo", prioridad: 2 },
  { nombre: "gemini_flash",   proveedor: "google_antigravity", estado: "activo", prioridad: 3 },
  { nombre: "perplexity",     proveedor: "perplexity",         estado: "activo", prioridad: 4 },
  { nombre: "openrouter_llama", proveedor: "openrouter",       estado: "activo", prioridad: 5 },
  { nombre: "groq_llama",     proveedor: "groq",               estado: "activo", prioridad: 6 }
];

// ─── HEALTH CHECK ──────────────────────────────────────────────────────────
app.get("/", (req, res) => {
  res.json({
    status: "OmniRouter HBOS activo",
    casos_totales: 45,
    protocolo: "R768",
    vector_db: "Qdrant Cloud",
    costo: 0
  });
});

// ─── QDRANT: VERIFICACION DE CONEXION ──────────────────────────────────────
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
      protocolo: "R768",
      timestamp: new Date().toISOString()
    });
  } catch (e) {
    res.status(500).json({
      evento: "conexion_qdrant",
      estado: "ERROR",
      detalle: e.message,
      timestamp: new Date().toISOString()
    });
  }
});

// ─── MODELOS ───────────────────────────────────────────────────────────────
app.get("/v1/combos/best_free_plus", (req, res) => {
  res.json({ nombre: "best_free_plus", jerarquia: modelos, estado: "activo", costo: 0 });
});

// ─── ARBITRATOR ────────────────────────────────────────────────────────────
app.post("/v1/arbitrator/failover", (req, res) => {
  const { modelo } = req.body;
  const idx = modelos.findIndex(m => m.nombre === modelo);
  if (idx !== -1) modelos[idx].estado = "fallido";
  const siguiente = modelos.find(m => m.estado === "activo");
  res.json({ failover: modelo, siguiente, costo: 0 });
});

// ─── CASOS DE USO ──────────────────────────────────────────────────────────
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

// ─── WEBHOOK TELEGRAM ──────────────────────────────────────────────────────
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
