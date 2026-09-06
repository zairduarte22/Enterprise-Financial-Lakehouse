"""
Pipeline de Transformación Capa Silver (Cleansed & Conformed Lakehouse)
Aplica tipado estricto, deduplicación, enriquecimiento temporal y particionamiento por Año/Mes.
"""

import os
import sys
import time
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

def run_silver_pipeline(
    raw_dir: str = "data/raw",
    silver_dir: str = "data/silver"
) -> bool:
    start_time = time.time()
    print("=" * 65)
    print("     INICIANDO PIPELINE DE CAPA SILVER (CLEANSED & CONFORMED)")
    print("=" * 65)
    
    os.makedirs(silver_dir, exist_ok=True)
    dim_out_dir = os.path.join(silver_dir, "dimensions")
    os.makedirs(dim_out_dir, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. Transformación de Catálogos Maestros (Dimensiones Silver)
    # -------------------------------------------------------------
    print("\n[*] 1/4 Procesando y estandarizando dimensiones maestras...")
    
    # 1.1 Chart of Accounts
    coa_raw = os.path.join(raw_dir, "chart_of_accounts.csv")
    df_coa = pd.read_csv(coa_raw)
    df_coa["account_code"] = df_coa["account_code"].astype(str).str.strip()
    df_coa["account_name"] = df_coa["account_name"].astype(str).str.strip()
    df_coa["statement"] = df_coa["statement"].astype(str).str.upper()
    df_coa["financial_class"] = df_coa["financial_class"].astype(str).str.upper()
    df_coa["subclass"] = df_coa["subclass"].astype(str).str.upper()
    df_coa["normal_balance"] = df_coa["normal_balance"].astype(str).str.upper()
    
    coa_silver_path = os.path.join(dim_out_dir, "dim_chart_of_accounts.parquet")
    df_coa.to_parquet(coa_silver_path, index=False, engine="pyarrow")
    print(f"    [+] {len(df_coa)} cuentas guardadas en {coa_silver_path}")
    
    # 1.2 Entities
    entities_raw = os.path.join(raw_dir, "entities.csv")
    df_entities = pd.read_csv(entities_raw)
    df_entities["entity_id"] = df_entities["entity_id"].astype(str).str.strip()
    df_entities["entity_name"] = df_entities["entity_name"].astype(str).str.strip()
    df_entities["country"] = df_entities["country"].astype(str).str.strip()
    df_entities["currency"] = df_entities["currency"].astype(str).str.strip().str.upper()
    
    entities_silver_path = os.path.join(dim_out_dir, "dim_entities.parquet")
    df_entities.to_parquet(entities_silver_path, index=False, engine="pyarrow")
    print(f"    [+] {len(df_entities)} entidades guardadas en {entities_silver_path}")
    
    # 1.3 Cost Centers
    cc_raw = os.path.join(raw_dir, "cost_centers.csv")
    df_cc = pd.read_csv(cc_raw)
    df_cc["cost_center_id"] = df_cc["cost_center_id"].astype(str).str.strip()
    df_cc["cost_center_name"] = df_cc["cost_center_name"].astype(str).str.strip()
    
    cc_silver_path = os.path.join(dim_out_dir, "dim_cost_centers.parquet")
    df_cc.to_parquet(cc_silver_path, index=False, engine="pyarrow")
    print(f"    [+] {len(df_cc)} centros de costo guardados en {cc_silver_path}")
    
    # -------------------------------------------------------------
    # 2. Ingesta y Limpieza del Libro Diario (General Ledger)
    # -------------------------------------------------------------
    print("\n[*] 2/4 Ingestando General Ledger crudo desde formato columnar...")
    gl_raw_path = os.path.join(raw_dir, "general_ledger_entries.parquet")
    df_gl = pd.read_parquet(gl_raw_path, engine="pyarrow")
    initial_rows = len(df_gl)
    print(f"    Registros crudos cargados: {initial_rows:,}")
    
    # 2.1 Deduplicación por clave primaria compuesta
    print("[*] Aplicando deduplicación por (entry_id, line_number)...")
    df_gl = df_gl.drop_duplicates(subset=["entry_id", "line_number"], keep="last")
    post_dedup_rows = len(df_gl)
    print(f"    Registros tras deduplicación: {post_dedup_rows:,} (duplicados eliminados: {initial_rows - post_dedup_rows})")
    
    # -------------------------------------------------------------
    # 3. Tipado Estricto y Enriquecimiento Temporal
    # -------------------------------------------------------------
    print("\n[*] 3/4 Aplicando tipado estricto y derivando columnas analíticas...")
    df_gl["entry_date"] = pd.to_datetime(df_gl["entry_date"])
    df_gl["timestamp"] = pd.to_datetime(df_gl["timestamp"])
    
    # Derivadas temporales para particionamiento y analítica
    df_gl["year"] = df_gl["entry_date"].dt.year.astype(int)
    df_gl["month"] = df_gl["entry_date"].dt.month.astype(int)
    df_gl["quarter"] = df_gl["entry_date"].dt.quarter.astype(int)
    df_gl["day_name"] = df_gl["entry_date"].dt.day_name()
    df_gl["is_weekend"] = df_gl["entry_date"].dt.dayofweek >= 5
    
    # Tipado numérico y estandarización de strings
    df_gl["amount_local"] = df_gl["amount_local"].round(2).astype(float)
    df_gl["exchange_rate_to_usd"] = df_gl["exchange_rate_to_usd"].astype(float)
    df_gl["amount_usd"] = df_gl["amount_usd"].round(2).astype(float)
    
    df_gl["entry_id"] = df_gl["entry_id"].astype(str).str.strip()
    df_gl["line_number"] = df_gl["line_number"].astype(int)
    df_gl["entity_id"] = df_gl["entity_id"].astype(str).str.strip()
    df_gl["cost_center_id"] = df_gl["cost_center_id"].astype(str).str.strip()
    df_gl["account_code"] = df_gl["account_code"].astype(str).str.strip()
    df_gl["entry_type"] = df_gl["entry_type"].astype(str).str.upper().str.strip()
    df_gl["currency_code"] = df_gl["currency_code"].astype(str).str.upper().str.strip()
    
    # -------------------------------------------------------------
    # 4. Particionamiento Físico y Escritura Columnar
    # -------------------------------------------------------------
    gl_silver_dir = os.path.join(silver_dir, "general_ledger")
    print(f"\n[*] 4/4 Escribiendo dataset columnar particionado en {gl_silver_dir}...")
    print("    Estrategia de particionamiento: year / month")
    
    # Convertir a tabla PyArrow para escritura particionada de alto rendimiento
    table = pa.Table.from_pandas(df_gl, preserve_index=False)
    
    ds.write_dataset(
        data=table,
        base_dir=gl_silver_dir,
        format="parquet",
        partitioning=["year", "month"],
        partitioning_flavor="hive",
        existing_data_behavior="overwrite_or_ignore"
    )
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f" [V] PIPELINE SILVER COMPLETADO CON ÉXITO EN {elapsed:.2f} SEGUNDOS")
    print("=" * 65)
    print(f"Total filas procesadas en Silver: {len(df_gl):,}")
    print(f"Particiones generadas: {df_gl['year'].nunique()} años ({sorted(df_gl['year'].unique())})")
    
    # Mostrar resumen de particiones
    part_counts = df_gl.groupby(["year", "quarter"]).size()
    print("\nResumen de volumen por Año y Trimestre:")
    for (yr, qtr), count in part_counts.items():
        print(f"  - Año {yr} Q{qtr}: {count:,} líneas")
        
    return True

if __name__ == "__main__":
    raw_directory = "data/raw"
    silver_directory = "data/silver"
    run_silver_pipeline(raw_directory, silver_directory)
