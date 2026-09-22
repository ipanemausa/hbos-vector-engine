# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
cur = conn.cursor()
rows = cur.execute("SELECT platform, model_id, display_name FROM media_models").fetchall()
print(f"=== TOTAL MEDIA MODELS: {len(rows)} ===")
for r in rows:
    print(f"  {r[0]:15} | {r[1]:35} | {r[2]}")
conn.close()
