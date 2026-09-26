import sqlite3, json
c = sqlite3.connect(r'C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db').cursor()
# Buscar tablas relacionadas con chains/perfiles
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)
# Buscar en profiles o fallback_config
for t in ['fallback_config', 'profiles', 'profile_models']:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in c.fetchall()]
        print(f'Table {t} columns: {cols}')
        try:
            c.execute(f"SELECT * FROM {t} LIMIT 20")
            for row in c.fetchall():
                print(f'  {t}: {row}')
        except Exception as e:
            print(f'  err reading {t}: {e}')
