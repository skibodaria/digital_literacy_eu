-- models/staging/stg_eurobar_2025_metrics.sql
{{ config(materialized='table') }}

SELECT
	eb.country as country_code,
	eb.QA6_1_1 * 100  AS tr_party,
	eb.QA6_5_1 * 100 AS tr_authority,
	eb.QA6_7_1 * 100 AS tr_nat_gov,
	eb.QA6_8_1 * 100 AS tr_nat_par,
	eb.QA6_9_1 * 100 AS tr_eu,
	eb.QA8_1_1 * 100 AS tr_eu_par,
	eb.QE3_1_1 * 100 AS tr_press,
	eb.QE3_5_1 * 100 AS tr_soc_netw_online,
	(eb.QE7_1_1 + eb.QE7_1_2) * 100 AS nat_media_tr_info,
	(eb.QE7_4_1 + eb.QE7_4_2) * 100 AS nat_media_free_pressure,
	(eb.QE6R_2_1 + eb.QE6R_2_2) * 100 AS tr_info_polit_on_soc_net,
	sp.QE9_9_1 * 100 as eff_acc_to_tech,
	(sp.QE1_5_1 + sp.QE1_5_2) * 100 as eff_improve_democr_life,
	(sp.QE1_10_1 + sp.QE1_10_2) * 100 as eff_improve_acc_pub_services,
	(sp.QE1_1_1 + sp.QE1_1_2) * 100 as eff_work_remote
FROM {{ source('eurobars', 'eurobarometer_104_data')}} as eb
JOIN {{ source('eurobars', 'eurobarometer_sp566_data')}} as sp
USING(country)