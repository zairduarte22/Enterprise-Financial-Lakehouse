{{ config(materialized='view') }}

with source as (
    select * from read_parquet('../data/silver/dimensions/dim_cost_centers.parquet')
),

renamed as (
    select
        trim(cost_center_id) as cost_center_id,
        trim(cost_center_name) as cost_center_name
    from source
)

select * from renamed
