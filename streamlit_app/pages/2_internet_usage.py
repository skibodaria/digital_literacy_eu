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
# --- Gender Tab ---
gen_metrics = usage_maps["gender"]["base_metrics"]
gen_columns = usage_maps["gender"]["chart_cols"]

# --- Education Tab ---
edu_metrics = usage_maps["education"]["base_metrics"]
edu_columns = usage_maps["education"]["chart_cols"]

# --- Urbanization Tab ---
urban_metrics = usage_maps["urbanization"]["base_metrics"]
urban_columns = usage_maps["urbanization"]["chart_cols"]

# --- Age Tab ---
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
        
    with col_skills_text:
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

    col_gen_table, col_gender_insights = st.columns([3,2])

    with col_gen_table:
        st.subheader("Is Gender Statistically Significant for Digital Skills Levels?")
        st.caption("Note: This table reflects aggregate EU-wide significance statistics (N=27) and remains fixed to preserve test sample validity.")
        
        paired_gen_columns = []
        for metric in gen_metrics:
            paired_gen_columns.extend([f"{metric}_f_y16_74", f"{metric}_m_y16_74"])

        df_usage_gen_results = funcs.run_t_test_pair(
            df=df_usage, 
            column_list=paired_gen_columns, 
            suffix_to_remove='_f_y16_74',
            label_dict=usage_labels
        )
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

    st.subheader(funcs.get_dynamic_subheader(df_filtered_usage))
    
    gender_filter = st.selectbox(
        "Select Demographic View:",
        options=["Both", "Female", "Male"],
        index=0
    )

    chart_summary_rows = []

    if not df_filtered_usage.empty:
        
        for i in range(0, len(gen_columns), 2):
            fem_col = gen_columns[i]
            male_col = gen_columns[i+1]
            
            if fem_col in df_filtered_usage.columns and male_col in df_filtered_usage.columns:
                mean_fem = df_filtered_usage[fem_col].mean()
                mean_male = df_filtered_usage[male_col].mean()
                
                raw_title = usage_labels.get(fem_col, fem_col)
                
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

# ==============================================================================
# --- TAB 3: AGE GROUPS ---
# ==============================================================================
with tab_age:
    st.markdown("### Digital Utility Splits Across Generational Cohorts")
    st.write("""
        This module visualizes the correlation between age groups (spanning from youth cohorts to seniors 74 years old) 
        and digital behavioral patterns. It combines a rigorous statistical test (Friedman Chi-Square) to determine 
        if generational gaps are mathematically significant across the EU, paired with an interactive component breakdown.
    """)

    col_table_age, col_insights_age = st.columns([3, 2])

    with col_table_age:
        # 📊 Run the statistical significance test on the aggregate data
        df_age_results = funcs.run_friedman_multigroups(
            df=df_usage,
            metrics_list=age_metrics,
            group_suffixes=['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'],
            group_labels=['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'],
            metadata_dict=usage_labels
        )

        if not df_age_results.empty:
            st.subheader("Is Generational Cohort Statistically Significant for Digital Access?")
            st.caption("Note: This table reflects aggregate EU-wide significance statistics (N=27) and remains fixed to preserve test sample validity.")
            
            # Drop the raw average percentage columns to keep the significance grid lean
            cols_to_drop_age = [f"{label} Avg (%)" for label in ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']]
            df_display_age = df_age_results.drop(columns=cols_to_drop_age, errors='ignore')

            st.dataframe(
                df_display_age,
                column_config={
                    "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No tracking indicators matched your data criteria for the age group metrics.")

    with col_insights_age:
        st.subheader("Key Insights")
        with st.expander("**1. The Classic Generational Gradient**"):
            st.write(
                """
                - Advanced services and communication frequency scale inversely with age. 
                - Younger cohorts (16-34) present peak usage densities, which taper off gradually through middle-aged groups and fall sharply among cohorts aged 65-74.
                """
            )
        with st.expander("**2. Entertainment & Gaming Skews Heavily to Youth**"):
            st.write(
                """
                - Online gaming and multimedia consumption exhibit the largest generational divides across the dataset.
                - The point spread between the youngest cohort (16-19) and oldest cohort (65-74) marks a massive structural gap in recreational internet use.
                """
            )
        with st.expander("**3. Structural Friction Affects All Ages**"):
            st.write(
                """
                - Much like urbanization levels and gender, encountering technical usage difficulties presents high stability (low variance) across working age cohorts.
                - Digital friction is experienced across the board, though the oldest brackets face compounded exclusion patterns.
                """
            )

    st.write("---")
    st.subheader(funcs.get_dynamic_subheader(df_filtered_usage))

    # 📈 Render the interactive bar chart using the flat global columns variable
    funcs.render_demographic_chart(
        df_filtered_usage, 
        age_columns, 
        ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'], 
        usage_labels,
        color_map=None  # Plotly will dynamically handle the sequential palette cleanly for 7 items
    )








# ==============================================================================
# --- TAB 4: EDUCATION LEVELS ---
# ==============================================================================


with tab_edu:
    st.subheader("Granular Component Evaluation")
    st.write("Placeholder: In-depth breakdowns of specific subsets.")

    col_table_edu, col_insights_edu = st.columns([3,2])

    with col_table_edu: 
        df_edu_results = funcs.run_friedman_multigroups(
            df=df_usage,  # Static pipeline on full data for test validity
            metrics_list=edu_metrics,
            group_suffixes=['_i0_2', '_i3_4', '_i5_8'],
            group_labels=['Low Edu', 'Medium Edu', 'High Edu'],
            metadata_dict=usage_labels
        )

        cols_to_drop = [f"{label} Avg (%)" for label in ['Low Edu', 'Medium Edu', 'High Edu']]
        df_display_edu = df_edu_results.drop(columns=cols_to_drop, errors='ignore')

        st.dataframe(
            df_display_edu,
            column_config={
            "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
            "P-Value": st.column_config.NumberColumn(format="%.6f") # 🎯 Force 6 decimal places
            },
            hide_index=True,
            use_container_width=True
        )
    with col_insights_edu:
        st.subheader("Key Insights")
        st.expander("**1.**")
        st.expander("**2.**")
        st.expander("**3.**")



    st.subheader(funcs.get_dynamic_subheader(df_filtered_usage))

    funcs.render_demographic_chart(
        df_filtered_usage, 
        edu_columns, 
        ['Low Edu', 'Medium Edu', 'High Edu'], 
        usage_labels,
        color_map=COLOR_MAPS["education"]
    )


# ==============================================================================
# --- TAB 4: URBANIZATION LEVELS ---
# ==============================================================================
with tab_urban:
    st.markdown("### Digital Utility vs. Degree of Urbanization")
    st.write("""
        This module visualizes the correlation between degree of urbanization (Cities vs. Suburbs vs. Rural Areas) 
        and digital utility. It combines a rigorous statistical test (Friedman Chi-Square) to determine 
        if urban-rural gaps are mathematically significant, paired with an interactive chart to illustrate 
        the intensity of those gaps across specific digital activities..
    """)

    col_table_urb, col_insights_urban = st.columns([3,2])

    with col_table_urb:
        df_urban_results = funcs.run_friedman_multigroups(
            df=df_usage,
            metrics_list=urban_metrics,
            group_suffixes=['_ind_deg1', '_ind_deg2', '_ind_deg3'],
            group_labels=['Cities', 'Suburbs', 'Rural',],
            metadata_dict=usage_labels
        )

        if not df_urban_results.empty:
            st.subheader("Is Settlement Density Statistically Significant for Digital Access?")
            st.caption("Note: This table reflects aggregate EU-wide significance statistics (N=27) and remains fixed to preserve test sample validity.")
            
            cols_to_drop = [f"{label} Avg (%)" for label in ['Cities', 'Suburbs', 'Rural']]
            df_display = df_urban_results.drop(columns=cols_to_drop, errors='ignore')

            st.dataframe(
                df_display,
                column_config={
                    "Max Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No tracking indicators matched your data criteria for the urbanization metrics.")

    with col_insights_urban:
        st.subheader("Key Insights")
        with st.expander("**1. The Urban Advantage is Pervasive**"):
            st.write(
                """
                - For almost every metric -- especially Use of Generative AI Tools, Messages Exchange, and Daily Access -- there is a clear, 
                     downward trend as we move from Cities to Rural areas. 
                - High-density urban environments act as accelerators for digital adoption.
            """)
        with st.expander('**2. Generative AI as the "Gap Leader"**'):
            st.write(
                """
                - With a massive 15.4-point gap between cities and rural areas, Generative AI tools represent 
                the single largest point of inequality. 
                - Advanced or emerging tech is currently much more concentrated in metropolitan hubs compared to simpler tasks.
            """)
        
        with st.expander('**3. Rural "Penalty" in Online Political Participation**'):
            st.write(
                """
                - People, who live in cities, are significantly more likely to express opinions on civic/political issues and 
                participate in political activities online compared to those in rural areas. 
                - **Potential "civic digital divide" detected!**
            """)
        
        with st.expander("**4. Digital Difficulties Are Very Egalitatian**"):
            st.write(
                """
                - The analysis shows no statistically significant difference across three groups.
                - Digital friction is "democratically" distributed: everyone, regardless of where they live,
                struggles with digital tasks at the same rate.
            """)

    funcs.render_demographic_chart(
        df_filtered_usage, 
        urban_columns, 
        ['City', 'Town/Suburbs', 'Rural Areas'], 
        usage_labels,
        color_map=COLOR_MAPS["urban"]
    )


# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025). Data on Digital Skills 
           and ICT Usage collected in the framework od [ESS ICT Survey](https://ec.europa.eu/eurostat/web/microdata/collections-research/survey-ict-use-households-individuals)
    """)