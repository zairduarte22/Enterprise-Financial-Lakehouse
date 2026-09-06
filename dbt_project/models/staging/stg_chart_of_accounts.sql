{{ config(materialized='view') }}

with source as (
    select * from read_parquet('../data/silver/dimensions/dim_chart_of_accounts.parquet')
),

renamed as (
    select
        trim(account_code) as account_code,
        trim(account_name) as account_name,
        trim(statement) as statement,
        trim(financial_class) as financial_class,
        trim(subclass) as subclass,
        trim(normal_balance) as normal_balance
    from source
)

select * from renamed
