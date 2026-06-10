-- models/staging/stg_alias_indicators.sql
-- {{ config(materialized='table') }}

WITH unified_metadata AS (
    SELECT * FROM {{ ref ('prep_merge_indicators')}}
), 

display_title_mapping (indicator_code, aliased_column_name, dynamic_display_title) AS (
    -- Eurostat Metrics (No alias changes, code matches column name)
    -- skills
        ('I_DSK2_AB', 'i_dsk2_ab', 'Above Basic Digital Skills (% of individuals)'),
        ('I_DSK2_B',  'i_dsk2_b',  'Basic Digital Skills (% of individuals)'),
        ('I_DSK2_LW', 'i_dks2_lw', 'Low Digital Skills (% of individuals)'), 
        ('I_DSK2_N', 'i_dskn', 'Narrow Digital Skills (% of individuals)'),
        ('I_DSK2_LM', 'i_dsk2_lm', 'Limited Digital Skills (% of individuals)'),
        ('I_DSK2_X','i_dsk_x', 'No Digital Skills (% of individuals)'),
    -- usage
        ('I_IDAY', 'i_iday', 'Daily Internet Access (% of individuals)'),
        ('I_IUAI','i_iuai', 'Use of Generative AI Tools (% of individuals)'), 
        ('I_IEID','i_ieid', 'Access to Online Resvices via eID (% of individuals)'),
        ('I_MAPS','i_maps', 'Managing Access to Personal Data, last 3 months (% of individuals)'),
        ('I_IUCPP','i_iucpp', 'Internet Usage for Civic/Political Participation (% of individuals)'),
        'I_IUPDG',
        'I_IUPS',
        'I_IUCHAT1'
    -- gov
    'I_IGOVAPR','I_IGOVTAX2','I_IUGOV1','I_IGOVBE','I_IGOVRCC', 'I_IGOVRX', 
    -- media
    'I_IUPOL2','I_TIC','I_UDI', 
    -- non using eID 
    'I_IREIDNO','I_IREIDNA', 'I_IREIDSEC','I_IREIDTEC', 'I_IREIDNN', 'I_IREIDDEV', 'I_IREIDOTH',
    -- e-gov legacy data
    'I_IGOV12FM', 'I_IGOV12IF', 'I_IIGOVX', 
    -- no internet usage
    'I_IUID1X', 'I_IUX', 


    -- Eurobarometer Metrics (Translating Survey Codes to your new clean Aliases!)
        ('QA6_1_1',  'tr_party',                     'Trust in Political Parties'),
        ('QA6_5_1',  'tr_authority',                 'Trust in Local/Public Authorities'),
        ('QA6_7_1',  'tr_nat_gov',                   'Trust in National Government'),
        ('QA6_8_1',  'tr_nat_par',                   'Trust in National Parliament'),
        ('QA6_9_1',  'tr_eu',                        'Trust in the European Union'),
        ('QA8_1_1',  'tr_eu_par',                    'Trust in the European Parliament'),
        ('QE3_1_1',  'tr_press',                     'Trust in the Written Press'),
        ('QE3_5_1',  'tr_soc_netw_online',           'Trust in Online Social Networks'),
        ('QE7_1_1',  'nat_media_tr_info',            'Perceived Media Trustworthiness (Combined)'),
        ('QE7_4_1',  'nat_media_free_pressure',       'Perceived Media Freedom from Pressure (Combined)'),
        ('QE6R_2_1', 'tr_info_polit_on_soc_net',      'Trust in Political Info on Social Networks (Combined)'),
        ('QE9_9_1',  'eff_acc_to_tech',              'Impact: Access to Technology'),
        ('QE1_5_1',  'eff_improve_democr_life',      'Impact: Improving Democratic Life (Combined)'),
        ('QE1_10_1', 'eff_improve_acc_pub_services', 'Impact: Access to Public Services (Combined)'),
        ('QE1_1_1',  'eff_work_remote',              'Impact: Ability to Work Remotely (Combined)')
)