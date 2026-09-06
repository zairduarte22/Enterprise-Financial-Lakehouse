{{ config(materialized='table') }}

with stg_cc as (
    select * from {{ ref('stg_cost_centers') }}
)

select
    md5(cost_center_id) as cost_center_key,
    cost_center_id,
    cost_center_name
from stg_cc
