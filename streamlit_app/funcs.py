import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats 
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

def run_t_test_pair(df, column_list, suffix_to_remove, label_dict=None):
    """
    Loops through paired columns, pulls clean labels from a dictionary safely,
    calculates metrics, runs a paired t-test, and returns a perfectly ordered summary DataFrame.
    """
    summary_data = []
    
    # Loop through pairs (Group 1 / Group 2 columns)
    for i in range(0, len(column_list), 2):
        fem_col = column_list[i]
        male_col = column_list[i+1]
        
        # Step 1: Look up the full column name in the dictionary if provided
        raw_title = None
        if label_dict:
            raw_title = label_dict.get(fem_col, None)
            
        if raw_title:
            skill_label = raw_title.split(" (")[0].strip()
        else:
            skill_label = fem_col.replace(suffix_to_remove, '').replace('_', ' ').title()
        
        # Isolate columns and drop rows with missing country values
        cleaned_df = df[[male_col, fem_col]].dropna()
        
        if len(cleaned_df) > 0:
            mean_fem = cleaned_df[fem_col].mean()
            mean_male = cleaned_df[male_col].mean()
            gap = mean_male - mean_fem  
            
            # Paired t-test
            # t_stat, p_value = stats.ttest_rel(
            #     cleaned_df[fem_col], 
            #     cleaned_df[male_col], 
            #     nan_policy='omit'
            # )

            # Wilcoxon Signed-Rank Test
            wilcox_stat, p_value = stats.wilcoxon(cleaned_df[fem_col], cleaned_df[male_col])
            
            summary_data.append({
                'col_code': fem_col, # 💡 Keep the raw column code tracking flag here
                'Indicator': skill_label,
                'Valid Countries (N)': len(cleaned_df),
                'Female Avg (%)': round(mean_fem, 1),
                'Male Avg (%)': round(mean_male, 1),
                'Gap (Points)': round(gap, 1),
                'Wilcoxon P-Value': round(p_value, 4) if not pd.isna(p_value) else 'N/A',
                #'Wilcox_Stat': round(wilcox_stat,4),
                'Significant? (α=0.05)': '✅ Yes' if (not pd.isna(p_value) and p_value < 0.05) else '❌ No'
            })
            
    df_results = pd.DataFrame(summary_data)
    
    if df_results.empty:
        return df_results

    # 🎯 Step 2: Create a rank function based on the raw code substrings
    def get_skill_rank_by_label(label):
        if 'Above Basic' in label: return 1
        if 'Basic' in label:       return 2
        if 'Low' in label:         return 3
        if 'Narrow' in label:      return 4
        if 'Limited' in label:     return 5
        if 'No Skills' in label:   return 6
        return 7 # Fallback catch-all

    # 🎯 Sort structurally by label rank, then clean up helper columns
    df_results['sort_rank'] = df_results['Indicator'].apply(get_skill_rank_by_label)
    df_results = df_results.sort_values('sort_rank').drop(columns=['sort_rank']).reset_index(drop=True)
    df_results = df_results.drop(columns={'col_code'})
            
    return df_results