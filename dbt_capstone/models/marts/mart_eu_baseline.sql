-- models/mart/mart_eu_baseline.sql
{{ config(materialized='table') }}

WITH joined_data AS (
    SELECT *
    FROM {{ ref('stg_eurobar_2025_metrics') }}
    JOIN {{ ref('stg_eurostat_baseline') }} USING (country_code)
    JOIN {{ ref('prep_countries') }} ON country_code = original_country_code
)

SELECT
    country_code,
    i_dsk2_ab, 
    i_dsk2_b,
    i_dsk2_lw,
    i_dsk2_n,
    i_dsk2_lm, 
    i_dsk2_x,
    i_iday,
    i_ieid,
    i_igovapr,
    i_igovtax2,
    i_iuai,
    i_iugov1, 
    i_iupol2,
    i_iux,
    i_maps,
    i_tic,
    i_udi,
    i_ireidno,
    i_dsk2_bab,
    
    -- all Eurobarometer but not a country code
    tr_party, tr_authority, tr_nat_gov,
    tr_nat_par, tr_eu, tr_eu_par, tr_press, tr_soc_netw_online,
    nat_media_tr_info, nat_media_free_pressure,
    tr_info_polit_on_soc_net, eff_acc_to_tech,
    eff_improve_democr_life, eff_improve_acc_pub_services, eff_work_remote,

    -- country data
    plotly_country_code,
    clean_country_name

FROM joined_data