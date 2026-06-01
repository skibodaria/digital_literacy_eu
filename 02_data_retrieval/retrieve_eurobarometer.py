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

# data extractor:
def read_eurobarometer(file_path:str, sheet_name=None):
    """Reads an Excel file to get each tab from it and save it a dictionary of pandas dataframes.
    Takes two arguments:
    - a path to the file (string)
    - sheet_name (a string); by defalut takes all data-strings (no meta-data tabs like Content and B (Countries))
    Returns dataframe (if sheet_name is Content) -- for questions/answers mapping;
    returns dictionary of dataframes (if sheet_name is not specified, process all the data tabs).
    """
    try: 
        # case 1: if meta-data (Content) is being processed for mapping:
        if sheet_name == 'Content':
            df_content = pd.read_excel(file_path, sheet_name='Content', header=4)
            return df_content
        # special case of meta-data on tab "B" with countries:
        elif sheet_name == 'B':
            print('You are trying to process meta-data tab "Countries".')
        # case 2: all tabs are being processed:
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
    """Helper function containing cleaning logic for a single DataFrame.
    Takes one dataframe.
    """
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

# clean full function (for dataframe):
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
        # case 1: Work with a single specified sheet
        if sheet is not None:
            if sheet not in dict_of_dfs:
                print(f"Sheet '{sheet}' not found in the dictionary.")
                return None
            return clean_single_sheet(dict_of_dfs[sheet], sheet)
            
        # case 2: Work with ALL sheets if sheet=None
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

# re-index columns (change long names to short codes) to be able to process to PostgreSQL:
def index_data(dict_of_dfs, sheet_name: str = None):
    """Renames columns of DataFrames to match a specific map structure (e.g., d70_1, d70_2).
    Takes two arguments:
    - dict_of_dfs: a dictionary of dataframes
    - sheet_name: (string, optional) Name of a specific tab. Default is None.
    
    Returns:
    - A single indexed DataFrame if sheet_name is provided.
    - A dictionary of indexed DataFrames if sheet_name=None.
    """
    
    def apply_indexing(df, sheet):
        """Helper to execute your exact renaming logic on a single dataframe."""
        df_copy = df.copy()
        indexed_cols = []
        col_num = 1
        
        for col in df_copy.columns:
            if str(col).lower().strip() == 'country':
                indexed_cols.append('country')
            else:
                col_str = f'{sheet}_'.lower() + str(col_num)
                indexed_cols.append(col_str)
                col_num += 1
                
        df_copy.columns = indexed_cols
        return df_copy

    try:
        # case 1: re-index a single specified sheet
        if sheet_name is not None:
            if sheet_name not in dict_of_dfs:
                print(f"Sheet '{sheet_name}' not found for indexing.")
                return None
            return apply_indexing(dict_of_dfs[sheet_name], sheet_name)
            
        # case 2: iterate and process all sheets using dictionary keys
        else:
            indexed_dict = {}
            for key_sheet_name, df in dict_of_dfs.items():
                indexed_dict[key_sheet_name] = apply_indexing(df, key_sheet_name)
            return indexed_dict
            
    except Exception as e:
        target = sheet_name if sheet_name is not None else "all sheets"
        print(f"Something went wrong while indexing columns for {target}: {e}.")
        return None

# create map:
def map_questions(file_path):
    """Reads an Excel file, returns a DataFrame of sheet_names and questions.
    Serves to save meta-data from a particular survey and being able to de-code the column names
    from indexed (question_id_n) to real (what was asked and answered in the survey).
    Returns a dataframe of questions and their codes.
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

# map survey answers:
def map_answers(dict_of_dfs):
    """Maps answers from a dataframe.
    Saves them, matches them to questions and saves them to a file with questions.
    Returns dictionary of dataframes.
    """
    try:
        all_rows = []
        for sheet_name, df in dict_of_dfs.items():
            answer_counter = 1 
            for col in df.columns:
                if str(col).lower().strip() == 'country':
                    continue
                col_str = str(col).lower().strip()    
                col_str = col_str.replace("'", "").replace(",", "")
                col_str = col_str.replace(":", "").replace(" ", "_")
                col_str = col_str.replace("(", "").replace(")", "")
                
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

# merges map to a one dataframe:
def merge_map(df_questions, df_answers):
    """Merges together questions map and answers map. 
    Returns a dataframe.
    """
    try:
        full_map_df = pd.merge(df_questions, df_answers, on='sheet', how='outer')
        return full_map_df
    except Exception as e:
        print(f"Couldn't merge questions/answers to a map dataframe: {e}.")

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

# create a MAP table for PostgreSQL:
def create_map_table(df):
    """This function creates a structure for a future map table in PostgreSQL database.
    It prepares the work of copy_expert for the mapping data.
    It takes one argument: a dataframe.
    It returns two SQL strings:
    - table structure (all columns typed as TEXT)
    - formatted columns (string for copy_expert)
    """
    raw_columns = df.columns.tolist()
    structure_elements = []
    for col in raw_columns:
        structure_elements.append(f'"{col}" text')
    table_structure = ', '.join(structure_elements)
    formatted_columns = ', '.join([f'"{col}"' for col in raw_columns])
    return table_structure, formatted_columns

# uploader:
def upload_to_postgres(df, connection_string:str, table_name: str, table_type: str='data'):
    """This function connects to PostgreSQL database, creates a table there and 
    uploads the table from the dataframe directly to PostgreSQL.
    It takes four arguments:
    - dataframe to be uploaded,
    - connection string which has database name (dbname) and user name (user) to connect
    to the desired PostgreSQL database,
    - table name (string) to be created on PostgreSQL,
    - type of table: either 'data' or 'map'.
    """
    if table_type == 'map':
        table_structure, formatted_columns = create_map_table(df)
    elif table_type == 'data':
         table_structure, formatted_columns = create_table(df)
    else:
        print(f"This type of table {table_type} doesn't exist. Try either 'map' or 'data'.")

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
        raise e

# process an Excel file final function:
def process_eurobarometer(
        file_path: str,
        data_table_name: str,
        map_table_name: str,
        connection_string: str
):
    """Runs the entire Eurobarometer ETL/ELT pipeline:
    1. Extracts and cleans meta-data (questions + answers mapping)
    2. Builds the mapping dataframe and uploads it to PostgreSQL
    3. Extracts, cleans, and merges all EU-27 data sheets.
    4. Dynamically builds and uploads the consolidated data table to PostgreSQL
    """
    try:
        print(f"Starting pipeline for {file_path}.")
        # ==========================================
        # 1. MAPPING PART
        # ==========================================
        print("--- Processing Meta-Data and Mapping")
        questions = map_questions(file_path)
        dict_all_sheets = read_eurobarometer(file_path)
        dict_all_sheets_clean = clean_eurobarometer(dict_all_sheets)
        answers = map_answers(dict_all_sheets_clean)
        map_df = merge_map(questions,answers)
        upload_to_postgres(map_df, connection_string, map_table_name, 'map')

        # ==========================================
        # 2. DATA PART
        # ==========================================
        print("--- Processing and Merging Data ---")
        indexed_dict = index_data(dict_all_sheets_clean)
        all_tabs = []

        for sheet_name, df in indexed_dict.items():
            if df is None or df.empty or df.shape[0] == 0:
                print(f"Skipping sheet 'sheet_name' -- contains no EU-27 member states.")
                continue
            all_tabs.append(df)
        
        if not all_tabs:
            print("Error: No valid EU-27 data sheets found to merge.")
            return
        
        df_final = reduce(lambda left, right: pd.merge(left, right, on=['country'], how='inner'), all_tabs)
        print(f"Final DataFrame created. Shape to upload: {df_final.shape}.")
        
        upload_to_postgres(df_final, connection_string, data_table_name, 'data')
        print(f"Successfully processed and uploaded everything for {file_path}.")

    except Exception as e:
        print(f"======= Unfortunately, pipeline failed: {e}.")
        raise e
              
# =====================================================================
# THE MAIN EXECUTION BLOCK
# =====================================================================
if __name__ == "__main__":

    load_dotenv(dotenv_path='.env')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    connection_string_final = f'dbname = {db_name} user = {db_user}'
    path_test = './eurobarometer_data/eb_105.xlsx'

    process_eurobarometer(path_test, 'eb_105_test', 'map_105_test', connection_string_final)

