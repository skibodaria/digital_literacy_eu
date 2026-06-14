import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles
import scipy.stats as stats

# -- Page configuration:
st.set_page_config(layout="wide")
COLOR_MAPS = {
    "education": {'Low Edu': '#cbd5e1', 'Medium Edu': '#64748b', 'High Edu': '#0f172a'},
    "gender": {'Female': '#498cdb', 'Male': '#001f63'},
    "urban": {'Cities': '#3b82f6', 'Suburbs': '#60a5fa', 'Rural': '#93c5fd'}
}

# ==============================================================================
# DATA LOADING (Executed once and cached via database.py)
# ==============================================================================
try:
    df_usage, usage_labels = funcs.load_tab_data("stg_usage_demog", "mart_usage_map")
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    df_ai, ai_labels = funcs.load_tab_data("stg_ai","mart_indicators")
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# ==============================================================================
# METRICS CONFIGURATION (Global Tab Mappings)
# ==============================================================================
usage_maps = funcs.extract_demographic_metrics(df_usage)

gen_metrics = usage_maps["gender"]["base_metrics"]
gen_columns = usage_maps["gender"]["chart_cols"]

edu_metrics = usage_maps["education"]["base_metrics"]
edu_columns = usage_maps["education"]["chart_cols"]

urban_metrics = usage_maps["urbanization"]["base_metrics"]
urban_columns = usage_maps["urbanization"]["chart_cols"]

age_metrics  = usage_maps["age"]["base_metrics"]
age_columns = usage_maps["age"]["chart_cols"]

# ==============================================================================
# SIDEBAR GLOBAL FILTERS (Country Multi-Select)
# ==============================================================================
st.sidebar.header("Geo Filters")

country_col = 'clean_country_name'
available_countries = sorted(df_usage[country_col].unique())
select_all = st.sidebar.checkbox("Select All Countries", value=True)

if select_all:
    selected_countries = available_countries
    st.sidebar.multiselect(
        "Active Countries", options=available_countries, 
        default=available_countries, disabled=True, placeholder="All countries active"
    )
else:
    selected_countries = st.sidebar.multiselect(
        "Select Countries", options=available_countries, default=[]
    )

if not selected_countries:
    st.info("Please select at least one country from the sidebar menu to display the visualizations.")
    st.stop()

df_filtered_usage = df_usage[df_usage[country_col].isin(selected_countries)]
df_filtered_ai = df_ai[df_ai[country_col].isin(selected_countries)]
df_filtered_baseline = df_baseline[df_baseline[country_col].isin(selected_countries)]

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.title("Internet Usage Analysis Workspace")
st.markdown("""
    This module shifts focus from general literacy levels to real-world behavioral utility. 
    It tracks how individuals engage with the internet across the EU—ranging from baseline communication 
    frequency to advanced interactions like generative AI usage, civic engagement, misinformation exposure, 
    and encountered usage obstacles.
    """)

st.write("---")

# ==============================================================================
# COMPACT TWO-TAB ARCHITECTURE
# ==============================================================================
tab_overview, tab_demographics = st.tabs([
    "Overview & National Baselines", 
    "Demographic Variance Gaps"
])

# Advanced title formatting helper function
def clean_metric_label(raw_string):
    return (str(raw_string)
            .replace('Internet:', '')
            .replace('Media:', '')
            .replace('eID Non-Use:', '')
            .replace('e-Gov:', '')
            .replace('(% of individuals)', '')
            .strip())

# ==============================================================================
# --- TAB 1: OVERVIEW ---
# ==============================================================================
with tab_overview:
    st.subheader("Macro Trends & National Baselines")
    
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric(label="Daily Internet Usage", value=f"{df_filtered_baseline['i_iday'].mean().round(1)}%")
    with kpi2:
        st.metric(label="AI Tools Adoption", value=f"{df_filtered_baseline['i_iuai'].mean().round(1)}%")
    with kpi3:
        st.metric(label="Civic Participation", value=f"{((df_filtered_usage['i_iucpp_f_y16_74'].mean().round(1)+df_filtered_usage['i_iucpp_m_y16_74'].mean().round(1))/2).round(1)}%")
    with kpi4:
        st.metric(label="Playing Games", value=f"{((df_filtered_usage['i_iupdg_m_y16_74'].mean().round(1)+df_filtered_usage['i_iupdg_f_y16_74'].mean().round(1))/2).round(1)}%")
    with kpi5:
        st.metric(label="Messaging", value=f"{((df_filtered_usage['i_iuchat1_m_y16_74'].mean().round(1)+df_filtered_usage['i_iuchat1_f_y16_74'].mean().round(1))/2).round(1)}%")
    with kpi6:
        st.metric(label="Encountered Difficulties", value=f"{((df_filtered_usage['i_iups_m_y16_74'].mean().round(1)+df_filtered_usage['i_iups_f_y16_74'].mean().round(1))/2).round(1)}%")
        
    st.write("---")

    col_skills_map, col_skills_text = st.columns([3, 1])

    with col_skills_map:
        st.markdown("### Geographic Distribution")
        
        map_radio_options = {
            "Using Internet Daily": "i_iday",
            "Using AI Tools": "i_iuai",
            "Civic and Political Participation Online": "i_iucpp",
            "Playing Online Games": "i_iupdg",
            "Expressing Political Opinion on Social Media":"i_iupol2",
            "Facing Doubtful/Untrue Info Online":"i_udi",
            "Encountering Difficulties While Using Internet":"i_iups",
            "Messaging": 'i_iuchat1',
            "Never Used Internet": "i_iux"
        }
        
        chosen_label = st.radio(
            "Select Skill Baseline to Map:",
            options=list(map_radio_options.keys()),
            horizontal=True
        )
        chosen_indicator_code = map_radio_options[chosen_label]
        
        fig = px.choropleth(
            df_filtered_baseline,                           
            locations='plotly_country_code',   
            locationmode='ISO-3',               
            color=chosen_indicator_code,                    
            hover_name='clean_country_name',  
            color_continuous_scale=styles.EU_CORNFLOWER,
            height=520
        )
        
        fig.update_geos(
            projection_type="mercator",   
            center=dict(lon=10, lat=52),  
            projection_scale=4.5,         
            visible=False,                
            showframe=False,              
            showcoastlines=True,          
            coastlinecolor="LightGray",
            bgcolor="rgba(0,0,0,0)"
        )
        
        fig.update_layout(
            margin={"r":0, "t":10, "l":0, "b":0},
            coloraxis_colorbar=dict(title="% of Pop")
        )
        st.plotly_chart(fig, use_container_width=True)        
        
    with col_skills_text:
        st.markdown("### Section Context")
        st.markdown(f"""
            This geographic baseline displays aggregated usage trends across individual member states. 
            Use the radio buttons above to shift the spatial layout between communication frequency, 
            frontier AI adoption, or friction layers.
        """)

        with st.expander("Framework Methodology"):
            st.markdown("""
                * **Data Scope:** Uniform country aggregates across selected valid European states.
                * **Base Variable Evaluation:** Indicators represent percentages of the population aged 16-74.
            """)

# ==============================================================================
# --- TAB 2: DEMOGRAPHIC GAPS (CONSOLIDATED) ---
# ==============================================================================
with tab_demographics:
    st.header("Comparative Demographic Variance Analysis")
    st.markdown("""
        Analyze structural variations across the European Union across four principal demographic splits.
        The tables below run static statistical validations (Wilcoxon Signed-Rank and Friedman Chi-Square) 
        across all 27 member states to isolate genuine structural gaps from random variance.
    """)

    # ------------------ SIGNIFICANCE MATRICES SECTION ------------------
    col_tables_left, col_insights_right = st.columns([3, 2])

    with col_tables_left:
        
        # --- 1. Gender Significance Matrix ---
        with st.expander("Gender Gaps Significance Matrices (Usage)", expanded=True):
            paired_gen_columns = []
            for metric in gen_metrics:
                paired_gen_columns.extend([f"{metric}_f_y16_74", f"{metric}_m_y16_74"])

            df_gender_res = funcs.run_t_test_pair(df_usage, paired_gen_columns, '_f_y16_74', usage_labels)
            df_gender_res.columns = ['Indicator', 'Valid Countries (N)', 'Female Avg (%)', 'Male Avg (%)', 'Gap (Points)', 'Wilcoxon P-Value', 'Significant? (α=0.05)']
            df_gender_res['Indicator'] = df_gender_res['Indicator'].apply(clean_metric_label)
            
            # Drop Averages to keep matrix clean
            cols_to_drop_g = [c for c in ["Female Avg (%)", "Male Avg (%)"] if c in df_gender_res.columns]
            df_gender_res = df_gender_res.drop(columns=cols_to_drop_g)
            
            st.dataframe(df_gender_res, column_config={"Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"), "Wilcoxon P-Value": st.column_config.NumberColumn(format="%.4f")}, hide_index=True, use_container_width=True)

        # --- 2. Age Cohorts Matrix ---
        with st.expander("Age Cohorts Variance Matrix (Usage)", expanded=True):
            df_age_res = funcs.run_friedman_multigroups(df_usage, age_metrics, ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'], usage_labels)
            if not df_age_res.empty:
                df_age_res['Indicator'] = df_age_res['Indicator'].apply(clean_metric_label)
                cols_to_drop_a = [f"{lbl} Avg (%)" for lbl in ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']]
                df_age_res = df_age_res.drop(columns=cols_to_drop_a, errors='ignore')
                st.dataframe(df_age_res, column_config={"Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"), "P-Value": st.column_config.NumberColumn(format="%.4f")}, hide_index=True, use_container_width=True)

        # --- 3. Education Levels Matrix ---
        with st.expander("Education Level Variance Matrix (Usage)", expanded=True):
            df_edu_res = funcs.run_friedman_multigroups(df_usage, edu_metrics, ['_i0_2', '_i3_4', '_i5_8'], ['Low Edu', 'Medium Edu', 'High Edu'], usage_labels)
            if not df_edu_res.empty:
                df_edu_res['Indicator'] = df_edu_res['Indicator'].apply(clean_metric_label)
                cols_to_drop_e = [f"{lbl} Avg (%)" for lbl in ['Low Edu', 'Medium Edu', 'High Edu']]
                df_edu_res = df_edu_res.drop(columns=cols_to_drop_e, errors='ignore')
                st.dataframe(df_edu_res, column_config={"Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"), "P-Value": st.column_config.NumberColumn(format="%.6f")}, hide_index=True, use_container_width=True)

        # --- 4. Urbanization Density Matrix ---
        with st.expander("Urbanization Split Variance Matrix (Usage)", expanded=True):
            df_urban_res = funcs.run_friedman_multigroups(df_usage, urban_metrics, ['_ind_deg1', '_ind_deg2', '_ind_deg3'], ['Cities', 'Suburbs', 'Rural'], usage_labels)
            if not df_urban_res.empty:
                df_urban_res['Indicator'] = df_urban_res['Indicator'].apply(clean_metric_label)
                cols_to_drop_u = [f"{lbl} Avg (%)" for lbl in ['Cities', 'Suburbs', 'Rural']]
                df_urban_res = df_urban_res.drop(columns=cols_to_drop_u, errors='ignore')
                st.dataframe(df_urban_res, column_config={"Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"), "P-Value": st.column_config.NumberColumn(format="%.4f")}, hide_index=True, use_container_width=True)

    with col_insights_right:
        st.subheader("Cross-Dimension Structural Insights")
        with st.expander("**1. Frontier Tech Skews Men and Urban Hubs**"):
            st.write("""
                Advanced digital tasks show compounding advantages. Men outpace women in emerging AI adoption by 3.5 points, 
                while metropolitan hubs hold a massive 15.4 point acceleration curve over rural sectors on identical metrics.
            """)
        with st.expander("**2. Public Voices vs Private Channels**"):
            st.write("""
                Women maintain a stable lead in routine private communication layers (+3.0 points in messaging). 
                However, digital public-facing actions (civic commentary, political tracking) showcase statistically significant skews toward male and highly educated brackets.
            """)
        with st.expander("**3. The Egalitarian Distribution of Friction**"):
            st.write("""
                Interestingly, encountering technical difficulties features high p-values across all tests. 
                This denotes that digital complexity acts as a uniform friction layer, impacting populations evenly regardless of gender or geography.
            """)

    st.write("---")
    
    # ------------------ INTERACTIVE COMPONENT VISUALIZATION STUDIO ------------------
    st.subheader("Demographic Component Studio")
    st.caption(funcs.get_dynamic_subheader(df_filtered_usage))

    # Single selector layout to drive any dimension selection on demand
    col_sel_dim, col_sel_filter = st.columns([2, 2])
    
    with col_sel_dim:
        selected_dimension = st.selectbox(
            "Select Demographic Dimension to Chart:",
            options=["Gender", "Age Cohorts", "Education Levels", "Urbanization Levels"]
        )

    # Contextually update variables based on chosen selection
    if selected_dimension == "Gender":
        active_cols = gen_columns
        active_labels = ['Female', 'Male']
        active_color = COLOR_MAPS["gender"]
    elif selected_dimension == "Age Cohorts":
        active_cols = age_columns
        active_labels = ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']
        active_color = None
    elif selected_dimension == "Education Levels":
        active_cols = edu_columns
        active_labels = ['Low Edu', 'Medium Edu', 'High Edu']
        active_color = COLOR_MAPS["education"]
    else:
        active_cols = urban_columns
        active_labels = ['City', 'Town/Suburbs', 'Rural Areas']
        active_color = COLOR_MAPS["urban"]

    # Render unified chart dynamically
    funcs.render_demographic_chart(
        df_filtered_usage, 
        active_cols, 
        active_labels, 
        usage_labels,
        color_map=active_color
    )

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
    and ICT Usage collected in the framework of the ESS ICT Survey.
""")