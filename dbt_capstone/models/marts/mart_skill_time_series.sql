WITH raw_seed_source AS (
    SELECT
        -- 💡 Switch all raw seed source columns to lowercase
        LOWER(geo) AS raw_country_code,
        CAST(year AS INT) AS reporting_year,  -- ✨ Changed from TIME_PERIOD to time_period
        CAST(value AS NUMERIC) AS indicator_value, -- ✨ Changed from OBS_VALUE to obs_value
        
        ind_type AS demographic_segment_code,
        "Individual type" AS demographic_segment_label, -- Keep quotes if there's a space, but make the first word lowercase if needed
        indic_is AS indicator_code,
        "Information society indicator" AS indicator_label
        
    FROM {{ ref('dig_skills_bab_time_series') }} 
    WHERE value IS NOT NULL
),
country_reference AS (
    SELECT 
        original_country_code,
        clean_country_name,
        plotly_country_code,
        iso_alpha2
    FROM {{ ref('prep_countries') }}
)

SELECT
    c.clean_country_name,
    c.original_country_code,
    c.plotly_country_code,
    s.reporting_year,
    s.indicator_code,
    s.indicator_label,
    s.indicator_value
FROM raw_seed_source s
INNER JOIN country_reference c 
    ON s.raw_country_code = LOWER(c.original_country_code)
ORDER BY 
    c.clean_country_name ASC, 
    s.reporting_year DESC