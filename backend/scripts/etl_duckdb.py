import os
import sys
import psycopg2
import pandas as pd
import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

DUCKDB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "marts.duckdb")

def executar_etl_duckdb():
    print("🚀 Iniciando Extração OLTP (Neon) -> OLAP (DuckDB)")
    
    print("🔗 Conectando ao NeonDB...")
    conn_pg = psycopg2.connect(settings.database_url)
    
    print("📥 Extraindo mart_vendas...")
    query_vendas = """
    SELECT 
        v.id as venda_id,
        v.data_venda,
        EXTRACT(YEAR FROM v.data_venda)::INT AS ano,
        EXTRACT(MONTH FROM v.data_venda)::INT AS mes,
        p.nome AS produto,
        c.nome AS categoria,
        cli.nome AS cliente,
        v.quantidade,
        v.valor_unitario,
        v.valor_total AS faturamento,
        (v.valor_total - (p.preco_custo * v.quantidade)) AS lucro
    FROM fato_vendas v
    JOIN dim_produtos p ON v.produto_id = p.id
    JOIN dim_categorias c ON p.categoria_id = c.id
    LEFT JOIN dim_clientes cli ON v.cliente_id = cli.id;
    """
    df_vendas = pd.read_sql_query(query_vendas, conn_pg)
    
    print("📥 Extraindo mart_auditoria...")
    query_auditoria = """
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
        p.id AS sku_id,
        p.nome AS produto,
        c.nome AS categoria,
        e.quantidade_atual AS estoque_atual,
        (e.quantidade_atual * p.preco_custo) AS valor_estoque_custo,
        p.estoque_minimo,
        e.data_validade,
        (e.data_validade - CURRENT_DATE)::INT AS dias_para_vencer,
        COALESCE(vr.vendas_30dias, 0) AS vendas_30dias,
        COALESCE(vr.total_vendido, 0) AS vendas_totais_historico,
        (CURRENT_DATE - COALESCE(vr.data_ultima_venda, CURRENT_DATE))::INT AS dias_sem_venda
    FROM dim_produtos p
    JOIN dim_categorias c ON p.categoria_id = c.id
    JOIN fato_estoque e ON p.id = e.produto_id
    LEFT JOIN vendas_resumo vr ON p.id = vr.produto_id;
    """
    df_auditoria = pd.read_sql_query(query_auditoria, conn_pg)
    conn_pg.close()

    print("💾 Gravando dados locais no DuckDB...")
    con_db = duckdb.connect(database=DUCKDB_PATH)
    con_db.execute("CREATE OR REPLACE TABLE mart_vendas AS SELECT * FROM df_vendas")
    con_db.execute("CREATE OR REPLACE TABLE mart_auditoria AS SELECT * FROM df_auditoria")
    con_db.close()
    
    print("🎉 ETL finalizado! DuckDB Marts operacionais localmente.")

if __name__ == "__main__":
    executar_etl_duckdb()
