"""
Motor Generador Vectorizado de Datos Financieros Sintéticos
Enterprise Financial Lakehouse - Generación de Asientos con Partida Doble Estricta
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from chart_of_accounts import (
    ENTITIES,
    COST_CENTERS,
    CHART_OF_ACCOUNTS,
    TRANSACTION_TEMPLATES
)

def get_daily_fx_rates(start_date: datetime, end_date: datetime, seed: int = 42) -> dict:
    """
    Genera curvas realistas de tipo de cambio diario a USD para EUR, COP y VES.
    Convención: fx_multiplier tal que: amount_usd = amount_local * fx_multiplier
    """
    rng = np.random.default_rng(seed)
    num_days = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # 1. EUR: Fluctúa en torno a 1.05 - 1.12 USD por EUR
    eur_walk = 1.08 + np.cumsum(rng.normal(0, 0.002, num_days))
    eur_rates = np.clip(eur_walk, 1.02, 1.15)
    
    # 2. COP: De ~3900 a ~4300 COP por USD -> Multiplicador = 1 / COP_por_USD
    cop_usd_rate = 3950 + np.cumsum(rng.normal(0.5, 8.0, num_days))
    cop_rates = 1.0 / np.clip(cop_usd_rate, 3700, 4600)
    
    # 3. VES: Trayectoria realista 2024-2026 de ~36 VES/USD a ~150+ VES/USD
    # Multiplicador = 1 / VES_por_USD
    t = np.linspace(36.0, 160.0, num_days) + np.cumsum(rng.normal(0.02, 0.15, num_days))
    ves_usd_rate = np.clip(t, 35.0, 200.0)
    ves_rates = 1.0 / ves_usd_rate
    
    fx_dict = {}
    for idx, d in enumerate(dates):
        d_str = d.strftime("%Y-%m-%d")
        fx_dict[d_str] = {
            "USD": 1.0,
            "EUR": float(eur_rates[idx]),
            "COP": float(cop_rates[idx]),
            "VES": float(ves_rates[idx])
        }
    return fx_dict


def generate_synthetic_ledger(
    num_entries: int = 150000,
    start_date_str: str = "2024-01-01",
    end_date_str: str = "2026-08-31",
    seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Genera de forma vectorizada y en lotes un libro diario balanceado de asientos contables.
    Cada asiento contiene 2 líneas (Débito y Crédito) con cuadre exacto.
    """
    start_time = time.time()
    rng = np.random.default_rng(seed)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    total_seconds = int((end_date - start_date).total_seconds())
    
    print(f"[*] Generando curvas de tasas de cambio históricas ({start_date_str} a {end_date_str})...")
    fx_rates = get_daily_fx_rates(start_date, end_date, seed=seed)
    
    # Mapeo rápido de cuentas por código
    coa_dict = {acc["account_code"]: acc for acc in CHART_OF_ACCOUNTS}
    
    # 1. Asignar Entidades
    entity_ids = [e["entity_id"] for e in ENTITIES]
    entity_weights = [e["weight"] for e in ENTITIES]
    entity_currencies = {e["entity_id"]: e["currency"] for e in ENTITIES}
    chosen_entities = rng.choice(entity_ids, size=num_entries, p=entity_weights)
    
    # 2. Asignar Plantillas de Transacción
    template_indices = np.arange(len(TRANSACTION_TEMPLATES))
    template_weights = [t["weight"] for t in TRANSACTION_TEMPLATES]
    chosen_template_idx = rng.choice(template_indices, size=num_entries, p=template_weights)
    
    # 3. Generar Fechas y Timestamps vectorizados
    random_seconds = rng.integers(0, total_seconds, size=num_entries)
    base_ts = start_date.timestamp()
    entry_timestamps = [datetime.fromtimestamp(base_ts + s) for s in random_seconds]
    entry_timestamps.sort()  # Orden cronológico realista
    
    print(f"[*] Construyendo {num_entries:,} asientos contables ({num_entries * 2:,} líneas de diario)...")
    
    # Pre-reservar arrays para máxima velocidad y uso mínimo de RAM
    total_lines = num_entries * 2
    
    arr_entry_id = np.empty(total_lines, dtype=object)
    arr_line_num = np.empty(total_lines, dtype=np.int32)
    arr_entry_date = np.empty(total_lines, dtype=object)
    arr_timestamp = np.empty(total_lines, dtype=object)
    arr_entity_id = np.empty(total_lines, dtype=object)
    arr_cost_center_id = np.empty(total_lines, dtype=object)
    arr_account_code = np.empty(total_lines, dtype=object)
    arr_account_name = np.empty(total_lines, dtype=object)
    arr_financial_statement = np.empty(total_lines, dtype=object)
    arr_financial_class = np.empty(total_lines, dtype=object)
    arr_entry_type = np.empty(total_lines, dtype=object)
    arr_currency_code = np.empty(total_lines, dtype=object)
    arr_amount_local = np.empty(total_lines, dtype=np.float64)
    arr_fx_rate = np.empty(total_lines, dtype=np.float64)
    arr_amount_usd = np.empty(total_lines, dtype=np.float64)
    arr_doc_ref = np.empty(total_lines, dtype=object)
    arr_description = np.empty(total_lines, dtype=object)
    
    for i in range(num_entries):
        ts = entry_timestamps[i]
        d_str = ts.strftime("%Y-%m-%d")
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        entry_code = f"GL-{ts.year}-{i+1:08d}"
        doc_code = f"DOC-{ts.strftime('%y%m')}-{rng.integers(100000, 999999)}"
        
        ent_id = chosen_entities[i]
        curr = entity_currencies[ent_id]
        fx = fx_rates[d_str][curr]
        
        tmpl = TRANSACTION_TEMPLATES[chosen_template_idx[i]]
        cc_id = tmpl["cost_center_id"]
        min_usd, max_usd = tmpl["amount_range_usd"]
        
        # Monto base en USD y conversión a moneda local
        amount_usd_base = round(float(rng.uniform(min_usd, max_usd)), 2)
        amount_local_base = round(amount_usd_base / fx, 2)
        # Recalcular USD con redondeo bancario estricto para cuadratura
        amount_usd_final = round(amount_local_base * fx, 2)
        
        desc = f"{tmpl['description_prefix']} ref: {doc_code}"
        
        line_debit = tmpl["lines"][0]
        line_credit = tmpl["lines"][1]
        
        idx1 = i * 2
        idx2 = idx1 + 1
        
        acc_deb = coa_dict[line_debit["account_code"]]
        acc_cred = coa_dict[line_credit["account_code"]]
        
        # --- LÍNEA 1: DÉBITO ---
        arr_entry_id[idx1] = entry_code
        arr_line_num[idx1] = 1
        arr_entry_date[idx1] = d_str
        arr_timestamp[idx1] = ts_str
        arr_entity_id[idx1] = ent_id
        arr_cost_center_id[idx1] = cc_id
        arr_account_code[idx1] = acc_deb["account_code"]
        arr_account_name[idx1] = acc_deb["account_name"]
        arr_financial_statement[idx1] = acc_deb["statement"]
        arr_financial_class[idx1] = acc_deb["financial_class"]
        arr_entry_type[idx1] = "DEBIT"
        arr_currency_code[idx1] = curr
        arr_amount_local[idx1] = amount_local_base
        arr_fx_rate[idx1] = fx
        arr_amount_usd[idx1] = amount_usd_final
        arr_doc_ref[idx1] = doc_code
        arr_description[idx1] = desc
        
        # --- LÍNEA 2: CRÉDITO ---
        arr_entry_id[idx2] = entry_code
        arr_line_num[idx2] = 2
        arr_entry_date[idx2] = d_str
        arr_timestamp[idx2] = ts_str
        arr_entity_id[idx2] = ent_id
        arr_cost_center_id[idx2] = cc_id
        arr_account_code[idx2] = acc_cred["account_code"]
        arr_account_name[idx2] = acc_cred["account_name"]
        arr_financial_statement[idx2] = acc_cred["statement"]
        arr_financial_class[idx2] = acc_cred["financial_class"]
        arr_entry_type[idx2] = "CREDIT"
        arr_currency_code[idx2] = curr
        arr_amount_local[idx2] = amount_local_base
        arr_fx_rate[idx2] = fx
        arr_amount_usd[idx2] = amount_usd_final
        arr_doc_ref[idx2] = doc_code
        arr_description[idx2] = desc

    print("[*] Empaquetando en DataFrame de Pandas...")
    df_ledger = pd.DataFrame({
        "entry_id": arr_entry_id,
        "line_number": arr_line_num,
        "entry_date": arr_entry_date,
        "timestamp": arr_timestamp,
        "entity_id": arr_entity_id,
        "cost_center_id": arr_cost_center_id,
        "account_code": arr_account_code,
        "account_name": arr_account_name,
        "financial_statement": arr_financial_statement,
        "financial_class": arr_financial_class,
        "entry_type": arr_entry_type,
        "currency_code": arr_currency_code,
        "amount_local": arr_amount_local,
        "exchange_rate_to_usd": arr_fx_rate,
        "amount_usd": arr_amount_usd,
        "document_reference": arr_doc_ref,
        "description": arr_description
    })
    
    df_coa = pd.DataFrame(CHART_OF_ACCOUNTS)
    df_entities = pd.DataFrame(ENTITIES)
    df_cc = pd.DataFrame(COST_CENTERS)
    
    elapsed = time.time() - start_time
    print(f"[OK] Generación completada en {elapsed:.2f} segundos. Total filas generadas: {len(df_ledger):,}")
    return df_ledger, df_coa, df_entities, df_cc


def validate_accounting_integrity(df_ledger: pd.DataFrame) -> bool:
    """
    Ejecuta auditoría matemática estricta de partida doble y consistencia.
    """
    print("\n" + "=" * 60)
    print("        AUDITORÍA DE INTEGRIDAD FINANCIERA Y CONTABLE")
    print("=" * 60)
    
    # 1. Cuadratura global Débitos vs Créditos
    total_debits_usd = df_ledger[df_ledger["entry_type"] == "DEBIT"]["amount_usd"].sum()
    total_credits_usd = df_ledger[df_ledger["entry_type"] == "CREDIT"]["amount_usd"].sum()
    diff_usd = round(total_debits_usd - total_credits_usd, 2)
    
    print(f"Total Débitos (USD):  ${total_debits_usd:,.2f}")
    print(f"Total Créditos (USD): ${total_credits_usd:,.2f}")
    print(f"Diferencia Neta USD:  ${diff_usd:,.2f}")
    
    assert diff_usd == 0.0, f"ERROR CONTABLE: Descuadre en USD de {diff_usd}"
    
    # 2. Verificación por Asiento (Partida Doble Individual)
    piv = df_ledger.pivot_table(
        index="entry_id",
        columns="entry_type",
        values="amount_usd",
        aggfunc="sum",
        fill_value=0.0
    )
    unbalanced = (piv["DEBIT"] - piv["CREDIT"]).abs() > 0.001
    unbalanced_count = int(unbalanced.sum())
    
    print(f"Asientos desbalanceados: {unbalanced_count} de {len(piv):,}")
    assert unbalanced_count == 0, f"Existen {unbalanced_count} asientos desbalanceados!"
    
    # 3. Comprobación de Nulos
    null_counts = df_ledger.isnull().sum().sum()
    print(f"Valores nulos en dataset: {null_counts}")
    assert null_counts == 0, "Existen valores nulos en el dataset!"
    
    # 4. Distribución por Filiales
    print("\nDistribución de transacciones por filial:")
    ent_summary = df_ledger.groupby("entity_id").agg(
        num_lineas=("entry_id", "count"),
        volumen_usd=("amount_usd", "sum")
    )
    for ent_id, row in ent_summary.iterrows():
        print(f"  - {ent_id}: {row['num_lineas']:,} líneas | ${row['volumen_usd']:,.2f} USD")
        
    print("\n[V] AUDITORÍA SATISFACTORIA: Partida doble perfecta al 100%.")
    print("=" * 60 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generador de Dataset Contable Sintético para Enterprise Lakehouse")
    parser.add_argument("--entries", type=int, default=150000, help="Número de asientos contables (cada asiento produce 2 líneas, default 150k -> 300k filas)")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Directorio de destino para los archivos CSV y Parquet")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria para reproducibilidad")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    df_ledger, df_coa, df_entities, df_cc = generate_synthetic_ledger(
        num_entries=args.entries,
        seed=args.seed
    )
    
    validate_accounting_integrity(df_ledger)
    
    # Exportar Catálogos Maestros
    coa_path = os.path.join(args.output_dir, "chart_of_accounts.csv")
    entities_path = os.path.join(args.output_dir, "entities.csv")
    cc_path = os.path.join(args.output_dir, "cost_centers.csv")
    
    df_coa.to_csv(coa_path, index=False)
    df_entities.to_csv(entities_path, index=False)
    df_cc.to_csv(cc_path, index=False)
    print(f"[+] Catálogos exportados a {args.output_dir}:")
    print(f"    - {coa_path}")
    print(f"    - {entities_path}")
    print(f"    - {cc_path}")
    
    # Exportar Libro Diario en CSV y Parquet
    ledger_csv_path = os.path.join(args.output_dir, "general_ledger_entries.csv")
    ledger_parquet_path = os.path.join(args.output_dir, "general_ledger_entries.parquet")
    
    print(f"[*] Guardando {ledger_csv_path} (esto puede tomar unos segundos)...")
    df_ledger.to_csv(ledger_csv_path, index=False)
    
    try:
        print(f"[*] Guardando formato columnar optimizado {ledger_parquet_path}...")
        df_ledger.to_parquet(ledger_parquet_path, index=False, engine="pyarrow", compression="snappy")
        print(f"[OK] Parquet generado con éxito: {os.path.getsize(ledger_parquet_path) / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"[WARN] No se pudo guardar Parquet ({e}), se mantiene CSV.")
        
    print(f"\n[ÉXITO] Paso 1 completado: Datasets listos para ingesta en Lakehouse / Databricks / dbt.")

if __name__ == "__main__":
    main()
