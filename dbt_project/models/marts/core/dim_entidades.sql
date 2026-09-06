{{ config(materialized='table') }}

with stg_entities as (
    select * from {{ ref('stg_entities') }}
)

select
    md5(entity_id) as entity_key,
    entity_id,
    entity_name,
    country,
    currency as functional_currency
from stg_entities
