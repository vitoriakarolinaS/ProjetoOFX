-- Consultas úteis para validar os dados no DBeaver
-- (banco: neondb | tabela: movimentacoes)

-- 1) Criar a tabela (o importar_db.py já faz isso automaticamente)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);

-- 2) Ver todas as movimentações
SELECT * FROM movimentacoes ORDER BY data_movimentacao, id;

-- 3) Quantidade de registros
SELECT COUNT(*) AS total_registros FROM movimentacoes;

-- 4) Total de entradas, saídas e saldo
SELECT
    SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END) AS total_entradas,
    SUM(CASE WHEN valor < 0 THEN valor ELSE 0 END) AS total_saidas,
    SUM(valor)                                     AS saldo
FROM movimentacoes;

-- 5) Maiores entradas
SELECT data_movimentacao, valor, descricao
FROM movimentacoes
WHERE valor > 0
ORDER BY valor DESC
LIMIT 3;

-- 6) Maiores saídas
SELECT data_movimentacao, valor, descricao
FROM movimentacoes
WHERE valor < 0
ORDER BY valor ASC
LIMIT 3;

-- 7) Validar que NÃO há duplicados (deve retornar zero linhas)
SELECT data_movimentacao, valor, descricao, COUNT(*) AS repeticoes
FROM movimentacoes
GROUP BY data_movimentacao, valor, descricao
HAVING COUNT(*) > 1;

-- 8) Resumo por dia
SELECT data_movimentacao, COUNT(*) AS qtd, SUM(valor) AS total_dia
FROM movimentacoes
GROUP BY data_movimentacao
ORDER BY data_movimentacao;