import psycopg2
from ofxparse import OfxParser

DATABASE_URL = "postgresql://neondb_owner:senha@ep-holy-cell-b5tmde5o-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require"

with open("extrato.ofx", "rb") as arquivo:
    ofx = OfxParser.parse(arquivo)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

inseridas = 0
ignoradas = 0

for t in ofx.account.statement.transactions:

    cur.execute(
        """
        SELECT 1 FROM movimentacoes
        WHERE data_movimentacao = %s AND valor = %s AND descricao = %s
        """,
        (t.date.date(), t.amount, t.memo),
    )

    if cur.fetchone():
        ignoradas += 1
        continue

    cur.execute(
        """
        INSERT INTO movimentacoes (data_movimentacao, valor, descricao)
        VALUES (%s, %s, %s)
        """,
        (t.date.date(), t.amount, t.memo),
    )
    inseridas += 1

conn.commit()
cur.close()
conn.close()

print(f"Inseridas: {inseridas} | Ignoradas (duplicadas): {ignoradas}")