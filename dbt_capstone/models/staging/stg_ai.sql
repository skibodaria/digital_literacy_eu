-- models/staging/stg_ai.sql
{{ config(materialized='table') }}

-- declare the demographic categories:
{% set ind_type_list = [ 
    'F_Y16_74', 'M_Y16_74',               
    'I0_2', 'I3_4', 'I5_8',               
    'IND_DEG1', 'IND_DEG2', 'IND_DEG3',   
    'Y16_19', 'Y20_24', 'Y25_34', 'Y35_44',
    'Y45_54', 'Y55_64', 'Y65_74'
] %}

-- AI Usage Metrics:
{% set indicator_list_new = [
    'I_IUAI','I_IUAIFE', 'I_IUAIPR','I_IUAIWP'
] %}

with filtered_source as (
    select
        country_code,
        indicator_code,
        ind_type,
        indicator_value,
        unit
    from {{ ref('prep_eurostat_filtered') }}
    where
      -- filters for the demographic categories in the list
      ind_type in (
          {% for demog in ind_type_list %}
          '{{ demog }}'{% if not loop.last %},{% endif %}
          {% endfor %}
      )
      -- filters only the mentioned metrics
      and indicator_code in (
          {% for ind in indicator_list_new %}
          '{{ ind }}'{% if not loop.last %},{% endif %}
          {% endfor %}
      )
      -- 👇 Filters strictly for percentages of individuals
      and unit = 'PC_IND'
),

latest_available_records as (
    select
        country_code,
        indicator_code,
        ind_type,
        indicator_value
    from filtered_source
),

pivoted_data as (
    select
        country_code
        -- nested Jinja Loops: Generates columns named
        {% for ind in indicator_list_new %}
            {% for demog in ind_type_list %}
            , max(case when indicator_code = '{{ ind }}' and ind_type = '{{ demog }}' then indicator_value end) as {{ ind | lower }}_{{ demog | lower }}
            {% endfor %}
        {% endfor %}

    from latest_available_records
    group by 1
)

-- --- THE DEFINITIVE POSTGRES JOIN FIX ---
select
    c.clean_country_name,         
    c.plotly_country_code,        
    p.*
from pivoted_data p
left join {{ ref('prep_countries') }} c
    on p.country_code = c.original_country_code -- Matches your table schema exactly!