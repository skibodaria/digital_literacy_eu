# =====================================================================
# DATA RETRIEVAL EUROBAROMETER
# =====================================================================

# importing libraries:
import io
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from functools import reduce 
import re


# DECLARING THE FUNCTIONS:

# data extractor
def read_eurobarometer(file_path:str, header=8):
    """This functions reads an Excel file to get each tab from it and save it a dictionary of pandas dataframes.
    Takes two arguments:
    - a path to the file (string)
    - amount of rows before the header (by default 8 as in most of the Eurobarometer files) (integer)
    The function drops first two tabs (normally Content and Countries).
    Returns a dictionary of dataframes.
    """
    # read all the sheets as dictionary of dataframes:
    try: 
        dict_of_dfs = pd.read_excel(file_path, sheet_name=None, header=8)

        # get rid of the front page and country list:
        front_page = next(iter(dict_of_dfs))
        del dict_of_dfs[front_page]
        country_page = next(iter(dict_of_dfs))
        del dict_of_dfs[country_page]

        return dict_of_dfs
    
    except Exception as e:
        print(f"Something went wrong with file reading: {e}.")


# data cleaner
def clean_eurobarometer(dict_of_dfs, sheet:str):
    """This function helps to deal with messy data from Eurobarometer.
    It takes two arguments: 
    - a dictionary of dataframes (dict_of_dfs)
    - a name of a tab from Excel file (string)
    Cleans it, pivots it, re-assigns data types and removes obsolete data.
    It also drops all the countries which are not EU.
    It returns a clean data frame.
    """

    eu_countries = [
        'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
        'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
        'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE'
    ]

    try: 
        # drop emptty columns + totals for EU:
        df = dict_of_dfs[sheet].drop(columns={'<<Back to content','UE27\nEU27', 'UE27\\nEU27'},errors='ignore').copy()
        # drop first two rows:
        df = df.drop(df.index[:2])
        df.reset_index()
        # drop all rows with French / absolute numbers
        df = df.iloc[1::2]
        # turn all columns to numeric
        num_cols = df.columns.drop('Unnamed: 1')
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
        # ret index for the answers:
        df.set_index('Unnamed: 1',inplace=True)
        # flip the table:
        df = df.T
        # name the new index column:
        df.index.name = 'country'
        # drop all rows which are not in the list of the EU countries
        df = df[df.index.isin(eu_countries)]
        # reset index:
        df.reset_index(inplace=True)
        df.columns.name = None

        # rename columns to match the map:
        indexed_cols = []
        col_num = 1
        for col in df.columns:
            if col == 'country':
                indexed_cols.append(col)
            else:
                col_str = f'{sheet}_'.lower() + str(col_num)
                indexed_cols.append(col_str)
                col_num = col_num + 1
        df.columns = indexed_cols

        return df
    except Exception as e:
        print(f"Something went wrong with cleaning {sheet}: {e}.")

# create map:
def map_questions(file_path):
    """Reads an Excel file, returns a DataFrame of sheet_names and questions.
    """
    try: 
        df = pd.read_excel(file_path, sheet_name='Content', header=4)
        df = df.drop(columns={'Question French'})
        df = df.drop(df.index[0])
        df = df.replace(',', '', regex=True)
        return df
    except Exception as e:
        print(f'Something went wrong with building a map of questions: {e}.')

def map_answers(dict_of_dfs,map_path):
    """Maps answers from a dataframe.
    Saves them, matches them to questions and saves them to a file with questions.
    """
    with map_path:
        try:
            mapped_columns = []
            for sheet_name, df in dict_of_dfs.items():
                for col in df.columns:
                    if col == 'country':
                        continue
                    else:
                        col_str = str(col).lower().strip()
                        col_str = col_str.replace("'", "").replace(",", "")
                        col_str = col_str.replace(":", "").replace(" ", "_")
                        col_str = col_str.replace("(", "").replace(")", "")
                        mapped_columns.append(col_str)
        mapped_columns


# table creator for PostgreSQL:
def create_table(df):
    """This function creates a structure for a future table in PostgreSQL database.
    It prepares the work of copy_expert.
    It takes one argument: a dataframe.
    It returns two SQL strings:
    - table sttucture (names of columns + their data types)
    - formatted columns (string for copy_expert)
    """
    raw_columns =  df.columns.tolist()
    structure_elements = []

    for col in raw_columns:
        if str(col) == 'country':
            structure_elements.append(f'"{col}" varchar')
        else:
            structure_elements.append(f'"{col}" numeric')
    table_structure = ', '.join(structure_elements)

    formatted_columns = ', '.join([f'"{col}"'for col in raw_columns])
    return table_structure, formatted_columns

# uploader
def upload_to_postgres(df, connection_string:str, table_name: str):
    """This function connects to PostgreSQL database, creates a table there and 
    uploads the table from the dataframe directly to PostgreSQL.
    It takes three arguments:
    - dataframe to be uploaded,
    - connection string which has database name (dbname) and user name (user) to connect
    to the desired PostgreSQL database,
    - table name (string).
    """
    table_structure, formatted_columns = create_table(df)
    try: 
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f'DROP TABLE IF EXISTS "{table_name}";')
                cur.execute(f'CREATE TABLE "{table_name}" ({table_structure});')
                sql = f"""
                    COPY {table_name} ({formatted_columns})
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER true, DELIMITER ',');
                """
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                buffer.seek(0)

                cur.copy_expert(sql, buffer)
                conn.commit()
                print(f"Successfully built table and imported {table_name} dynamically!")
    except Exception as e:
        print(f'Something went wrong with PostgreSQL connection: {e}.')



# =====================================================================
# THE MAIN EXECUTION BLOCK
# =====================================================================
if __name__ == "__main__":

    # FINAL RUN (table sp566) -- works:
    # path = './eurobarometer_data/eb_sp566.xlsx'
    # dict_dfs = read_eurobarometer(path)

    # all_tabs = []
    # map_path = 'mapping_columns.csv'
    # for sheet_name, df in dict_dfs.items():
    #     df_clean = clean_eurobarometer(dict_dfs,sheet_name,map_path)
    #     all_tabs.append(df_clean)

    # df_final = reduce(lambda left, right: pd.merge(left, right, on=['country'], how='inner'), all_tabs)
    # df_final['year']=2025

    # load_dotenv(dotenv_path='.env')
    # db_name = os.getenv('DB_NAME')
    # db_user = os.getenv('DB_USER')
    # connection_string_final = f'dbname = {db_name} user = {db_user}'
    # table_name = 'eurobarometer_sp566'
    # upload_to_postgres(df_final, connection_string_final, table_name)

    # Try on a different table:
    path = './eurobarometer_data/eb_105.xlsx'
    dict_dfs = read_eurobarometer(path)
    map_path = 'mapping_columns.csv'

    eu_countries = [
        'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
        'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
        'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE'
    ]

    all_tabs = []
    for sheet_name, raw_df in dict_dfs.items():
        sheet_cols = [str(c).upper().strip() for c in raw_df.columns]
        has_eu_data = any(country in sheet_cols for country in eu_countries)
        if not has_eu_data:
            print(f"Skipping regional/candidate sheet: {sheet_name}. No EU-columns found.")
            continue
        df_clean = clean_eurobarometer(dict_dfs,sheet_name)
        # if df_clean is not None:
        #     all_tabs.append(df_clean)
        all_tabs = []
        if df_clean is not None:
            audit_mapping(df_clean, map_path, sheet_name.lower())
            all_tabs.append(df_clean)

    # if all_tabs:
    #     df_final = reduce(lambda left, right: pd.merge(left, right, on=['country'], how='inner'), all_tabs)
    #     df_final['year']=2026

    #     load_dotenv(dotenv_path='.env')
    #     db_name = os.getenv('DB_NAME')
    #     db_user = os.getenv('DB_USER')
    #     connection_string_final = f'dbname = {db_name} user = {db_user}'
    #     table_name = 'eurobarometer_105'
    #     upload_to_postgres(df_final, connection_string_final, table_name)
    # else:
    #     print("No valid EU-27 dtaframes were obtained")





