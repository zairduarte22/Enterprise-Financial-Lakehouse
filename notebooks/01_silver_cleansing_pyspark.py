# Databricks notebook source
# MAGIC %md
# MAGIC # 🥈 Enterprise Financial Lakehouse: Capa Silver con PySpark & Delta Lake
# MAGIC 
# MAGIC ### Arquitectura Medallion (Cleansed & Conformed Layer)
# MAGIC Este notebook implementa la transformación de ingeniería de datos a escala para transacciones financieras multinacionales:
# MAGIC 1. **Ingesta desde Capa Bronze**: Lectura de datasets Parquet / Delta crudos.
# MAGIC 2. **Validación de Esquema y Tipado Fuerte**: Aplicación de tipos estrictos (`DecimalType`, `TimestampType`, `StringType`).
# MAGIC 3. **Deduplicación por Clave Compuesta**: Eliminación de duplicados en `(entry_id, line_number)`.
# MAGIC 4. **Enriquecimiento Temporal & Reglas Financieras**: Derivación de particiones `year`, `month`, `quarter`, y control de balances.
# MAGIC 5. **Persistencia en Delta Lake**: Particionamiento físico optimizado (`partitionBy("year", "month")`) y registro en el metastore/Unity Catalog.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuración del Entorno Spark y Dependencias

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    DoubleType, TimestampType, DateType, DecimalType
)
from pyspark.sql.functions import (
    col, to_date, to_timestamp, year, month, quarter, 
    dayofweek, date_format, when, round as spark_round,
    count, sum as spark_sum, abs as spark_abs, max as spark_max
)

# En Databricks, spark y display() vienen pre-inicializados.
# Definimos fallback para compatibilidad con linters locales de Python / IDEs:
try:
    display  # type: ignore
except NameError:
    def display(df):
        df.show()

spark = SparkSession.builder \
    .appName("EnterpriseFinancialLakehouse-Silver") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

print(f"Spark Version: {spark.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Definición del Esquema Estricto e Ingesta desde Capa Bronze

# COMMAND ----------

# Definición formal del esquema para prevenir schema drift en la ingesta
bronze_schema = StructType([
    StructField("entry_id", StringType(), False),
    StructField("line_number", IntegerType(), False),
    StructField("entry_date", StringType(), False),
    StructField("timestamp", StringType(), False),
    StructField("entity_id", StringType(), False),
    StructField("cost_center_id", StringType(), False),
    StructField("account_code", StringType(), False),
    StructField("account_name", StringType(), False),
    StructField("financial_statement", StringType(), False),
    StructField("financial_class", StringType(), False),
    StructField("entry_type", StringType(), False),
    StructField("currency_code", StringType(), False),
    StructField("amount_local", DoubleType(), False),
    StructField("exchange_rate_to_usd", DoubleType(), False),
    StructField("amount_usd", DoubleType(), False),
    StructField("document_reference", StringType(), False),
    StructField("description", StringType(), True)
])

# Ruta de almacenamiento (DBFS / S3 / ADLS / Local)
BRONZE_PATH = "/mnt/datalake/bronze/general_ledger_entries.parquet"
# Para pruebas locales o rutas relativas:
# BRONZE_PATH = "data/raw/general_ledger_entries.parquet"

df_bronze = spark.read.schema(bronze_schema).parquet(BRONZE_PATH)
raw_count = df_bronze.count()
print(f"Total registros leídos en Capa Bronze: {raw_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Deduplicación por Clave Primaria Compuesta `(entry_id, line_number)`

# COMMAND ----------

df_dedup = df_bronze.dropDuplicates(["entry_id", "line_number"])
dedup_count = df_dedup.count()
print(f"Registros tras deduplicación: {dedup_count:,} (Duplicados descartados: {raw_count - dedup_count})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Tipado Estricto y Enriquecimiento de Atributos Temporales

# COMMAND ----------

df_silver = df_dedup \
    .withColumn("entry_date", to_date(col("entry_date"), "yyyy-MM-dd")) \
    .withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("amount_local", col("amount_local").cast(DecimalType(18, 2))) \
    .withColumn("exchange_rate_to_usd", col("exchange_rate_to_usd").cast(DecimalType(18, 6))) \
    .withColumn("amount_usd", col("amount_usd").cast(DecimalType(18, 2))) \
    .withColumn("year", year(col("entry_date"))) \
    .withColumn("month", month(col("entry_date"))) \
    .withColumn("quarter", quarter(col("entry_date"))) \
    .withColumn("day_name", date_format(col("entry_date"), "EEEE")) \
    .withColumn("is_weekend", when(dayofweek(col("entry_date")).isin(1, 7), True).otherwise(False))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Control de Calidad y Auditoría de Balance Contable en Spark

# COMMAND ----------

# Validación de cuadre contable Débito vs Crédito en PySpark
balance_audit = df_silver.groupBy("entry_type").agg(
    spark_sum("amount_usd").alias("total_usd"),
    count("entry_id").alias("total_lines")
)
display(balance_audit)

# Validación por asiento (partida doble estricta)
unbalanced_entries = df_silver.groupBy("entry_id").agg(
    spark_sum(when(col("entry_type") == "DEBIT", col("amount_usd")).otherwise(0)).alias("debit_sum"),
    spark_sum(when(col("entry_type") == "CREDIT", col("amount_usd")).otherwise(0)).alias("credit_sum")
).filter(spark_abs(col("debit_sum") - col("credit_sum")) > 0.01)

unbalanced_count = unbalanced_entries.count()
print(f"Asientos desbalanceados detectados: {unbalanced_count}")
assert unbalanced_count == 0, "Alerta: Se detectaron asientos desbalanceados en Silver!"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Persistencia en Formato Delta Lake con Particionamiento Columnar

# COMMAND ----------

SILVER_DELTA_PATH = "/mnt/datalake/silver/general_ledger"

# Escritura optimizada con particionamiento por Año y Mes
df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .option("overwriteSchema", "true") \
    .save(SILVER_DELTA_PATH)

# Registrar como tabla administrada en Unity Catalog / Hive Metastore
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS silver_general_ledger
    USING DELTA
    LOCATION '{SILVER_DELTA_PATH}'
""")

print(" Pipeline de Capa Silver completado con éxito y registrado en Delta Lake.")
