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
def clean_eurobarometer(dict_of_dfs, sheet:str, map_path):
    """This function helps to deal with messy data from Eurobarometer.
    It takes three arguments: 
    - a dictionary of dataframes (dict_of_dfs)
    - a name of a tab from Excel file (string)
    - map (a .csv file for column names mapping)
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
        mapping_df = pd.read_csv(map_path)
        mapping_df['raw_phrase'] = mapping_df['raw_phrase'].astype(str).str.lower().str.strip()
        mapping_df['clean_phrase'] = mapping_df['clean_phrase'].astype(str).str.lower().str.strip()
        
        mapping_df['phrase_len'] = mapping_df['raw_phrase'].str.len()
        mapping_df = mapping_df.sort_values(by='phrase_len', ascending=False)
        column_replacements = dict(zip(mapping_df['raw_phrase'], mapping_df['clean_phrase']))
        mapping_df.to_csv('mapping_columns.csv', index=False)
    except Exception as e:
        print(f"Error loading mapping file: {e}.")

    try: 
        df = dict_of_dfs[sheet].drop(columns={'<<Back to content','UE27\nEU27', 'UE27\\nEU27'},errors='ignore').copy()
        num_cols = df.columns.drop('Unnamed: 1')
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
        df = df[df['BE'] < 1]
        df.set_index('Unnamed: 1',inplace=True)
        df = df.T
        df.index.name = 'country'
        df = df[df.index.isin(eu_countries)]
        df.reset_index(inplace=True)
        df.columns.name = None

        cleaned_cols = []
        for col in df.columns:
            if col == 'country':
                cleaned_cols.append(col)
            else:
                col_str = str(col).lower().strip()
                col_str = col_str.replace("'", "").replace(",", "")
                col_str = col_str.replace(":", "_").replace(" ", "_")
                col_str = re.sub(r'_+', '_', col_str)  # collapses ___ down to _
                cleaned_cols.append(col_str)
        df.columns = cleaned_cols

        for long_phrase, short_phrase in column_replacements.items():
            df.columns = df.columns.str.replace(long_phrase, short_phrase, regex=False)

        prefixed_cols = []
    
        for col in df.columns:
            if col == 'country':
                prefixed_cols.append(col)
            else:
                prefixed_cols.append(f"{sheet}_".lower() + col)
            
        final_cols = []
        counts = {}

        for col in prefixed_cols:
            if col in final_cols:
                counts[col]=counts.get(col,1)+1
                final_cols.append(f"{col}_{counts[col]}") # ensures that if there are duplicated columns, they both will be saved and names altered
            else:
                final_cols.append(col)
        df.columns = final_cols

        long_cols = [col for col in df.columns if len(col) > 63]
        if long_cols:
            print(f"Warning in sheet '{sheet}': Columns exceed 63 chars: {long_cols}")

        return df
    except Exception as e:
        print(f"Something went wrong with cleaning {sheet}: {e}.")

# cleaning audit:
def audit_mapping(df, map_path, sheet):
    """
    Compares actual cleaned column names against mapping file.
    Reports: which mappings never fired, and which long columns slipped through.
    """
    mapping_df = pd.read_csv(map_path)
    raw_phrases = set(mapping_df['raw_phrase'].str.lower().str.strip())
    clean_phrases = set(mapping_df['clean_phrase'].str.lower().str.strip())

    actual_cols = set(df.columns) - {'country'}

    # 1. Long columns that should have been shortened but weren't
    long_cols = [c for c in actual_cols if len(c) > 63]
    if long_cols:
        print(f"\n[{sheet}] Long columns that mapping DIDN'T catch:")
        for c in long_cols:
            # Strip the sheet prefix to get what the raw_phrase should look like
            stripped = c[len(sheet)+1:]  # removes e.g. "qa7b_"
            print(f"  actual:   '{stripped}'")
            # Find closest match in mapping keys
            close = [r for r in raw_phrases if r[:20] == stripped[:20]]
            if close:
                print(f"  closest in mapping: '{close[0]}'")
            else:
                print(f"  --> NOT FOUND in mapping at all")

    # 2. Mappings that exist in CSV but never matched anything
    unused = raw_phrases - {c[len(sheet)+1:] for c in actual_cols}
    if unused:
        print(f"\n[{sheet}] Mapping rules that fired on NOTHING (probably key mismatch):")
        for u in sorted(unused):
            if len(u) > 40:  # only care about the long ones
                print(f"  '{u}'")


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
        df_clean = clean_eurobarometer(dict_dfs,sheet_name,map_path)
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





