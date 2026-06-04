-- models/staging/stg_eurostat_baseline.sql

{{ config(materialized='table') }}

with filtered_source as (
    select
        country_code,
        indicator_code,
        indicator_value,
        year,
        row_number() over (
            partition by country_code, indicator_code
            order by year desc
        ) as rn
    from {{ ref('prep_eurostat_filtered') }}
    where unit = 'PC_IND'
      and ind_type = 'IND_TOTAL'
),

latest_available_records as (
    select
        country_code,
        indicator_code,
        indicator_value,
        year as source_year
    from filtered_source
    where rn = 1
)

-- 1. PASTE YOUR 34 CODES INSIDE THIS LIST (Replace my examples below)
{% set indicator_list = [
    'I_DSK2_AB','I_DSK2_B','I_DSK2_IL_AB','I_DSK2_IL_B','I_DSK2_LM','I_DSK2_LW','I_DSK2_N', 'I_DSK2_NA',
    'I_DSK2_SF_AB','I_DSK2_SF_B','I_DSK2_X','I_IDAY','I_IEID','I_IGOVAPR','I_IGOVTAX2','I_IMT12',
    'I_IREIDNO','I_IU3','I_IUAI','I_IUEM','I_IUEVR','I_IUGOV1','I_IUPOL2','I_IUX','I_MAPS','I_TIC',
    'I_UDI'

] %}

select
    country_code
    -- 2. The loop dynamically generates the value columns
    {% for ind in indicator_list %}
    , max(case when indicator_code = '{{ ind }}' then indicator_value end) as {{ ind | lower }}_value
    {% endfor %}

    -- 3. The loop dynamically generates the source year columns
    {% for ind in indicator_list %}
    , max(case when indicator_code = '{{ ind }}' then source_year end) as {{ ind | lower }}_source_year
    {% endfor %}

from latest_available_records
group by 1