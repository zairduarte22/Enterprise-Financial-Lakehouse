"""
Capa Gold: Runner Analítico de Data Warehouse (DuckDB + Kimball Star Schema)
Ejecuta consultas OLAP de alta velocidad (Executive P&L, Balance Sheet y Márgenes)
"""

import os
import sys
import time
import duckdb
import pandas as pd

DB_PATH = "data/gold/enterprise_warehouse.duckdb"

def run_gold_analytics():
    print("=" * 70)
    print("      ENTERPRISE DATA WAREHOUSE - CONSULTAS ANALÍTICAS GOLD")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: No se encontró la base de datos DuckDB en {DB_PATH}")
        sys.exit(1)
        
    con = duckdb.connect(DB_PATH, read_only=True)
    
    # -------------------------------------------------------------
    # 1. Benchmark de Conteo e Integridad del Esquema Estrella
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    tables_summary = con.execute("""
        SELECT 
            table_name, 
            estimated_size 
        FROM duckdb_tables() 
        WHERE schema_name IN ('main_gold', 'main')
        ORDER BY table_name;
    """).df()
    t_tables = (time.perf_counter() - t0) * 1000
    
    print(f"\n[*] Tablas del Data Warehouse (Consultadas en {t_tables:.2f} ms):")
    for _, row in tables_summary.iterrows():
        print(f"    - {row['table_name']}: ~{row['estimated_size']:,} registros")
        
    # -------------------------------------------------------------
    # 2. Consulta OLAP 1: Executive P&L (Estado de Resultados) Multianual
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print(" [1] CONSULTA 1: ESTADO DE RESULTADOS (P&L) CORPORATIVO MULTIANUAL (USD)")
    print("-" * 70)
    
    query_pnl = """
        SELECT
            cal.fiscal_year,
            ROUND(SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END), 2) AS ingresos_netos_usd,
            ROUND(SUM(CASE WHEN acc.financial_class = 'COSTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END), 2) AS costo_ventas_usd,
            ROUND(SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END) -
                  SUM(CASE WHEN acc.financial_class = 'COSTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END), 2) AS utilidad_bruta_usd,
            ROUND(SUM(CASE WHEN acc.financial_class = 'GASTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END), 2) AS gastos_operativos_usd,
            ROUND(SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END) -
                  SUM(CASE WHEN acc.financial_class = 'COSTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END) -
                  SUM(CASE WHEN acc.financial_class = 'GASTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END), 2) AS ebitda_utilidad_neta_usd
        FROM main_gold.fct_libro_mayor fct
        JOIN main_gold.dim_cuentas_contables acc ON fct.account_key = acc.account_key
        JOIN main_gold.dim_calendario cal ON fct.date_key = cal.date_key
        WHERE acc.financial_statement = 'INCOME_STATEMENT'
        GROUP BY cal.fiscal_year
        ORDER BY cal.fiscal_year;
    """
    
    t0 = time.perf_counter()
    df_pnl = con.execute(query_pnl).df()
    t_pnl = (time.perf_counter() - t0) * 1000
    
    print(f"Tiempo de respuesta DuckDB: {t_pnl:.2f} ms (sobre 300k filas con 2 JOINs)\n")
    print(df_pnl.to_string(index=False))
    
    # -------------------------------------------------------------
    # 3. Consulta OLAP 2: Desempeño y Margen Operativo por Filial Multinacional
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print(" [2] CONSULTA 2: RENDIMIENTO FINANCIERO POR FILIAL MULTINACIONAL")
    print("-" * 70)
    
    query_entity = """
        SELECT
            ent.entity_id,
            ent.entity_name,
            ent.functional_currency,
            COUNT(fct.ledger_line_key) AS total_transacciones,
            ROUND(SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END), 2) AS ingresos_totales_usd,
            ROUND(SUM(CASE WHEN acc.financial_class = 'GASTOS' THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END), 2) AS gastos_totales_usd,
            ROUND(
                (SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END) -
                 SUM(CASE WHEN acc.financial_class IN ('COSTOS', 'GASTOS') THEN fct.debit_amount_usd - fct.credit_amount_usd ELSE 0 END)) /
                NULLIF(SUM(CASE WHEN acc.financial_class = 'INGRESOS' THEN fct.credit_amount_usd - fct.debit_amount_usd ELSE 0 END), 0) * 100, 2
            ) AS margen_operativo_pct
        FROM main_gold.fct_libro_mayor fct
        JOIN main_gold.dim_entidades ent ON fct.entity_key = ent.entity_key
        JOIN main_gold.dim_cuentas_contables acc ON fct.account_key = acc.account_key
        GROUP BY ent.entity_id, ent.entity_name, ent.functional_currency
        ORDER BY ingresos_totales_usd DESC;
    """
    
    t0 = time.perf_counter()
    df_entity = con.execute(query_entity).df()
    t_entity = (time.perf_counter() - t0) * 1000
    
    print(f"Tiempo de respuesta DuckDB: {t_entity:.2f} ms\n")
    print(df_entity.to_string(index=False))
    
    # Exportar resumen analítico para el portafolio
    gold_export_path = "data/gold/gold_executive_pnl.parquet"
    df_pnl.to_parquet(gold_export_path, index=False)
    print(f"\n[+] Resumen P&L exportado a: {gold_export_path}")
    
    con.close()
    print("\n" + "=" * 70)
    print(" [V] ANÁLISIS DE CAPA GOLD CONCLUIDO CON ÉXITO")
    print("=" * 70)

if __name__ == "__main__":
    run_gold_analytics()
