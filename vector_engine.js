import { QdrantClient } from "@qdrant/qdrant-js";
import { pipeline } from "@huggingface/transformers";

class VectorEngine {
  constructor() {
    this.qdrant = new QdrantClient({
      url: process.env.QDRANT_URL,
      apiKey: process.env.QDRANT_API_KEY
    });
    this.embedder = null;
    this.collection = "casos_uso_hbos";
  }

  async init() {
    this.embedder = await pipeline("feature-extraction", "sentence-transformers/all-MiniLM-L6-v2");
    await this.ensureCollection();
  }

  async ensureCollection() {
    try {
      const collections = await this.qdrant.getCollections();
      if (!collections.collections.some(c => c.name === this.collection)) {
        await this.qdrant.createCollection(this.collection, {
          vectors: { size: 384, distance: "Cosine" }
        });
      }
    } catch (e) {
      console.log("Colección lista o error:", e.message);
    }
  }

  async embed(texto) {
    const output = await this.embedder(texto, { pooling: "mean", normalize: true });
    return Array.from(output.data);
  }

  async addCase(id, descripcion, herramientas, modelos, categoria) {
    const vector = await this.embed(descripcion);
    await this.qdrant.upsert(this.collection, {
      points: [{ id, vector, payload: { descripcion, herramientas, modelos, categoria } }]
    });
  }

  async searchSimilar(texto, limit = 5) {
    const vector = await this.embed(texto);
    return await this.qdrant.search(this.collection, { vector, limit, with_payload: true });
  }
}

export default new VectorEngine();
