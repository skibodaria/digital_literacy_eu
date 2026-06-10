# =====================================================================
# EDA DIGITAL SKILLS
# =====================================================================

# importing libraries:
#import io
import os
#import psycopg2
import pandas as pd
from dotenv import load_dotenv
#from functools import reduce 
#import re
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import numpy as np


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

def get_full_df(engine, table_name:str, sql=None):
    """Returns a DataFrame from PostgreSQL."""
    try: 
        if sql is None:
            query = f"SELECT * FROM public.{table_name}"
        else:
            query = sql
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        print(f"Something went wrong with {table_name} or your query {sql}: {e}.")

if __name__ == "__main__":
    engine = connect_postgres()
    custom_query = "SELECT country, year_2025 FROM public.isoc_ai_iaiu WHERE country = 'DE'"
    df_de = get_full_df(engine, table_name='isoc_ai_iaiu', sql=custom_query)
