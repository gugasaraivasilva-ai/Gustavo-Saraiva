import sqlite3

conn = sqlite3.connect("memoria.db")
cursor = conn.cursor()

# Apagar TUDO
cursor.execute("DELETE FROM historico")

# OU apagar apenas registros antigos (ex: mais de 30 dias)
# cursor.execute("DELETE FROM historico WHERE rowid NOT IN (SELECT rowid FROM historico ORDER BY id DESC LIMIT 100)")

conn.commit()
print(f"✅ {cursor.rowcount} registros removidos.")
conn.close()