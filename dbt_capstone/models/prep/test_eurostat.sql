{{ config(materialized='table') }}

select *
from {{source('raw_data','isoc_ai_iaiu')}}