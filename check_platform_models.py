# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
cur = conn.cursor()

platforms = [
    "github", "groq", "mistral", "cerebras", "cohere", 
    "cloudflare", "nvidia", "sambanova", "elevenlabs", "fal", "replicate"
]

print("=== CONTEO DE MODELOS POR PLATAFORMA EN freeapi.db ===")
for p in platforms:
    m_count = cur.execute("SELECT COUNT(*) FROM models WHERE platform = ?", (p,)).fetchone()[0]
    med_count = cur.execute("SELECT COUNT(*) FROM media_models WHERE platform = ?", (p,)).fetchone()[0]
    emb_count = cur.execute("SELECT COUNT(*) FROM embedding_models WHERE platform = ?", (p,)).fetchone()[0]
    print(f"  {p:15}: chat/comp={m_count:3} | media={med_count:2} | embed={emb_count:2}")

conn.close()
