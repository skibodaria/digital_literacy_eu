import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles


# ==========================================
# DATA LOADING (Executed once and cached)
# ==========================================
try:
    # Tab 1 & 2: Baseline Mart & Metadata
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    
    # Tab 4: E-Governance Data & Metadata
    df_egov, egov_labels = funcs.load_tab_data("stg_gov_demog_2025", "mart_indicators")
    
    # add more dataframes/tables here
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# --- HEADER & PRESENTATION CONTEXT ---
st.title("🇪🇺 Digital Skills, Internet Usage, E-Governance, and Civic Trust")
st.markdown("""
    **Graduation Capstone Project** | An analysis of 27 EU Member States utilizing Eurostat & Eurobarometer data.\n
    This application investigates how structural digital baselines condition human trust and behavioral outcomes across Europe.
""")

# --- SIDEBAR GLOBAL FILTERS ---
st.sidebar.header("Country")
available_countries = sorted(df_baseline['clean_country_name'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries to Filter",
    options=available_countries,
    default=available_countries
)

# Filter the baseline dataframe in memory for speedy rendering
df_filtered = df_baseline[df_baseline['clean_country_name'].isin(selected_countries)]

# --- TABS CONFIGURATION ---
tabs = st.tabs([
    "Overview", 
    "Research Questions", 
    "Data",
    "Pipeline & Methods"
])

# ==========================================
# TAB 1: PROJECT OVERVIEW
# ==========================================
with tabs[0]:
    st.subheader("Intro to EU Digital Mapping | Main Metrics")
    st.markdown("""
        I need to add here more information about the project -- what is it about, what i'm trying to understand, 
        why ii is valid etc. What are the main concepts i'm looking into and why there is a map here.
    """)
    display_name_to_code = {v: k for k, v in baseline_labels.items()}
    available_columns = df_filtered.columns.tolist()
    filtered_display_options = {
        proper_name: code 
        for proper_name, code in display_name_to_code.items() 
        if code in available_columns
    }

    filtered_display_options = dict(sorted(filtered_display_options.items()))
    
    # KPI Row
    # --- 1. INJECT CUSTOM KPI CARD STYLE OVERRIDES ---
    st.markdown("""
        <style>
        /* Define the structure for your custom metric card */
        .kpi-card {
            background-color: #41748d;       /* Darker teal card background */
            border: 1px solid #4A857A;       /* Crisp, subtle border */
            border-radius: 8px;              /* Clean rounded corners */
            padding: 15px 20px;              /* Padding inside the card */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Soft drop shadow */
            text-align: center;              /* Center align text metrics */
            margin-bottom: 15px;             /* Spacing below the rows */
        }
        
        /* Style the small uppercase metric label text */
        .kpi-label {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;       /* Light gray for high contrast on teal */
            text-transform: uppercase;       /* Professional dashboard aesthetic */
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        /* Style the massive bold metric value text */
        .kpi-value {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;       /* Pristine white values */
        }
        </style>
    """, unsafe_allow_html=True)


    # --- 2. THE UPDATED KPI ROW LAYOUT ---
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Basic+ Digital Skills</div>
                <div class="kpi-value">{df_filtered['i_dsk2_bab'].mean().round(2)}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">EU Tagret by 2030</div>
                <div class="kpi-value">80%</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Daily Internet Usage</div>
                <div class="kpi-value">{df_filtered['i_iday'].mean().round(2)}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">eID Usage</div>
                <div class="kpi-value">{df_filtered['i_ieid'].mean().round(2)}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">AI Usage</div>
                <div class="kpi-value">{df_filtered['i_iuai'].mean().round(2)}%</div>
            </div>
        """, unsafe_allow_html=True)


    # col1, col2, col3, col4, col5 = st.columns(5)
    # col1.metric(label="Avg High Digital Skills", value=df_filtered['i_dsk2_ab'].mean().round(2))
    # col2.metric(label="Analyzed Countries", value=f"{len(selected_countries)} / 27")
    # col3.metric(label="Avg Daily Internet Usage", value=df_filtered['i_iday'].mean().round(2))
    # col4.metric(label="Avg AI Usage", value=df_filtered['i_iuai'].mean().round(2))
    # col5.metric(label="Avg National Governmnet Trust", value=df_filtered['tr_nat_gov'].mean().round(2))
    
    st.markdown("---")


    # Dynamically select indicator for map visualization
    selected_title = st.selectbox(
        "Select Indicator:",
        options=list(filtered_display_options.keys())
    )
    chosen_indicator_code = filtered_display_options[selected_title]
        
    st.markdown(f"### {selected_title}") 
    
    # 1. Generate the Choropleth Figure
    fig = px.choropleth(
        df_filtered,                           
        locations='plotly_country_code',   
        locationmode='ISO-3',               
        color=chosen_indicator_code,                    
        hover_name='clean_country_name',    
        hover_data=[chosen_indicator_code], 
        color_continuous_scale=styles.EU_CORNFLOWER,
        title=None,
        height=700
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br><br>Value: %{z:.2f}%<extra></extra>"
    )
    # 2. Apply your Geospatial Projections (Mercator + Malta high-resolution fix)
    fig.update_geos(
        projection_type="mercator",   
        center=dict(lon=10, lat=52),  
        projection_scale=4.5,         
        visible=False,                
        showframe=False,              
        showcoastlines=True,          
        coastlinecolor="LightGray",
        resolution=50,
        bgcolor="rgba(0,0,0,0)" # transperency                 
    )

    # 3. Clean up margins and fonts for web dashboards
    fig.update_layout(
        title="",
        annotations=[],
        margin={"r":0, "t":0, "l":0, "b":0},
        paper_bgcolor="rgba(0,0,0,0)",  # Makes the outer chart box transparent
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # 4. Render natively inside the Streamlit Tab canvas
    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# TAB 2: RESEARCH QUESTIONS
# ==========================================
with tabs[1]:
    st.header("""
        Do it!
            """)
    st.markdown(
        """
        Here i need to put my main questions and hypotheses."""
    )

# ==========================================
# TAB 3: DATA
# ==========================================
with tabs[2]:
    st.header("""
        Do it!
            """)
    st.markdown(
        """
        Here is gonna be some data, where to get it, how i got it and what i did with it."""
    )

# ==========================================
# TAB 4: PIPELINE&METHODS
# ==========================================
with tabs[3]:
    st.header("""
        Do it now!
            """)
    st.markdown(
        """
        Here i need to put 
        - the order of actions
        - links to documentation
        - tech stack"""
    )


# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025), [Eurobarometer Standard (104)](https://europa.eu/eurobarometer/surveys/detail/3378) and [Eurobarometer Special (sp566)](https://europa.eu/eurobarometer/surveys/detail/3362).
""")