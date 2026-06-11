-- models/prep/prep_countries.sql
{{ config(materialized='view') }}

WITH raw_countries AS (
    SELECT 
        country_code AS raw_code,
        UPPER(country_code) AS clean_raw_code 
    FROM {{ source('eurostat_raw', 'countries') }}
),

iso_map AS (
    SELECT * FROM {{ ref('country_iso_mapping') }}
)

SELECT
    r.raw_code AS original_country_code,
    COALESCE(m.iso_alpha3, r.clean_raw_code) AS plotly_country_code,
    COALESCE(m.country_name, r.raw_code) AS clean_country_name,
    m.iso_alpha2
FROM raw_countries r
LEFT JOIN iso_map m 
    ON r.clean_raw_code = m.eurostat_code