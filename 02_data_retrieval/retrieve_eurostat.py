# =====================================================================
# DATA RETRIEVAL EUROSTAT
# =====================================================================

# importing libraries:
import io
import os
import eurostat
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# defining the function
def fetch_and_load_eurostat(dataset_id:str):
    """
    Downloads a dataset from Eurostat and bulk-loads it dynamically into PostgreSQL.
    """

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    connection_string = f'dbname={db_name} user={db_user}'
    
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            try:
                print(f"Starting pipeline for dataset: {dataset_id}...")
                df = eurostat.get_data_df(dataset_id)
                df = df.rename(columns={r'geo\TIME_PERIOD':'country'})
                df.columns = [str(col).strip() for col in df.columns]
                
                cleaned_columns = []
                for col in df.columns:
                    clean_col = col.replace('.0', '')
                    if clean_col.isdigit() and len(clean_col) == 4:
                        cleaned_columns.append(f"year_{clean_col}")
                    else:
                        cleaned_columns.append(col)
                df.columns = cleaned_columns

                raw_columns = df.columns.tolist()
                output_buffer = io.StringIO()
                df.to_csv(output_buffer, index=False, header=True)
                output_buffer.seek(0)

                structure_elements = []
                for col in raw_columns:
                    if str(col).startswith("year_"):
                        structure_elements.append(f'"{col}" numeric')
                    else:
                        structure_elements.append(f'"{col}" varchar')
                table_structure = ', '.join(structure_elements)

                cur.execute(f"DROP TABLE IF EXISTS {dataset_id};")
                cur.execute(f"CREATE TABLE {dataset_id} ({table_structure});")

                formatted_cols = ", ".join([f'"{col}"' for col in raw_columns])
                sql = f"""
                    COPY {dataset_id} ({formatted_cols})
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER true, DELIMITER ',');
                """

                cur.copy_expert(sql, output_buffer)
                conn.commit()
                print(f"Successfully built table and imported {dataset_id} dynamically!")
                
            except Exception as e:
                print(f"Oooops, something went wrong: {e}")
                conn.rollback()

# =====================================================================
# THE MAIN EXECUTION BLOCK
# =====================================================================
if __name__ == "__main__":
    # This code only runs when you execute this file directly.
    
    # get the .env file:
    load_dotenv(dotenv_path='.env')
    
    # read the file with all tables names and codes:
    df_tables = pd.read_csv('eurostat_tables.csv')

    # get the list of table codes:
    table_codes = df_tables.iloc[:,0].tolist()
    
    # trigger the function for each table in the metadata file:
    for table_code in table_codes:
        fetch_and_load_eurostat(table_code)