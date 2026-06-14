import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import funcs

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(layout="wide")

# ==============================================================================
# 2. DATA INGESTION & DICTIONARY RUNTIME INITIALIZATION
# ==============================================================================
try:
    df_gov, gov_labels = funcs.load_tab_data('stg_gov_demog_2025', 'mart_gov_map')
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# Build the custom structured column mapping dictionary using your new helper function
gov_maps = funcs.extract_demographic_metrics(df_gov)

# Helper map to bypass case-sensitivity when checking for dataframes
gov_cols_lower = {c.lower(): c for c in df_gov.columns}

country_col = 'clean_country_name'
iso_col = 'plotly_country_code'

# ==============================================================================
# 3. SIDEBAR GLOBAL FILTER
# ==============================================================================
st.sidebar.header("Geo Filters")

country_col = 'CLEAN_COUNTRY_NAME' if 'CLEAN_COUNTRY_NAME' in df_gov.columns else 'clean_country_name'
available_countries = sorted(df_gov[country_col].unique())

select_all = st.sidebar.checkbox("Select All Countries", value=True)
if select_all:
    selected_countries = available_countries
    st.sidebar.multiselect("Active Countries", options=available_countries, default=available_countries, disabled=True)
else:
    selected_countries = st.sidebar.multiselect("Select Countries", options=available_countries, default=[])

if not selected_countries:
    st.info("Please select at least one country from the sidebar menu to display the visualizations.")
    st.stop()

df_filtered_gov = df_gov[df_gov[country_col].isin(selected_countries)]

# ==============================================================================
# 4. APPLICATION HEADER
# ==============================================================================
st.title("Modern E-Governance Demographics Workspace")
st.markdown("""
    ### Examining the Socio-Demographic Layers of European E-ID & E-Gov Services
    This workspace uses structured significance metrics to isolate digital governance variance across your selected countries.
""")
st.write("---")

# ==============================================================================
# 5. MAIN HIGH-LEVEL TABS ARCHITECTURE
# ==============================================================================
tab_usage, tab_barriers = st.tabs([
    "📊 E-Governance Usage & Engagement", 
    "🚫 Barriers & Reasons for Non-Usage"
])

DIMENSIONS = {
    "Gender": {"suffixes": ['_f_y16_74', '_m_y16_74'], "labels": ['Female', 'Male']},
    "Education Level": {"suffixes": ['_i0_2', '_i3_4', '_i5_8'], "labels": ['Low Edu', 'Med Edu', 'High Edu']},
    "Urbanization Level": {"suffixes": ['_ind_deg1', '_ind_deg2', '_ind_deg3'], "labels": ['Cities', 'Suburbs', 'Rural']},
    "Age Cohorts": {"suffixes": ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], "labels": ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']}
}

# ==============================================================================
# TAB 1: USAGE & ENGAGEMENT FRAMEWORK
# ==============================================================================
with tab_usage:
    # --- MAP INSERTION (USAGE) ---
    gen_usage_cols = [c for c in gov_maps["gender"]["chart_cols"] if not c.lower().startswith('i_ireid')]
    
    if gen_usage_cols and iso_col in df_filtered_gov.columns:
        primary_map_col = gen_usage_cols[0]  # Dynamically selects the first usage metric column
        
        # Pull the descriptive text title out safely from your metadata matrix
        base_metric_code = primary_map_col.split('_')[0] if '_' in primary_map_col else primary_map_col
        friendly_title = gov_labels.get(base_metric_code, "E-Gov Usage")
        
        st.subheader("Geographic Variation Overview")
        fig_map_usage = px.choropleth(
            df_filtered_gov,
            locations=iso_col,
            locationmode="ISO-3",
            color=primary_map_col,
            hover_name=country_col,
            color_continuous_scale="Viridis",
            labels={primary_map_col: "Percentage (%)"},
            title=f"Spatial Distribution Matrix: {friendly_title} (Primary Slice)"
        )
        fig_map_usage.update_geos(scope="europe", visible=True, showcountries=True, countrycolor="LightGrey")
        fig_map_usage.update_layout(height=400, margin={"r":0, "t":40, "l":0, "b":0}, geo=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_map_usage, use_container_width=True)
        st.write("---")
    

    # ------------------ DYNAMIC BOXPLOT STUDIO ------------------
    st.subheader("Dynamic Distribution Studio")
    usage_base_metrics = [m for m in gov_maps["education"]["base_metrics"] if not m.lower().startswith('i_ireid')]
    
    if usage_base_metrics:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            selected_metric = st.selectbox(
                "Select Metric for Distribution Analysis", 
                options=usage_base_metrics, 
                format_func=lambda x: f"{x.upper()} - {gov_labels.get(x, '')[:60]}..."
            )
        with b_col2:
            selected_dim = st.selectbox("Select Demographic Dimension Breakout", options=list(DIMENSIONS.keys()), key="usage_dim")
            
        # Dynamically build and check target dataframe columns
        dim_cfg = DIMENSIONS[selected_dim]
        target_cols = [f"{selected_metric}{sfx}" for sfx in dim_cfg["suffixes"]]
        df_cols_upper = [c.upper() for c in df_filtered_gov.columns]
        
        # Verify that these target columns exist in the dataframe row space
        valid_cols = [c for c in target_cols if c.upper() in df_cols_upper]
        
        if len(valid_cols) == len(target_cols):
            # Match case exactly to dataframe columns
            real_cols = [df_filtered_gov.columns[[c.upper() for c in df_filtered_gov.columns].index(vc.upper())] for vc in valid_cols]
            
            # Melt columns from wide format to long format for a clean box plot representation
            df_melted = df_filtered_gov.melt(
                id_vars=[country_col], 
                value_vars=real_cols, 
                var_name="Demographic Slice", 
                value_name="Percentage"
            )
            
            # Map technical suffixes to friendly cohort labels
            suffix_to_label = dict(zip([rc.lower() for rc in real_cols], dim_cfg["labels"]))
            df_melted["Demographic Slice"] = df_melted["Demographic Slice"].str.lower().map(suffix_to_label)
            
            fig_box = px.box(
                df_melted, 
                x="Demographic Slice", 
                y="Percentage", 
                color="Demographic Slice",
                points="all", 
                hover_data=[country_col],
                title=f"Distribution Dispersal Matrix: {gov_labels.get(selected_metric, selected_metric)}"
            )
            fig_box.update_layout(height=400, showlegend=False, margin={"t":40, "b":40})
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.caption("The selected demographic combination is not completely mapped for this metric in the database tables.")
    st.write("---")
    

    # ------ Significance of Demographic Dimensions --------
    st.subheader("Comparative Demographic Significance Matrices")
    # --- 1. Gender Usage ---
    with st.expander("Gender Gaps Significance (Usage)", expanded=True):
        # Filter chart columns to exclude 'i_ireid' reason codes
        gen_usage_cols = [c for c in gov_maps["gender"]["chart_cols"] if not c.lower().startswith('i_ireid')]
        
        if gen_usage_cols:
            df_gender = funcs.run_t_test_pair(df_filtered_gov, gen_usage_cols, '_y16_74', gov_labels)
            st.dataframe(df_gender, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching gender usage columns located.")

    # --- 2. Education Usage ---
    with st.expander("Education Level Variance (Usage)", expanded=True):
        edu_usage_metrics = [m for m in gov_maps["education"]["base_metrics"] if not m.lower().startswith('i_ireid')]
        
        if edu_usage_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=edu_usage_metrics,
                group_suffixes=['_i0_2', '_i3_4', '_i5_8'],
                group_labels=['Low Edu', 'Med Edu', 'High Edu'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching education usage variables mapped.")

    # --- 3. Urbanization Usage ---
    with st.expander("Urbanization Split Variance (Usage)", expanded=True):
        urban_usage_metrics = [m for m in gov_maps["urbanization"]["base_metrics"] if not m.lower().startswith('i_ireid')]
        
        if urban_usage_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=urban_usage_metrics,
                group_suffixes=['_ind_deg1', '_ind_deg2', '_ind_deg3'],
                group_labels=['Cities', 'Suburbs', 'Rural'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching urbanization usage variables mapped.")

    # --- 4. Age Cohorts Usage ---
    with st.expander("Age Cohorts Variance (Usage)", expanded=True):
        age_usage_metrics = [m for m in gov_maps["age"]["base_metrics"] if not m.lower().startswith('i_ireid')]
        
        if age_usage_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=age_usage_metrics,
                group_suffixes=['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'],
                group_labels=['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching age cohort usage variables mapped.")

# ==============================================================================
# TAB 2: BARRIERS & REASONS FOR NON-USAGE
# ==============================================================================
with tab_barriers:
    st.subheader("Analyzing Barriers to E-ID Adoption")
    
    # --- 1. Gender Barriers ---
    with st.expander("Gender Gaps Significance (Barriers)", expanded=True):
        # Filter chart columns to ONLY include 'i_ireid' reason codes
        gen_barr_cols = [c for c in gov_maps["gender"]["chart_cols"] if c.lower().startswith('i_ireid')]
        
        if gen_barr_cols:
            df_gender_barr = funcs.run_t_test_pair(df_filtered_gov, gen_barr_cols, '_y16_74', gov_labels)
            st.dataframe(df_gender_barr, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching gender barrier columns located.")

    # --- 2. Education Barriers ---
    with st.expander("Education Level Variance (Barriers)", expanded=True):
        edu_barr_metrics = [m for m in gov_maps["education"]["base_metrics"] if m.lower().startswith('i_ireid')]
        
        if edu_barr_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=edu_barr_metrics,
                group_suffixes=['_i0_2', '_i3_4', '_i5_8'],
                group_labels=['Low Edu', 'Med Edu', 'High Edu'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching education barrier variables mapped.")

    # --- 3. Urbanization Barriers ---
    with st.expander("Urbanization Split Variance (Barriers)", expanded=True):
        urban_barr_metrics = [m for m in gov_maps["urbanization"]["base_metrics"] if m.lower().startswith('i_ireid')]
        
        if urban_barr_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=urban_barr_metrics,
                group_suffixes=['_ind_deg1', '_ind_deg2', '_ind_deg3'],
                group_labels=['Cities', 'Suburbs', 'Rural'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching urbanization barrier variables mapped.")

    # --- 4. Age Cohorts Barriers ---
    with st.expander("Age Cohorts Variance (Barriers)", expanded=True):
        age_barr_metrics = [m for m in gov_maps["age"]["base_metrics"] if m.lower().startswith('i_ireid')]
        
        if age_barr_metrics:
            df_results = funcs.run_friedman_multigroups(
                df=df_filtered_gov,
                metrics_list=age_barr_metrics,
                group_suffixes=['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'],
                group_labels=['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'],
                metadata_dict=gov_labels
            )
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching age cohort barrier variables mapped.")

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("Data Source Reference: Eurostat Digital Economy and Society Statistics (2025).")

# gov_cols_lower = {c.lower(): c for c in df_gov.columns}

# gov_maps = funcs.extract_demographic_metrics(df_gov)
# # --- Gender Tab ---
# gen_metrics = gov_maps["gender"]["base_metrics"]
# gen_columns = gov_maps["gender"]["chart_cols"]

# # --- Education Tab ---
# edu_metrics = gov_maps["education"]["base_metrics"]
# edu_columns = gov_maps["education"]["chart_cols"]

# # --- Urbanization Tab ---
# urban_metrics = gov_maps["urbanization"]["base_metrics"]
# urban_columns = gov_maps["urbanization"]["chart_cols"]

# # --- Age Tab ---
# age_metrics  = gov_maps["age"]["base_metrics"]
# age_columns = gov_maps["age"]["chart_cols"]