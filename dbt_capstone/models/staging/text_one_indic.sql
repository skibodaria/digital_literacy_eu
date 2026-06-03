SELECT 
	*,
	-- extract age group:
	CASE
		WHEN ind_type IN ('Y0_15', 'Y16_19', 'Y20_24','Y25_34','Y35_44','Y45_54','Y55_64','Y65_74','Y75_MAX')
	END AS gender,
	
	-- extract education:
	CASE
		WHEN ind_type IN ('I0','I3','I5')
	END AS edu_level,
	
	-- extract settlement:
	CASE
		WHEN ind_type IN ('IND_DEG1','IND_DEG2','IND_DEG3')
	END AS settlemnt,
	
	-- extraxt total:
	CASE
		WHEN ind_type = 'IND_TOTAL'
	END AS total,
	
	-- extract education and gender:
	CASE
		WHEN ind_type IN ('M_I0_2', 'M_I3_4', 'M_I5_8')
	END AS male_edu,
	
	CASE
		WHEN ind_type IN ('F_I0_2','F_I3_4', 'F_I5_8')
	END AS fem_edu,
	
	-- extract age + low education:
	CASE
		WHEN ind_type IN ('Y16_24LO','Y16_29LO','Y25_54LO','Y25_64LO')
	END AS age_low_edu
	
	-- extract age + middle education:
	CASE
		WHEN ind_type -- CONTINUE HERE!!!
	END
	
	
	-- extract age + fem_gender:
	CASE
		WHEN ind_type IN ('F_Y16_19','F_Y20_24','F_Y25_29','F_Y35_44','F_Y45_54','F_Y55_64','F_Y65_74', 'F_Y75_89')
	END AS age_groups_female
	CASE
		WHEN ind_type IN ('M_Y16_19', 'M_Y20_24', 'M_Y25_29','M_Y35_44', 'M_Y45_54', 'M_Y55_64', 'M_Y65_74','M_Y75_89')
	END AS age_groups_male
	
	-- extract gender (16-74)
	CASE
		WHEN ind_type = 'F_Y16_74'
	END AS total_females
	CASE
		WHEN ind_type = 'M_Y16_74'
	END AS total_males
	
	
	
	
	
	
	
	
	
	
FROM public.stg_dig_skills_baseline
WHERE 
	indicator_code = 'I_DSK2_AB'
	AND "year" = 2025
;




    -- Extract Gender
    CASE 
        WHEN ind_type IN ('M', 'F') THEN ind_type 
        ELSE 'TOTAL' 
    END AS gender,
    
   
FROM clean_data
