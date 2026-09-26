import sqlite3
c = sqlite3.connect(r'C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db').cursor()
c.execute("PRAGMA table_info(api_keys)")
cols = [r[1] for r in c.fetchall()]
print('api_keys columns:', cols)
c.execute("SELECT COUNT(*) FROM api_keys WHERE enabled=1")
print('Enabled keys:', c.fetchone()[0])
c.execute("SELECT name, platform, enabled FROM api_keys")
for row in c.fetchall():
    print(f'  {row[0]} | {row[1]} | enabled={row[2]}')
