<h1 align="center">📄 ProjetoOFX</h1>

<p align="center">
  Leitura de extratos bancários OFX com Python, análise em terminal e carga em PostgreSQL.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/ETL-Integração_de_Dados-2EA44F" alt="ETL">
  <img src="https://img.shields.io/badge/formato-OFX-F28C28" alt="OFX">
  <img src="https://img.shields.io/badge/interface-terminal-black?logo=windowsterminal&logoColor=white" alt="Terminal">
  <img src="https://img.shields.io/badge/status-concluído-brightgreen" alt="Status">
</p>

---

## Sumário

- [Sobre o projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Fluxo de dados (ETL)](#-fluxo-de-dados-etl)
- [Tecnologias](#-tecnologias)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Como executar](#-como-executar)
- [Configuração do banco de dados](#-configuração-do-banco-de-dados)
- [Exemplo de saída](#-exemplo-de-saída)
- [Decisões técnicas](#-decisões-técnicas)
- [Limitações e melhorias futuras](#-limitações-e-melhorias-futuras)
- [Competências aplicadas](#-competências-aplicadas)
- [Autora](#-autora)

---

## Sobre o projeto

Aplicação de linha de comando que lê extratos bancários no formato **OFX** (*Open Financial Exchange*), o padrão que os bancos usam para exportar movimentações. O programa extrai as transações, calcula indicadores financeiros e permite gravar os dados em um banco **PostgreSQL** hospedado no **Neon**, sem registros duplicados.

Desenvolvido na unidade de estudos de **Integração de Dados** (UNIFEOB) como uma implementação simplificada de um processo **ETL**, o mesmo tipo de rotina usada em escritórios contábeis e instituições financeiras para conciliação bancária.

---

## Funcionalidades

### Menu interativo (`app.py`)

| Opção | Ação |
|:---:|---|
| `1` | Extrato completo, com saldo acumulado a cada movimentação |
| `2` | Resumo: total de entradas, total de saídas e saldo |
| `3` | Estatísticas: maior entrada, maior saída, médias e dia mais movimentado |
| `4` | Busca por trecho da descrição |
| `5` | Filtro por tipo (entradas ou saídas) |
| `6` | Filtro por período (`dd/mm/aaaa`) |
| `7` | Exportação de relatório em **CSV** (compatível com Excel) |
| `8` | Importação das movimentações para o **PostgreSQL** |
| `9` | Consulta dos registros gravados no banco |
| `0` | Sair |

### Destaques

- ✅ Validação de entradas: opção inexistente ou data inválida não derrubam o programa
- ✅ Valores formatados em reais (`R$ 1.234,56`)
- ✅ Cálculos com `Decimal`, sem erros de arredondamento
- ✅ Importação **idempotente**: pode ser executada várias vezes sem duplicar dados
- ✅ Gravação transacional, com `rollback` em caso de falha
- ✅ Credenciais fora do código, em arquivo `.env`

---

## Fluxo de dados (ETL)

```mermaid
flowchart LR
    A[("📄 extrato.ofx")] -->|Extração| B["main.py<br/>leitura e cálculos"]
    B -->|Transformação| C["app.py<br/>menu e relatórios"]
    B --> D["importar_db.py"]
    D -->|Carga| E[("🐘 PostgreSQL<br/>Neon")]

    classDef origem fill:#FFF3CD,stroke:#F0AD4E,color:#000
    classDef codigo fill:#D6E4FF,stroke:#3776AB,color:#000
    classDef destino fill:#D4EDDA,stroke:#2EA44F,color:#000
    class A origem
    class B,C,D codigo
    class E destino
```

| Etapa | Implementação |
|---|---|
| **E**xtração | Leitura do `extrato.ofx` com a biblioteca `ofxparse` |
| **T**ransformação | Cálculo de totais, saldo e estatísticas; formatação monetária |
| **L**oad (Carga) | Gravação na tabela `movimentacoes` do PostgreSQL, com verificação de duplicados |

---

## Tecnologias

| Categoria | Ferramentas |
|---|---|
| Linguagem | Python 3.10+ |
| Leitura de dados | `ofxparse` |
| Banco de dados | PostgreSQL (Neon), `psycopg2` |
| Configuração | `python-dotenv` |
| Ferramentas | VS Code, DBeaver, Git e GitHub |

---

## Estrutura do projeto

```text
ProjetoOFX
├── app.py               # menu interativo (ponto de entrada)
├── main.py              # leitura do OFX, cálculos, estatísticas e CSV
├── importar_db.py       # carga no PostgreSQL
├── consultas.sql        # consultas de validação (DBeaver)
├── extrato.ofx          # extrato de exemplo (15 movimentações)
├── requirements.txt     # dependências
├── .env.example         # modelo de configuração da conexão
├── .gitignore
└── README.md
```

O código foi dividido por responsabilidade: `main.py` cuida do extrato, `importar_db.py` cuida do banco e `app.py` só orquestra as duas partes, sem repetir lógica.

---

## Como executar

**Pré-requisitos:** Python 3.10+, Git e, para a parte do banco, uma conta no [Neon](https://neon.tech).

**1. Clonar o repositório**

```bash
git clone https://github.com/vitoriakarolinaS/ProjetoOFX.git
cd ProjetoOFX
```

**2. Criar e ativar o ambiente virtual**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux
```

**3. Instalar as dependências**

```bash
pip install -r requirements.txt
```

**4. Executar**

```bash
python app.py       # menu interativo
python main.py      # relatório completo, sem menu
```

As opções de `1` a `7` dependem apenas do arquivo OFX. As opções `8` e `9` exigem a configuração do banco, descrita abaixo.

---

## Configuração do banco de dados

A conexão é lida da variável `DATABASE_URL`, definida em um arquivo `.env` local que **não é versionado** (está no `.gitignore`).

**1. Criar o `.env` a partir do modelo**

```bash
copy .env.example .env       # Windows
# cp .env.example .env       # Mac / Linux
```

**2. Informar a connection string do Neon** (painel do Neon → *Connect* → *Show password*)

```ini
DATABASE_URL=postgresql://USUARIO:SENHA@HOST/neondb?sslmode=require
```

**3. Importar** pela opção `8` do menu ou diretamente:

```bash
python importar_db.py
```

Na primeira execução, as 15 movimentações são inseridas. Nas seguintes, todas são ignoradas como duplicadas.

### Estrutura da tabela

```sql
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);
```

### Validação no DBeaver

Conexão PostgreSQL com porta `5432`, banco `neondb` e a propriedade de driver `sslmode=require`. O arquivo [`consultas.sql`](consultas.sql) reúne consultas prontas:

```sql
-- Entradas, saídas e saldo
SELECT
    SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END) AS total_entradas,
    SUM(CASE WHEN valor < 0 THEN valor ELSE 0 END) AS total_saidas,
    SUM(valor)                                     AS saldo
FROM movimentacoes;

-- Verificação de duplicados (deve retornar zero linhas)
SELECT data_movimentacao, valor, descricao, COUNT(*) AS repeticoes
FROM movimentacoes
GROUP BY data_movimentacao, valor, descricao
HAVING COUNT(*) > 1;
```

---

## Exemplo de saída

Resumo gerado a partir do `extrato.ofx` de exemplo:

```text
RESUMO
------------------------------------------------------------------------------
Total de movimentações : 15
Quantidade de entradas : 5
Quantidade de saídas   : 10
Total de entradas      : R$ 17.900,00
Total de saídas        : -R$ 6.059,70
Saldo calculado        : R$ 11.840,30
Saldo informado (OFX)  : R$ 12.030,20
```

Resultado da importação executada duas vezes seguidas:

```text
# 1ª execução
Inseridas : 15
Ignoradas (duplicadas): 0

# 2ª execução
Inseridas : 0
Ignoradas (duplicadas): 15
```

---

## Decisões técnicas

### Credenciais fora do código

A string de conexão fica no `.env`, e o repositório traz apenas o `.env.example`, sem dados reais.

```diff
- DATABASE_URL = "postgresql://usuario:senha@host/neondb"   # senha exposta no código
+ DATABASE_URL = os.getenv("DATABASE_URL")                  # senha no .env (não versionado)
```

### Importação idempotente

Antes de cada `INSERT`, uma consulta verifica se a movimentação já existe (mesma data, valor e descrição). Isso permite reexecutar a importação com segurança:

```python
cur.execute(SQL_EXISTE, dados)
if cur.fetchone():
    ignoradas += 1
    continue

cur.execute(SQL_INSERIR, dados)
inseridas += 1
```

### Transação com rollback

Toda a carga acontece dentro de uma única transação. Se ocorrer qualquer erro, nada é gravado:

```python
try:
    # ... SELECTs e INSERTs ...
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

### Precisão monetária

Os valores usam `Decimal` em vez de `float`, evitando imprecisões de ponto flutuante em somas de dinheiro.

### Saldo calculado × saldo do OFX

O saldo calculado é a soma das movimentações do período (R$ 11.840,30 no exemplo). O saldo do OFX é o saldo contábil final informado pelo banco (R$ 12.030,20), que pode incluir valores anteriores ao início do extrato. O programa exibe os dois.

---

## Limitações e melhorias futuras

- [ ] Identificar duplicados pelo **FITID** (código único da transação no OFX), já que o critério atual (data + valor + descrição) trataria duas compras idênticas no mesmo dia como uma só
- [ ] Permitir a escolha entre vários arquivos OFX
- [ ] Categorização automática das movimentações (ex.: aluguel, folha, clientes)
- [ ] Interface web com tabela e gráficos
- [ ] Testes automatizados com `pytest`

---

## Competências aplicadas

- **ETL:** extração, transformação e carga de dados de uma fonte real
- **Python:** funções, tratamento de exceções, manipulação de datas, arquivos e CSV
- **SQL / PostgreSQL:** modelagem de tabela, consultas, agregações e validação de dados
- **Boas práticas:** separação de responsabilidades, segredos fora do código, idempotência e transações
- **Ferramentas:** Git, GitHub, ambientes virtuais, DBeaver e banco em nuvem (Neon)

---

## Autora

**Vitória Karolina**

[![GitHub](https://img.shields.io/badge/GitHub-vitoriakarolinaS-181717?logo=github&logoColor=white)](https://github.com/vitoriakarolinaS)
