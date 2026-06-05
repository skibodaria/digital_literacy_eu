-- models/staging/mart_eu_baseline.sql
{{ config(materialized='table') }}

SELECT *
FROM {{ ref ('stg_eurobar_2025_metrics')}}
JOIN {{ ref ('stg_eurostat_baseline')}}
USING(country_code)