-- models/mart/mart_indicators.sql
{{ config(materialized='table') }}


WITH unified_metadata AS (
    SELECT * FROM {{ ref('stg_eu_indicators_map') }}
),

display_title_mapping (indicator_code, dynamic_display_title) AS (
    VALUES
        -- Eurostat Metrics
        ('I_DSK2_AB', 'High Digital Skills (% of individuals)'),
        ('I_DSK2_B', 'Basic Digital Skills (% of individuals)'),
        ('I_IDAY', 'Daily Internet Usage (% of individuals)'),
        
        
        -- Eurobarometer Combined Metrics
        ('QE7_1_1', 'Trust in the European Parliament (Combined)'),
        ('QE7_4_1', 'Trust in National Government (Combined)'),
        ('QE6R_2_1', 'Institutional Transparency Perception')
        
        -- You can keep adding lines here manually as needed!
)

SELECT 
    meta.indicator_code,
    -- Fallback to the original name if you forgot to map a title manually
    COALESCE(map.dynamic_display_title, meta.indicator_name) AS dynamic_display_title,
    meta.indicator_name AS original_technical_name,
    meta.table_code,
    meta.source_system
FROM unified_metadata meta
LEFT JOIN display_title_mapping map 
    ON meta.indicator_code = map.indicator_code