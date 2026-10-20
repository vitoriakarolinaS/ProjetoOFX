# ProjetoOFX - Leitura de Extratos Bancários (OFX) com Python

Atividade da unidade de estudos **Integração de Dados** (UNIFEOB).

O projeto implementa um processo **ETL** simplificado:

| Etapa | O que acontece |
|---|---|
| **Extração** | Leitura do arquivo `extrato.ofx` com a biblioteca `ofxparse` |
| **Transformação** | Cálculo de entradas, saídas, saldo e estatísticas; formatação em R$ |
| **Carga** | Gravação das movimentações em um banco PostgreSQL (Neon), sem duplicados |

## Funcionalidades

**`app.py`** (aplicação interativa - execute este)

Menu no terminal em que o usuário escolhe o que fazer, com validação de entradas:

| Opção | Ação |
|---|---|
| 1 | Ver extrato completo |
| 2 | Resumo: entradas, saídas e saldo |
| 3 | Estatísticas |
| 4 | Buscar movimentações por descrição |
| 5 | Filtrar por tipo (entradas ou saídas) |
| 6 | Filtrar por período (dd/mm/aaaa) |
| 7 | Exportar relatório CSV |
| 8 | Importar para o PostgreSQL |
| 9 | Ver as movimentações gravadas no banco |
| 0 | Sair |

**`main.py`**
- Exibe os dados da conta (banco, agência, conta e período do extrato).
- Lista cada movimentação com data, descrição, valor e saldo acumulado.
- Mostra a quantidade total de movimentações, de entradas e de saídas.
- Calcula total de entradas, total de saídas e saldo.
- Estatísticas: maior entrada, maior saída, médias e dia com mais movimentações.
- Gera o arquivo `relatorio_movimentacoes.csv` (abre direto no Excel).
- Trata erros comuns (arquivo não encontrado ou inválido).

**`importar_db.py`** (desafio extra e bônus)
- Conecta ao PostgreSQL usando a variável `DATABASE_URL` (a senha fica fora do código).
- Cria a tabela `movimentacoes` se ela não existir.
- Insere cada transação do OFX.
- **Bônus:** ignora transações duplicadas (mesma data, valor e descrição), então o script pode ser executado várias vezes com segurança.
- Usa transação: se algo falhar, faz `rollback` e nada é gravado pela metade.

**`consultas.sql`**
- Consultas para validar os dados no DBeaver (totais, maiores valores, verificação de duplicados e resumo por dia).

## Estrutura do projeto

```
ProjetoOFX
├── app.py               # menu interativo (ponto de entrada)
├── main.py              # leitura, totais e relatório
├── importar_db.py       # importação para o PostgreSQL
├── consultas.sql        # consultas de validação (DBeaver)
├── extrato.ofx          # arquivo OFX de exemplo
├── requirements.txt     # dependências
├── .env.example         # modelo de configuração da conexão
├── .gitignore
└── README.md
```

## Como executar

**1. Clonar o projeto e criar o ambiente virtual**
```bash
git clone https://github.com/vitoriakarolinaS/ProjetoOFX.git
cd ProjetoOFX
python -m venv venv
venv\Scripts\activate        # Windows
```

**2. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**3. Executar a aplicação interativa**
```bash
python app.py
```
Para ver apenas o relatório completo de uma vez, sem menu: `python main.py`

**4. (Desafio extra) Importar para o PostgreSQL**

1. Copie o arquivo `.env.example` para `.env`.
2. Abra o `.env` e troque `SUA_SENHA` pela senha real do banco no Neon.
3. Execute `python app.py` e use a opção **8** (ou, direto: `python importar_db.py`).

Na primeira execução, as 15 movimentações são inseridas. Ao executar novamente, todas são
ignoradas como duplicadas, o que comprova a validação do bônus.

**5. Validar no DBeaver**

Conecte ao banco (host do Neon, porta `5432`, banco `neondb`, driver property `sslmode=require`) e execute
as consultas do arquivo `consultas.sql`.

## Observação sobre o saldo

O **saldo calculado** é a soma das movimentações do período. O **saldo informado no OFX** é o saldo
contábil final da conta, que pode incluir valores anteriores ao período do extrato, por isso os dois
podem ser diferentes.

## Tecnologias

Python 3 · ofxparse · psycopg2 · python-dotenv · PostgreSQL (Neon) · DBeaver · Git/GitHub · VS Code