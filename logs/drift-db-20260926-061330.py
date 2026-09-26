import sqlite3
c = sqlite3.connect(r'C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db').cursor()
c.execute('SELECT COUNT(*) FROM models'); print('  catalog total:', c.fetchone()[0])
c.execute('SELECT COUNT(*) FROM models WHERE enabled=1'); print('  catalog enabled:', c.fetchone()[0])
try:
    c.execute('SELECT platform, COUNT(*) FROM models GROUP BY platform')
    for row in c.fetchall(): print('  platform', row[0], '=', row[1])
except Exception as e: print('  platform query err:', e)
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('  tables:', [r[0] for r in c.fetchall()])
except Exception as e: print('  tables err:', e)
