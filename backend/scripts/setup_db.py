"""
Cria (ou recria) toda a estrutura do banco:
- Tabelas dimensão e fato
- View analítica de auditoria

Execute apenas uma vez para inicializar o ambiente,
ou quando quiser resetar o banco completamente.

Uso:
    python scripts/setup_db.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config.settings import settings


DDL = """
-- Limpeza para garantir reprodutibilidade
DROP VIEW IF EXISTS vw_dashboard_auditoria CASCADE;
DROP TABLE IF EXISTS fato_vendas CASCADE;
DROP TABLE IF EXISTS fato_estoque CASCADE;
DROP TABLE IF EXISTS dim_produtos CASCADE;
DROP TABLE IF EXISTS dim_clientes CASCADE;
DROP TABLE IF EXISTS dim_categorias CASCADE;

-- Dimensões
CREATE TABLE dim_categorias (
    id   SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE dim_produtos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(255) NOT NULL,
    categoria_id    INT REFERENCES dim_categorias(id),
    preco_custo     DECIMAL(10, 2),
    preco_venda     DECIMAL(10, 2),
    estoque_minimo  INT DEFAULT 10
);

CREATE TABLE dim_clientes (
    id     SERIAL PRIMARY KEY,
    nome   VARCHAR(255) NOT NULL,
    cidade VARCHAR(100),
    estado CHAR(2)
);

-- Fatos
CREATE TABLE fato_estoque (
    id              SERIAL PRIMARY KEY,
    produto_id      INT REFERENCES dim_produtos(id),
    quantidade_atual INT NOT NULL,
    data_validade   DATE
);

CREATE TABLE fato_vendas (
    id            SERIAL PRIMARY KEY,
    data_venda    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    produto_id    INT REFERENCES dim_produtos(id),
    cliente_id    INT REFERENCES dim_clientes(id),
    quantidade    INT NOT NULL,
    valor_unitario DECIMAL(10, 2),
    valor_total   DECIMAL(10, 2)
);
"""

VIEW = """
CREATE VIEW vw_dashboard_auditoria AS
WITH vendas_resumo AS (
    SELECT
        produto_id,
        COUNT(*) FILTER (WHERE data_venda >= CURRENT_DATE - INTERVAL '30 days') AS vendas_30dias,
        SUM(quantidade) AS total_vendido,
        MAX(data_venda)::DATE AS data_ultima_venda
    FROM fato_vendas
    GROUP BY produto_id
)
SELECT
    p.id                                                    AS sku_id,
    p.nome                                                  AS produto,
    c.nome                                                  AS categoria,
    p.preco_custo,
    p.preco_venda,
    e.quantidade_atual                                      AS estoque_atual,
    (e.quantidade_atual * p.preco_custo)                    AS valor_estoque_custo,
    (e.quantidade_atual * p.preco_venda)                    AS valor_potencial_venda,
    p.estoque_minimo,
    e.data_validade,
    (e.data_validade - CURRENT_DATE)::INT                   AS dias_para_vencer,
    CASE
        WHEN (e.data_validade - CURRENT_DATE) < 0  THEN 'Vencido'
        WHEN (e.data_validade - CURRENT_DATE) < 15 THEN 'Vermelho (Crítico)'
        WHEN (e.data_validade - CURRENT_DATE) < 46 THEN 'Amarelo (Atenção)'
        ELSE 'Verde (Seguro)'
    END                                                     AS status_validade,
    COALESCE(vr.vendas_30dias, 0)                           AS vendas_30dias,
    COALESCE(vr.total_vendido, 0)                           AS vendas_totais_historico,
    (CURRENT_DATE - vr.data_ultima_venda)::INT              AS dias_sem_venda,
    CASE
        WHEN e.quantidade_atual <= p.estoque_minimo THEN 'Reposição Necessária'
        WHEN vr.data_ultima_venda < CURRENT_DATE - INTERVAL '30 days' OR vr.data_ultima_venda IS NULL THEN 'Estoque Parado'
        ELSE 'Normal'
    END                                                     AS alerta_gestao
FROM dim_produtos p
JOIN dim_categorias c ON p.categoria_id = c.id
JOIN fato_estoque e ON p.id = e.produto_id
LEFT JOIN vendas_resumo vr ON p.id = vr.produto_id;
"""

VIEW_FATURAMENTO = """
CREATE OR REPLACE VIEW vw_faturamento_temporal AS
SELECT 
    v.data_venda,
    EXTRACT(YEAR FROM v.data_venda)::INT AS ano,
    EXTRACT(MONTH FROM v.data_venda)::INT AS mes,
    p.nome AS produto,
    c.nome AS categoria,
    cli.nome AS cliente,
    cli.cidade AS cliente_cidade,
    cli.estado AS cliente_estado,
    v.quantidade,
    v.valor_total AS faturamento,
    (v.valor_total - (p.preco_custo * v.quantidade)) AS lucro
FROM fato_vendas v
JOIN dim_produtos p ON v.produto_id = p.id
JOIN dim_categorias c ON p.categoria_id = c.id
LEFT JOIN dim_clientes cli ON v.cliente_id = cli.id;
"""


def executar_setup() -> None:
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()

        print("1. Recriando estrutura do banco...")
        cursor.execute(DDL)

        print("2. Criando views de auditoria e financeiras...")
        cursor.execute(VIEW)
        cursor.execute(VIEW_FATURAMENTO)

        conn.commit()
        print("✅ Setup concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro no setup: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    executar_setup()
