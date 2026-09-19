import sqlite3

db_path = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Tablas:")
cur.execute("SELECT key, value FROM settings;")
print("\nSettings:")
for k, v in cur.fetchall():
    print(f"  {k}: {v}")

cur.execute("SELECT id, username FROM users;")
print("\nUsers:")
for u in cur.fetchall():
    print(f"  {u}")
