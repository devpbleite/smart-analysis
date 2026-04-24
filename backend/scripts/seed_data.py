"""
Popula o banco com dados fictícios para desenvolvimento e testes.
Utiliza Faker com locale pt_BR para nomes realistas.

Uso:
    python scripts/seed_data.py

Requer que o banco já tenha sido criado via:
    python scripts/setup_db.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from faker import Faker
from config.settings import settings

fake = Faker("pt_BR")

CATEGORIAS = {
    "Alimentos":  ["Arroz 5kg", "Feijão Carioca", "Leite Integral UHT", "Iogurte Natural", "Molho de Tomate"],
    "Bebidas":    ["Cerveja Pilsen", "Refrigerante Cola 2L", "Suco de Uva Integral", "Água Mineral", "Vinho Tinto"],
    "Farmácia":   ["Vitamina C", "Analgésico Gotas", "Protetor Solar FPS 50", "Soro Fisiológico", "Xarope Infantil"],
    "Cosméticos": ["Shampoo Anticaspa", "Creme Hidratante Corporal", "Desodorante Aerosol", "Sabonete Líquido"],
}


def _validade_aleatoria() -> datetime:
    r = random.random()
    if r < 0.10:     # 10% vencidos
        return datetime.now() - timedelta(days=random.randint(1, 60))
    elif r < 0.25:   # 15% críticos (1-14 dias)
        return datetime.now() + timedelta(days=random.randint(1, 14))
    elif r < 0.45:   # 20% atenção (15-45 dias)
        return datetime.now() + timedelta(days=random.randint(15, 45))
    else:            # 55% seguros (46-365 dias)
        return datetime.now() + timedelta(days=random.randint(46, 365))


def _preco_custo_abc() -> float:
    r = random.random()
    if r < 0.20:     return round(random.uniform(1000, 5000), 2)   # Curva A
    elif r < 0.50:   return round(random.uniform(200, 999), 2)     # Curva B
    else:            return round(random.uniform(10, 199), 2)      # Curva C


def popular_banco(conn) -> None:
    cursor = conn.cursor()

    print("  🧹 Limpando dados antigos...")
    cursor.execute(
        "TRUNCATE fato_vendas, fato_estoque, dim_produtos, dim_clientes, dim_categorias "
        "RESTART IDENTITY CASCADE"
    )

    # 1. Categorias
    print("  📂 Inserindo categorias...")
    cat_ids: dict[str, int] = {}
    for cat in CATEGORIAS:
        cursor.execute("INSERT INTO dim_categorias (nome) VALUES (%s) RETURNING id", (cat,))
        cat_ids[cat] = cursor.fetchone()[0]

    # 2. Produtos (500 SKUs com curva ABC de preços)
    print("  📦 Gerando 500 SKUs...")
    prod_ids: list[int] = []
    for _ in range(500):
        cat = random.choice(list(CATEGORIAS))
        prefixo = random.choice(CATEGORIAS[cat])
        nome = f"{prefixo} {fake.color_name().capitalize()} Mod-{random.randint(100, 999)}"
        custo = _preco_custo_abc()
        cursor.execute(
            "INSERT INTO dim_produtos (nome, categoria_id, preco_custo, preco_venda) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (nome, cat_ids[cat], custo, round(custo * 1.35, 2)),
        )
        prod_ids.append(cursor.fetchone()[0])

    # 3. Clientes (50)
    print("  👥 Gerando 50 clientes...")
    cliente_ids: list[int] = []
    for _ in range(50):
        cursor.execute(
            "INSERT INTO dim_clientes (nome, cidade, estado) VALUES (%s, %s, %s) RETURNING id",
            (fake.name(), fake.city(), fake.state_abbr()),
        )
        cliente_ids.append(cursor.fetchone()[0])

    # 4. Estoque (6.000 lotes com regra de validade)
    print("  🏭 Gerando 6.000 registros de estoque...")
    for _ in range(6000):
        cursor.execute(
            "INSERT INTO fato_estoque (produto_id, quantidade_atual, data_validade) VALUES (%s, %s, %s)",
            (random.choice(prod_ids), random.randint(1, 100), _validade_aleatoria()),
        )

    # 5. Vendas (5.000 transações históricas espalhadas entre 2024 e o momento presente - Apr/2026)
    print("  🛒 Gerando 5.000 vendas (Período 2024 a 2026)...")
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    
    for _ in range(5000):
        p_id = random.choice(prod_ids)
        cursor.execute("SELECT preco_venda FROM dim_produtos WHERE id = %s", (p_id,))
        preco = cursor.fetchone()[0]
        qtd = random.randint(1, 5)
        
        # Gera data aleatória dentro dos 800+ dias (2024-2026)
        data = start_date + timedelta(days=random.randint(0, delta.days))
        
        cursor.execute(
            "INSERT INTO fato_vendas (data_venda, produto_id, cliente_id, quantidade, valor_unitario, valor_total) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (data, p_id, random.choice(cliente_ids), qtd, preco, round(preco * qtd, 2)),
        )

    conn.commit()
    cursor.close()


def main() -> None:
    conn = None
    try:
        conn = psycopg2.connect(settings.database_url)
        print("🚀 Iniciando população do banco de dados...")
        popular_banco(conn)
        print("✅ Banco populado com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
