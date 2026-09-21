"""
hbos_fam_t.py — IMPLEMENTACIÓN DE SOFTWARE DEL NAVEGADOR FORMAL FAM@-T
Ecosistema Soberano HBOS · Modo Experto ALEJAVI · Vigente desde op=252
Formalización: FAM@-T: T x ENTORNO TOTAL -> OUTPUT_HÍBRIDO
"""

import os, math, hashlib
from typing import Dict, Any, List
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")

class FAM_T_Navigator:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=15)
        self.collections = [c.name for c in self.client.get_collections().collections]

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        words = text.lower().split()
        if not words: return [1.0 / math.sqrt(self.dim)] * self.dim
        for i, w in enumerate(words):
            h = int(hashlib.sha256(f"{w}_{i % 7}".encode('utf-8')).hexdigest(), 16)
            vec[h % self.dim] += 1.0 + (1.0 / (1.0 + (h % 11)))
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(self.dim)] * self.dim

    def navigate(self, query: str, target_collection: str = "hbos_canon", limit: int = 3) -> Dict[str, Any]:
        """Proyecta la tarea 'T' directamente en el espacio vectorial 384d."""
        if target_collection not in self.collections:
            return {"error": f"Colección '{target_collection}' no existe en Qdrant."}
        q_vec = self._embed(query)
        res = self.client.query_points(collection_name=target_collection, query=q_vec, limit=limit)
        return {
            "query": query,
            "target": target_collection,
            "hits": [
                {"id": p.id, "score": round(p.score if hasattr(p, 'score') else 1.0, 4), "payload": p.payload}
                for p in res.points
            ]
        }

if __name__ == "__main__":
    nav = FAM_T_Navigator()
    res = nav.navigate("R62 420 micro-movimientos")
    print(f"[FAM@-T ENGINE] Resultados para '{res['query']}': {len(res['hits'])} coincidencias.")
    for h in res['hits']:
        print(f"  -> Score: {h['score']} | [{h['payload'].get('regla_id')}] {h['payload'].get('nombre')}: {h['payload'].get('texto')[:90]}...")

    res_famt = nav.navigate("FAM@-T navegación entorno total")
    print(f"\n[FAM@-T ENGINE] Resultados para '{res_famt['query']}': {len(res_famt['hits'])} coincidencias.")
    for h in res_famt['hits']:
        print(f"  -> Score: {h['score']} | [{h['payload'].get('regla_id')}] {h['payload'].get('nombre')}: {h['payload'].get('texto')[:90]}...")
