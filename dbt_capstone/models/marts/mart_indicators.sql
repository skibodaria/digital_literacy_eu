-- models/marts/mart_indicators.sql
{{ config(materialized='table') }}

WITH 
unified_metadata AS (
    SELECT 
        source_system,
        table_code,
        TRIM(LOWER(indicator_code)) AS indicator_code, 
        indicator_name AS original_indicator_name
    FROM {{ ref('stg_unified_indicators') }}
),

eurostat_clean_titles AS (
    SELECT 
        TRIM(LOWER(indicator_code)) AS indicator_code,
        dynamic_display_title
    FROM {{ ref('indicator_mappings') }}
)

SELECT
    m.source_system,
    m.table_code,
    m.indicator_code,                
    e.dynamic_display_title          
FROM unified_metadata m
LEFT JOIN eurostat_clean_titles e 
    ON m.indicator_code = e.indicator_code
WHERE e.dynamic_display_title IS NOT NULL