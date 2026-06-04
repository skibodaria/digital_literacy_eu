-- models/prep/prep_eurostat_map.sql
--{{ config(materialized='table') }}

with indicator as (
    select * from {{ source('eurostat', 'eurostat_indicators') }}
),
tab_catalog as (
    select * from {{ source('eurostat', 'eurostat_table_catalog') }}
),
bridge as (
    select * from {{ source('eurostat', 'eurostat_bridge')}}
)
select
    t.table_code,
	t.table_name,
	i.indicator_code,
	i.indicator_name
from bridge as b
join indicator as i
using(indicator_code)
join tab_catalog as t
using(table_code)