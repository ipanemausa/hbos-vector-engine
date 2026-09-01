import { QdrantClient } from "@qdrant/qdrant-js";

// ── VALIDACION DE CREDENCIALES (Vercel Secrets) ────────────────────────
const QDRANT_URL = process.env.QDRANT_URL;
const QDRANT_API_KEY = process.env.QDRANT_API_KEY;

if (!QDRANT_URL)     throw new Error("[HBOS] QDRANT_URL no está definida en Vercel Secrets.");
if (!QDRANT_API_KEY) throw new Error("[HBOS] QDRANT_API_KEY no está definida en Vercel Secrets.");

// ── R384: MiniLM-L6-v2 — dimensión real de casos_uso_hbos (45 puntos activos)
const COLLECTION_NAME      = "casos_uso_hbos";
const VECTOR_SIZE          = 384;      // Dimensión real confirmada en Qdrant Cloud
const VECTOR_DISTANCE      = "Cosine";
const SIMILARITY_THRESHOLD = 0.75;    // Umbral Cosine para MiniLM-L6-v2

class VectorEngine {
  constructor() {
    this.qdrant     = new QdrantClient({ url: QDRANT_URL, apiKey: QDRANT_API_KEY });
    this.collection = COLLECTION_NAME;
  }

  /** Verifica la conexión con Qdrant — consulta /collections */
  async checkConnection() {
    try {
      const result = await this.qdrant.getCollections();
      return {
        ok: true,
        collections: result.collections.map(c => c.name),
        count: result.collections.length
      };
    } catch (e) {
      const msg = e.message || String(e);
      if (msg.includes("403"))       return { ok: false, error: "403_FORBIDDEN",  detail: msg };
      if (msg.includes("ENOTFOUND")) return { ok: false, error: "ENOTFOUND_URL",  detail: msg };
      if (msg.includes("timeout"))   return { ok: false, error: "TIMEOUT",        detail: msg };
      return { ok: false, error: "UNKNOWN", detail: msg };
    }
  }

  /** Verifica si la colección principal existe (NO la crea) */
  async checkCollection() {
    try {
      const result = await this.qdrant.getCollections();
      const exists = result.collections.some(c => c.name === this.collection);
      return { exists, collection: this.collection, vector_size: VECTOR_SIZE };
    } catch (e) {
      return { exists: false, error: e.message };
    }
  }

  /** Búsqueda vectorial — requiere vectores de 384 dims (MiniLM-L6-v2) */
  async searchSimilar(vector, limit = 5) {
    if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
      throw new Error(`[R384] El vector debe tener ${VECTOR_SIZE} dimensiones. Recibido: ${vector?.length}`);
    }
    return await this.qdrant.search(this.collection, {
      vector,
      limit,
      with_payload: true,
      score_threshold: SIMILARITY_THRESHOLD
    });
  }

  /** Inserta un caso de uso — acepta vector pre-generado de 384 dims */
  async addCase(id, descripcion, vector, payload = {}) {
    if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
      throw new Error(`[R384] Vector inválido. Se requieren ${VECTOR_SIZE} dimensiones.`);
    }
    await this.qdrant.upsert(this.collection, {
      points: [{ id, vector, payload: { descripcion, ...payload } }]
    });
    return { ok: true, id, collection: this.collection };
  }
}

export default new VectorEngine();
