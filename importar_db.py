"""
Importa as movimentações do extrato OFX para o PostgreSQL (Neon).

- Cria a tabela 'movimentacoes' caso ela ainda não exista.
- Evita gravar transações duplicadas (mesma data, valor e descrição).
- Se qualquer erro ocorrer, desfaz tudo (rollback) para não deixar dados pela metade.

A conexão é lida da variável DATABASE_URL (arquivo .env ou variável de ambiente).
Pode ser executado direto (python importar_db.py) ou usado pelo menu (app.py).
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv
from ofxparse import OfxParser

ARQUIVO_OFX = "extrato.ofx"

SQL_CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);
"""

SQL_EXISTE = """
SELECT 1 FROM movimentacoes
WHERE data_movimentacao = %s AND valor = %s AND descricao = %s
"""

SQL_INSERIR = """
INSERT INTO movimentacoes (data_movimentacao, valor, descricao)
VALUES (%s, %s, %s)
"""


def obter_database_url():
    """Lê DATABASE_URL do .env. Levanta RuntimeError se não estiver configurada."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url or "SUA_SENHA" in url:
        raise RuntimeError(
            "Configure a variável DATABASE_URL no arquivo .env "
            "(veja o .env.example) com a senha real do banco."
        )
    return url


def importar_para_banco(transacoes):
    """
    Grava as transações no banco, ignorando duplicadas.
    Retorna (inseridas, ignoradas, total_na_tabela, soma_dos_valores).
    """
    conn = psycopg2.connect(obter_database_url())
    inseridas = 0
    ignoradas = 0

    try:
        with conn.cursor() as cur:
            cur.execute(SQL_CRIAR_TABELA)

            for t in transacoes:
                dados = (t.date.date(), t.amount, (t.memo or "").strip())

                cur.execute(SQL_EXISTE, dados)
                if cur.fetchone():
                    ignoradas += 1
                    continue

                cur.execute(SQL_INSERIR, dados)
                inseridas += 1

            cur.execute("SELECT COUNT(*), COALESCE(SUM(valor), 0) FROM movimentacoes")
            total, soma = cur.fetchone()

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return inseridas, ignoradas, total, soma


def listar_do_banco():
    """Retorna todas as linhas da tabela: (id, data, valor, descricao)."""
    conn = psycopg2.connect(obter_database_url())
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, data_movimentacao, valor, descricao "
                "FROM movimentacoes ORDER BY data_movimentacao, id"
            )
            return cur.fetchall()
    finally:
        conn.close()


def main():
    try:
        with open(ARQUIVO_OFX, "rb") as arquivo:
            transacoes = OfxParser.parse(arquivo).account.statement.transactions
    except FileNotFoundError:
        sys.exit(f"Erro: arquivo '{ARQUIVO_OFX}' não encontrado.")

    print(f"Movimentações encontradas no OFX: {len(transacoes)}")

    try:
        inseridas, ignoradas, total, soma = importar_para_banco(transacoes)
    except RuntimeError as erro:
        sys.exit(f"Erro: {erro}")
    except Exception as erro:
        sys.exit(f"Erro durante a importação (nada foi gravado): {erro}")

    print(f"Inseridas : {inseridas}")
    print(f"Ignoradas (duplicadas): {ignoradas}")
    print(f"Total na tabela 'movimentacoes': {total} registros | soma: R$ {soma:.2f}")


if __name__ == "__main__":
    main()