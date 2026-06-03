-- models/prep/prep_eurostat_filtered.sql

{{ config(materialized='table') }}

WITH melted_data AS (
    SELECT * FROM {{ ref('prep_eurostat_melted_long') }}
)
SELECT 
	table_code AS origin_table,
	indicator_code AS indicator,
	country_code,
	ind_type,
	unit,
	"year",
	indicator_value
FROM melted_data
WHERE 
    unit = 'PC_IND'
    AND ind_type NOT LIKE ALL(ARRAY['%DIS%','%CB%','%EMP%','FAM','CC%','HHI%','RETIR%','F_Y16_24','F_Y16_29',
    'F_Y25_54','F_Y25_64','F_Y55_74','F_Y25_34', 'ISCO%', 'M_Y16_24','M_Y16_29', 'M_Y25_34', 'M_Y25_54', 'M_Y25_64',
    'M_Y55_74', 'RF_GE1','RF_GE2', 'SAL%', 'SELF%', 'STUD', 'UNE', 'F_I0_2_75_89', 'F_I3_4_75_89', 'F_I5_8_75_89',
    'M_I0_2_75_89','M_I3_4_75_89', 'M_I5_8_75_89','Y16_17','Y16_24','Y16_29', 'Y25_54', 'Y25_64', 'Y16_24HI',
    'Y16_24LO','Y16_24ME', 'Y25_29', 'Y25_64HI', 'Y25_64LO', 'Y25_64ME', 'Y25_64_RETIROTH', 'Y25_64_SALSELFFAM',
    'Y25_64_UNE', 'Y55_74'])