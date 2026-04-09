import sqlite3

conn = sqlite3.connect("memoria.db")
cursor = conn.cursor()

cursor.execute("SELECT id, pergunta, resposta FROM historico ORDER BY id DESC")
rows = cursor.fetchall()

for row in rows:
    print(f"\n🔹 ID: {row[0]}")
    print(f"❓ Pergunta: {row[1]}")
    print(f"💬 Resposta: {row[2]}")
    print("-" * 60)

conn.close()