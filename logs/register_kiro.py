import sqlite3
import json
import uuid
from datetime import datetime

db_path = r'C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Inspect schema
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)

# Try to find the provider/api_keys table
for t in ['api_keys', 'providers', 'custom_providers']:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        cols = [(r[1], r[2]) for r in c.fetchall()]
        print(f'Table {t} columns:', cols)

# Check if kiro-gateway already exists
if 'api_keys' in tables:
    c.execute("SELECT COUNT(*) FROM api_keys WHERE platform='kiro' OR name LIKE '%kiro%'")
    existing = c.fetchone()[0]
    print('Existing kiro entries:', existing)

    if existing == 0:
        # Insert new provider - adapt to actual schema
        try:
            c.execute("PRAGMA table_info(api_keys)")
            cols = [r[1] for r in c.fetchall()]
            print('api_keys columns:', cols)

            # Build insert dynamically
            values = {
                'id': str(uuid.uuid4()),
                'name': 'kiro-gateway',
                'platform': 'kiro',
                'api_key': 'hbos-kiro-local-key-2026',
                'base_url': 'http://127.0.0.1:10088/v1',
                'enabled': 1,
                'created_at': datetime.now().isoformat()
            }
            # Filter to only columns that exist
            insert_cols = [k for k in values.keys() if k in cols]
            insert_vals = [values[k] for k in insert_cols]
            placeholders = ','.join(['?'] * len(insert_cols))
            query = f"INSERT INTO api_keys ({','.join(insert_cols)}) VALUES ({placeholders})"
            c.execute(query, insert_vals)
            conn.commit()
            print('INSERTED kiro-gateway')
        except Exception as e:
            print('Insert failed:', e)
    else:
        print('Kiro already present, skipping insert')

conn.close()
