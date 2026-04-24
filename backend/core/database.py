"""
Gerencia a conexão com o banco de dados PostgreSQL (NeonDB).
Retorna uma instância de SQLDatabase pronta para uso pelo agente.
"""

from langchain_community.utilities import SQLDatabase
from config.settings import settings

# Data Marts em DuckDB que o agente pode enxergar — princípio do menor privilégio
ALLOWED_VIEWS = ["mart_auditoria", "mart_vendas"]


def get_database() -> SQLDatabase:
    """
    Cria e retorna a conexão com o banco de dados Analítico (DuckDB).
    """
    import os
    
    # Monta a URI do banco local adaptando barras para Windows
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'marts.duckdb')
    duck_uri = f"duckdb:///{db_path.replace(chr(92), '/')}"
    
    return SQLDatabase.from_uri(
        database_uri=duck_uri,
        include_tables=ALLOWED_VIEWS,
        sample_rows_in_table_info=settings.db_sample_rows,
        view_support=True,
        engine_args={"connect_args": {"read_only": True}},
    )
