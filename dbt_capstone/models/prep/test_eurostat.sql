{{ config(materialized='table') }}

with raw_survey as (
    select * from {{ source('raw_data', 'isoc_ai_iaiu') }}
),

indicator_mapping as (
    select * from {{ source('raw_data', 'eurostat_indicators') }}
)

select
    survey.country,
    survey.indic_is as indicator_code,
    mapping.indicator_name,
    survey."2025" as per_users
from raw_survey as survey
left join indicator_mapping as mapping
    on survey.indic_is = mapping.indicator_code