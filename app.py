"""
ProjetoOFX - Aplicação interativa no terminal.

Menu para o usuário escolher o que fazer com o extrato OFX:
consultar, filtrar, buscar, exportar e enviar para o PostgreSQL.

Execute com:  python app.py
"""

import os
import sys
from datetime import datetime

from main import (
    ARQUIVO_CSV,
    ARQUIVO_OFX,
    LARGURA,
    exportar_csv,
    ler_ofx,
    mostrar_cabecalho,
    mostrar_estatisticas,
    mostrar_movimentacoes,
    mostrar_resumo,
    moeda,
)

MENU = """
┌──────────────────────────────────────────────┐
│          ANÁLISE DE EXTRATO BANCÁRIO         │
├──────────────────────────────────────────────┤
│  1 - Ver extrato completo                    │
│  2 - Resumo (entradas, saídas e saldo)       │
│  3 - Estatísticas                            │
│  4 - Buscar por descrição                    │
│  5 - Filtrar por tipo (entradas / saídas)    │
│  6 - Filtrar por período                     │
│  7 - Exportar relatório CSV                  │
│  8 - Importar para o PostgreSQL              │
│  9 - Ver movimentações gravadas no banco     │
│  0 - Sair                                    │
└──────────────────────────────────────────────┘"""


def pausar():
    input("\nPressione Enter para voltar ao menu...")


def limpar_tela():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def ler_data(texto):
    """Pede uma data no formato dd/mm/aaaa até o usuário digitar corretamente."""
    while True:
        valor = input(texto).strip()
        try:
            return datetime.strptime(valor, "%d/%m/%Y").date()
        except ValueError:
            print("  Data inválida. Use o formato dd/mm/aaaa (ex.: 05/10/2026).")


def mostrar_lista(lista, titulo):
    print(f"\n{titulo}")
    if not lista:
        print("Nenhuma movimentação encontrada.")
        return
    mostrar_movimentacoes(lista)
    total = sum(t.amount for t in lista)
    print(f"{len(lista)} movimentação(ões) | Soma: {moeda(total)}")


def opcao_buscar(transacoes):
    termo = input("Digite parte da descrição (ex.: cliente): ").strip().lower()
    if not termo:
        print("Nenhum termo informado.")
        return
    achadas = [t for t in transacoes if termo in (t.memo or "").lower()]
    mostrar_lista(achadas, f"RESULTADO DA BUSCA POR '{termo}'")


def opcao_filtrar_tipo(transacoes):
    print("\n  1 - Somente entradas")
    print("  2 - Somente saídas")
    escolha = input("Escolha: ").strip()
    if escolha == "1":
        mostrar_lista([t for t in transacoes if t.amount > 0], "ENTRADAS")
    elif escolha == "2":
        mostrar_lista([t for t in transacoes if t.amount < 0], "SAÍDAS")
    else:
        print("Opção inválida.")


def opcao_filtrar_periodo(transacoes):
    inicio = ler_data("Data inicial (dd/mm/aaaa): ")
    fim = ler_data("Data final   (dd/mm/aaaa): ")
    if inicio > fim:
        inicio, fim = fim, inicio
        print("  (datas invertidas, ajustei a ordem)")
    achadas = [t for t in transacoes if inicio <= t.date.date() <= fim]
    mostrar_lista(
        achadas,
        f"MOVIMENTAÇÕES DE {inicio.strftime('%d/%m/%Y')} A {fim.strftime('%d/%m/%Y')}",
    )


def opcao_importar(transacoes):
    from importar_db import importar_para_banco

    print("\nConectando ao PostgreSQL e importando...")
    try:
        inseridas, ignoradas, total, soma = importar_para_banco(transacoes)
    except RuntimeError as erro:
        print(f"Erro de configuração: {erro}")
        return
    except Exception as erro:
        print(f"Erro na importação (nada foi gravado): {erro}")
        return

    print(f"Inseridas : {inseridas}")
    print(f"Ignoradas (duplicadas): {ignoradas}")
    print(f"Total na tabela: {total} registros | soma: {moeda(soma)}")


def opcao_ver_banco():
    from importar_db import listar_do_banco

    print("\nConsultando o banco de dados...")
    try:
        linhas = listar_do_banco()
    except RuntimeError as erro:
        print(f"Erro de configuração: {erro}")
        return
    except Exception as erro:
        print(f"Erro ao consultar o banco: {erro}")
        return

    if not linhas:
        print("A tabela 'movimentacoes' está vazia. Use a opção 8 para importar.")
        return

    print("\nMOVIMENTAÇÕES NO BANCO")
    print(f"{'ID':<5}{'DATA':<12}{'DESCRIÇÃO':<40}{'VALOR':>14}")
    print("-" * LARGURA)
    for id_, data, valor, descricao in linhas:
        print(f"{id_:<5}{data.strftime('%d/%m/%Y'):<12}{descricao[:38]:<40}{moeda(valor):>14}")
    print("-" * LARGURA)
    print(f"{len(linhas)} registro(s) no banco.")


def main():
    ofx = ler_ofx(ARQUIVO_OFX)
    transacoes = ofx.account.statement.transactions
    saldo_banco = getattr(ofx.account.statement, "balance", None)

    if not transacoes:
        sys.exit("O arquivo OFX não possui movimentações.")

    while True:
        limpar_tela()
        print(MENU)
        print(f"Arquivo carregado: {ARQUIVO_OFX} ({len(transacoes)} movimentações)")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "0":
            print("\nAté logo!")
            break
        elif opcao == "1":
            mostrar_cabecalho(ofx)
            mostrar_movimentacoes(transacoes)
        elif opcao == "2":
            mostrar_resumo(transacoes, saldo_banco)
        elif opcao == "3":
            mostrar_estatisticas(transacoes)
        elif opcao == "4":
            opcao_buscar(transacoes)
        elif opcao == "5":
            opcao_filtrar_tipo(transacoes)
        elif opcao == "6":
            opcao_filtrar_periodo(transacoes)
        elif opcao == "7":
            exportar_csv(transacoes, ARQUIVO_CSV)
        elif opcao == "8":
            opcao_importar(transacoes)
        elif opcao == "9":
            opcao_ver_banco()
        else:
            print("\nOpção inválida. Digite um número de 0 a 9.")

        pausar()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nEncerrado pelo usuário.")