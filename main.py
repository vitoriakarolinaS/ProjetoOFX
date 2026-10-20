"""
ProjetoOFX - Leitura de extrato bancário (OFX) com Python.

Lê o arquivo extrato.ofx, exibe as movimentações, calcula os totais
(entradas, saídas e saldo), mostra estatísticas e gera um relatório CSV.
"""

import csv
import sys
from decimal import Decimal

from ofxparse import OfxParser

ARQUIVO_OFX = "extrato.ofx"
ARQUIVO_CSV = "relatorio_movimentacoes.csv"
LARGURA = 78


def moeda(valor):
    """Formata um número como moeda brasileira: R$ 1.234,56"""
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {texto}"


def ler_ofx(caminho):
    """Abre e interpreta o arquivo OFX. Encerra com mensagem clara em caso de erro."""
    try:
        with open(caminho, "rb") as arquivo:
            return OfxParser.parse(arquivo)
    except FileNotFoundError:
        sys.exit(f"Erro: arquivo '{caminho}' não encontrado na pasta do projeto.")
    except Exception as erro:
        sys.exit(f"Erro ao ler o arquivo OFX: {erro}")


def mostrar_cabecalho(ofx):
    conta = ofx.account
    extrato = conta.statement

    print("=" * LARGURA)
    print("EXTRATO BANCÁRIO".center(LARGURA))
    print("=" * LARGURA)
    print(f"Banco   : {getattr(conta, 'routing_number', '-')}")
    print(f"Agência : {getattr(conta, 'branch_id', '-')}")
    print(f"Conta   : {getattr(conta, 'account_id', '-')}")
    if extrato.start_date and extrato.end_date:
        print(
            f"Período : {extrato.start_date.strftime('%d/%m/%Y')} "
            f"a {extrato.end_date.strftime('%d/%m/%Y')}"
        )
    print("=" * LARGURA)


def mostrar_movimentacoes(transacoes):
    print(f"{'DATA':<12}{'DESCRIÇÃO':<38}{'VALOR':>14}{'SALDO ACUM.':>14}")
    print("-" * LARGURA)

    acumulado = Decimal("0")
    for t in transacoes:
        acumulado += t.amount
        descricao = (t.memo or "").strip()[:36]
        print(
            f"{t.date.strftime('%d/%m/%Y'):<12}"
            f"{descricao:<38}"
            f"{moeda(t.amount):>14}"
            f"{moeda(acumulado):>14}"
        )
    print("-" * LARGURA)


def calcular_totais(transacoes):
    entradas = sum((t.amount for t in transacoes if t.amount > 0), Decimal("0"))
    saidas = sum((t.amount for t in transacoes if t.amount < 0), Decimal("0"))
    return entradas, saidas, entradas + saidas


def mostrar_resumo(transacoes, saldo_banco=None):
    entradas, saidas, saldo = calcular_totais(transacoes)
    qtd_entradas = sum(1 for t in transacoes if t.amount > 0)
    qtd_saidas = sum(1 for t in transacoes if t.amount < 0)

    print("\nRESUMO")
    print("-" * LARGURA)
    print(f"Total de movimentações : {len(transacoes)}")
    print(f"Quantidade de entradas : {qtd_entradas}")
    print(f"Quantidade de saídas   : {qtd_saidas}")
    print(f"Total de entradas      : {moeda(entradas)}")
    print(f"Total de saídas        : {moeda(saidas)}")
    print(f"Saldo calculado        : {moeda(saldo)}")

    # Saldo informado pelo próprio banco (se existir no arquivo)
    if saldo_banco is not None:
        print(f"Saldo informado (OFX)  : {moeda(saldo_banco)}")


def mostrar_estatisticas(transacoes):
    entradas = [t for t in transacoes if t.amount > 0]
    saidas = [t for t in transacoes if t.amount < 0]

    print("\nESTATÍSTICAS")
    print("-" * LARGURA)

    if entradas:
        maior_entrada = max(entradas, key=lambda t: t.amount)
        media_entradas = sum(t.amount for t in entradas) / len(entradas)
        print(f"Maior entrada  : {moeda(maior_entrada.amount)} - {maior_entrada.memo}")
        print(f"Média entradas : {moeda(media_entradas)}")

    if saidas:
        maior_saida = min(saidas, key=lambda t: t.amount)
        media_saidas = sum(t.amount for t in saidas) / len(saidas)
        print(f"Maior saída    : {moeda(maior_saida.amount)} - {maior_saida.memo}")
        print(f"Média saídas   : {moeda(media_saidas)}")

    por_dia = {}
    for t in transacoes:
        dia = t.date.strftime("%d/%m/%Y")
        por_dia[dia] = por_dia.get(dia, 0) + 1
    dia_mais_movimentado = max(por_dia, key=por_dia.get)
    print(
        f"Dia com mais movimentações: {dia_mais_movimentado} "
        f"({por_dia[dia_mais_movimentado]})"
    )


def exportar_csv(transacoes, caminho):
    """Gera um CSV (separador ';' e UTF-8 com BOM para abrir direto no Excel)."""
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["data", "tipo", "valor", "descricao"])
        for t in transacoes:
            tipo = "ENTRADA" if t.amount > 0 else "SAIDA"
            escritor.writerow(
                [
                    t.date.strftime("%d/%m/%Y"),
                    tipo,
                    f"{t.amount:.2f}".replace(".", ","),
                    (t.memo or "").strip(),
                ]
            )
    print(f"\nRelatório gerado: {caminho}")


if __name__ == "__main__":
    ofx = ler_ofx(ARQUIVO_OFX)
    transacoes = ofx.account.statement.transactions

    if not transacoes:
        sys.exit("O arquivo OFX não possui movimentações.")

    mostrar_cabecalho(ofx)
    mostrar_movimentacoes(transacoes)
    mostrar_resumo(transacoes, getattr(ofx.account.statement, "balance", None))
    mostrar_estatisticas(transacoes)
    exportar_csv(transacoes, ARQUIVO_CSV)