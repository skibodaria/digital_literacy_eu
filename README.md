# Connected but Excluded?
### Testing the Limits of Digital Literacy against Disinformation Vulnerability and Bureaucratic Barriers

## Project Overview
This repository contains the data pipeline, analytical transformations, and research assets for a comprehensive audit of the European digital landscape. 

Using macro-level and individual-level survey data in 2025-2026, this study investigates the existence of a **"Second-Level Digital Divide"** across the 27 European Union member states. Moving beyond basic internet access, the project explores how an individual's actual digital capability maps against demographic inequality lines, affects their vulnerability to fake news/disinformation, and correlates with their overall trust in national and European governance.

---

## Core Research Questions
1. **The Macro Overview:** What is the current state baseline of internet usage frequency and overall digital skill levels across the EU-27?
2. **The Sociodemographic Split:** Does the Digital Divide match traditional socio-demographic inequality lines (e.g., age, gender, education level, migration background, type of settlement)?
3. **Institutional Trust:** How does an individual’s digital literacy correlate with their trust in national governments and EU-level institutions?
4. **Disinformation Resilience:** Does higher digital literacy correlate with a stronger ability to identify and deal with fake news and disinformation?

---

## Main Data Sources
The project dynamically downloads and unifies diverse public datasets:
* **Eurostat | ICT Statistics (2025 and before):** Captures country-level macro trends regarding internet usage frequency and established digital skill matrices.
* **Eurobarometer | Digital Decade (2025):** Tracks citizens' perceptions of digital public services and infrastructure goals.
* **Eurobarometer | Standard Surveys (2025 & 2026):** Individual-level tracking of societal trust, media habits, and institutional perspectives.

---

## Project Architecture & Workflow

The pipeline is split into iterative layers moving data systematically from raw files to analysis:

### 1. Data Obtaining Layer (`02_data_retrieval/`)
* Automatically fetches configuration-driven datasets via the **Eurostat API**.
* Employs custom robust Python ETL scripts to ingest, transpose, filter for **EU-27** boundaries, and resolve column length schemas for complex, nested **Eurobarometer** Excel workbooks.
* Loads raw structured tables and relational survey metadata maps into a local **PostgreSQL** data warehouse.

### 2. Transformation Layer (`dbt/`)
* Uses **dbt (data build tool)** locally to run transformations, clean data types, filter out analytical noise, and curate final database dimensions and facts.
* Decodes question IDs back into human-readable survey dimensions via the custom metadata map tables.

### 3. Analytics & Modeling Layer (Next Phase)
* Curates **dbt mart tables** optimized for exploratory data analysis (EDA).
* Generates geographic distribution maps, demographic cluster models, and evaluates relational hypotheses.

---

## Project Roadmap & Milestones

### Week 1 Report (Setup & Obtaining Data) — *Status: Done!*
* Configured local project pipeline infrastructure (PostgreSQL and local dbt setup).
* Successfully automated the parsing, filtering, and migration of messy Eurobarometer workbooks into Postgres tables.
* Downloaded and gathered data using programmatic API requests and optimized scripts.

### Week 2 Plan (EDA & Hypothesis Testing) — *Status: Current Phase*
* **Exploratory Data Analysis:** Build initial visualizations, basic distributions, and geographic mapping layers.
* **dbt Consolidation:** Continue database cleaning inside dbt to drop unnecessary variables and isolate high-value research columns.
* **Focus on Hypotheses:** Begin cross-sectional modeling to study relationship patterns (e.g., relationship between demographic clusters like age/residence vs trust metrics or disinformation resilience).