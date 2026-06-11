import streamlit as st
import pandas as pd
import psycopg2

@st.cache_resource
def init_connection():
    """Establishes and caches the PostgreSQL connection using st.secrets."""
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["username"],
        password=st.secrets["postgres"]["password"]
    )

@st.cache_data
def load_tab_data(data_table_name, map_table_name):
    """
    Generic helper to load both the metrics table and its corresponding 
    indicator metadata dictionary table for any given tab.
    """
    conn = init_connection()
    
    df_data = pd.read_sql_query(f"SELECT * FROM {data_table_name};", conn)
    df_map = pd.read_sql_query(f"SELECT * FROM {map_table_name};", conn)
    
    # Convert the mapping dataframe into a fast-lookup Python dictionary
    # Assumes column names are 'indicator_code' and 'proper_name'
    mapping_dict = dict(zip(df_map['indicator_code'], df_map['dynamic_display_title']))
    
    return df_data, mapping_dict