# =====================================================================
# BRIDGING INDICATORS AND TABLES | EUROSTAT
# =====================================================================

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# functions definitions

# connection (reused from EDA, fix it later)
def connect_postgres():
    """Creates an engine and connects to PostgreSQL."""
    load_dotenv()
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")

    if not db_name or not db_user:
        raise ValueError("Error: DB_NAME or DB_USER not found in environment variables. Check your .env file!")

    engine = create_engine(f"postgresql://{db_user}@localhost/{db_name}")
    print("SQLalchemy engine was created and can be used.")
    return engine

# building the bridge between indicators and tables
def build_table_indicator_bridge(tables_list_path):
    """Takes a list of Eurostat tables from documentation (string with path requested), 
    connects to PostgreSQL, requests the list of indicators per table, creates a dataframe,
    uploads it to PostgreSQL.
    Why: to be able to connect two tables together.
    """

    engine = connect_postgres()
    df_tables = pd.read_csv(tables_list_path)
    active_tables = df_tables.iloc[:,0].tolist() 
    
    bridge_records = []
    print("Scanning active data tables to map indicators...")
    for table in active_tables:
        try:
            query = f"SELECT DISTINCT indic_is FROM public.{table};"
            unique_indicators = pd.read_sql(query, con=engine)['indic_is'].tolist()
            
            for indicator in unique_indicators:
                bridge_records.append({
                    'table_code': table,
                    'indicator_code': indicator
                })
        except Exception as e:
            print(f"Skipping table {table} (not loaded yet or schema differs): {e}")
            
    df_bridge = pd.DataFrame(bridge_records)
    
    if df_bridge.empty:
        print("No connections found.")
        return
        
    print(f"Uploading {len(df_bridge)} mapping linkages to the database...")
    df_bridge.to_sql(
        'eurostat_bridge', 
        con=engine, 
        if_exists='replace', 
        index=False
    )
    
    print("Setting up Primary Key constraints on the bridge...")

    with engine.connect() as conn:
        with conn.begin():
            with conn.connection.cursor() as raw_cursor:
                raw_cursor.execute("ALTER TABLE eurostat_bridge ADD PRIMARY KEY (table_code, indicator_code);")
        
    print("Success! The bridge table is fully built.")

if __name__ == "__main__":
    build_table_indicator_bridge('eurostat_tables.csv')