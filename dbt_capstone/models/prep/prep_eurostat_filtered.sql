-- models/prep/prep_eurostat_filtered.sql

{{ config(materialized='table') }}

WITH melted_data AS (
    SELECT * FROM {{ ref('prep_eurostat_melted_long') }}
)
SELECT 
	table_code AS origin_table,
	indicator_code,
	country_code,
	ind_type,
	unit,
	"year",
	indicator_value
FROM melted_data
WHERE 
    ind_type NOT LIKE ALL(ARRAY[
        '%DIS%','%CB%','%EMP%','FAM','CC%','HHI%','RETIR%','F_Y16_24','F_Y16_29',
        'F_Y25_54','F_Y25_64','F_Y55_74','F_Y25_34', 'ISCO%', 'M_Y16_24','M_Y16_29', 'M_Y25_34', 
        'M_Y25_54', 'M_Y25_64','M_Y55_74', 'RF_GE1','RF_GE2', 'SAL%', 'SELF%', 'STUD', 'UNE', 
        'F_I0_2_75_89', 'F_I3_4_75_89', 'F_I5_8_75_89','M_I0_2_75_89','M_I3_4_75_89', 'M_I5_8_75_89',
        'Y16_17','Y16_24','Y16_29', 'Y25_54', 'Y25_64', 'Y16_24HI','Y16_24LO','Y16_24ME', 'Y25_29', 
        'Y25_64HI', 'Y25_64LO', 'Y25_64ME', 'Y25_64_RETIROTH', 'Y25_64_SALSELFFAM','Y25_64_UNE', 'Y55_74'])
    AND indicator_code NOT LIKE ALL(ARRAY[
        'I_CCONF1','I_CEPVA1','I_CINSAPP1','I_CPRES2','I_CPRG2','I_CWRD1','I_CXFER1','I_CXLS1','I_CXLSADV1',
        'I_DSK2_CC_AB', 'I_DSK2_CC_B', 'I_DSK2_CC_BAB', 'I_DSK2_DCC_AB', 'I_DSK2_DCC_B', 'I_DSK2_DCC_BAB',
        'I_DSK2_PS_AB', 'I_DSK2_PS_B', 'I_DSK2_PS_BAB', 'I_HM','I_HMA', 'I_HMD','I_HMOTH', 'I_HMPS', 'I_HMRB',
        'I_HMRE', 'I_HMSE', 'I_HMSO','I_I3_12', 'I_IEIDBS','I_IEIDBSNE', 'I_IEIDEC', 'I_IEIDECNE', 'I_IEIDOC',
        'I_IHIF', 'I_IHIFMH','I_IHIFPH', 'I_ILT12','I_ILTWK', 'I_IUBK','I_IUIF','I_IUIFSP', 'I_IUJOB','I_IUMT12',
        'I_IUNW1','I_IUOANY', 'I_IUOCIS1','I_IUOLANY','I_IUOLC','I_IUOLM','I_IUPH1','I_IUPHCHAT1', 'I_IUPSFIX', 
        'I_IUPSNO','I_IUPSOTH','I_IUPSSE','I_IUSE','I_IUSELL','I_IWK', 'I_MAPS_3','I_MAPS_5', 'I_MAPS_APD',
        'I_MAPS_CWSC','I_MAPS_LAP','I_MAPS_RAAD','I_MAPS_RPS','I_MAPS_RRGL','I_PCOOK1','I_USLCOOK', 'I_DSK2_BAB',
        'I_DSK2_IC_S', 'I_DSK2_IL_BAB','I_DSK2_SF_BAB'
    ])
    AND country_code IN (
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 
        'ES', 'FI', 'FR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 
        'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
    )