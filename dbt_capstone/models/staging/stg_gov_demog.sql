-- models/staging/stg_gov_demog.sql

{{ config(materialized='table') }}

-- 1. Declare the demographic categories:
{% set ind_type_list = [ 
    'F_Y16_74', 'M_Y16_74',               
    'I0_2', 'I3_4', 'I5_8',               
    'IND_DEG1', 'IND_DEG2', 'IND_DEG3',   
    'Y16_19', 'Y20_24', 'Y25_34', 'Y35_44',
    'Y45_54', 'Y55_64', 'Y65_74', 'Y75_MAX'
] %}

-- 2. Declare the specific Digital Government Usage indicators
{% set indicator_list = [
    'I_IGOV12FM', 'I_IGOV12IF', 'I_IGOVAPR', 'I_IGOVBE', 'I_IGOVDOC', 
    'I_IGOVRCC', 'I_IGOVSS', 'I_IGOVTAX', 'I_IIGOVX', 'I_IUGOV1', 'I_IUID1X',
    'I_IEID'
] %}

with filtered_source as (
    select
        country_code,
        indicator_code,
        ind_type,
        indicator_value,
        year,
        -- all the data available for 2025!
        row_number() over (
            partition by country_code, indicator_code, ind_type
            order by year desc
        ) as rn
    from {{ ref('prep_eurostat_filtered') }}
    where unit = 'PC_IND'
      -- filters for the demographic categories in the list
      and ind_type in (
          {% for demog in ind_type_list %}
          '{{ demog }}'{% if not loop.last %},{% endif %}
          {% endfor %}
      )
      -- filters only the mentioned metrics
      and indicator_code in (
          {% for ind in indicator_list %}
          '{{ ind }}'{% if not loop.last %},{% endif %}
          {% endfor %}
      )
),

latest_available_records as (
    select
        country_code,
        indicator_code,
        ind_type,
        indicator_value
    from filtered_source
    where rn = 1
)

select
    country_code

    -- nested Jinja Loops: Generates columns named
    {% for ind in indicator_list %}
        {% for demog in ind_type_list %}
        , max(case when indicator_code = '{{ ind }}' and ind_type = '{{ demog }}' then indicator_value end) as {{ ind | lower }}_{{ demog | lower }}
        {% endfor %}
    {% endfor %}

from latest_available_records
group by 1