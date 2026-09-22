# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- TABLES ---")
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(" ", r[0])

print("\n--- api_keys COLUMNS ---")
for c in cur.execute("PRAGMA table_info(api_keys)"):
    print(" ", c)

print("\n--- PLATFORMS IN MODELS ---")
platforms = [r[0] for r in cur.execute("SELECT DISTINCT platform FROM models")]
print(" ", platforms)

print("\n--- ANY ROWS IN api_keys ---")
rows = cur.execute("SELECT * FROM api_keys").fetchall()
print(f"  Count: {len(rows)}")
for row in rows:
    print(" ", row)

print("\n--- PLATFORMS TABLE (if exists) ---")
try:
    for c in cur.execute("SELECT * FROM platforms LIMIT 5"):
        print(" ", c)
except Exception as e:
    print("  No platforms table:", e)

conn.close()
