-- models/staging/stg_gov_demog_old.sql
{{ config(materialized='table') }}

{% set ind_type_list = [ 
    'F_Y16_74', 'M_Y16_74',               
    'I0_2', 'I3_4', 'I5_8',               
    'IND_DEG1', 'IND_DEG2', 'IND_DEG3',   
    'Y16_19', 'Y20_24', 'Y25_34', 'Y35_44',
    'Y45_54', 'Y55_64', 'Y65_74', 'Y75_MAX'
] %}

-- The data is available for different years (2020-2024) but not 2025, so it's just a legacy model:
{% set indicator_list_old = [
    'I_IGOV12FM', 'I_IGOV12IF', 'I_IIGOVX',  
    'I_IUID1X'
] %}

with filtered_source as (
    select
        country_code,
        indicator_code,
        ind_type,
        indicator_value,
        year,
        row_number() over (
            partition by country_code, indicator_code, ind_type
            order by year desc
        ) as rn
    from {{ ref('prep_eurostat_filtered') }}
    where unit = 'PC_IND'
      and year < 2025 -- filters out the new data to capture the legacy baseline
      and ind_type in (
          {% for demog in ind_type_list %}
          '{{ demog }}'{% if not loop.last %},{% endif %}
          {% endfor %}
      )
      and indicator_code in (
          {% for ind in indicator_list_old %}
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

    {% for ind in indicator_list_old %}
        {% for demog in ind_type_list %}
        , max(case when indicator_code = '{{ ind }}' and ind_type = '{{ demog }}' then indicator_value end) as {{ ind | lower }}_{{ demog | lower }}
        {% endfor %}
    {% endfor %}

from latest_available_records
group by 1


