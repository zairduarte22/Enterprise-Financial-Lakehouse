{{ config(materialized='table') }}

with stg_accounts as (
    select * from {{ ref('stg_chart_of_accounts') }}
)

select
    -- Surrogate Key (Hash MD5 de la clave natural de negocio)
    md5(account_code) as account_key,
    account_code,
    account_name,
    statement as financial_statement,
    financial_class,
    subclass,
    normal_balance,
    case
        when normal_balance = 'DEBIT' then 1
        when normal_balance = 'CREDIT' then -1
        else 0
    end as normal_balance_multiplier
from stg_accounts
