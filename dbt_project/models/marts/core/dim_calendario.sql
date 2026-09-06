{{ config(materialized='table') }}

with date_spine as (
    select
        cast(range as date) as full_date
    from range(date '2024-01-01', date '2026-12-31' + interval 1 day, interval 1 day)
)

select
    -- Surrogate Key con formato numérico YYYYMMDD para consultas analíticas ultra-rápidas
    cast(strftime(full_date, '%Y%m%d') as integer) as date_key,
    full_date,
    cast(extract(year from full_date) as integer) as year,
    cast(extract(month from full_date) as integer) as month,
    cast(extract(quarter from full_date) as integer) as quarter,
    strftime(full_date, '%B') as month_name,
    strftime(full_date, '%A') as day_name,
    cast(extract(dayofweek from full_date) as integer) as day_of_week,
    case when extract(dayofweek from full_date) in (0, 6) then true else false end as is_weekend,
    -- Periodos fiscales corporativos
    'FY' || cast(extract(year from full_date) as varchar) as fiscal_year,
    'Q' || cast(extract(quarter from full_date) as varchar) || '-' || cast(extract(year from full_date) as varchar) as fiscal_quarter
from date_spine
