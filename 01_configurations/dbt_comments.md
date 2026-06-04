# `dbt` Modeling: Comments

## 1. Data Intake and Preprocessing Pipeline
### Structural Alignment
Before initializing the core analytics pipeline, the raw **Eurostat** data required schema stabilization and environment mapping:

- **Schema Standardization**: Due to inconsistent column naming across source files (e.g., conflicting dimensions like `indic_is` vs. `hhtype`), naming conventions were standardized directly within the PostgreSQL database layer to ensure structural consistency across all source inputs.

- **dbt Environment Configuration**: Implemented a formal `sources.yml` manifest to register and control raw database tables. The pipeline separates production code into staging models while tracking secondary references—such as custom dimensionality mapping files—as independent project assets.

### Pipeline Stage 1: The Preprocessing Workflow (/models/prep/)
*Here to do: Eurobarometer (drop redundant columns, calculate new fields, merge with the master table for the EU Baseline level)*

To transform fragmented regional files into a centralized statistical engine, data was passed through a three-stage preprocessing sequence:

1. Indicator-to-Table Mapping
Asset: `models/prep/prep_eurostat_map.sql`
Execution: Constructed a centralized relational mapping reference that links individual indicator metadata, structural codes, and their respective source tables, creating an audit trail for the entire downstream pipeline.

2. Wide-to-Long Normalization (melting)
Asset: `models/prep/prep_eurostat_melted_long.sql`
Execution: Unpivoted (melted) the horizontal temporal headers (`year_202X`) across **all 34 independent Eurostat source tables** into continuous row-wise observations. These normalized outputs were vertically stacked using a global `UNION ALL` operation, collapsing distinct source files into a single master long-format ledger.

3. Strategic Feature Filtering & Scope Reduction
Asset: `models/prep/prep_eurostat_filtered.sql`
Execution: Applied data-cleansing solutions to eliminate noise and isolate variables relevant to the core research hypotheses:
- Demographic Trimming: Stripped out extraneous demographic confounding layers not central to the study (e.g., segregating population groups by employment metrics or complex household types).
- Geographic Scoping: Dropped non-EU data points to restrict the final observation matrix to the 27 official EU member states, ensuring perfect geographic alignment for comparative statistical cross-validation.

--- 
### Pipeline Stage 2: Mart Models
*(to do)*

---

## 2. Reshaping Multi-Dimensional Eurostat Data for Statistical Analysis
Eurostat datasets are inherently hierarchical and highly packed, often combining baseline indicators, demographic dimensions, and specific units of measurement vertically into a single long-format structure. While this is optimal for storage and querying, it is incompatible with machine learning and statistical libraries (like `pandas` and `scikit-learn`), which require a wide/tidy data format where every column represents an independent feature and every row represents a unique unit of observation.

1. Core Principles for Statistical Analysis
To run meaningful correlations (`df.corr()`) or clustering algorithms (such as `K-Means`), the raw Eurostat structure must be transformed according to the following constraints:
- The Unit of Observation: For cross-national EU comparisons, the row identifier must be collapsed to the Country (or Country + Year).
- The Feature Space: Every demographic slice, sub-metric, or indicator must be pivoted out of rows and into its own independent, continuous numerical Column.
- Level of Aggregation Isolation: Parent dimensions (e.g., National Totals) and sub-dimensions (e.g., Male, Youth, High Education) must be separated into isolated statistical matrices to prevent mathematical collinearity and part-whole biases.

2. Data Pipeline Architecture
To keep Python runtimes lightweight and analysis notebooks clean, the data transformation is divided between the Data Engineering layer (`dbt`) and the Data Science layer (`pandas`).

1. Data Engineering Layer (`dbt`)
Instead of executing volatile matrix pivots downstream, `dbt` handles the structural heavy lifting inside the data warehouse using conditional aggregation.
- Granularity Filtering: Filters data to a single analytical year (e.g., `2025`) and standardizes demographic codes.
- Dimensional Unpacking: Employs explicit grouping (`GROUP BY country`) and logical evaluation (`MAX(CASE WHEN...)`) to shift complex combinations of indicator_code, ind_type, and unit_code into a flattened table.
- Feature Renaming: Replaces cryptic Eurostat composite strings with intuitive, human-readable column aliases (e.g., `digital_skills_male`, `ai_adoption_active_users`).

2. Data Science Layer (`pandas` / EDA)
Once the database serves a flat table, the Python environment focuses exclusively on analytical workflows rather than data cleaning:
- The Macro View: Isolates rows restricted to national totals and primary denominators (`PC_IND` - Percentage of Individuals) to construct a high-level country baseline. This allows clear analysis of macro trends (e.g., correlating overall national digital literacy with baseline economic metrics).
- The Micro/Demographic View: Evaluates targeted sub-matrices (e.g., intersectional groups like gender paired with education level) across smaller thematic buckets to uncover micro-sociological insights without causing data density errors or sparse matrices (`NaN` values).
--- 
## 3. Last Available Year (LAY) Approach for EU Baseline Metrics
Eurostat indicators are asynchronous; some surveys are run annually, some biennially, and others every three to five years.
Since the goal of this project is a macro **cross-sectional baseline of Europe**, I have two standard data science strategies to handle this: choosing a strict year (e.g., 2025) and dropping the metrics which were not yer aquired or calculated for this year (approach a), or going with the last available year (approach b).
If I strictly filtered for a single calendar year like 2025 across all 34 indicators, my baseline matrix would be riddled with missing values (NaN), completely breaking your correlation matrices and clustering algorithms.
Instead of a strict calendar year, I define the time dimension as **the most recent state of the country**. I take the newest available data point for each specific indicator-country combination within a reasonable recent window (e.g., **between 2021 and 2025**).
