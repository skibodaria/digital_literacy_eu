# =====================================================================
# EU-27 COUNTRY COORDINATES LOADING PIPELINE
# =====================================================================

import os
import io
import requests
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def load_eu_country_coordinates():
    """
    Fetches canonical country coordinates, filters strictly for the 27 EU 
    member states (handling the Eurostat 'EL' exception), and loads to PostgreSQL.
    """
    load_dotenv()
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    connection_string = f'dbname={db_name} user={db_user}'
    
    table_name = "countries"
    
    # Define the strict EU-27 country code list (Eurostat format)
    eu_countries = [
        'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
        'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
        'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE'
    ]
    
    url = "https://developers.google.com/public-data/docs/canonical/countries_csv"
    
    try:
        print("Fetching country coordinates dataset online...")
        tables = pd.read_html(url)
        df_raw = tables[0]
        
        # Standardize column names
        df = df_raw.rename(columns={
            'country': 'country_code',
            'name': 'country_name',
            'latitude': 'lat',
            'longitude': 'lon'
        })
        
        # Ensure country codes are clean, uppercase strings
        df['country_code'] = df['country_code'].astype(str).str.upper().str.strip()
        
        print("Aligning standard ISO codes with Eurostat exceptions...")
        # Handle Greece exception: Duplicate 'GR' rows as 'EL' so it can be filtered/joined correctly
        greece_data = df[df['country_code'] == 'GR'].copy()
        if not greece_data.empty:
            greece_data['country_code'] = 'EL'
            df = pd.concat([df, greece_data], ignore_index=True)
            
        # Strict Filtering: Keep ONLY the 27 specific country codes you requested
        df_filtered = df[df['country_code'].isin(eu_countries)].copy()
        
        # Double-check if we captured all 27 rows
        found_countries = df_filtered['country_code'].nunique()
        print(f"Filtering complete. Kept {found_countries} out of 27 target EU countries.")

        # Stream straight into PostgreSQL
        output_buffer = io.StringIO()
        df_filtered.to_csv(output_buffer, index=False, header=True)
        output_buffer.seek(0)
        
        print(f"Connecting to database '{db_name}' to build table...")
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                cur.execute(f"""
                    CREATE TABLE {table_name} (
                        country_code VARCHAR PRIMARY KEY,
                        country_name VARCHAR,
                        lat NUMERIC,
                        lon NUMERIC
                    );
                """)
                
                sql = f"""
                    COPY {table_name} (country_code, lat, lon, country_name)
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER true, DELIMITER ',');
                """
                cur.copy_expert(sql, output_buffer)
                conn.commit()
                print(f"Success! Imported {len(df_filtered)} EU country records into public.{table_name}")
                
    except Exception as e:
        print(f"Oops, pipeline failed: {e}")

if __name__ == "__main__":
    load_eu_country_coordinates()