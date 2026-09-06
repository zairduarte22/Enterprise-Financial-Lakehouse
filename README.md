# Enterprise Financial Lakehouse & Dimensional Warehouse
> **End-to-End Modern Data Stack Pipeline: Medallion Architecture (Bronze, Silver, Gold), PySpark en Databricks, dbt Core 1.12 & Kimball Star Schema sobre DuckDB**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Engine-Apache%20Spark%20%2F%20PySpark-E25A1C.svg)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Format-Delta%20Lake%20%2F%20Parquet-00A4E4.svg)](https://delta.io/)
[![dbt Core](https://img.shields.io/badge/Transformation-dbt%20Core%201.12-FF694B.svg)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB%20OLAP-FFF000.svg)](https://duckdb.org/)
[![Data Quality](https://img.shields.io/badge/Testing-17%2F17%20dbt%20Tests%20PASS-success.svg)](#)

---

## 🏛️ Arquitectura del Sistema (Medallion Architecture)

```text
  [ FUENTES ERP / SISTEMAS TRANSACCIONALES ]
  Transacciones Multimoneda (USD, EUR, COP, VES) + Plan de Cuentas IFRS
                             │
                             ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ 🥉 CAPA BRONZE (Data Lake Raw Storage - S3 / Local Parquet)     │
 │ - Ingesta batch inmutable de 300.000+ líneas contables          │
 │ - Almacenamiento columnar Parquet con compresión Snappy         │
 └─────────────────────────────────────────────────────────────────┘
                             │
                             ▼  [ PySpark en Databricks Community / Delta Lake ]
 ┌─────────────────────────────────────────────────────────────────┐
 │ 🥈 CAPA SILVER (Cleansed & Conformed Lakehouse)                 │
 │ - Esquema validado (Decimal 18,2) y deduplicación compuesta     │
 │ - Conversión cambiaria diaria histórica a moneda base (USD)     │
 │ - Particionamiento Hive por Año y Mes (year=YYYY/month=MM/)     │
 └─────────────────────────────────────────────────────────────────┘
                             │
                             ▼  [ dbt Core 1.12 + Modelado Kimball (Star Schema) ]
 ┌─────────────────────────────────────────────────────────────────┐
 │ 🥇 CAPA GOLD (Data Warehouse Empresarial sobre DuckDB)          │
 │ - Tabla de Hechos Central: fct_libro_mayor (300,000 registros)  │
 │ - Dimensiones Conformes: dim_cuentas_contables, dim_entidades,  │
 │                          dim_centros_costo, dim_calendario      │
 │ - 17 Tests de integridad (cuadre contable Débito == Crédito)    │
 └─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
  [ CONSUMO ANALÍTICO OLAP & BI ]
  Estado de Resultados (P&L) en 29 ms + Dashboards en Power BI
```

---

## 📊 Benchmark de Rendimiento & Auditoría Contable

| Indicador Clave | Métrica Lograda | Impacto de Ingeniería |
|---|---|---|
| **Latencia de Consulta OLAP (P&L)** | **29.52 ms** | Agregación multianual con 2 JOINs sobre 300k filas en DuckDB |
| **Diferencia Neta Débito vs Crédito** | **$0.00 USD** | 100% de partida doble balanceada sobre **$3.99B USD** auditados |
| **Pruebas de Calidad (`dbt test`)** | **17 / 17 PASS** | 0 fallos en unicidad, no-nulidad y reglas contables en 0.90s |
| **Compresión Columnar** | **-86.6%** | Reducción de 77.6 MB (CSV) a 10.4 MB (Parquet Snappy) |
| **Costo de Infraestructura** | **$0.00** | Ejecución local y Databricks Community Edition |

---

## 📂 Estructura del Repositorio

```text
enterprise-financial-lakehouse/
├── data/
│   ├── raw/                           # 🥉 Capa Bronze (Archivos crudos inmutables)
│   │   ├── general_ledger_entries.parquet  # 10.39 MB (Snappy)
│   │   ├── general_ledger_sample.csv       # Muestra de 1,000 filas para previsualización
│   │   ├── chart_of_accounts.csv           # 23 Cuentas IFRS
│   │   ├── entities.csv                    # 4 Filiales (USA, España, Colombia, Venezuela)
│   │   └── cost_centers.csv                # 5 Centros de Costos
│   ├── silver/                        # 🥈 Capa Silver (Particionada por Año/Mes)
│   │   ├── general_ledger/
│   │   │   ├── year=2024/month={1..12}/    # 112,748 registros
│   │   │   ├── year=2025/month={1..12}/    # 112,538 registros
│   │   │   └── year=2026/month={1..8}/     # 74,714 registros
│   │   └── dimensions/
│   │       ├── dim_chart_of_accounts.parquet
│   │       ├── dim_entities.parquet
│   │       └── dim_cost_centers.parquet
│   └── gold/                          # 🥇 Capa Gold (Enterprise Data Warehouse)
│       ├── enterprise_warehouse.duckdb     # Base de datos dimensional OLAP
│       └── gold_executive_pnl.parquet      # Resumen analítico multianual
├── notebooks/
│   ├── 01_silver_cleansing_pyspark.py      # Notebook nativo Databricks
│   └── 01_silver_cleansing_pyspark.ipynb   # Notebook interactivo renderizable en GitHub
├── dbt_project/                       # Proyecto dbt Core 1.12
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/ (stg_general_ledger, stg_chart_of_accounts, stg_entities, stg_cost_centers)
│   │   └── marts/core/
│   │       ├── dim_calendario.sql          # 1,096 días (FY2024–FY2026)
│   │       ├── dim_cuentas_contables.sql   # Jerarquía IFRS y balance normal
│   │       ├── dim_entidades.sql           # Subsidiarias internacionales
│   │       ├── dim_centros_costo.sql       # Imputación operativa y cloud
│   │       ├── fct_libro_mayor.sql         # Fact Table central (300,000 filas)
│   │       └── schema.yml                  # 16 tests genéricos (unique, not_null)
│   └── tests/
│       └── assert_general_ledger_balanced.sql # Test singular contable (Débito == Crédito)
├── src/
│   ├── generator/
│   │   ├── chart_of_accounts.py            # Reglas contables IFRS
│   │   └── generate_ledger.py              # Motor vectorizado con auditoría contable
│   └── pipelines/
│       ├── silver_transform.py             # Pipeline local de Capa Silver
│       └── gold_transform.py               # Runner analítico OLAP DuckDB
├── requirements.txt
└── README.md
```

---

## 🚀 Guía de Ejecución Paso a Paso

### 1. Preparar el Entorno
```bash
git clone https://github.com/zairduarte22/Enterprise-Financial-Lakehouse.git
cd Enterprise-Financial-Lakehouse
pip install -r requirements.txt
```

### 2. Generar Datos Crudos (Capa Bronze)
```bash
python src/generator/generate_ledger.py --entries 150000 --output-dir data/raw
```
* Genera **300.000 líneas contables** con partida doble balanceada en 5 segundos.

### 3. Ejecutar Pipeline de Limpieza & Particionamiento (Capa Silver)
```bash
python src/pipelines/silver_transform.py
```
* Aplica tipado estricto y genera el particionamiento Hive `data/silver/general_ledger/year=YYYY/month=MM/`.
* *Para Databricks*: Importar `notebooks/01_silver_cleansing_pyspark.ipynb` en tu Workspace.

### 4. Compilar Modelos y Pruebas Dimensionales (Capa Gold con dbt)
```bash
cd dbt_project
python -m dbt.cli.main run --profiles-dir .
python -m dbt.cli.main test --profiles-dir .
```
* Materializa las vistas de staging y las tablas del Esquema Estrella en DuckDB.
* Ejecuta **17 pruebas de calidad de datos automáticas**.

### 5. Consultas Analíticas OLAP Instantáneas
```bash
cd ..
python src/pipelines/gold_transform.py
```
* Imprime en consola el Estado de Resultados (P&L) multianual y el rendimiento por filial en menos de **30 milisegundos**.
