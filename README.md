# Connected but Excluded?
### Testing the Limits of Digital Literacy against Disinformation Vulnerability and Bureaucratic Barriers

## Project Overview
This repository contains the data pipeline, analytical transformations, and research assets for a comprehensive audit of the European digital landscape. 

Using macro-level survey data (Eurobarometer and Eurostat 2025), this study investigates the existence of a **"Second-Level Digital Divide"** across the 27 European Union member states. Moving beyond basic Internet access, the project explores how an individual's actual digital skills map against demographic inequality lines, affects their vulnerability to fake news/disinformation [1], and correlates with their overall trust in national and European governance.
([1] The media consumption, disinformation, and correlation between them and digital skills will come in the future iterations of the project)

---

## Core Research Questions
1. **The Macro Overview:** What is the current state baseline of Internet usage frequency and overall digital skill levels across the EU-27?
2. **The Sociodemographic Split:** Does the Digital Divide match traditional socio-demographic inequality lines (e.g., age, gender, education level, migration background [2], type of settlement)?
3. **Institutional Trust:** How does an individual’s digital literacy correlate with their trust in national governments and EU-level institutions?
4. **Disinformation Resilience:** Does higher digital literacy correlate with a stronger ability to identify and deal with fake news and disinformation? [3]
([2] Migration background also comes with the future developments of the project.  
[3] Research into disinformation resilience comes with the next iteration.)

---

## Main Data Sources
The project dynamically downloads and unifies diverse public datasets:
* **Eurostat | ICT Statistics (2025 and before):** Captures country-level macro trends regarding internet usage frequency and established digital skill matrices.
* **Eurobarometer | Digital Decade (2025):** Tracks citizens' perceptions of digital public services and infrastructure goals.
* **Eurobarometer | Standard Survey (2025):** Macro-level tracking of societal trust, media habits, and institutional perspectives.

---

## Project Architecture & Workflow

The pipeline is split into iterative layers moving data systematically from raw files to analysis:

### 1. Data Obtaining Layer (`data_retrieval/`)
* Automatically fetches configuration-driven datasets via the **Eurostat API**
* Employs custom robust Python ETL scripts to ingest, transpose, filter for **EU-27** boundaries, and resolve column length schemas for complex, nested **Eurobarometer** Excel workbooks
* Loads raw structured tables and relational survey metadata maps into a local **PostgreSQL** data warehouse

### 2. Transformation Layer (`dbt/`)
* Uses **dbt (data build tool)** locally to run transformations, clean data types, filter out analytical noise, and curate final database dimensions and facts
* Decodes question IDs back into human-readable survey dimensions via the custom metadata map tables

### 3. Analytics & Modeling Layer (`analysis`)
* Curates **dbt mart tables** optimized for exploratory data analysis (EDA)
* Generates geographic distribution maps, demographic cluster models, and evaluates relational hypotheses
* Performs statistical test (Wilcoxon Signed-Ranked Test, Friedman Multi-Groups Test, regression, Pearson Correlation)

### 4. Presenting the Results (`streamlit_app`)
* Gets the data from `PostgreSQL` database
* Renders visualizations and coefficients on several pages/tabs, exploring digital skills in detail and searching for correlation between digital literacy and E-Gov tools usage

---

## Project Roadmap & Milestones

### Week 1 Setup & Obtaining Data — *Status: Done!*
* Configured local project pipeline infrastructure (PostgreSQL and local dbt setup)
* Successfully automated the parsing, filtering, and migration of messy Eurobarometer workbooks into Postgres tables
* Downloaded and gathered data using programmatic API requests and optimized scripts

### Week 2 EDA & Hypothesis Testing — *Status: Done!*
* **Exploratory Data Analysis:** Build initial visualizations, basic distributions, and geographic mapping layers
* **dbt Consolidation:** Continue database cleaning inside dbt to drop unnecessary variables and isolate high-value research columns
* **Focus on Hypotheses:** Begin cross-sectional modeling to study relationship patterns (e.g., relationship between demographic clusters like age/residence vs trust metrics or disinformation resilience)
* **Iterations Loop**: Permament return to `dbt` stage, re-doing and transforming mart and staging models; retrieving more data, selecting more metrics, and using different approaches to match together Eurostat and Eurobarometer datasets

### Week 3 Analysis & Visualizations - *Status: Done!*
* **Conrinuous Iteration**: Going back to previous stages and revising the theoretical choices and analytical approaches
* **Editing Database**: Retrieving and seeding more data (e.g., time series on digital skills from 2015)
* **Data Quality Check**: Working on missing data or strange behaviour of certain metrics
* **Analysis Quality Check**: Using several tests to prove / disapprove statistical significance, correlations, and build robust models

### Week 4 Report, Insights, and Presentation - *Status: Almost There!*
* **Structuring the Findings**: Building a `Streamlit` app around the findings and creating a structure, which is logical and suitable for presentation
* **App Mechanics**: Creating the core of the app, a set of `.py` files, which both use syntax to form a user-friednly layout and perform on a fly complex statistical tests
* **Graduation**: Presenting the findings to a diverse audience