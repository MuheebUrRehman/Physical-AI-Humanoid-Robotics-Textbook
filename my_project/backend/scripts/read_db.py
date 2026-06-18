import sqlite3, os
db_path = os.path.join(os.path.dirname(__file__), "..", "chatkit.db")
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("Tables:", tables)
for table_name in tables:
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [c[1] for c in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print(f"\n=== {table_name} ({len(rows)} rows) ===")
    print("Columns:", cols)
    for row in rows:
        for i, val in enumerate(row):
            print(f"  {cols[i]}: {str(val)[:120]}")
        print()
conn.close()
