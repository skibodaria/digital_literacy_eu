import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles

# -- Page configuration:
st.set_page_config(layout="wide")

# ==============================================================================
# DATA LOADING (Executed once and cached via your database.py)
# ==============================================================================
try:
    df_skills, skills_labels = funcs.load_tab_data("stg_dig_skills_demog", "mart_dig_skills_map")
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# ==============================================================================
# SIDEBAR GLOBAL FILTERS (Country Multi-Select)
# ==============================================================================
st.sidebar.header("Geo Filters")

country_col = 'clean_country_name'
available_countries = sorted(df_skills[country_col].unique())
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

df_filtered_skills = df_skills[df_skills[country_col].isin(selected_countries)]
df_filtered_baseline = df_baseline[df_baseline[country_col].isin(selected_countries)]

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.title("Digital Skills Analysis Workspace")
st.markdown("""
    ### Examining the Socio-Demographic Layers of European Digital Literacy
    This workspace breaks down the high, basic, and low digital skill distributions 
    across stratified population segments in the EU.
""")

st.write("---") # Visual divider line


# ==============================================================================
# MAIN TABS ARCHITECTURE
# ==============================================================================
tab_overview, tab_demographics, tab_deep_dive = st.tabs([
    "Overview", 
    "Demographic Stratification", 
    "Skill Metric Deep Dive"
])

# ==============================================================================
# --- TAB 1: OVERVIEW ---
# ==============================================================================
with tab_overview:
    
    st.subheader("Macro Trends & National Baselines")
    
    # --------------------------------------------------------------------------
    # 5 KPI METRIC COLUMNS (Averaged by Selected Countries)
    # --------------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.metric(label="Above Basic Skills", value=f"{df_filtered_baseline['i_dsk2_ab'].mean().round(2)}%")
        
    with kpi2:
        st.metric(label="Basic Skills", value=f"{df_filtered_baseline['i_dsk2_b'].mean().round(2)}%")
        
    with kpi3:
        st.metric(label="Low Skills", value=f"{df_filtered_baseline['i_dsk2_lw'].mean().round(2)}%")
        
    with kpi5:
        st.metric(label="Limited Skills", value=f"{df_filtered_baseline['i_dsk2_lm'].mean().round(2)}%")
    
    with kpi4:
        st.metric(label="Narrow Skills", value=f"{df_filtered_baseline['i_dsk2_n'].mean().round(2)}%")
   
    with kpi6:
        st.metric(label="No Digital Skills", value=f"{df_filtered_baseline['i_dsk2_x'].mean().round(2)}%")
        
    st.write("---")

    # --------------------------------------------------------------------------
    # TWO COLUMN LAYOUT: MAP (LEFT) & TEXT EXPLANATION (RIGHT)
    # --------------------------------------------------------------------------
    col_map, col_text = st.columns([3, 1])

    with col_map:
        st.markdown("### 🗺️ Geographic Distribution")
        
        # 1. Clean explicit mapping for the 5 baseline skill levels
        # Keys are what the user clicks; values match your baseline dataframe columns
        map_radio_options = {
            "Above Basic Skills": "i_dsk2_ab",
            "Basic Skills": "i_dsk2_b",
            "Low Skills": "i_dsk2_lw",
            "Narrow Skills": "i_dsk2_n",
            "Limited Skills": "i_dsk2_lm",
            "No Digital Skills": "i_dsk2_x"
        }
        
        # 2. Render horizontal radio buttons for quick toggling
        chosen_label = st.radio(
            "Select Skill Baseline to Map:",
            options=list(map_radio_options.keys()),
            horizontal=True
        )
        chosen_indicator_code = map_radio_options[chosen_label]
        
        # 3. Build the EU Choropleth Map using your TOTAL aggregation baseline dataframe
        fig = px.choropleth(
            df_filtered_baseline,                           
            locations='plotly_country_code',   
            locationmode='ISO-3',               
            color=chosen_indicator_code,                    
            hover_name='clean_country_name',  
            color_continuous_scale="teal",
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
            resolution=50
        )
        
        fig.update_layout(
            margin={"r":0, "t":10, "l":0, "b":0},
            coloraxis_colorbar=dict(title="% of Pop")
        )
        
        st.plotly_chart(fig, use_container_width=True)        
        
    with col_text:
        st.markdown("### WOW things here:")
        st.markdown(f"""
            * Country with the highest level of above basic digital skills: 
            * wow two
            * wow three
        """)

    with st.expander("Click to view Framework Methodology & Definitions"):
        st.markdown(
            """
            Eurostat measures citizens' digital proficiency via the Digital Skills Indicator (DSI), which is based 
            on [the European Commission's DigComp 2.0 framework](https://ec.europa.eu/eurostat/cache/metadata/en/isoc_sk_dskl_i21_esmsip2.htm#indicatorDisseminated). The methodology tracks a user's activities across five domains.

            **What Are Those Domains?**
            1. Information & Data Literacy:	Searching for information, reading news, health research, and online fact-checking.
            2. Communication & Collaboration: Emails, video calls, social media, messaging, and online civic voting/political expression.
            3. Digital Content Creation: Word processing, spreadsheets (basic & advanced), photo/video editing, file management, and programming.
            4. Safety & Privacy: Checking website security, reading privacy rules, disabling location services, and blocking cookies.
            5. Problem Solving: Installing apps, changing settings, online shopping/banking, selling items, or using online learning resources.

            **How the Overall Score is Calculated?**
            The final composite score groups individuals based on how many of the five sub-areas they successfully master:
            - Above Basic Skills: Scored "Above Basic" in all 5 areas.
            - Basic Skills: Scored "At least Basic" in all 5 areas (but didn't hit maximum in all 5).
            - Low Skills: Scored "At least Basic" in 4 areas (0 skills in 1 area).
            - Narrow Skills: Scored "At least Basic" in 3 areas (0 skills in 2 areas).
            - Limited Skills: Scored "At least Basic" in 2 areas (0 skills in 3 areas).
            - No Digital Skills: Scored "0 skills" in 4 or all 5 areas (despite recent internet use).
            - Not Applicable / Assessed: Individuals who have not used the internet at all in the past 3 months.
            """
        )

# ==============================================================================
# --- REGULAR TAB LAYOUTS ---
# ==============================================================================
with tab_demographics:
    st.subheader("Digital Skills vs. Sociodemographic Factors")
    st.write("Placeholder: Cross-tabulations and distributions segmented by Education, Gender, Urbanization, and Age groups.")

with tab_deep_dive:
    st.subheader("Granular Component Evaluation")
    st.write("Placeholder: In-depth breakdowns of specific subsets.")

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
           and ICT Usage collected in the framework od [ESS ICT Survey](https://ec.europa.eu/eurostat/web/microdata/collections-research/survey-ict-use-households-individuals)
""")