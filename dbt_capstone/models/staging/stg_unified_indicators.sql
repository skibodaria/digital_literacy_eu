-- models/staging/stg_unified_indicators.sql
{{ config(materialized='ephemeral') }}

WITH 
-- 1/ Eurostat Metadata Map
-- remove prep_eurostat_map
eurostat_map AS (
    SELECT
        'Eurostat' AS source_system,
        t.table_code,
        t.table_name,
        i.indicator_code,
        i.indicator_name
    FROM {{ source('eurostat', 'eurostat_bridge') }} as b
    JOIN {{ source('eurostat', 'eurostat_indicators') }} as i USING (indicator_code)
    JOIN {{ source('eurostat', 'eurostat_table_catalog') }} as t USING (table_code)
),

-- 2/ Eurobarometer Special Map (sp566)
eurobar_sp566_map AS (
    SELECT
        'Eurobarometer Special' AS source_system,
        'sp566_' || LOWER(sheet) AS table_code, 
        'Eurobarometer Special ' || sheet AS table_name, -- Generates a clean table name dynamically
        answer_id AS indicator_code,
        CASE
            WHEN answer_id IN ('QE1_5_1', 'QE1_5_2') THEN 'combined' || question_english || '_' || answer_text || '_fairly important'
            WHEN answer_id IN ('QE1_10_1', 'QE1_10_2') THEN 'combined' || question_english || '_' || answer_text || '_fairly_important'
            WHEN answer_id IN ('QE1_1_1', 'QE1_1_2') THEN 'combined' || question_english || '_' || answer_text || 'fairly_important'
            ELSE question_english || '_' || answer_text
        END AS indicator_name
    FROM {{ source('eurobars', 'eurobarometer_sp566_map') }} -- Kept as source macro for dbt best practices
    WHERE answer_id IN ('QE9_9_1', 'QE1_5_1', 'QE1_10_1', 'QE1_1_1')
),

-- 3/ Eurobarometer Standard Map (104)
eurobar_104_map AS (
    SELECT
        'Eurobarometer Standard' AS source_system,
        'eb104_' || LOWER(sheet) AS table_code,
        'Eurobarometer Standard ' || sheet AS table_name,
        answer_id AS indicator_code,
        CASE
            WHEN answer_id IN ('QE7_1_1', 'QE7_1_2') THEN 'combined_' || question_english || '_' || answer_text
            WHEN answer_id IN ('QE7_4_1', 'QE7_4_2') THEN 'combined_' || question_english || '_' || answer_text
            WHEN answer_id IN ('QE6R_2_1', 'QE6R_2_2') THEN 'combined_' || question_english || '_' || answer_text
            ELSE question_english || '_' || answer_text
        END AS indicator_name
    FROM {{ source('eurobars', 'eurobarometer_104_map') }}
    WHERE answer_id IN (
        'QA6_1_1', 'QA6_5_1', 'QA6_7_1', 'QA6_8_1', 'QA6_9_1', 
        'QA8_1_1', 'QE3_1_1', 'QE3_5_1', 'QE7_1_1', 'QE7_4_1', 'QE6R_2_1'
    )
)

-- 4/ combine everything into one data-map:
SELECT * FROM eurostat_map
UNION ALL
SELECT * FROM eurobar_sp566_map
UNION ALL
SELECT * FROM eurobar_104_map