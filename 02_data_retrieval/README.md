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

2. **Eurobarometer ETL Pipeline** (`terrieve_eurobarometer.py`)
Eurobarometer data is distributed in highly nested, multi-tab Excel workbooks. This robust ETL script standardizes and flattens the layout into an analytics-ready structure:
- **Extraction**: Obtains complex local Excel workbooks (e.g., `eb_105.xlsx`).
- **Data Cleaning & Filtering**: Isolates core data rows, handles missing metrics, drops non-data tabs, and filters specifically for the EU-27 member states while skipping candidate or regional breakdown tabs.
- **Column Re-indexing**: Supports PostgreSQL column length limits by mapping long-form survey questions to short alphanumeric IDs (e.g., `d71_1`, `c2_1`).
- **Merging**: Uses a functional `reduce` outer merge to horizontally unify over a hundred survey tabs into a single table indexed by country and tracking year.
- **Metadata Mapping**: Simultaneously extracts survey questions text and response choices, generating a relational metadata "map" table uploaded to Postgres alongside the core dataset.
---
## Directory Structure & Additional Files
|File/Folder|Description|
|---|---|
|`retrieve_eurostat.py`|Automated script for the Eurostat API pipeline|
|`retrieve_eurobarometer.py`|Complete ETL pipeline script for processing and loading Eurobarometer workbooks|
|`eurostat_tables.csv`|Look-up file containing the list of Eurostat table codes and descriptions utilized in this project|
|`requirements.txt`|Python dependencies required for this pipeline|
|`01_data_sources.md`|Documentation detailing the specific tables selected for the project scope and the analytical justification behind them|
|`02_data_extraction_eurostat.ipynb`|Learning materials for building a pipeline on Eurostat data (part of the Capstone project). Explores the initial API approaches, alternative extraction techniques, and details why specific data obraining pathways were chosen|
|`03_data_extraction_eurobarometer.ipynb`|Learning materials for building a pipeline on Eurobarometer data (also part of the Capstone project). Documents the iterative development of the Excel transposing logic, regex cleaning patterns, and the debugging steps required to solve the structural tab-merge challenges|
|`.env`|Hidden file with credentials for PostgreSQL accessl see `.gitignore`|
|`eurobarometer_data`|Folder (not git-tracked) with raw Eurobarometer data; see `.gitignore`|