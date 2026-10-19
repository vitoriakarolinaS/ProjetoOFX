from ofxparse import OfxParser

with open("extrato.ofx", "rb") as arquivo:
    ofx = OfxParser.parse(arquivo)

transacoes = ofx.account.statement.transactions

print("EXTRATO BANCÁRIO")
print("=" * 50)

entradas = 0
saidas = 0

for t in transacoes:
    print(f"Data      : {t.date.strftime('%d/%m/%Y')}")
    print(f"Valor     : R$ {t.amount:.2f}")
    print(f"Descrição : {t.memo}")
    print("-" * 50)

    if t.amount > 0:
        entradas += t.amount
    else:
        saidas += t.amount

saldo = entradas + saidas

print(f"Total de movimentações: {len(transacoes)}")
print(f"Entradas: R$ {entradas:.2f}")
print(f"Saídas:   R$ {saidas:.2f}")
print(f"Saldo:    R$ {saldo:.2f}")