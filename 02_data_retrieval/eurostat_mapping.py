# =====================================================================
# INDICATORS MAPPING EUROSTAT
# =====================================================================

import os
import io
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def fetch_and_load_eurostat_dictionary():
    """
    Downloads the master indicator definitions from Eurostat API 
    and bulk-loads them straight into PostgreSQL.
    """
    load_dotenv(dotenv_path='.env')
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    connection_string = f'dbname={db_name} user={db_user}'
    
    table_name = "eurostat_indicators"
    
    try:
        print("Fetching indicator definitions from Eurostat API...")
        # 1. Query Eurostat's master dimension metadata
        url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/INDIC_IS"
        response = requests.get(url)
        response.raise_for_status()

        # 2. Parse the XML data into a Pandas DataFrame
        root = ET.fromstring(response.content)
        
        # We explicitly map the 'xml' prefix alongside the SDMX prefixes
        namespaces = {
            's': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
            'c': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
            'xml': 'http://www.w3.org/XML/1998/namespace'  # <-- Fixes the prefix error
        }
        
        code_dict = []
        for code in root.findall('.//s:Code', namespaces):
            code_id = code.get('id')
            
            # Query using the mapped xml namespace prefix
            name_el = code.find(".//c:Name[@xml:lang='en']", namespaces)
            if name_el is not None:
                code_dict.append({'indicator_code': code_id, 'indicator_name': name_el.text})
        
        df = pd.DataFrame(code_dict)
        
        if df.empty:
            print("Warning: No indicators extracted from XML structure.")
            return

        # 3. Stream to PostgreSQL using the StringIO buffer
        output_buffer = io.StringIO()
        df.to_csv(output_buffer, index=False, header=True)
        output_buffer.seek(0)
        
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                cur.execute(f"""
                    CREATE TABLE {table_name} (
                        indicator_code VARCHAR PRIMARY KEY,
                        indicator_name VARCHAR
                    );
                """)
                
                sql = f"""
                    COPY {table_name} (indicator_code, indicator_name)
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER true, DELIMITER ',');
                """
                cur.copy_expert(sql, output_buffer)
                conn.commit()
                print(f"Successfully built table and imported {table_name}!")
                
    except Exception as e:
        print(f"Oooops, something went wrong with the dictionary: {e}")

if __name__ == "__main__":
    # ONLY run the dictionary process. The table loops are completely gone.
    fetch_and_load_eurostat_dictionary()