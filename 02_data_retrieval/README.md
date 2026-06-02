# Data Retrieval & Pipeline Layer

This directory contains the pipeline modules, development notebooks, and documentation required to programmatically ingest, clean, and load data from **Eurostat** and **Eurobarometer Surveys** into a PostgreSQL data warehouse.

---
## System Prerequisites

Before running the automation scripts, ensure your local environment is configured:

1. **Dependencies**: Install the required Python packages:
   ```bash 
   pip install -r requirements.txt
   ``` 

2. **Environment Variables**: Create a `.env` file in this directory with your PostgreSQL credentials:
    ```bash
    DB_NAME=your_database_name
    DB_USER=your_database_user
---
## Data Obtaining Pipelines 
1. **Eurostat Automation** (`retrieve_eurostat.py`)  
This script automates data fetching from the official Eurostat API using a configuration-driven approach:
- **Configuration**: Reads targeted dataset IDs directly from `eurostat_tables.csv`.
- **Obtaining**: Connects to the `Eurostat API` using the `eurostat` Python library.
- **Storage**: Dynamically builds database schemas and loads the raw tables into `PostgreSQL`.

2. **Eurobarometer ETL Pipeline** (`retrieve_eurobarometer.py`)
Eurobarometer data is distributed in highly nested, multi-tab Excel workbooks. This robust ETL script standardizes and flattens the layout into an analytics-ready structure:
- **Extraction**: Obtains complex local Excel workbooks (e.g., `eb_105.xlsx`).
- **Data Cleaning & Filtering**: Isolates core data rows, handles missing metrics, drops non-data tabs, and filters specifically for the EU-27 member states while skipping candidate or regional breakdown tabs.
- **Column Re-indexing**: Supports PostgreSQL column length limits by mapping long-form survey questions to short alphanumeric IDs (e.g., `d71_1`, `c2_1`).
- **Merging**: Uses a functional `reduce` outer merge to horizontally unify over a hundred survey tabs into a single table indexed by country and tracking year.
- **Metadata Mapping**: Simultaneously extracts survey questions text and response choices, generating a relational metadata "map" table uploaded to Postgres alongside the core dataset.
---
## Dimension & Metadata Mapping Layer
To build a fully relational reporting layer, these specialized modules scrape or query official websites and geographic data online to create structured dimensional lookup tables.
- `country_coordinates.py`: downloads global geographic datasets and filters them strictly for the target 27 EU member states; it handles structural Eurostat anomalies (e.g., translates standard GR code for Greece to legacy 'EL');
- `eurostat_mapping.py`: gets the metadata from Eurostat to save human-readable descriptions for indicator variables (e.g., mapping `I_IUAI` to its English title);
- `eurostat_tables_map.py`: gets the codes and names of tables from Eurostat official website; links physical datasets (e.g., `isoc_ai_iaiu`) to their English descriptions;
- `eurostat_map_individuals.py` & `eurostat_units_map.py`: downloads and clean categorical dimensions from Eurostat code lists, translating metadata like **units** (`PC_IND` as Percentage of Individuals) and **ind_types** (like `IND_TOTAL` as Total Population).

---
## Directory Structure & Additional Files

The files are now divided in two folders -- related to `eurobarometer/` and to `eurostat/`.

|File/Folder|Description|
|---|---|
|Pipeline Scripts|
|`retrieve_eurostat.py`|Core automated pipeline for processing the Eurostat API|
|`retrieve_eurobarometer.py`|ETL pipeline for processing, cleaning and linking complex Eurobarometer Excel sheets|
| Mapping Tools|
|`country_coordinates.py`|Fetches, adjusts, and uploads coordinates for the 27 EU member states|
|`eurostat_tables_map.py`|Generates a clean table connecting physical Eurostat table codes to readable titles|
|`eurostat_indicators.py`|Fetches and saves codes and names of Eurostat indicators|
|`eurostat_units_map.py`|Downloads and saves Eurostat measurement unit descriptions|
|`eurostat_map_individuals.py`|Maps socio-demographic individual category types into a table|
|`eurostat_tables.csv`|Contains targeted Eurostat tables used for processing in Eurostat pipeline (configuration file)|
|Other files|
|`requirements.txt`|List of required Python packages for the Data Retrieval stage (dependencies)|
|`01_data_sources.md`|Analytical explanation and catalog of datasets selected for the project (documentation)|
|`02_data_extraction_eurostat.ipynb`|Playground exploring early workflows, alternative query methods, and architectural notes (progress tracking notebook)|
|`03_data_extraction_eurobarometer.ipynb`|Playground documenting regex patterns, Excel transposing logic, and tab-merge testing (progress tracking notebook)|
|`eurobarometer_data/`|Local directory containing raw input Eurobarometer `.xlsx` workfiles (*Ignored by Git*) (data staging area)|
|`.env`|Contains local environment variables and database access parameters (*Ignored by Git*)(credentials)|
---
## Recommended Execution Order
To safely generate the database tables alongside their foundational lookup definitions, run the scripts sequentially from within this directory:
```bash
# 1. Map the tables / indicators / countries / units / individuals types:
python country_coordinates.py
python eurostat_tables_map.py
python eurostat_mapping.py
python eurostat_units_map.py
python eurostat_map_individuals.py

# 2. Obtain data:
python retrieve_eurostat.py
python retrieve_eurobarometer.py
```