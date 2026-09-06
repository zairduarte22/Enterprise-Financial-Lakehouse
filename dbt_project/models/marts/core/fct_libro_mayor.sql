{{ config(materialized='table') }}

with stg_gl as (
    select * from {{ ref('stg_general_ledger') }}
)

select
    -- Primary Key de la tabla de hechos
    md5(entry_id || '-' || cast(line_number as varchar)) as ledger_line_key,
    
    -- Claves Foráneas hacia el Esquema Estrella (Surrogate Keys)
    cast(strftime(entry_date, '%Y%m%d') as integer) as date_key,
    md5(account_code) as account_key,
    md5(entity_id) as entity_key,
    md5(cost_center_id) as cost_center_key,
    
    -- Dimensiones Degeneradas y Atributos de Auditoría
    entry_id,
    line_number,
    entry_date,
    entry_timestamp,
    document_reference,
    entry_type,
    currency_code,
    description,
    
    -- Métricas y Hechos Numéricos Aditivos
    amount_local,
    exchange_rate_to_usd,
    amount_usd,
    
    -- Columnas calculadas para agregaciones contables instantáneas (P&L y Balance)
    case when entry_type = 'DEBIT' then amount_usd else 0.0 end as debit_amount_usd,
    case when entry_type = 'CREDIT' then amount_usd else 0.0 end as credit_amount_usd,
    case when entry_type = 'DEBIT' then amount_usd else -amount_usd end as net_debit_credit_usd
from stg_gl
