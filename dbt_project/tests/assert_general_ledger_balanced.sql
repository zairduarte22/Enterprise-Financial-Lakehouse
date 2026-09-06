-- Test singular de auditoría contable de partida doble en el Data Warehouse
-- Si la diferencia neta entre débitos y créditos en USD es mayor a 0, el test falla.

with totals as (
    select
        round(sum(debit_amount_usd), 2) as total_debits,
        round(sum(credit_amount_usd), 2) as total_credits,
        round(abs(sum(debit_amount_usd) - sum(credit_amount_usd)), 2) as net_diff
    from {{ ref('fct_libro_mayor') }}
)

select *
from totals
where net_diff > 0.01
