-- models/mart/mart_eu_baseline.sql
{{ config(materialized='table') }}

SELECT *
FROM {{ ref ('stg_eurobar_2025_metrics')}}
JOIN {{ ref ('stg_eurostat_baseline')}}
USING(country_code)
JOIN {{ source ('eurostat_raw', 'countries')}}
USING(country_code)
