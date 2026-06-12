import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles
import scipy.stats as stats 
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt

# -- Page configuration:
st.set_page_config(layout="wide")

# ==============================================================================
# DATA LOADING (Executed once and cached via your database.py)
# ==============================================================================
try:
    df_skills, skills_labels = funcs.load_tab_data("stg_dig_skills_demog", "mart_dig_skills_map")
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    df_time_series, time_labels = funcs.load_tab_data("mart_skill_time_series","mart_indicators")
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
df_filtered_time = df_time_series[df_time_series[country_col].isin(selected_countries)]

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
tab_overview, tab_gender, tab_age, tab_edu, tab_urban, tab_deep_dive = st.tabs([
    "Overview", 
    "Gender", 
    "Age Groups",
    "Education Levels",
    "Urbanization Levels",
    "Skill Metric Deep Dive"
])

# ==============================================================================
# --- TAB 1: OVERVIEW ---
# ==============================================================================
with tab_overview:
    
    st.subheader("Macro Trends & National Baselines")
    
    # --------------------------------------------------------------------------
    # 6 KPI METRIC COLUMNS (do not change with country selection!)
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
        st.markdown("### Geographic Distribution")
        
        map_radio_options = {
            "Above Basic Skills": "i_dsk2_ab",
            "Basic Skills": "i_dsk2_b",
            "Low Skills": "i_dsk2_lw",
            "Narrow Skills": "i_dsk2_n",
            "Limited Skills": "i_dsk2_lm",
            "No Digital Skills": "i_dsk2_x"
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
            resolution=50,
            bgcolor="rgba(0,0,0,0)"
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
    
    col_explain, col_time = st.columns([2,3])

    # ---------------------------------------------
    # MAP WITH TREND OVER TIME (but just three years)
    # ---------------------------------------------

    with col_time:
        st.markdown("""
                    \n_Based on current growth rates for individuals with At Least Basic Digital Skills (2021, 2023, 2025)_
                    """)

        # 1. Extract the current 2025 status and historical slope
        df_trend = df_time_series[df_time_series['indicator_code'] == 'I_DSK2_BAB']
        df_eu_avg = df_trend.groupby('reporting_year')['indicator_value'].mean().reset_index()
        df_eu_avg = df_eu_avg.sort_values('reporting_year')
        
        if df_eu_avg.empty:
            st.warning("No data available for indicator 'I_DSK2_BAB'.")
        else:
            # Dynamically grab the earliest and latest available years (2021 and 2025)
            year_min = df_eu_avg['reporting_year'].min()
            year_max = df_eu_avg['reporting_year'].max()
            
            val_min = df_eu_avg[df_eu_avg['reporting_year'] == year_min]['indicator_value'].values[0]
            val_max = df_eu_avg[df_eu_avg['reporting_year'] == year_max]['indicator_value'].values[0]
            
            # Calculate total time spans
            years_passed = year_max - year_min  # e.g., 2025 - 2021 = 4 years
            years_to_target = 2030 - year_max   # e.g., 2030 - 2025 = 5 years
            
            # Calculate annual growth and run the linear projection out to 2030
            annual_growth = (val_max - val_min) / years_passed
            projected_2030 = val_max + (annual_growth * years_to_target)
            target_value = 80.0

            # 2. Build structured comparison dataframe using the variables correctly!
            data = {
                'Status': [
                    f'Current Status ({year_max})', 
                    f'Projected 2030 Status'
                ],
                'Percentage': [val_max, projected_2030],
                'Color': ['#1f77b4', '#aec7e8']
            }
            df_plot = pd.DataFrame(data)

            # 3. Create the progress bars
            fig = px.bar(
                df_plot,
                x='Percentage',
                y='Status',
                orientation='h',
                text='Percentage',
                range_x=[0, 100]
            )

            # Clean up bar styles and add text strings
            fig.update_traces(
                marker_color=df_plot['Color'],
                texttemplate='%{text:.1f}%',
                textposition='inside',
                insidetextanchor='end',
                hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
            )

            # 4. Add the definitive 2030 Target Line
            fig.add_shape(
                type="line",
                x0=target_value, y0=-0.5,
                x1=target_value, y1=1.5,
                line=dict(color="crimson", width=3, dash="dash"),
            )

            # Add a clean text annotation directly over the target line
            fig.add_annotation(
                x=target_value,
                y=1.6,
                text="Target: 80% Baseline",
                showarrow=False,
                font=dict(color="crimson", size=12, family="sans-serif"),
                xanchor="center"
            )

            # 5. Clean up structural borders and text layout
            fig.update_layout(
                xaxis_title="% of Population",
                yaxis_title="",
                showlegend=False,
                height=300,
                margin=dict(t=40, b=40, l=220, r=40), # Slightly widened left margin for the longer text labels
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='rgba(220, 220, 220, 0.5)')

            st.plotly_chart(fig, use_container_width=True)
            
    with col_explain:
        st.subheader(
            """
            Is EU Going to Meet the 2030 Goal?
            """
        )

        with st.expander("Merhodology & Limitations Notice"):
            st.markdown(
                """
                Historical Eurostat data for the updated Digital Competence Framework 
                is currently limited, with assessments occurring biennially in **2021**, **2023**, and **2025**. 
                Because three data points are statistically insufficient for training complex predictive time-series models, 
                this dashboard uses a linear trend projection. By calculating the average annual growth rate across the full 4-year historical baseline, 
                we extend a straight-line trajectory to estimate the 2030 outlook against official policy benchmarks. 
            """
            )
        
        st.markdown(
            f"""
            **Key Insights**
            - Between 2021 and 2025, the percent of EU citizes with at least basic digital skills grew from {val_min.round(2)}% to 61%. 
            Annual expansion is about **1.5 percentage points**.
            - At the current speed, the EU is on track to reach **66.9%** digital proficiency by 2030. This creates a structural deficit of **13.1** percentage points, meaning that the EU
            will officially fail to meet its Digital Decade milestone unless member states drastically accelerate digital literacy programs.
            - Linear model we used here assumes constant progress, but systemic shifts (e.g., AI adoption or national funding injections) could create non-linear growth.
            At the same time, this experimet illustrates, that **incremental progress is no longer enough**.
            """
        )
# ==============================================================================
# --- GENDER ---
# ==============================================================================
with tab_gender:
    st.header("Digital Skills vs. Gender")
    st.write("Placeholder: Cross-tabulations and distributions segmented by Education, Gender, Urbanization, and Age groups.")

    # extract columns by demographic characteristics (gender, education, urbanization, age)
    columns = df_skills.columns
    gen_dig_skills = []
    urb_dig_skills = []
    edu_dig_skills = []
    age_dig_skills = []

    age_substrings = ['y16_19', 'y20_24', 'y25_34', 'y35_44', 'y45_54', 'y55_64', 'y65_74']

    for col in columns:

        # check gender:
        if ('_f_' in col) or ('_m_' in col):
            gen_dig_skills.append(col)
            
        # check settlement/urban:
        if ('ind_deg1' in col) or ('ind_deg2' in col) or ('ind_deg3' in col):
            urb_dig_skills.append(col)
            
        # check education:
        if ('i0_2' in col) or ('i3_4' in col) or ('i5_8' in col):
            edu_dig_skills.append(col)
            
        # check age (and not having gender!)
        has_age = any(age_tag in col for age_tag in age_substrings)
        has_gender = ('_f_' in col) or ('_m_' in col)
        
        if has_age and not has_gender:
            age_dig_skills.append(col)

    col_table, col_gender_insights = st.columns([2,3])
    with col_table:
        st.subheader("Is Gender Statistically Significant for Digital Skills Levels?")
        df_gender_results = funcs.run_t_test_pair(df_skills, gen_dig_skills, '_y16_74', skills_labels)
        df_gender_results_table=df_gender_results.drop(columns=['Female Avg (%)', 'Male Avg (%)'])
        st.dataframe(
            df_gender_results_table,
            column_config={
                #"Female Avg (%)": st.column_config.NumberColumn(format="%.1f%%"),
                #"Male Avg (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                "P-Value": st.column_config.NumberColumn(format="%.4f")
            },
            hide_index=True,
            use_container_width=True
        )

    with col_gender_insights:
        st.subheader("Key Insights")
        st.markdown("**1. The 'High-Skill' Premium Favors Men**")
        st.markdown(
            "The gender gap is narrowing globally, but men across the EU are still "
            "significantly more likely to cross the threshold into advanced digital competencies "
            "This has direct "
            "implications filling high-paying tech and engineering roles."
        )
        st.markdown("**2. Women Dominate the Solid 'Baseline' Competencies**")
        st.markdown(
            "Women are significantly better represented in the 'middle tier' of digital literacy. "
            "They hold a solid base of everyday digital skills. The data suggests that the "
            "core issue is a bottleneck "
            "preventing women with basic/low skills from transitioning into the 'Above Basic' tier."
        )
        st.markdown("**3. Statistically Identical Floors**")
        st.markdown(
            "At the bottom end of the digital skills scale, gender is an irrelevant factor. "
            "The portion of the population that is completely digitally excluded or highly restricted "
            "is identical regardless of gender. Exclusion here is likely driven by other structural vectors."
        )

    df_chart = df_gender_results[['Indicator', 'Female Avg (%)', 'Male Avg (%)']].copy()
    df_chart.columns = ['Indicator', 'Female', 'Male']
    df_chart['Skill Level'] = (
        df_chart['Skill Level']
        .str.replace('Digital Skills:', '', case=False)
        .str.strip()
    )

    df_melted = df_chart.melt(
        id_vars=['Skill Level'], 
        value_vars=['Female', 'Male'], 
        var_name='Gender', 
        value_name='Percentage (%)'
    )

    # 3. Create a beautiful, interactive grouped bar chart
    fig = px.bar(
        df_melted, 
        x='Skill Level', 
        y='Percentage (%)', 
        color='Gender', 
        barmode='group', # 💡 This explicitly forces them side-by-side!
        color_discrete_map={'Female': '#498cdb', 'Male': '#001f63'},
        height=400
    )

    # 4. Clean up the layout aesthetics to match your clean UI standard
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average Percentage (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    # Fix grid lines to be subtle
    fig.update_yaxes(showgrid=True, gridcolor='rgba(226, 232, 240, 0.5)')

    # 5. Render it in Streamlit
    st.subheader("Digital Skills Competency Comparison")
    st.plotly_chart(fig, use_container_width=True)







    



with tab_edu:
    st.subheader("Granular Component Evaluation")
    st.write("Placeholder: In-depth breakdowns of specific subsets.")


# ==============================================================================
# --- REGULAR TAB LAYOUTS ---
# ==============================================================================
with tab_urban:
    st.subheader("Digital Skills vs. Sociodemographic Factors")
    st.write("Placeholder: Cross-tabulations and distributions segmented by Education, Gender, Urbanization, and Age groups.")


# ==============================================================================
# --- REGULAR TAB LAYOUTS ---
# ==============================================================================
with tab_deep_dive:
    st.subheader("Digital Skills vs. Sociodemographic Factors")
    st.write("Placeholder: Cross-tabulations and distributions segmented by Education, Gender, Urbanization, and Age groups.")

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
           and ICT Usage collected in the framework od [ESS ICT Survey](https://ec.europa.eu/eurostat/web/microdata/collections-research/survey-ict-use-households-individuals)
""")