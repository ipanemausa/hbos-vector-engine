# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = os.path.expandvars(r"%APPDATA%\FreeLLMAPI\freeapi.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
rows = cur.execute("SELECT platform, status, enabled FROM api_keys ORDER BY id").fetchall()
print("TOTAL:", len(rows))
for r in rows:
    print(f"  {r[0]:15} | {r[1]:10} | enabled={r[2]}")
conn.close()
