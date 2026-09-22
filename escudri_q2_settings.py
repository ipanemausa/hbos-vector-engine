# -*- coding: utf-8 -*-
import sqlite3

dbPath = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
conn = sqlite3.connect(dbPath)
cur = conn.cursor()
cur.execute('SELECT key, value FROM settings')
for key, value in cur.fetchall():
    if isinstance(value, str) and len(value) > 40:
        value = value[:20] + '...***'
    print(f'  {key}: {value}')
