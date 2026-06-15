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
tab_overview, tab_demog, tab_deep_dive = st.tabs([
    "Overview", 
    "Demographical Dimensions",
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

    # ------------------------------------------------------------------------------
    # --- MODULE: 2030 DIGITAL DECADE FORECAST PANELS (HISTORICAL BRIDGE OVERHAUL) ---
    # ------------------------------------------------------------------------------
    with col_time:
        st.markdown("#### Digital Literacy Trends | OLS")
        st.markdown("""
            \n_Based on Ordinary Least Squares (OLS) historical growth rates bridging pre-2021 (`I_DSK_BAB` = Above Basic or Basic Digital Skills) and post-2021 (`I_DSK2_BAB` = also Above Basic or Basic Digital Skills) Eurostat frameworks._
        """)

        target_codes = ['I_DSK_BAB', 'I_DSK2_BAB']
        df_trend = df_time_series[df_time_series['indicator_code'].isin(target_codes)]
        
        df_eu_avg = df_trend.groupby('reporting_year')['indicator_value'].mean().reset_index()
        
        df_eu_avg['reporting_year'] = df_eu_avg['reporting_year'].astype(int)
        df_eu_avg['indicator_value'] = df_eu_avg['indicator_value'].astype(float)
        df_eu_avg = df_eu_avg.sort_values('reporting_year')
        
        if df_eu_avg.empty:
            st.warning("No time-series history records found for the selected indicator codes.")
        else:
            year_min = int(df_eu_avg['reporting_year'].min())  # Will dynamically become 2015
            year_max = int(df_eu_avg['reporting_year'].max())  # Will dynamically become 2025
            
            val_min = df_eu_avg[df_eu_avg['reporting_year'] == year_min]['indicator_value'].values[0]
            val_max = df_eu_avg[df_eu_avg['reporting_year'] == year_max]['indicator_value'].values[0]
            
            from scipy import stats
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_eu_avg['reporting_year'], df_eu_avg['indicator_value']
            )
            
            annual_growth = slope
            years_to_target = 2030 - year_max
            projected_2030 = val_max + (annual_growth * years_to_target)
            
            target_value = 80.0
            structural_deficit = target_value - projected_2030

            # 2. Build structured comparison dataframe
            data = {
                'Status': [
                    f'Current Status ({year_max})', 
                    f'Projected 2030 Status'
                ],
                'Percentage': [val_max, projected_2030],
                'Color': ['#1f77b4', '#aec7e8']
            }
            df_plot = pd.DataFrame(data)

            # 3. Create the horizontal progress bars
            fig = px.bar(
                df_plot,
                x='Percentage',
                y='Status',
                orientation='h',
                text='Percentage',
                range_x=[0, 100]
            )

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

            fig.add_annotation(
                x=target_value, y=1.6,
                text="Target: 80% Baseline",
                showarrow=False,
                font=dict(color="crimson", size=12, family="sans-serif"),
                xanchor="center"
            )

            fig.update_layout(
                xaxis_title="% of Population", yaxis_title="",
                showlegend=False, height=300,
                margin=dict(t=40, b=40, l=180, r=40),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=True, gridcolor='rgba(220, 220, 220, 0.5)')
            st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------------------------------------------
        # --- VISUALIZATION: DIGITAL SKILLS HISTORICAL TRAJECTORY (2015-2025) ---
        # ------------------------------------------------------------------------------
        st.markdown("#### Historical Progression of At Least Basic Digital Skills")

        if not df_eu_avg.empty:
            
            full_years = np.append(df_eu_avg['reporting_year'].values, [2030])
            
            df_proj = pd.DataFrame({
                'reporting_year': full_years,
                # Calculate the theoretical regression value for every point: y = mx + c
                'regression_value': slope * full_years + intercept
            })

            fig_line = px.line(
                df_eu_avg,
                x='reporting_year',
                y='indicator_value',
                markers=True,
                text=df_eu_avg['indicator_value'].map(lambda x: f"{x:.1f}%"),
                labels={
                    'reporting_year': 'Reporting Year',
                    'indicator_value': 'EU Average (% of Population)'
                }
            )

            fig_line.update_traces(
                line=dict(color='#41748d', width=4),
                marker=dict(size=9, color='#005f73'),
                textposition='top center',
                name='Historical Reality'
            )

            val_2030 = df_proj[df_proj['reporting_year'] == 2030]['regression_value'].values[0]
            
            fig_line.add_scatter(
                x=df_proj['reporting_year'],
                y=df_proj['regression_value'],
                mode='lines+markers',
                line=dict(color='crimson', width=2, dash='dash'),
                marker=dict(
                    size=np.where(df_proj['reporting_year'] == 2030, 10, 0).tolist(), # Highlight ONLY the 2030 node
                    color='crimson'
                ),
                text=np.where(df_proj['reporting_year'] == 2030, f"2030 Forecast: {val_2030:.1f}%", "").tolist(),
                textposition="bottom right",
                name='OLS Linear Trendline'
            )

            fig_line.add_shape(
                type="line",
                x0=2015, y0=80,
                x1=2030, y1=80,
                line=dict(color="#2a9d8f", width=2, dash="dot")
            )
            fig_line.add_annotation(
                x=2017, y=82,
                text="Official EU 2030 Goal: 80%",
                showarrow=False,
                font=dict(color="#2a9d8f", size=11, weight="bold")
            )

            fig_line.add_shape(
                type="line",
                x0=2021, y0=35,
                x1=2021, y1=85,
                line=dict(color="orange", width=1.5, dash="dot")
            )
            fig_line.add_annotation(
                x=2021, y=38,
                text="Methodology Shift",
                showarrow=False,
                font=dict(color="orange", size=9),
                xanchor="center"
            )

            fig_line.update_layout(
                height=400,
                showlegend=False,
                xaxis=dict(
                    tickmode='array',
                    tickvals=[2015, 2016, 2017, 2019, 2021, 2023, 2025, 2030], 
                    showgrid=False,
                    range=[2014, 2032] 
                ),
                yaxis=dict(
                    range=[35, 90],
                    showgrid=True,
                    gridcolor='rgba(220, 220, 220, 0.4)'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=20, l=20, r=20)
            )

            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Unable to render historical trajectory line plot due to missing data layers.")


        
        
with col_explain:
    st.subheader("Is the EU Going to Meet the 2030 Goal?")

    with st.expander("Methodology & Limitations Notice"):
        st.markdown(f"""
            **Framework Bridge Activated:** In 2021, Eurostat updated its official Digital Competence operational framework. 
            To construct a robust 10-year analytics runway, this model constructs a structural indicator bridge, joining legacy indicators (`I_DSK_BAB` from {year_min}–2019) 
            with modern metrics (`I_DSK2_BAB` from 2021–{year_max}). 
            
            By running an **Ordinary Least Squares (OLS) Linear Regression** across this composite 10-year horizon, we establish a mathematically grounded annual growth vector ($\beta$) that dampens single-year variance anomalies.
        """)
    
    # The insights will now fully update to display the genuine, long-term 10-year trajectory values!
    st.markdown(
        f"""
        **Key Insights**
        - Over the full data runway from **{year_min}** to **{year_max}**, the percentage of EU citizens with at least basic digital skills expanded from **{val_min:.1f}%** to **{val_max:.1f}%**.
        - Based on our OLS regression across all data cohorts, the long-term historical baseline reveals a steady expansion of **{annual_growth:.2f} percentage points** per year.
        - At this specific velocity, the EU is on track to reach a projected proficiency level of **{projected_2030:.1f}%** by 2030. 
        - This leaves an official policy **structural deficit of {structural_deficit:.1f} percentage points**.""")
    st.warning(" **Strategic Takeaway:** Even when factoring in a decade of long-term development history, the empirical modeling confirms that **incremental progress is not enough**. Unless member states implement aggressive, non-linear structural interventions, the 80% milestone will be missed.")
       






    # # OLD VERSION
    # # ---------------------------------------------
    # # MAP WITH TREND OVER TIME (but just three years)
    # # ---------------------------------------------

    # with col_time:
    #     st.markdown("""
    #                 \n_Based on current growth rates for individuals with At Least Basic Digital Skills (2021, 2023, 2025)_
    #                 """)

    #     # 1. Extract the current 2025 status and historical slope
    #     df_trend = df_time_series[df_time_series['indicator_code'] == 'I_DSK2_BAB']
    #     df_eu_avg = df_trend.groupby('reporting_year')['indicator_value'].mean().reset_index()
    #     df_eu_avg = df_eu_avg.sort_values('reporting_year')
        
    #     if df_eu_avg.empty:
    #         st.warning("No data available for indicator 'I_DSK2_BAB'.")
    #     else:
    #         # Dynamically grab the earliest and latest available years (2021 and 2025)
    #         year_min = df_eu_avg['reporting_year'].min()
    #         year_max = df_eu_avg['reporting_year'].max()
            
    #         val_min = df_eu_avg[df_eu_avg['reporting_year'] == year_min]['indicator_value'].values[0]
    #         val_max = df_eu_avg[df_eu_avg['reporting_year'] == year_max]['indicator_value'].values[0]
            
    #         # Calculate total time spans
    #         years_passed = year_max - year_min  # e.g., 2025 - 2021 = 4 years
    #         years_to_target = 2030 - year_max   # e.g., 2030 - 2025 = 5 years
            
    #         # Calculate annual growth and run the linear projection out to 2030
    #         annual_growth = (val_max - val_min) / years_passed
    #         projected_2030 = val_max + (annual_growth * years_to_target)
    #         target_value = 80.0

    #         # 2. Build structured comparison dataframe using the variables correctly!
    #         data = {
    #             'Status': [
    #                 f'Current Status ({year_max})', 
    #                 f'Projected 2030 Status'
    #             ],
    #             'Percentage': [val_max, projected_2030],
    #             'Color': ['#1f77b4', '#aec7e8']
    #         }
    #         df_plot = pd.DataFrame(data)

    #         # 3. Create the progress bars
    #         fig = px.bar(
    #             df_plot,
    #             x='Percentage',
    #             y='Status',
    #             orientation='h',
    #             text='Percentage',
    #             range_x=[0, 100]
    #         )

    #         # Clean up bar styles and add text strings
    #         fig.update_traces(
    #             marker_color=df_plot['Color'],
    #             texttemplate='%{text:.1f}%',
    #             textposition='inside',
    #             insidetextanchor='end',
    #             hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
    #         )

    #         # 4. Add the definitive 2030 Target Line
    #         fig.add_shape(
    #             type="line",
    #             x0=target_value, y0=-0.5,
    #             x1=target_value, y1=1.5,
    #             line=dict(color="crimson", width=3, dash="dash"),
    #         )

    #         # Add a clean text annotation directly over the target line
    #         fig.add_annotation(
    #             x=target_value,
    #             y=1.6,
    #             text="Target: 80% Baseline",
    #             showarrow=False,
    #             font=dict(color="crimson", size=12, family="sans-serif"),
    #             xanchor="center"
    #         )

    #         # 5. Clean up structural borders and text layout
    #         fig.update_layout(
    #             xaxis_title="% of Population",
    #             yaxis_title="",
    #             showlegend=False,
    #             height=300,
    #             margin=dict(t=40, b=40, l=220, r=40), # Slightly widened left margin for the longer text labels
    #             plot_bgcolor='rgba(0,0,0,0)',
    #             paper_bgcolor='rgba(0,0,0,0)'
    #         )
            
    #         fig.update_xaxes(showgrid=True, gridcolor='rgba(220, 220, 220, 0.5)')

    #         st.plotly_chart(fig, use_container_width=True)
            
    # with col_explain:
    #     st.subheader(
    #         """
    #         Is EU Going to Meet the 2030 Goal?
    #         """
    #     )

    #     with st.expander("Merhodology & Limitations Notice"):
    #         st.markdown(
    #             """
    #             Historical Eurostat data for the updated Digital Competence Framework 
    #             is currently limited, with assessments occurring biennially in **2021**, **2023**, and **2025**. 
    #             Because three data points are statistically insufficient for training complex predictive time-series models, 
    #             this dashboard uses a linear trend projection. By calculating the average annual growth rate across the full 4-year historical baseline, 
    #             we extend a straight-line trajectory to estimate the 2030 outlook against official policy benchmarks. 
    #         """
    #         )
        
    #     st.markdown(
    #         f"""
    #         **Key Insights**
    #         - Between 2021 and 2025, the percent of EU citizes with at least basic digital skills grew from {val_min.round(2)}% to 61%. 
    #         Annual expansion is about **1.5 percentage points**.
    #         - At the current speed, the EU is on track to reach **66.9%** digital proficiency by 2030. This creates a structural deficit of **13.1** percentage points, meaning that the EU
    #         will officially fail to meet its Digital Decade milestone unless member states drastically accelerate digital literacy programs.
    #         - Linear model we used here assumes constant progress, but systemic shifts (e.g., AI adoption or national funding injections) could create non-linear growth.
    #         At the same time, this experimet illustrates, that **incremental progress is no longer enough**.
    #         """
    #     )




# ==============================================================================
# --- TAB 2: DEMOGRAPHIC DIMENSIONS ---
# ==============================================================================
with tab_demog:
    st.header("Socio-Demographic Literacy Layers")
    st.write("Explore how digital skills thresholds distribute across specific sub-populations.")
    
    # --- STEP 1: Interactive Segment Map Components (Dependent on Country Filter) ---
    st.subheader(funcs.get_dynamic_subheader(df_filtered_skills))
    
    demo_metric_choice = st.selectbox(
        "Select Demographic Slice to Plot:",
        options=["Gender", "Age Cohorts", "Education Levels", "Urbanization Levels"]
    )
    
    # Dynamically extract and resolve clean suffix tracking arrays from column names
    if demo_metric_choice == "Gender":
        target_cols = [c for c in df_skills.columns if ('_f_' in c or '_m_' in c) and '_y16_74' in c]
        labels_list = ['Female', 'Male']
        color_blueprint = {'Female': '#498cdb', 'Male': '#001f63'}
    elif demo_metric_choice == "Age Cohorts":
        target_cols = [c for c in df_skills.columns if any(sfx in c for sfx in ['y16_19', 'y20_24', 'y25_34', 'y35_44', 'y45_54', 'y55_64', 'y65_74']) and not ('_f_' in c or '_m_' in c)]
        labels_list = ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']
        color_blueprint = None
    elif demo_metric_choice == "Education Levels":
        target_cols = [c for c in df_skills.columns if any(sfx in c for sfx in ['i0_2', 'i3_4', 'i5_8'])]
        labels_list = ['Low Edu', 'Medium Edu', 'High Edu']
        color_blueprint = {'Low Edu': '#cbd5e1', 'Medium Edu': '#64748b', 'High Edu': '#0f172a'}
    else:  # Urbanization
        target_cols = [c for c in df_skills.columns if any(sfx in c for sfx in ['ind_deg1', 'ind_deg2', 'ind_deg3'])]
        labels_list = ['Cities', 'Suburbs', 'Rural']
        color_blueprint = {'Cities': '#3b82f6', 'Suburbs': '#60a5fa', 'Rural': '#93c5fd'}

    funcs.render_demographic_chart(
        df_filtered_skills, target_cols, labels_list, skills_labels, color_map=color_blueprint
    )
    
    st.write("---")
    st.subheader("Global EU Significance Tests (Fixed Sample Baselines)")
    
    # --- STEP 2: Strict Fixed Global Statistical Inference Tables (Expandable, NO Country Filters) ---
    
    # 1. Gender Table Module
    with st.expander("Gender Gaps Significance (Wilcoxon Signed-Rank)", expanded=False):
        col_tbl, col_ins = st.columns([3, 2])
        with col_tbl:
            # 🎯 FIX: Explicitly target only total population slices to prevent NaN evaluations
            gen_clean_cols = [c for c in df_skills.columns if ('_f_' in c or '_m_' in c) and c.endswith('_y16_74')]
            if gen_clean_cols:
                df_gender = funcs.run_t_test_pair(df_skills, gen_clean_cols, '_y16_74', skills_labels)
                df_gender = df_gender.drop(columns=[c for c in ["Female Avg (%)", "Male Avg (%)"] if c in df_gender.columns])
                st.dataframe(
                    df_gender, 
                    column_config={
                        "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                        "P-Value": st.column_config.NumberColumn(format="%.6f") # 🎯 Force 6 decimals
                    }, hide_index=True, use_container_width=True
                )
        with col_ins:
            st.markdown("**Key Insights:**\n* Men maintain a significant lead at the 'Above Basic' threshold, while entry-level exclusion rates remain identical.")

    # 2. Age Cohorts Table Module
    with st.expander("Age Cohorts Variance Significance (Friedman Multi-Group)", expanded=False):
        col_tbl, col_ins = st.columns([3, 2])
        with col_tbl:
            age_metrics_clean = sorted(list(set([c.split('_y16')[0].split('_y20')[0].split('_y25')[0].split('_y35')[0].split('_y45')[0].split('_y55')[0].split('_y65')[0].lower() for c in df_skills.columns if any(sfx in c.lower() for sfx in ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74']) and not ('_f_' in c or '_m_' in c)])))
            if age_metrics_clean:
                df_age = funcs.run_friedman_multigroups(df_skills, age_metrics_clean, ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'], skills_labels)
                df_age = df_age.drop(columns=[f"{l} Avg (%)" for l in ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']], errors='ignore')
                st.dataframe(
                    df_age,
                    column_config={
                        "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                        "P-Value": st.column_config.NumberColumn(format="%.6f") # 🎯 Force 6 decimals
                    }, hide_index=True, use_container_width=True
                )
        with col_ins:
            st.markdown("**Key Insights:**\n* Strong generational downward step patterns emerge as cohorts age.")

    # 3. Education Table Module
    with st.expander("Education Levels Variance Significance (Friedman Multi-Group)", expanded=False):
        col_tbl, col_ins = st.columns([3, 2])
        with col_tbl:
            edu_metrics_clean = sorted(list(set([c.split('_i0_2')[0].split('_i3_4')[0].split('_i5_8')[0].lower() for c in df_skills.columns if any(sfx in c.lower() for sfx in ['_i0_2', '_i3_4', '_i5_8'])])))
            if edu_metrics_clean:
                df_edu = funcs.run_friedman_multigroups(df_skills, edu_metrics_clean, ['_i0_2', '_i3_4', '_i5_8'], ['Low Edu', 'Medium Edu', 'High Edu'], skills_labels)
                df_edu = df_edu.drop(columns=[f"{l} Avg (%)" for l in ['Low Edu', 'Medium Edu', 'High Edu']], errors='ignore')
                st.dataframe(
                    df_edu,
                    column_config={
                        "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                        "P-Value": st.column_config.NumberColumn(format="%.6f") # 🎯 Force 6 decimals
                    }, hide_index=True, use_container_width=True
                )
        with col_ins:
            st.markdown("**Key Insights:**\n* Formal educational attainment is the strongest institutional predictor of advanced skills across the dataset.")

    # 4. Settlement Density / Urbanization Table Module
    with st.expander("Settlement Density Variance Significance (Friedman Multi-Group)", expanded=False):
        col_tbl, col_ins = st.columns([3, 2])
        with col_tbl:
            urb_metrics_clean = sorted(list(set([c.split('_ind_deg1')[0].split('_ind_deg2')[0].split('_ind_deg3')[0].lower() for c in df_skills.columns if any(sfx in c.lower() for sfx in ['_ind_deg1', '_ind_deg2', '_ind_deg3'])])))
            if urb_metrics_clean:
                df_urb = funcs.run_friedman_multigroups(df_skills, urb_metrics_clean, ['_ind_deg1', '_ind_deg2', '_ind_deg3'], ['Cities', 'Suburbs', 'Rural'], skills_labels)
                df_urb = df_urb.drop(columns=[f"{l} Avg (%)" for l in ['Cities', 'Suburbs', 'Rural']], errors='ignore')
                st.dataframe(
                    df_urb,
                    column_config={
                        "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                        "P-Value": st.column_config.NumberColumn(format="%.6f") # 🎯 Force 6 decimals
                    }, hide_index=True, use_container_width=True
                )
        with col_ins:
            st.markdown("**Key Insights:**\n* Metropolitan hubs show a clear adoption lead over rural communities.")

# ==============================================================================
# --- TAB 6: SKILL METRIC DEEP DIVE ---
# ==============================================================================
with tab_deep_dive:
    st.header("Strategic Competence Dimension Deep Dive")
    st.markdown("""
        This module decomposes the overall Digital Skills Indicator into its **five structural foundational vectors** defined by the European Commission's DigComp Framework. Rather than focusing on a single metric, 
        this workspace visualizes comparative structural footprints and pinpoints exactly where socio-demographic disparities live.
    """)

    # --------------------------------------------------------------------------
    # 0. DATABASE DATA EXTRACTION & CONFIGURATION
    # --------------------------------------------------------------------------
    try:
        # Load the newly created dbt mart table and its metadata indicators
        df_deep, deep_labels = funcs.load_tab_data("stg_skills_deep_dive", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract deep dive dimension data: {e}")
        df_deep = pd.DataFrame()

    if df_deep.empty:
        st.warning("Deep Dive data asset pipeline empty. Verify your 'stg_skills_deep_dive' table status.")
    else:
        # Filter deep dive frame down to the user's active sidebar geographic choices
        df_filtered_deep = df_deep[df_deep['clean_country_name'].isin(selected_countries)]

        # Human-readable mapping dictionary for our 5 Core Framework Dimension prefixes
        DIMENSION_MAP = {
            'i_dsk2_il_bab': 'Information & Data Literacy',
            'i_dsk2_cc_bab': 'Communication & Collaboration',
            'i_dsk2_dcc_bab': 'Digital Content Creation',
            'i_dsk2_sf_bab': 'Safety & Privacy Competence',
            'i_dsk2_ps_bab': 'Technical Problem Solving'
        }

        st.write("---")

        # ==============================================================================
        # COMPONENT 1: COUNTRY GEOGRAPHIC SIGNATURE FINGERPRINT (Radar Map Matrix)
        # ==============================================================================
        st.subheader("Cross-Dimension Competence Fingerprint")
        st.markdown("_Compare a country's baseline performance across all five capability pillars simultaneously._")

        # Single country filter dedicated strictly to the fingerprint vector
        fingerprint_country = st.selectbox(
            "Select Target Country for Fingerprint Analysis:",
            options=sorted(df_filtered_deep['clean_country_name'].unique()),
            index=0
        )

        df_country_fingerprint = df_filtered_deep[df_filtered_deep['clean_country_name'] == fingerprint_country]
        df_eu_fingerprint = df_deep.copy() # Use full unfiltered frame for a robust EU benchmark reference

        fingerprint_rows = []
        for prefix, label in DIMENSION_MAP.items():
            # Target the national total baseline suffix columns for the macro view
            f_col = f"{prefix}_f_y16_74"
            m_col = f"{prefix}_m_y16_74"
            
            if f_col in df_country_fingerprint.columns and m_col in df_country_fingerprint.columns:
                # Calculate National Average for total baseline
                country_avg = (df_country_fingerprint[f_col].mean() + df_country_fingerprint[m_col].mean()) / 2
                eu_avg = (df_eu_fingerprint[f_col].mean() + df_eu_fingerprint[m_col].mean()) / 2
                
                fingerprint_rows.append({
                    "Dimension": label,
                    f"{fingerprint_country} (%)": round(country_avg, 1) if not pd.isna(country_avg) else 0,
                    "EU Average (%)": round(eu_avg, 1) if not pd.isna(eu_avg) else 0
                })

        if fingerprint_rows:
            df_radar = pd.DataFrame(fingerprint_rows)
            
            # Construct a clean Radar diagram using Plotly Graph Objects
            fig_radar = go.Figure()
            
            # Trace 1: Target Country
            fig_radar.add_trace(go.Scatterpolar(
                r=df_radar[f"{fingerprint_country} (%)"],
                theta=df_radar['Dimension'],
                fill='toself',
                name=fingerprint_country,
                line_color='#001f63',
                fillcolor='rgba(0, 31, 99, 0.2)'
            ))
            
            # Trace 2: EU Average Benchmark
            fig_radar.add_trace(go.Scatterpolar(
                r=df_radar['EU Average (%)'],
                theta=df_radar['Dimension'],
                fill='toself',
                name='EU Average Baseline',
                line_color='#64748b',
                fillcolor='rgba(100, 116, 139, 0.15)',
                line=dict(dash='dash')
            ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%"),
                    bgcolor='rgba(0,0,0,0)'
                ),
                showlegend=True,
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                margin=dict(t=30, b=20, l=40, r=40)
            )
            
            col_radar, col_radar_desc = st.columns([3, 2])
            with col_radar:
                st.plotly_chart(fig_radar, use_container_width=True)
            with col_radar_desc:
                st.markdown(f"### {fingerprint_country} Structural Balance Sheet")
                st.markdown("""
                    **How to read this chart:**
                    * A perfectly symmetrical web indicate well-rounded national educational strategies.
                    * Sharp peaks point out targeted national specializations, while inward indents signal strategic bottlenecks.
                """)
                
                # Dynamically calculate and display performance callouts
                df_radar['Diff'] = df_radar[f"{fingerprint_country} (%)"] - df_radar['EU Average (%)']
                strongest_dim = df_radar.loc[df_radar['Diff'].idxmax()]
                weakest_dim = df_radar.loc[df_radar['Diff'].idxmin()]
                
                st.info(f"**Relative Strength:** *{strongest_dim['Dimension']}* is leading the EU average trend by **+{strongest_dim['Diff']:.1f} percentage points**.")
                st.warning(f"**Relative Bottleneck:** *{weakest_dim['Dimension']}* shows the widest lag behind the EU block (**{weakest_dim['Diff']:.1f} percentage points**).")
        else:
            st.warning("Dimension baseline signature tracks could not be isolated from database schema rows.")

        st.write("---")

        # ==============================================================================
        # COMPONENT 2: INTERACTIVE DISPARITY GRID MATRIX (Heatmap View)
        # ==============================================================================
        st.subheader("Macro Socio-Demographic Disparity Matrix")
        st.markdown("_Select an intersection layer to map variance density across all 5 framework dimensions at once._")

        deep_demo_choice = st.selectbox(
            "Select Demographic Stratification Layer:",
            options=["Age Cohorts", "Education Levels", "Urbanization Levels"],
            key="deep_demo_selectbox"
        )

        # Set up dictionary maps targeting the exact demographic key endings configured in your dbt cross join
        if deep_demo_choice == "Age Cohorts":
            slice_mapping = {'y16_19': '16-19', 'y20_24': '20-24', 'y25_34': '25-34', 'y35_44': '35-44', 'y45_54': '45-54', 'y55_64': '55-64', 'y65_74': '65-74'}
        elif deep_demo_choice == "Education Levels":
            slice_mapping = {'i0_2': 'Low Edu', 'i3_4': 'Medium Edu', 'i5_8': 'High Edu'}
        else:  # Urbanization
            slice_mapping = {'ind_deg1': 'Cities', 'ind_deg2': 'Suburbs', 'ind_deg3': 'Rural'}

        heatmap_data = []

        # Aggregate and calculate cross table matrices across all filtered countries
        for prefix, dim_label in DIMENSION_MAP.items():
            for suffix, label in slice_mapping.items():
                target_col = f"{prefix}_{suffix}"
                if target_col in df_filtered_deep.columns:
                    mean_val = df_filtered_deep[target_col].mean()
                    heatmap_data.append({
                        "Core Dimension": dim_label,
                        "Socio-Demographic Group": label,
                        "Mean Proficiency (%)": round(mean_val, 1) if not pd.isna(mean_val) else 0
                    })

        if heatmap_data:
            df_heat = pd.DataFrame(heatmap_data)
            
            # Pivot the flat array into a 2D grid matrix suitable for structural graphing
            df_heat_pivot = df_heat.pivot(
                index="Core Dimension", 
                columns="Socio-Demographic Group", 
                values="Mean Proficiency (%)"
            )
            
            # Retain structural order sorting across demographic series variables
            df_heat_pivot = df_heat_pivot[list(slice_mapping.values())]

            # Generate the visualization utilizing Plotly Express's Heatmap module
            fig_heat = px.imshow(
                df_heat_pivot,
                labels=dict(x="Demographic Group Segment", y="Competence Dimension", color="Avg %"),
                x=df_heat_pivot.columns,
                y=df_heat_pivot.index,
                color_continuous_scale=styles.EU_CORNFLOWER,
                text_auto='.1f',
                height=450
            )

            fig_heat.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(t=10, b=20, l=10, r=10)
            )

            st.plotly_chart(fig_heat, use_container_width=True)
            
            # Strategic Data-Driven Summary Insights Generator Box
            st.markdown("##### Matrix Structural Observations")
            
            # Calculate metrics to output dynamic commentary
            max_val = df_heat["Mean Proficiency (%)"].max()
            min_val = df_heat["Mean Proficiency (%)"].min()
            top_seg = df_heat.loc[df_heat["Mean Proficiency (%)"].idxmax()]
            bot_seg = df_heat.loc[df_heat["Mean Proficiency (%)"].idxmin()]
            
            st.markdown(f"""
                * **Peak Adoption Concentration:** Maximum proficiency is reached inside the **{top_seg['Socio-Demographic Group']}** subgroup evaluating **{top_seg['Core Dimension']}** at **{max_val}%**.
                * **Core Exclusion Point:** Structural friction is concentrated heaviest in the **{bot_seg['Socio-Demographic Group']}** cohort assessing **{bot_seg['Core Dimension']}**, dropping to **{min_val}%**.
                * **Vertical Line Check:** Scan the heatmap vertically. If colors transition rapidly from dark to light, it proves that **{deep_demo_choice}** exerts a dominant leverage force on digital integration regardless of the specific skill domain.
            """)
        else:
            st.warning("Matching metric matrix blocks could not be constructed for this segment setup.")



# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
           and ICT Usage collected in the framework od [ESS ICT Survey](https://ec.europa.eu/eurostat/web/microdata/collections-research/survey-ict-use-households-individuals)
""")