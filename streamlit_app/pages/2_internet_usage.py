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
# MAIN TABS ARCHITECTURE
# ==============================================================================
tab_overview, tab_gender, tab_age, tab_edu, tab_urban = st.tabs([
    "Overview", 
    "Gender", 
    "Age Groups",
    "Education Levels",
    "Urbanization Levels"
])

# ==============================================================================
# --- TAB 1: OVERVIEW ---
# ==============================================================================
with tab_overview:
    
    st.subheader("Macro Trends & National Baselines")
    
    # --------------------------------------------------------------------------
    # 6 KPI METRIC COLUMNS (change with country selection)
    # --------------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.metric(label="Daly Usage Internet", value=f"{df_filtered_baseline['i_iday'].mean().round(1)}%")
        
    with kpi2:
        st.metric(label="AI Tools", value=f"{df_filtered_baseline['i_iuai'].mean().round(1)}%")
        
    with kpi3:
        st.metric(label="Civic Participation", value=f"{((df_filtered_usage['i_iucpp_f_y16_74'].mean().round(1)+df_filtered_usage['i_iucpp_m_y16_74'].mean().round(1))/2).round(1)}%")
        
    with kpi5:
        st.metric(label="Messaging", value=f"{((df_filtered_usage['i_iuchat1_m_y16_74'].mean().round(1)+df_filtered_usage['i_iuchat1_f_y16_74'].mean().round(1))/2).round(1)}%")
    
    with kpi4:
        st.metric(label="Playing Games", value=f"{((df_filtered_usage['i_iupdg_m_y16_74'].mean().round(1)+df_filtered_usage['i_iupdg_f_y16_74'].mean().round(1))/2).round(1)}%")
   
    with kpi6:
        st.metric(label="Encountered Difficulties", value=f"{((df_filtered_usage['i_iups_m_y16_74'].mean().round(1)+df_filtered_usage['i_iups_f_y16_74'].mean().round(1))/2).round(1)}%")
        
    st.write("---")

    # --------------------------------------------------------------------------
    # TWO COLUMN LAYOUT: MAP (LEFT) & TEXT EXPLANATION (RIGHT)
    # --------------------------------------------------------------------------
    col_map, col_text = st.columns([3, 1])

    with col_map:
        st.markdown("### Geographic Distribution")
        
        map_radio_options = {
            "Using Internet Daily": "i_iday",
            "Using AI Tools": "i_iuai",
            "Civic and Political Participation Online": "i_iucpp",
            "Playing Online Games": "i_iupdg",
            "Expressing Political Opinion on Social Media":"i_iupol2",
            "Facing Doubtful/Untrue Info Online":"i_udi",
            "Encounering Difficulties While Using Internet":"i_iups",
            "Messaging": 'i_iuchat1',
            "Neve Used Internet": "i_iux"
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
        st.markdown("### Section Context")
        st.markdown(f"""
            This geographic baseline displays aggregated usage trends across individual member states. 
            Use the radio buttons above to shift the spatial layout between communication frequency, 
            frontier AI adoption, or friction layers.
        """)

        with st.expander("Click to view Framework Methodology & Definitions"):
            st.markdown("""
                * **Data Scope:** Uniform country aggregates across selected valid European states.
                * **Base Variable Evaluation:** Indicators represent percentages of the total population aged 16-74 within each localized region.
            """)
    
# ==============================================================================
# --- TAB 2: GENDER ---
# ==============================================================================
with tab_gender:
    st.header("### Gender Utility Splits & Distribution Signatures")
    st.write("""
            This section analyzes structural behavioral splits between male and female cohorts across 
            the EU. While basic volume access converges, utility pathways diverge significantly.
        """)

    internet_columns = [
        'i_iday_f_y16_74', 'i_iday_m_y16_74',
        'i_iuai_f_y16_74', 'i_iuai_m_y16_74',
        'i_iucpp_f_y16_74', 'i_iucpp_m_y16_74',
        'i_iupdg_f_y16_74', 'i_updg_m_y16_74', # Match your db typos exactly
        'i_iups_f_y16_74', 'i_iups_m_y16_74',
        'i_iux_f_y16_74', 'i_iux_m_y16_74',
        'i_udi_f_y16_74', 'i_udi_m_y16_74',
        'i_iuchat1_f_y16_74', 'i_iuchat1_m_y16_74',
        'i_iupol2_f_y16_74', 'i_iupol2_m_y16_74'
    ]

    columns = df_usage.columns
    gen_dig_skills = [c for c in columns if ('_f_' in c) or ('_m_' in c)]

    col_table, col_gender_insights = st.columns([3,2])

    with col_table:
        st.subheader("Is Gender Statistically Significant for Digital Skills Levels?")
        st.caption("Note: This table reflects aggregate EU-wide significance statistics (N=27) and remains fixed to preserve test sample validity.")
        
        df_usage_gen_results = funcs.run_t_test_pair(df_usage, gen_dig_skills, '_y16_74', usage_labels)
        df_usage_gen_results.columns = ['Indicator', 'Valid Countries (N)', 'Female Avg (%)', 'Male Avg (%)', 'Gap (Points)', 'Wilcoxon P-Value', 'Significant? (α=0.05)']
        df_usage_gen_results['Indicator'] = (
            df_usage_gen_results['Indicator']
                .str.replace('Internet:', '', case=False)
                .str.replace('Media: ', '',case=False)
                .str.replace(r'(\% of individuals)','', regex=True,case=False)
                .str.strip()
            )
        df_usage_gen_table = df_usage_gen_results.drop(columns=['Female Avg (%)', 'Male Avg (%)'])
        st.dataframe(
            df_usage_gen_table,
            column_config={
                "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                "Wilcoxon P-Value": st.column_config.NumberColumn(format="%.4f")
            },
            hide_index=True,
            use_container_width=True
        )

    with col_gender_insights:
        st.subheader("Key Insights")
        with st.expander("**1. The Dynamic Advanced Tech Gap**"):
            st.write(
                """
                - Men show a statistically significant lead in emerging and recreational tech spaces.  
                - Men outpace women by 3.5 percentage points in generative AI tool adoption and by 6.9 points in playing or downloading games.  
                - This suggests that early-stage adoption of frontier tech trends and recreational digital interaction 
                remains heavily skewed toward male demographics across the EU.
                """
        )
        with st.expander("**2. Women Lead on Essential Communication, Men on Public Voice**"):
            st.write(
                """
                - While women significantly dominate the private sphere of communication, men leverage digital channels more for public and political visibility.
                - Women hold a firm 3.0 percentage point lead in routine internet message exchanges.
                - Conversely, men lead by 2.3 points in expressing opinions on civic or political issues on social media and by 1.6 points in online political participation.
                - Digital utility splits along structural lines: women utilize the internet more for social cohesion and connectivity, while men are more likely to use it as a platform for public-facing discourse.
                """
        )
        with st.expander("**3. Equal Vulnerability to Misinformation & Access Obstacles**"):
            st.write(
                """ 
                - Negative internet experiences show no significant gender division.
                - Men are slightly more likely to report encountering untrue or doubtful information online.
                - Encountering technical difficulties and complete internet exclusion show high p-values, making them statistically identical across genders.
                """
        )
    st.write("---")


    if len(selected_countries) == 1:
        dynamic_subheader = f"Digital Activities Comparison — {selected_countries[0]}"
    elif len(selected_countries) == len(available_countries):
        dynamic_subheader = "Digital Activities Comparison — EU Aggregate (All Countries)"
    elif len(selected_countries) <= 3:
        dynamic_subheader = f"Digital Activities Comparison — {', '.join(selected_countries)}"
    else:
        dynamic_subheader = f"Digital Activities Comparison — Aggregated ({len(selected_countries)} Countries)"

    st.subheader(dynamic_subheader)
    
    gender_filter = st.selectbox(
        "Select Demographic View:",
        options=["Both", "Female", "Male"],
        index=0
    )

    chart_summary_rows = []

    # Ensure data exists for the selected countries
    if not df_filtered_usage.empty:
        
        # 💡 Loop directly through your paired columns array by steps of 2!
        for i in range(0, len(gen_dig_skills), 2):
            fem_col = gen_dig_skills[i]
            male_col = gen_dig_skills[i+1]
            
            # Double-check that these columns exist in the active dataframe stream
            if fem_col in df_filtered_usage.columns and male_col in df_filtered_usage.columns:
                mean_fem = df_filtered_usage[fem_col].mean()
                mean_male = df_filtered_usage[male_col].mean()
                
                # Grab the dynamic title from your labels dictionary using the female column key
                raw_title = usage_labels.get(fem_col, fem_col)
                
                # Clean up the prefixes inline instantly
                display_label = (
                    str(raw_title)
                    .replace('Internet:', '')
                    .replace('Media:', '')
                    .replace('(% of individuals)', '')
                    .strip()
                )
                
                chart_summary_rows.append({
                    'Indicator': display_label,
                    'Female': round(mean_fem, 1) if not pd.isna(mean_fem) else 0,
                    'Male': round(mean_male, 1) if not pd.isna(mean_male) else 0
                })

        # Render only if rows were found
        if chart_summary_rows:
            df_chart = pd.DataFrame(chart_summary_rows)
            
            df_melted = df_chart.melt(
                id_vars=['Indicator'], 
                value_vars=['Female', 'Male'], 
                var_name='Gender', 
                value_name='Percentage (%)'
            )
            df_melted = df_melted.sort_values('Percentage (%)')

            if gender_filter != 'Both':
                df_with_selection = df_melted[df_melted['Gender'] == gender_filter]
            else:
                df_with_selection = df_melted


            fig = px.bar(
                df_with_selection, 
                x='Percentage (%)', 
                y='Indicator', 
                color='Gender', 
                barmode='group',
                color_discrete_map={'Female': '#498cdb', 'Male': '#001f63'},
                height=450,
                labels={'Percentage (%)': 'Share', 'Gender': 'Group'},
                hover_data={'Indicator': True, 'Gender':True, 'Percentage (%)': ':.1f%'}
            )

            fig.update_layout(
                xaxis_title="Average Percentage (%)",
                yaxis_title=None,
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
                margin=dict(l=20, r=20, t=20, b=20)
            )

            fig.update_xaxes(showgrid=True, gridcolor='rgba(226, 232, 240, 0.5)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No tracking indicators matched your data criteria for this country choice.")
    else:
        st.warning("Please select at least one country from the sidebar to populate the chart visualization.")







    



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
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
           and ICT Usage collected in the framework od [ESS ICT Survey](https://ec.europa.eu/eurostat/web/microdata/collections-research/survey-ict-use-households-individuals)
    """)