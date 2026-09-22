# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
cur = conn.cursor()
rows = cur.execute("SELECT id, model_id, display_name FROM models WHERE platform = 'groq'").fetchall()
print("=== GROQ MODELS EN CATALOGO FreeLLMAPI ===")
for r in rows:
    print(f"  ID: {r[0]} | model_id: '{r[1]}' | display_name: '{r[2]}'")

rows_media = cur.execute("SELECT id, model_id, display_name FROM media_models WHERE platform = 'groq'").fetchall()
print("=== GROQ MEDIA MODELS ===")
for r in rows_media:
    print(f"  ID: {r[0]} | model_id: '{r[1]}' | display_name: '{r[2]}'")
conn.close()
