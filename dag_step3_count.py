# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = os.path.expandvars(r"%APPDATA%\FreeLLMAPI\freeapi.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
total = cur.execute("SELECT COUNT(*) FROM api_keys WHERE enabled=1").fetchone()[0]
platforms = [r[0] for r in cur.execute("SELECT DISTINCT platform FROM api_keys WHERE enabled=1").fetchall()]
print(f"Total enabled: {total}")
print(f"Platforms: {platforms}")
conn.close()
