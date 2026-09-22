# -*- coding: utf-8 -*-
import sqlite3

dbPath = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
conn = sqlite3.connect(dbPath)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('TABLAS:', tables)
print()
for t in ['client_profiles', 'url_tokens', 'api_keys', 'settings', 'users', 'sessions']:
    if t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur.fetchone()[0]
        print(f'=== {t} ({count} filas) ===')
        if count > 0 and count < 50:
            cur.execute(f'SELECT * FROM "{t}" LIMIT 10')
            for row in cur.fetchall():
                row_safe = []
                for v in row:
                    if isinstance(v, str) and len(v) > 40:
                        row_safe.append(v[:20] + '...***')
                    else:
                        row_safe.append(v)
                print(f'  {row_safe}')
        print()
