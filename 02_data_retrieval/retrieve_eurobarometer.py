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
def read_eurobarometer(file_path:str, sheet_name=None):
    """This functions reads an Excel file to get each tab from it and save it a dictionary of pandas dataframes.
    Takes two arguments:
    - a path to the file (string)
    - sheet_name (a string); by defalut takes all data-strings (no meta-data tabs like Content and B (Countries))
    Returns dataframe (if sheet_name is Content) -- for questions/answers mapping;
    returns dictionary of dataframes (if sheet_name is not specified, process all the data tabs).
    """
    # read all the sheets as dictionary of dataframes:
    try: 
        if sheet_name == 'Content':
            df_content = pd.read_excel(file_path, sheet_name='Content', header=4)
            return df_content
        if sheet_name == 'B':
            print('You are trying to process meta-data tab "Countries".')
        else:
            dict_of_dfs = pd.read_excel(file_path, sheet_name=None, header=8)

            # get rid of the front page and country list:
            front_page = next(iter(dict_of_dfs))
            del dict_of_dfs[front_page]
            country_page = next(iter(dict_of_dfs))
            del dict_of_dfs[country_page]

            return dict_of_dfs
    
    except Exception as e:
        print(f"Something went wrong with file reading: {e}.")


# clean one tab:
def clean_single_sheet(df_raw, sheet_name: str):
    """Helper function containing your original cleaning logic for a single DataFrame."""
    eu_countries = [
        'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
        'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
        'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE'
    ]
    
    try:
        df = df_raw.drop(columns={'<<Back to content','UE27\nEU27', 'UE27\\nEU27'}, errors='ignore').copy()
        df = df.drop(df.index[:2])
        df = df.iloc[1::2]
    
        num_cols = df.columns.drop('Unnamed: 1')
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
        df.set_index('Unnamed: 1', inplace=True)
        df = df.T
        df.index.name = 'country'
        df = df[df.index.isin(eu_countries)]
        df.reset_index(inplace=True)
        df.columns.name = None
        return df
    except Exception as e:
        print(f"Fail to clean sheet {sheet_name}: {e}.")


def clean_eurobarometer(dict_of_dfs, sheet: str = None):
    """Cleans messy data from Eurobarometer.
    Takes two arguments:
    - dict_of_dfs: a dictionary of dataframes
    - sheet: (string, optional) Name of a specific tab. Default is None.
    
    Returns:
    - A single cleaned DataFrame if a sheet name is provided.
    - A dictionary of cleaned DataFrames if sheet=None.
    """
    try:
        # Case 1: Work with a single specified sheet
        if sheet is not None:
            if sheet not in dict_of_dfs:
                print(f"Sheet '{sheet}' not found in the dictionary.")
                return None
            return clean_single_sheet(dict_of_dfs[sheet], sheet)
            
        # Case 2: Work with ALL sheets if sheet=None
        else:
            cleaned_dict = {}
            for sheet_name, df_raw in dict_of_dfs.items():
                print(f"Processing and cleaning sheet: {sheet_name}")
                cleaned_dict[sheet_name] = clean_single_sheet(df_raw, sheet_name)
            return cleaned_dict
            
    except Exception as e:
        target = sheet if sheet is not None else "all sheets"
        print(f"Something went wrong with cleaning {target}: {e}.")
        return None


# # re-indexing columns: WRITE IT TOMORROW!
# # rename columns to match the map:
#         indexed_cols = []
#         col_num = 1
#         for col in df.columns:
#             if col == 'country':
#                 indexed_cols.append(col)
#             else:
#                 col_str = f'{sheet}_'.lower() + str(col_num)
#                 indexed_cols.append(col_str)
#                 col_num = col_num + 1
#         df.columns = indexed_cols

# create map:
def map_questions(file_path):
    """Reads an Excel file, returns a DataFrame of sheet_names and questions.
    """
    try: 
        df = read_eurobarometer(file_path, sheet_name='Content')
        df = df.drop(columns={'Question French'})
        df = df.rename(columns=str.lower)
        df = df.drop(df.index[0])
        df = df.replace(',', '', regex=True)
        return df
    except Exception as e:
        print(f'Something went wrong with building a map of questions: {e}.')

def map_answers(dict_of_dfs):
    """Maps answers from a dataframe.
    Saves them, matches them to questions and saves them to a file with questions.
    """
    try:
        all_rows = []  # Flat list to store every answer row across all sheets
        
        for sheet_name, df in dict_of_dfs.items():
            # Reset the counter for each individual sheet (so answer_id starts at 1 for each question)
            answer_counter = 1 
            
            for col in df.columns:
                if str(col).lower().strip() == 'country':
                    continue
                
                # Clean the column text
                col_str = str(col).lower().strip()    
                col_str = col_str.replace("'", "").replace(",", "")
                col_str = col_str.replace(":", "").replace(" ", "_")
                col_str = col_str.replace("(", "").replace(")", "")
                
                # Append a distinct dictionary for THIS specific answer row
                all_rows.append({
                    'sheet': sheet_name,
                    'answer_id': f"{sheet_name}_{answer_counter}",
                    'answer_text': col_str
                })
                
                answer_counter += 1 
        df_answers = pd.DataFrame(all_rows)
        return df_answers

    except Exception as e:
        print(f'Something went wrong with mapping answers: {e}.')
        return None

def write_map(df_questions, df_answers, map_path):
    """Merges together questions map and answers map. 
    Writes it to a csv file.
    """
    try:
        result_df = pd.merge(df_questions, df_answers, on='sheet', how='outer')
        result_df.to_csv(map_path)
    except Exception as e:
        print(f"Couldn't write questions/answers map: {e}.")

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

    path = './eurobarometer_data/eb_105.xlsx'
    
    # 1. Get the questions map (returns a Single DataFrame)
    questions = map_questions(path)
    
    # 2. Get the data dictionary (Do NOT pass sheet_name='Content' here!)
    # This reads all tabs, drops meta tabs, and returns a TRUE dictionary
    dictionary_test = read_eurobarometer(path) 

    dictionary_clean_test = clean_eurobarometer(dictionary_test)
    
    # 3. Map the answers using the full dictionary
    answers = map_answers(dictionary_clean_test)
    
    # 4. Save your mapping configuration file
    path_map = 'map_test.csv'
    write_map(questions, answers, path_map)
    
    print("Successfully built and saved maps!")

