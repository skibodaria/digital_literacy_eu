-- models/staging/stg_dig_skills_baseline.sql
{{ config(materialized='table') }}

WITH filtered_data AS (
    SELECT * FROM {{ ref('prep_eurostat_filtered')}}
)
SELECT 
	f.indicator_code,
	m.indicator_name,
	f.indicator_value,
	c.country_code,
	c.country_name,
	c.lat,
	c.lon,
	--f.unit,
	f.ind_type,
	f."year"
	--f.origin_table,
    --f.table_name
FROM filtered_data as f
JOIN {{ source('eurostat_raw', 'countries')}} as c USING(country_code)
JOIN {{ ref('prep_eurostat_map')}} AS m USING(indicator_code)
WHERE
	f.indicator_code IN ('I_DSK2_X',
	'I_DSK2_NA',
	'I_IUAIPR',
	'I_IUAIWP',
	'I_DSK2_BAB',
	'I_DSK2_AB',
	'I_DSK2_IL_BAB',
    'I_IDAY')
	AND f.ind_type = 'IND_TOTAL'