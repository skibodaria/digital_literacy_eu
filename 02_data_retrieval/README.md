# Data Retrieval | Folder Structure
This folder consists of several files, which are relevant to the process of obtaining data from `Eurostat` website. The documents here give explanations about different approaches to the data retrieval, present Jupiter Notebooks in which I develop the approach, and, in the end, provide user with `retrieve_eurostat.py` script that allows to automate obtaining data.

The pipeline on this stage looks the following way:
- grab a table name (dataset_id) from a file
- connect to **Eurostat** API using `eurostat` library and get this table
- upload it to PostgreSQL.

The second part of the data retrieval is the **Eurobarometer** data. To extract and upload to PostgreSQL messy Excel files, use `retrieve_eurobarometer.py`.

The pipeline for this data looks the following way:
- read Excel file from hard drive;
- edit it by getting read of obsolete tabs, repetative data, etc.;
- clean column names, assign data types;
- deals with length of column names which are too long by re-indexing them to standard IDs;
- merge all the tabs together (if working with multiple tabs);
- connect to PostgreSQL and upload clean table there.

At the same time the same `.py` script:
- extracts questions and their codes from Excel file,
- saves them together with answers,
- uploads the created 'map' to PortgreSQL as a table.


Important notes:
- `.env` file with credentials to access PostgreSQL is needed in the current folder;
- `requrements.txt` should be executed in order to install neccessarily Python libraries;
- `eurostat_tables.csv` has table codes and table names; the ones used here were important for the current project.

File `01_data_sources.md` describes the tables I'm using for the current project and also stating the reasons for this choice.

Jupiter Notebook `02_data_extraction_eurostat.ipynb` is kept here since the project is part of my Data Analytics Bootcamp and illustrates the learning curve and the teaching journey. It might be useful to get more understanding of the 'how' and gives more context about possible scenarios of data retrieval (and why I didn't go with some of them).

Jupiter Notebook `03_data_extraction_eurobarometer.ipynb` is kept for the same reason: it has all the steps of developing the final Python script to read messy Excel files, deal with the structure of tabs, edit columns, convert the whole file intoa neat `.csv` and upload it to PostgreSQL.