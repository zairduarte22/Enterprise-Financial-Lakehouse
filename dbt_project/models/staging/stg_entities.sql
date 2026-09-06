{{ config(materialized='view') }}

with source as (
    select * from read_parquet('../data/silver/dimensions/dim_entities.parquet')
),

renamed as (
    select
        trim(entity_id) as entity_id,
        trim(entity_name) as entity_name,
        trim(country) as country,
        trim(currency) as currency
    from source
)

select * from renamed
