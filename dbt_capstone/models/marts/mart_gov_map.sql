-- models/marts/mart_gov_map.sql
{{ config(materialized='table') }}

WITH base_indicators AS (
    SELECT 
        source_system,
        table_code,
        indicator_code,    
        dynamic_display_title AS base_title 
    FROM {{ ref('mart_indicators') }}
    WHERE indicator_code IN (
        'i_ieid', 'i_igovapr', 'i_igovbe', 'i_igovrcc', 
        'i_iugov1', 'i_igovtax2', 'i_igovrx', 'i_ireidna',
        'i_ireidno', 'i_ireidsec', 'i_ireidtec', 'i_ireidnn', 
        'i_ireiddev', 'i_ireidoth'
    )
),
demographics AS (
    SELECT 
        TRIM(LOWER(demog_key)) AS demog_key,
        demog_title
    FROM {{ ref('demog_mapping') }}
    WHERE TRIM(LOWER(demog_key)) IN (
        'f_y16_74', 'm_y16_74',               
        'i0_2', 'i3_4', 'i5_8',               
        'ind_deg1', 'ind_deg2', 'ind_deg3',   
        'y16_19', 'y20_24', 'y25_34', 'y35_44',
        'y45_54', 'y55_64', 'y65_74'
    )
)
SELECT
    i.source_system,
    i.table_code,
    i.indicator_code || '_' || d.demog_key AS final_column_name,
    i.base_title || ' - ' || d.demog_title AS dynamic_display_title
FROM base_indicators i
CROSS JOIN demographics d