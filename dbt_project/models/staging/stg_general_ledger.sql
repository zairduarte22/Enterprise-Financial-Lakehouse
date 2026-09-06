{{ config(materialized='view') }}

with source as (
    select * from read_parquet('../data/silver/general_ledger/*/*/*.parquet', hive_partitioning=1)
),

renamed as (
    select
        trim(entry_id) as entry_id,
        cast(line_number as integer) as line_number,
        cast(entry_date as date) as entry_date,
        cast(timestamp as timestamp) as entry_timestamp,
        trim(entity_id) as entity_id,
        trim(cost_center_id) as cost_center_id,
        trim(account_code) as account_code,
        trim(entry_type) as entry_type,
        trim(currency_code) as currency_code,
        round(cast(amount_local as double), 2) as amount_local,
        cast(exchange_rate_to_usd as double) as exchange_rate_to_usd,
        round(cast(amount_usd as double), 2) as amount_usd,
        trim(document_reference) as document_reference,
        trim(description) as description,
        cast(year as integer) as year,
        cast(month as integer) as month
    from source
)

select * from renamed
