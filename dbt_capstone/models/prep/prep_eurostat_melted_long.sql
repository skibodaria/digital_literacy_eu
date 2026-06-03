-- models/prep/prep_eurostat_melted_long.sql
{{ config(materialized='table') }}

{% set tables = [
    'isoc_ai_iaiu', 'isoc_ai_iaiuxr', 'isoc_cbs', 'isoc_ci_ac_i', 'isoc_ci_hm',
    'isoc_ci_ifp_fu', 'isoc_ci_ifp_iu', 'isoc_ci_in_h', 'isoc_ciegi_ac', 'isoc_ciegi_pb22',
    'isoc_cisci_ip20', 'isoc_cisci_prv20', 'isoc_eid_ieid', 'isoc_iiu_iuprb', 'isoc_iiu_iuxr',
    'isoc_pbo', 'isoc_sk_cskl_i21', 'isoc_sk_dskl_i21', 'isoc_sk_edic_i21', 'isoc_tf',
    'tin00028', 'tin00091', 'tin00092', 'tin00093', 'tin00094', 'tin00095',
    'tin00098', 'tin00099', 'tin00101', 'tin00102', 'tin00103', 'tin00127',
    'tin00129', 'tin00134'
] %}

{% for table in tables %}
SELECT 
    '{{ table }}' AS table_code,
    -- Safely extract columns. If any column is completely missing in a table, it safely defaults to NULL instead of breaking!
    r.j ->> 'indic_is' AS indicator_code,
    r.j ->> 'country' AS country_code,
    r.j ->> 'ind_type' AS ind_type,
    r.j ->> 'unit' AS unit,
    r.j ->> 'freq' AS freq,
    
    -- Dynamically extract whatever year columns exist for this specific table
    CAST(REPLACE(kv.key, 'year_', '') AS INT) AS year,
    
    -- Clean up values (handles text notes like 'b' or 'e' and safely ignores empty ':' chars)
    CASE 
        WHEN kv.value ~ '^[0-9]' THEN CAST(SUBSTRING(kv.value FROM '^[0-9]+(?:\.[0-9]+)?') AS NUMERIC)
        ELSE NULL 
    END AS indicator_value
FROM (
    SELECT to_jsonb(t) AS j 
    FROM {{ source('eurostat_raw', table) }} t
) r,
LATERAL jsonb_each_text(r.j) kv
WHERE kv.key LIKE 'year_%' 
  AND kv.value IS NOT NULL 
  AND kv.value <> ':'

{% if not loop.last %} UNION ALL {% endif %}
{% endfor %}