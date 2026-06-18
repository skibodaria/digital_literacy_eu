import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats 
import psycopg2
import styles

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
                'Significant? (α=0.05)': '🏆 Yes' if (not pd.isna(p_value) and p_value < 0.05) else 'No'
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


def run_friedman_multigroups(
    df, 
    metrics_list, 
    group_suffixes, 
    group_labels, 
    metadata_dict=None
):
    """
    Executes dynamic multi-group significance tests (Friedman Chi-Square for 3+ groups, 
    Wilcoxon Signed-Rank for 2 groups) and generates an aggregate descriptive statistics table.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The data stream containing the target demographic columns.
    metrics_list : list
        List of base strings extracted from metadata (e.g., ['i_iday', 'i_iuai']).
    group_suffixes : list
        The specific database column suffixes matching the schema pattern (e.g., ['_i0_2', '_i3_4', '_i5_8']).
    group_labels : list
        Clean display titles mapped 1:1 to the suffixes (e.g., ['Low Edu', 'Medium Edu', 'High Edu']).
    metadata_dict : dict, optional
        Your official label mapping dictionary (e.g., usage_labels) to cleanly rename codes to display text.
        
    Returns:
    --------
    pd.DataFrame
    """
    summary_data = []
    num_groups = len(group_suffixes)
    
    for metric in metrics_list:
        # 1. Dynamically build expected column names
        target_cols = [f"{metric}{suffix}" for suffix in group_suffixes]
        
        # 2. Check if ALL necessary column dimensions are present in the dataframe
        if all(col in df.columns for col in target_cols):
            cleaned_df = df[target_cols].dropna()
            
            if len(cleaned_df) > 0:
                # Calculate group means dynamically
                means = [cleaned_df[col].mean() for col in target_cols]
                
                # Structural metric: Max absolute gap between the highest and lowest group means
                max_gap = max(means) - min(means)
                
                # 3. Route to the correct statistical test engine based on group count
                if num_groups >= 3:
                    # Multi-group non-parametric comparison
                    stat, p_value = stats.friedmanchisquare(*[cleaned_df[col] for col in target_cols])
                else:
                    # Fallback to pairwise Wilcoxon if only 2 groups are passed (e.g., Gender)
                    stat, p_value = stats.wilcoxon(cleaned_df[target_cols[0]], cleaned_df[target_cols[1]])
                
                # 4. Resolve clean display naming
                display_name = metric
                if metadata_dict:
                    # Look for the root metric or the first gendered variant as a lookup fallback
                    display_name = metadata_dict.get(metric, metadata_dict.get(f"{metric}_f_y16_74", metric))
                    # Apply your core layout text-stripping clean sequence
                    display_name = (
                        str(display_name)
                        .split(' - ')[0]
                        .replace('Internet:', '')
                        .replace('Media:', '')
                        .replace('(% of individuals)', '')
                        .strip()
                    )
                
                # 5. Populate structured row payload
                row_data = {
                    'Indicator': display_name,
                    'Valid Countries (N)': len(cleaned_df)
                }
                
                # Dynamically inject mean columns based on the group labels provided
                for label, mean_val in zip(group_labels, means):
                    row_data[f'{label} Avg (%)'] = round(mean_val, 2)
                
                # Inject performance gap and engine probability variables
                row_data['Max Gap (Points)'] = round(max_gap, 2)
                row_data['P-Value'] = round(p_value, 6) if not pd.isna(p_value) else 'N/A'
                row_data['Significant? (α=0.05)'] = '🏆 Yes' if (not pd.isna(p_value) and p_value < 0.05) else 'No'
                
                summary_data.append(row_data)
                
    return pd.DataFrame(summary_data)


def get_dynamic_subheader(df_filtered, title_prefix="Digital Activities Comparison"):
    """Generates a consistent subheader string based on country selection."""
    selected_count = df_filtered['clean_country_name'].nunique()
    country_list = df_filtered['clean_country_name'].unique().tolist()
    
    if selected_count == 1:
        return f"{title_prefix} — {country_list[0]}"
    elif selected_count >= 27:
        return f"{title_prefix} — EU Aggregate"
    elif selected_count <= 3:
        return f"{title_prefix} — {', '.join(country_list)}"
    else:
        return f"{title_prefix} — Aggregated ({selected_count} Countries)"
    
def render_demographic_chart(df_filtered, group_cols, group_labels, metadata, color_map=None):
    """
    Renders a dynamic horizontal bar chart comparing demographic groups.

    Parameters:
    -----------
    df_filtered : pd.DataFrame
        The subsetted dataframe containing the demographic columns.
    group_cols : list
        A list of column names in the dataframe corresponding to the demographic 
        groups, arranged in sequential order (e.g., [fem_col1, male_col1, ...]).
    group_labels : list
        A list of display strings corresponding to the columns in group_cols 
        (e.g., ['Female', 'Male']).
    metadata : dict
        A mapping dictionary where keys are raw column names (or base indicators) 
        and values are the clean titles to be displayed as y-axis labels.

    Returns:
    --------
    None
        This function performs side-effects by rendering Streamlit widgets (selectbox) 
        and a Plotly figure directly to the app interface.
    """
    selected_group = st.selectbox("Select Demographic View:", ["All"] + group_labels)

    chart_summary_rows = []
    
    step = len(group_labels)
    for i in range(0, len(group_cols), step):
        current_cols = group_cols[i : i+step]
        
        if all(col in df_filtered.columns for col in current_cols):
            means = [df_filtered[col].mean() for col in current_cols]
            
            raw_title = metadata.get(current_cols[0], current_cols[0])
            display_label = str(raw_title).split(' - ')[0].replace('Internet:', '').replace('Media:', '').strip()
            
            row = {'Indicator': display_label}
            for label, val in zip(group_labels, means):
                row[label] = round(val, 1)
            chart_summary_rows.append(row)

    if chart_summary_rows:
        df_chart = pd.DataFrame(chart_summary_rows)
        df_melted = df_chart.melt(id_vars=['Indicator'], var_name='Group', value_name='Percentage (%)')
        df_melted = df_melted.sort_values('Percentage (%)')
        
        if selected_group != "All":
            df_melted = df_melted[df_melted['Group'] == selected_group]

        fig = px.bar(
            df_melted, x='Percentage (%)', y='Indicator', color='Group', barmode='group',
            #color_discrete_map=styles.EU_CORNFLOWER,
            height=450, labels={'Percentage (%)': 'Share', 'Group': 'Demographic'}
        )
        
        fig.update_layout(xaxis_title="Average Percentage (%)", yaxis_title=None, 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
        fig.update_xaxes(showgrid=True, gridcolor='rgba(226, 232, 240, 0.5)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for this selection.")


def extract_demographic_metrics(df):
    """
    Scans a dataframe's columns and extracts structured base metrics 
    and sequential chart-ready column lists for all four demographics.
    """
    columns = df.columns
    age_tags = ['y16_19', 'y20_24', 'y25_34', 'y35_44', 'y45_54', 'y55_64', 'y65_74']
    
    gen_usage = [c for c in columns if ('_f_' in c) or ('_m_' in c)]
    gen_metrics = sorted(list(set([c.split('_f_')[0] for c in columns if '_f_' in c])))
    
    # 2. Education
    edu_metrics = sorted(list(set([c.split('_i0_2')[0] for c in columns if '_i0_2' in c])))
    edu_usage = []
    for m in edu_metrics:
        # 🎯 Order matters! This keeps groups side-by-side for the chart loops
        edu_usage.extend([f"{m}_i0_2", f"{m}_i3_4", f"{m}_i5_8"])
        
    # 3. Urbanization
    urban_metrics = sorted(list(set([c.split('_ind_deg1')[0] for c in columns if '_ind_deg1' in c])))
    urban_usage = []
    for m in urban_metrics:
        # 🎯 Order matters! This keeps groups side-by-side for the chart loops
        urban_usage.extend([f"{m}_ind_deg1", f"{m}_ind_deg2", f"{m}_ind_deg3"])
        
    raw_age_cols = [
        c for c in columns 
        if any(tag in c for tag in age_tags) and not ('_f_' in c or '_m_' in c)
    ]
    age_metrics = sorted(list(set([c.split('_y16_19')[0] for c in raw_age_cols if '_y16_19' in c])))
    age_usage = []
    for m in age_metrics:
        age_usage.extend([f"{m}_{tag}" for tag in age_tags])
        
    return {
        "gender": {"base_metrics": gen_metrics, "chart_cols": gen_usage},
        "education": {"base_metrics": edu_metrics, "chart_cols": edu_usage},
        "urbanization": {"base_metrics": urban_metrics, "chart_cols": urban_usage},
        "age": {"base_metrics": age_metrics, "chart_cols": age_usage}
    }

def add_authorship_footer():
    """
    Renders a standardized, minimalist authorship sign at the bottom of the page.
    """
    st.write("---")
    st.caption(
        """
        **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025), [Eurobarometer Standard (104)](https://europa.eu/eurobarometer/surveys/detail/3378) 
        and [Eurobarometer Special (sp566)](https://europa.eu/eurobarometer/surveys/detail/3362).
        \n
        <div style="text-align: left; color: #888888; font-size: 0.85rem; padding-top: 10px;">
            Designed & Engineered by <strong>Daria Skibo</strong> | Capstone Project © 2026
        </div>
        """,
        unsafe_allow_html=True
    )

def read_boxplot():
    with st.expander("**How to Read Boxplots**"):
        st.markdown(
            """
            * **The Middle Line**: The line inside the box represents the _median_ (the exact middle value of the data). 
            Half the data is above this line, and half is below.
            * **The Box**: The box itself represents the middle **50\\%** of the data (the "_interquartile range_"). 
            It shows where the bulk of the information is clustered.
            * **The "Whiskers"**: The lines extending from the box show the _range_ of the rest of the data. 
            They help spot the typical spread before hitting extreme values.
            * **The Dots**: Any individual dots outside the whiskers are _outliers_. 
            These are data points that are unusually high or low compared to the rest of the group.
        """)

def read_pearson():
    with st.expander("How to Understand Pearson Correlation Coefficients ($r$):"):
        st.markdown(
            """
            Here Pearson Coefficients ($r$) compare macro institutional sentiment variables with core E-Government adoption actions.
            There are **two** important characteristics here:
            * **Strength** ($r$ value): how tightly the data points on a scatter plot follow the line;
            * **Significance** ($p$ value): is the correlation a **real** thing, or is it a random coincidence.
            So, the correlation can be strong but abdolutely not statistically significant.

            What is consifered "strong" for $r$ value:
            * 0.00 - 0.19 : Very weak
            * 0.20 - 0.39 : Weak
            * 0.40 - 0.59 : Moderate
            * 0.60 - 0.79 : Strong
            * 0.80 - 1.00 : Very Strong

            What is considered "significant" for $p$ value:
            * $p < 0.05$: statistically significant (we can't say that something is random)
            * $p > 0.05$: quite a chance (more than 5%) that what we see is just random.
        """)