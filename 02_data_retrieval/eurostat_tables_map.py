# =====================================================================
# EUROSTAT TABLE CATALOG MAPPING
# =====================================================================

import os
import io
import requests
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def fetch_and_load_table_catalog():
    """
    Downloads Eurostat's active flat Table of Contents (TOC),
    extracts the raw table codes and English names, and bulk-loads them to PostgreSQL.
    """
    load_dotenv(dotenv_path='.env')
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    connection_string = f'dbname={db_name} user={db_user}'
    
    table_name = "eurostat_table_catalog"
    
    # Official updated Eurostat Catalogue API endpoint (TXT version)
    url = "https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en"
    
    try:
        print("Fetching Eurostat Table of Contents online...")
        response = requests.get(url)
        response.raise_for_status()
        
        # The file is a tab-separated text block with a header
        # We read it into Pandas using a StringIO wrapper
        raw_text = response.text
        df_raw = pd.read_csv(io.StringIO(raw_text), sep='\t')
        
        # Clean column spaces from the Eurostat output format
        df_raw.columns = df_raw.columns.str.strip()
        
        # We only need 'code', 'title', and 'type' columns
        # Filter for rows where type is 'dataset' or 'table' (ignores group folders)
        df_filtered = df_raw[df_raw['type'].isin(['dataset', 'table'])].copy()
        
        # Isolate and rename the destination dimensions
        df = df_filtered[['code', 'title']].rename(columns={
            'code': 'table_code',
            'title': 'table_name'
        })
        
        # Clean white spaces and cast text strings
        df['table_code'] = df['table_code'].astype(str).str.strip()
        df['table_name'] = df['table_name'].astype(str).str.strip()
        
        # Remove any unexpected duplicates to protect our PRIMARY KEY constraint
        df = df.drop_duplicates(subset=['table_code'])
        
        if df.empty:
            print("Warning: No active table rows were processed from the catalogue text.")
            return

        print(f"Processed {len(df)} unique tables. Streaming to PostgreSQL via COPY...")

        # Stream directly using the fast StringIO text buffer
        output_buffer = io.StringIO()
        df.to_csv(output_buffer, index=False, header=True)
        output_buffer.seek(0)
        
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                cur.execute(f"""
                    CREATE TABLE {table_name} (
                        table_code VARCHAR PRIMARY KEY,
                        table_name VARCHAR
                    );
                """)
                
                sql = f"""
                    COPY {table_name} (table_code, table_name)
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER true, DELIMITER ',');
                """
                cur.copy_expert(sql, output_buffer)
                conn.commit()
                print(f"Success! Rebuilt and imported {len(df)} rows into public.{table_name}!")
                
    except Exception as e:
        print(f"Oooops, something went wrong with the catalog: {e}")

if __name__ == "__main__":
    fetch_and_load_table_catalog()