# Data Retrieval | Folder Structure
This folder consists of several files, which are relevant to the process of obtaining data from `Eurostat` website. The documents here give explanations about different approaches to the data retrieval, present Jupiter Notebooks in which I develop the approach, and, in the end, provide user with `retrieve_eurostat.py` script that allows to automate obtaining data.

The pipeline on this stage looks the following way:
grab a table name from a file | connect to Eurostat and get this table | upload it to PostgreSQL

Important notes:
- `.env` file with credentials to access PostgreSQL is needed in the current folder;
- `requrements.txt` should be executed in order to install neccessarily Python libraries;
- `eurostat_tables.csv` has table codes and table names; the ones used here were important for the current project.

File `01_data_sources.md` describes the tables I'm using for the current project and also stating the reasons for this choice.

Jupiter Notebook `02_data_download.md` is kept here since the project is part of my Data Analytics Bootcamp and illustrates the learning curve and the teaching journey. It might be useful to get more understanding of the 'how' and gives more context about possible scenarios of data retrieval (and why I didn't go with some of them).