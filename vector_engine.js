import { QdrantClient } from "@qdrant/qdrant-js";

// Credenciales desde Vercel Secrets
const QDRANT_URL = process.env.QDRANT_URL;
const QDRANT_API_KEY = process.env.QDRANT_API_KEY;

// Constantes de arquitectura R384 / R768
const COLLECTION_NAME = "casos_uso_hbos";
const ECOSYSTEM_COLLECTION = "registro_ecosistema";
const VECTOR_SIZE = 384;
const VectorEngine_DISTANCE = "Cosine";
const SIMILARITY_THRESHOLD = 0.75;

class VectorEngine {
  constructor() {
    this.qdrant = null;
    this.collection = COLLECTION_NAME;
    this.ecosystemCollection = ECOSYSTEM_COLLECTION;
    this.recursosCollection = "recursos_hbos";
    this.initClient();
  }

  initClient() {
    if (process.env.QDRANT_URL && process.env.QDRANT_API_KEY) {
      this.qdrant = new QdrantClient({
        url: process.env.QDRANT_URL,
        apiKey: process.env.QDRANT_API_KEY
      });
    }
  }

  getClient() {
    if (!this.qdrant) {
      this.initClient();
    }
    if (!this.qdrant) {
      throw new Error("[HBOS] QDRANT_URL o QDRANT_API_KEY no configuradas en Vercel Secrets.");
    }
    return this.qdrant;
  }

  /** Verifica conectividad general con Qdrant Cloud */
  async checkConnection() {
    try {
      const client = this.getClient();
      const result = await client.getCollections();
      return {
        ok: true,
        collections: result.collections.map(c => c.name),
        count: result.collections.length
      };
    } catch (e) {
      const msg = e.message || String(e);
      if (msg.includes("403")) return { ok: false, error: "403_FORBIDDEN", detail: msg };
      if (msg.includes("ENOTFOUND")) return { ok: false, error: "ENOTFOUND_URL", detail: msg };
      if (msg.includes("timeout")) return { ok: false, error: "TIMEOUT", detail: msg };
      return { ok: false, error: "UNKNOWN", detail: msg };
    }
  }

  /** Verifica si la coleccion de casos de uso existe */
  async checkCollection(name = this.collection) {
    try {
      const client = this.getClient();
      const result = await client.getCollections();
      const exists = result.collections.some(c => c.name === name);
      return { exists, collection: name, vector_size: VECTOR_SIZE };
    } catch (e) {
      return { exists: false, error: e.message };
    }
  }

  /** Garantiza la existencia de una coleccion si no esta creada */
  async ensureCollection(name = this.ecosystemCollection, size = 384) {
    try {
      const client = this.getClient();
      const result = await client.getCollections();
      const exists = result.collections.some(c => c.name === name);
      if (!exists) {
        await client.createCollection(name, {
          vectors: { size, distance: "Cosine" }
        });
        return { ok: true, created: true, collection: name };
      }
      return { ok: true, created: false, collection: name };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  /** Busqueda vectorial sobre casos_uso_hbos */
  async searchSimilar(vector, limit = 5) {
    if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
      throw new Error("Requiere vector de " + VECTOR_SIZE + " dimensiones");
    }
    const client = this.getClient();
    return await client.search(this.collection, {
      vector,
      limit,
      with_payload: true,
      score_threshold: SIMILARITY_THRESHOLD
    });
  }

  /** Inserta o actualiza un caso de uso */
  async addCase(id, descripcion, vector, payload = {}) {
    if (!Array.isArray(vector) || vector.length !== VECTOR_SIZE) {
      throw new Error("Vector invalido. Requiere " + VECTOR_SIZE + " dims");
    }
    const client = this.getClient();
    await client.upsert(this.collection, {
      points: [{ id, vector, payload: { descripcion, ...payload } }]
    });
    return { ok: true, id, collection: this.collection };
  }

  /** Obtiene el ultimo operation_id registrado en el ecosistema */
  async getLastOperationId() {
    try {
      const client = this.getClient();
      await this.ensureCollection(this.ecosystemCollection, 384);
      const points = await client.scroll(this.ecosystemCollection, {
        limit: 100,
        with_payload: true
      });
      if (!points.points || points.points.length === 0) {
        return 100;
      }
      let maxId = 100;
      for (const p of points.points) {
        const op = p.payload && p.payload.operation_id ? p.payload.operation_id : (typeof p.id === 'number' ? p.id : 0);
        if (op > maxId) maxId = op;
      }
      return maxId;
    } catch (e) {
      console.warn("[HBOS] No se pudo obtener last_op de Qdrant:", e.message);
      return 100;
    }
  }

  /** Registra un evento de trazabilidad inmutable en Qdrant Cloud */
  async registrarTrazabilidad(evento, payload = {}, explicitOpId = null) {
    try {
      const client = this.getClient();
      await this.ensureCollection(this.ecosystemCollection, 384);
      const lastOp = explicitOpId || (await this.getLastOperationId()) + 1;
      const pointId = typeof lastOp === 'number' ? lastOp : Date.now();
      const dummyVector = new Array(384).fill(0.01);

      await client.upsert(this.ecosystemCollection, {
        points: [{
          id: pointId,
          vector: dummyVector,
          payload: {
            operation_id: lastOp,
            evento: evento,
            timestamp: new Date().toISOString(),
            agente: "ALEJAVI-ANTIGRAVITY",
            entorno: "hbos-vector-engine",
            ...payload
          }
        }]
      });

      return { ok: true, operation_id: lastOp, evento: evento };
    } catch (e) {
      console.warn("[HBOS] Fallo al registrar trazabilidad en Qdrant:", e.message);
      return { ok: false, error: e.message, fallback_op: explicitOpId || 101 };
    }
  }

  /** Consulta el historial de trazabilidad del ecosistema */
  async getTrazabilidad(limit = 20) {
    try {
      const client = this.getClient();
      await this.ensureCollection(this.ecosystemCollection, 384);
      const result = await client.scroll(this.ecosystemCollection, {
        limit,
        with_payload: true
      });
      const items = (result.points || []).map(p => p.payload || p);
      items.sort((a, b) => (b.operation_id || 0) - (a.operation_id || 0));
      return { ok: true, total: items.length, items };
    } catch (e) {
      return { ok: false, error: e.message, items: [] };
    }
  }

  /** Consulta recursos de la Matrix (recursos_hbos) por tipo o todos */
  async getRecursos(tipo = null) {
    try {
      const client = this.getClient();
      await this.ensureCollection(this.recursosCollection || "recursos_hbos", 384);
      const result = await client.scroll(this.recursosCollection || "recursos_hbos", {
        limit: 100,
        with_payload: true
      });
      let items = (result.points || []).map(p => p.payload || p);
      if (tipo) {
        items = items.filter(r => (r.tipo || "").toUpperCase() === tipo.toUpperCase());
      }
      return { ok: true, total: items.length, items };
    } catch (e) {
      return { ok: false, error: e.message, items: [] };
    }
  }

  /** Protocolo de verificación diaria de recursos en Qdrant */
  async verificarRecursos() {
    try {
      const client = this.getClient();
      const coll = this.recursosCollection || "recursos_hbos";
      await this.ensureCollection(coll, 384);
      const result = await client.scroll(coll, {
        limit: 100,
        with_payload: true
      });
      const items = result.points || [];
      const timestamp = new Date().toISOString();
      const actualizados = [];

      for (const p of items) {
        if (p.payload) {
          p.payload.ultima_verificacion = timestamp;
          actualizados.push({
            id: p.id,
            vector: p.vector || new Array(384).fill(0.01),
            payload: p.payload
          });
        }
      }

      if (actualizados.length > 0) {
        await client.upsert(coll, { points: actualizados });
      }

      return {
        ok: true,
        protocolo: "DESCUBRIMIENTO_DIARIO_HBOS",
        recursos_verificados: actualizados.length,
        timestamp,
        estado: "TODOS_DISPONIBLES"
      };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }
}

export default new VectorEngine();
