# `dbt` Modeling: Comments
Before starting the data transformations with `dbt`, several additional issues had to be addressed:
- `Eurostat` tables have different columns naming (e.g., `indic_is` and `hhtype` etc.); these had to be renamed semi-manually through direct access to the PostgreSQL database;
- `dbt` project required `source.yml` file, listing all the tables; in this case, I have a special source file for a side-table (mapping) and the main file in the `models/` directory;

## Prep Step
- created a mapping file of all the indicators and tables together; see `models/prep/prep_eurostat_map.sql`;
- created master table by melting `year_XXX` columns and `UNION ALL` all the 34 `Eurostat` tables together (see `models/prep/prep_eurostat_melted_long.sql`)
- created a filtered table:
    - removed `units` that I won't use for the analysis, 
    - removed categories of individuals which are not in focus (e.g., by employment status, or by type of household, etc.),
    - removed non-EU countries (kept 27 entries)

# Staging Step
Here I need to develop three models for three different hypotheses:
1. EU Digital Skills Baseline:
- `03_eda/dig_skills_rq1.ipynb` for explanations

2. Demographics
- `03_eda/dem_inequal_rq2.ipynb` for explanations

3. Trust & Disinformation
- `03_eda/trust_rq3.ipynb` for explanations