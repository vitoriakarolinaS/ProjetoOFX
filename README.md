# ProjetoOFX - Leitura de Arquivos OFX com Python

Atividade da unidade de estudos **Integração de Dados** (UNIFEOB).

## O que o projeto faz
- Lê um extrato bancário no formato OFX com a biblioteca `ofxparse`.
- Exibe data, valor e descrição de cada movimentação.
- Calcula quantidade de movimentações, total de entradas, total de saídas e saldo.
- **Desafio extra:** grava as movimentações em um banco PostgreSQL (Neon).
- **Bônus:** evita gravar transações duplicadas.

## Estrutura
```
ProjetoOFX
├── main.py          # leitura e totais do extrato
├── importar_db.py   # importação para o PostgreSQL
├── extrato.ofx      # arquivo de exemplo
└── .gitignore
```

## Como executar
```
python -m venv venv
venv\Scripts\activate
pip install ofxparse psycopg2-binary
python main.py
python importar_db.py
```
Antes de rodar o `importar_db.py`, substitua `SUA_SENHA` na variável `DATABASE_URL`
pela senha do seu banco no Neon.

## Tabela utilizada
```sql
CREATE TABLE movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);
```

## Tecnologias
Python, ofxparse, psycopg2, PostgreSQL (Neon), DBeaver, VS Code.
