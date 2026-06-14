import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import funcs
import styles
from scipy import stats

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(layout="wide")

# ==============================================================================
# 2. DATA INGESTION & DICTIONARY RUNTIME INITIALIZATION
# ==============================================================================
try:
    df_gov, gov_labels = funcs.load_tab_data('stg_gov_demog_2025', 'mart_indicators')
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
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

# Dynamic geographically-filtered slices
df_filtered_gov = df_gov[df_gov[country_col].isin(selected_countries)]
df_filtered_baseline = df_baseline[df_baseline[country_col].isin(selected_countries)]

# Target metric lists for maps
map_tab1_gov_use_metrics = ['i_ieid', 'i_igovapr', 'i_igovbe', 'i_igovrcc', 'i_iugov1', 'i_igovtax2', 'u_igovrx']
map_tab2_no_eid_metrics = ['i_ireidna', 'i_ireidno', 'i_ireidsec', 'i_ireidtec', 'i_ireidnn', 'i_ireiddev', 'i_ireidoth']
geo_columns = ['clean_country_name', 'country_code', 'plotly_country_code']

all_tab1_map_cols = map_tab1_gov_use_metrics + geo_columns
all_tab_2_map_cols = map_tab2_no_eid_metrics + geo_columns

# Slicing out map-specific dataframes from baseline data
df_tab1_map = df_filtered_baseline[[c for c in all_tab1_map_cols if c in df_filtered_baseline.columns]]
df_tab2_map = df_filtered_baseline[[c for c in all_tab_2_map_cols if c in df_filtered_baseline.columns]]

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
tab_usage, tab_barriers, tab_trust_correlations = st.tabs([
    "E-Governance Usage & Engagement", 
    "Barriers & Reasons for Non-Usage",
    "Institutional Trust & E-Governance"
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
    col_map_tab1, col_key_insights_tab1 = st.columns([3,2])

    with col_map_tab1:
        # --- MAP INSERTION (USAGE) ---
        # Create dictionary to map your specific 7 usage metrics to their descriptive titles

        tab1_display_options = {
            baseline_labels.get(code, code).replace("e-Gov: ", "").replace("eID", ""): code 
            for code in map_tab1_gov_use_metrics 
            if code in df_tab1_map.columns
        }

        tab1_display_options = dict(sorted(tab1_display_options.items()))

        selected_title = st.selectbox(
            "Select Indicator for Map Visualization:",
            options=list(tab1_display_options.keys()),
            key="map_usage_selector"
        )
        chosen_indicator_code = tab1_display_options[selected_title]
            
        st.markdown(f"### Distribution Map: {selected_title}") 

        if chosen_indicator_code:
            fig = px.choropleth(
                df_tab1_map,                           
                locations=iso_col,   
                locationmode='ISO-3',               
                color=chosen_indicator_code,                    
                hover_name=country_col,    
                hover_data=[chosen_indicator_code], 
                color_continuous_scale=styles.EU_CORNFLOWER,
                title=None,
                height=600
            )
            fig.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Value: %{z:.2f}%<extra></extra>")
            fig.update_geos(
                projection_type="mercator", center=dict(lon=10, lat=52), projection_scale=4.5,         
                visible=False, showframe=False, showcoastlines=True, coastlinecolor="LightGray",
                resolution=50, bgcolor="rgba(0,0,0,0)"                 
            )
            fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data columns located for this indicator setup.")
        
        st.write("---")
    with col_key_insights_tab1:
        st.write("there gonna be insights here")

    # ------------------ DYNAMIC BOXPLOT STUDIO ------------------
    st.subheader("Dynamic Distribution Studio")
    usage_base_metrics = [m for m in gov_maps["education"]["base_metrics"] if not m.lower().startswith('i_ireid')]
    
    if usage_base_metrics:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            def format_tab1_boxplot(x):
                # Pull directly from clean baseline labels, fall back to upper code if missing
                raw_label = baseline_labels.get(x.lower(), x.upper())
                # Strip out any remaining system headers cleanly
                clean_label = raw_label.replace("e-Gov: ", "").replace("eID: ", "")
                return clean_label

            selected_metric = st.selectbox(
                "Select Metric for Distribution Analysis", 
                options=usage_base_metrics, 
                format_func=format_tab1_boxplot,
                key="t1_boxplot_metric_dropdown"
            )
        with b_col2:
            selected_dim = st.selectbox("Select Demographic Dimension Breakout", options=list(DIMENSIONS.keys()), key="usage_dim")
            
        dim_cfg = DIMENSIONS[selected_dim]
        target_cols = [f"{selected_metric}{sfx}" for sfx in dim_cfg["suffixes"]]
        df_cols_upper = [c.upper() for c in df_filtered_gov.columns]
        
        valid_cols = [c for c in target_cols if c.upper() in df_cols_upper]
        
        if len(valid_cols) == len(target_cols):
            real_cols = [df_filtered_gov.columns[[c.upper() for c in df_filtered_gov.columns].index(vc.upper())] for vc in valid_cols]
            
            df_melted = df_filtered_gov.melt(
                id_vars=[country_col], 
                value_vars=real_cols, 
                var_name="Demographic Slice", 
                value_name="Percentage"
            )
            
            suffix_to_label = dict(zip([rc.lower() for rc in real_cols], dim_cfg["labels"]))
            df_melted["Demographic Slice"] = df_melted["Demographic Slice"].str.lower().map(suffix_to_label)
            
            # Dynamic clean plot header title using our clean baseline dictionary
            clean_plot_title = baseline_labels.get(selected_metric.lower(), selected_metric.upper())
            clean_plot_title = clean_plot_title.replace("e-Gov: ", "").replace("eID: ", "")

            fig_box = px.box(
                df_melted, 
                x="Demographic Slice", 
                y="Percentage", 
                color="Demographic Slice",
                points="all", 
                hover_data=[country_col],
                title=f"Distribution Dispersal Matrix: {clean_plot_title}"
            )
            fig_box.update_layout(height=400, showlegend=False, margin={"t":40, "b":40})
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.caption("The selected demographic combination is not completely mapped for this metric in the database tables.")
            
    st.write("---")
    
    # ------ Significance of Demographic Dimensions --------
    # ------ Significance of Demographic Dimensions --------
    st.subheader("Comparative Demographic Significance Matrices")
    
    # Advanced helper that handles both raw code strings and pre-labeled strings safely
    def get_clean_table_label(raw_string, prefix_to_strip):
        raw_str_clean = str(raw_string).strip()
        
        # Scenario A: If the string is already a descriptive title containing a system prefix,
        # skip the complex matching entirely and just strip the headers!
        if any(p in raw_str_clean for p in ["e-Gov:", "eID:", "eID Non-Use:", "eID Barriers:"]):
            return (raw_str_clean
                    .replace("e-Gov: ", "")
                    .replace("eID: ", "")
                    .replace("eID Non-Use: ", "")
                    .replace("eID Barriers: ", "")
                    .replace("e-Gov : ", "")
                    .strip())
            
        # Scenario B: It's a mangled key token from a t-test (e.g., "I Igovrx F")
        normalized_target = raw_str_clean.replace(" ", "").lower()
        if normalized_target.endswith('f') and not normalized_target.startswith('i_ireidf'):
            normalized_target = normalized_target[:-1]

        for k, v in baseline_labels.items():
            # Remove spaces and underscores from the dictionary key to ensure a structural match
            normalized_key = k.replace("_", "").replace(" ", "").lower()
            if normalized_key in normalized_target or normalized_target in normalized_key:
                return (v.replace("e-Gov: ", "")
                        .replace("eID: ", "")
                        .replace("eID Non-Use: ", "")
                        .replace("eID Barriers: ", "")
                        .replace("e-Gov : ", "")
                        .strip())
        return raw_str_clean

    with st.expander("Gender Gaps Significance (Usage)", expanded=False):
        gen_usage_cols = [c for c in df_filtered_gov.columns if not c.lower().startswith('i_ireid') and any(sfx in c.lower() for sfx in DIMENSIONS["Gender"]["suffixes"])]
        if gen_usage_cols:
            df_gender = funcs.run_t_test_pair(df_filtered_gov, gen_usage_cols, '_y16_74', baseline_labels)
            if "Indicator" in df_gender.columns:
                df_gender["Indicator"] = df_gender["Indicator"].apply(lambda x: get_clean_table_label(x, "e-Gov: "))

            cols_to_drop = [c for c in ["Female Avg (%)", "Male Avg (%)"] if c in df_gender.columns]
            df_gender = df_gender.drop(columns=cols_to_drop)
            st.dataframe(
                df_gender,
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "Wilcoxon P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.caption("No matching gender usage columns located.")

    with st.expander("Education Level Variance (Usage)", expanded=False):
        edu_usage_metrics = sorted(list(set([c.split('_i0_2')[0].split('_i3_4')[0].split('_i5_8')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Education Level"]["suffixes"]) and not c.lower().startswith('i_ireid')])))
        if edu_usage_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, edu_usage_metrics, ['_i0_2', '_i3_4', '_i5_8'], ['Low Edu', 'Med Edu', 'High Edu'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_table_label(x, "e-Gov: "))
            cols_to_drop = [c for c in ["Low Edu Avg (%)", "Med Edu Avg (%)", "High Edu Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)
            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True)
        else:
            st.caption("No matching education usage variables mapped.")

    with st.expander("Urbanization Split Variance (Usage)", expanded=False):
        urban_usage_metrics = sorted(list(set([c.split('_ind')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Urbanization Level"]["suffixes"]) and not c.lower().startswith('i_ireid')])))
        if urban_usage_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, urban_usage_metrics, ['_ind_deg1', '_ind_deg2', '_ind_deg3'], ['Cities', 'Suburbs', 'Rural'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_table_label(x, "e-Gov: "))
            
            cols_to_drop = [c for c in ["Cities Avg (%)", "Suburbs Avg (%)", "Rural Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)
            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True)
        else:
            st.caption("No matching urbanization usage variables mapped.")

    with st.expander("Age Cohorts Variance (Usage)", expanded=False):
        age_usage_metrics = sorted(list(set([c.split('_y16')[0].split('_y20')[0].split('_y25')[0].split('_y35')[0].split('_y45')[0].split('_y55')[0].split('_y65')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Age Cohorts"]["suffixes"]) and not c.lower().startswith('i_ireid')])))
        if age_usage_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, age_usage_metrics, ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_table_label(x, "e-Gov: "))
            cols_to_drop = [c for c in ["16-19 Avg (%)", "20-24 Avg (%)", "25-34 Avg (%)", "35-44 Avg (%)", "45-54 Avg (%)", "55-64 Avg (%)", "65-74 Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)
            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True)
        else: 
            st.caption("No matching age cohort usage variables mapped.")

# ==============================================================================
# TAB 2: BARRIERS & REASONS FOR NON-USAGE
# ==============================================================================
with tab_barriers:
    col_map_tab2, col_key_insights_tab2 = st.columns([2,3])
    
    with col_map_tab2:
        with col_map_tab2:
    # --- MAP INSERTION (BARRIERS) ---
            barrier_options_map = {}
            for metric_code in map_tab2_no_eid_metrics:
                # Check if the code (or its lowercase version) exists in your map dataframe columns
                # This prevents an empty dropdown if column cases shifted under the hood
                matched_col = next((c for c in df_tab2_map.columns if c.lower() == metric_code.lower()), None)
                
                if matched_col:
                    raw_label = baseline_labels.get(metric_code, metric_code)
                    
                    # Strip away all variations of system prefixes to keep the dropdown UI clean
                    clean_label = (raw_label
                                .replace("eID Non-Use: ", "")
                                .replace("eID Barriers: ", "")
                                .replace("e-Gov: ", "")
                                .replace("eID: ", "")
                                .strip())
                    
                    # Store the cleaned title as the key and the actual dataframe column name as the value
                    barrier_options_map[clean_label] = matched_col

            # Sort the options alphabetically by their clean titles for a better user experience
            barrier_options_map = dict(sorted(barrier_options_map.items()))

            if barrier_options_map:
                # 2. Render the Selectbox using the sorted clean titles
                selected_title_b = st.selectbox(
                    "Select Barrier for Map Visualization:",
                    options=list(barrier_options_map.keys()),
                    key="map_barrier_selector_dynamic" 
                )
        
                chosen_indicator_code_b = barrier_options_map[selected_title_b]
            
                st.markdown(f"### Distribution Map: {selected_title_b}")
            else:
                st.warning("No matching barrier metrics found in the map dataframe columns.")

        if chosen_indicator_code_b:
            fig_barr = px.choropleth(
                df_tab2_map,                           
                locations=iso_col,   
                locationmode='ISO-3',               
                color=chosen_indicator_code_b,                    
                hover_name=country_col,    
                hover_data=[chosen_indicator_code_b], 
                color_continuous_scale=styles.EU_CORNFLOWER,
                title=None,
                height=600
            )
            fig_barr.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Value: %{z:.2f}%<extra></extra>")
            fig_barr.update_geos(
                projection_type="mercator", center=dict(lon=10, lat=52), projection_scale=4.5,         
                visible=False, showframe=False, showcoastlines=True, coastlinecolor="LightGray",
                resolution=50, bgcolor="rgba(0,0,0,0)"                 
            )
            fig_barr.update_layout(margin={"r":0, "t":0, "l":0, "b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_barr, use_container_width=True)
        else:
            st.warning("No data columns located for this barrier setup.")
            
        st.write("---")
    
    with col_key_insights_tab2:
        st.write("there will be insights here")

    # ------------------ DYNAMIC BOXPLOT STUDIO ------------------
    st.subheader("Dynamic Distribution Studio")
    barr_base_metrics = [m for m in gov_maps["education"]["base_metrics"] if m.lower().startswith('i_ireid')]
    
    if barr_base_metrics:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            def format_tab2_boxplot(x):
                raw_label = baseline_labels.get(x.lower(), x.upper())
                clean_label = raw_label.replace("eID Non-Use: ", "").replace("eID Barriers: ", "")
                return clean_label

            selected_metric_b = st.selectbox(
                "Select Metric for Distribution Analysis", 
                options=barr_base_metrics, 
                format_func=format_tab2_boxplot,
                key="t2_boxplot_metric_dropdown"
            )
        with b_col2:
            selected_dim_b = st.selectbox("Select Demographic Dimension Breakout", options=list(DIMENSIONS.keys()), key="barr_dim")
            
        dim_cfg_b = DIMENSIONS[selected_dim_b]
        target_cols_b = [f"{selected_metric_b}{sfx}" for sfx in dim_cfg_b["suffixes"]]
        df_cols_upper_b = [c.upper() for c in df_filtered_gov.columns]
        
        valid_cols_b = [c for c in target_cols_b if c.upper() in df_cols_upper_b]
        
        if len(valid_cols_b) == len(target_cols_b):
            real_cols_b = [df_filtered_gov.columns[[c.upper() for c in df_filtered_gov.columns].index(vc.upper())] for vc in valid_cols_b]
            
            df_melted_b = df_filtered_gov.melt(
                id_vars=[country_col], 
                value_vars=real_cols_b, 
                var_name="Demographic Slice", 
                value_name="Percentage"
            )
            
            suffix_to_label_b = dict(zip([rc.lower() for rc in real_cols_b], dim_cfg_b["labels"]))
            df_melted_b["Demographic Slice"] = df_melted_b["Demographic Slice"].str.lower().map(suffix_to_label_b)
            
            # Dynamic clean plot header title for barriers
            clean_plot_title_b = baseline_labels.get(selected_metric_b.lower(), selected_metric_b.upper())
            clean_plot_title_b = clean_plot_title_b.replace("eID Non-Use: ", "").replace("eID Barriers: ", "")

            fig_box_b = px.box(
                df_melted_b, 
                x="Demographic Slice", 
                y="Percentage", 
                color="Demographic Slice",
                points="all", 
                hover_data=[country_col],
                title=f"Distribution Dispersal Matrix: {clean_plot_title_b}"
            )
            fig_box_b.update_layout(height=400, showlegend=False, margin={"t":40, "b":40})
            st.plotly_chart(fig_box_b, use_container_width=True)
        else:
            st.caption("The selected demographic combination is not completely mapped for this metric in the database tables.")
            
    st.write("---")

    # ------------------ SIGNIFICANCE MATRICES ------------------
    st.subheader("Analyzing Barriers to E-ID Adoption")
    
    def get_clean_barrier_label(raw_string, prefix_to_strip):
        raw_str_clean = str(raw_string).strip()
        
        if any(p in raw_str_clean for p in ["eID Non-Use:", "eID Barriers:", "e-Gov:", "eID:"]):
            return (raw_str_clean
                    .replace("eID Non-Use: ", "")
                    .replace("eID Barriers: ", "")
                    .replace("e-Gov: ", "")
                    .replace("eID: ", "")
                    .replace("e-Gov : ", "")
                    .strip())
            
        normalized_target = raw_str_clean.replace(" ", "").lower()
        if normalized_target.endswith('f'):
            normalized_target = normalized_target[:-1]
            
        for k, v in baseline_labels.items():
            normalized_key = k.replace("_", "").replace(" ", "").lower()
            if normalized_key in normalized_target or normalized_target in normalized_key:
                return (v.replace("eID Non-Use: ", "")
                        .replace("eID Barriers: ", "")
                        .replace("e-Gov: ", "")
                        .replace("eID: ", "")
                        .replace("e-Gov : ", "")
                        .strip())
                
        return raw_str_clean

    with st.expander("Gender Gaps Significance (Barriers)", expanded=False):
        gen_barr_cols = [c for c in df_filtered_gov.columns if c.lower().startswith('i_ireid') and any(sfx in c.lower() for sfx in DIMENSIONS["Gender"]["suffixes"])]
        if gen_barr_cols:
            df_gender_barr = funcs.run_t_test_pair(df_filtered_gov, gen_barr_cols, '_y16_74', baseline_labels)
            if "Indicator" in df_gender_barr.columns:
                df_gender_barr["Indicator"] = df_gender_barr["Indicator"].apply(lambda x: get_clean_barrier_label(x, "eID Non-Use: "))
            cols_to_drop = [c for c in ["Female Avg (%)", "Male Avg (%)"] if c in df_gender_barr.columns]
            df_gender_barr = df_gender_barr.drop(columns=cols_to_drop)

            st.dataframe(df_gender_barr, use_container_width=True, hide_index=True)
        else:
            st.caption("No matching gender barrier columns located.")

    with st.expander("Education Level Variance (Barriers)", expanded=False):
        # Loosened split logic to reliably capture the whole barrier code name
        edu_barr_metrics = sorted(list(set([c.split('_i0_2')[0].split('_i3_4')[0].split('_i5_8')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Education Level"]["suffixes"]) and c.lower().startswith('i_ireid')])))
        if edu_barr_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, edu_barr_metrics, ['_i0_2', '_i3_4', '_i5_8'], ['Low Edu', 'Med Edu', 'High Edu'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_barrier_label(x, "eID Non-Use: "))
            cols_to_drop = [c for c in ["Low Edu Avg (%)", "Med Edu Avg (%)", "High Edu Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)

            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True
            )
        else:
            st.caption("No matching education barrier variables mapped.")

    with st.expander("Urbanization Split Variance (Barriers)", expanded=False):
        urban_barr_metrics = sorted(list(set([c.split('_ind')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Urbanization Level"]["suffixes"]) and c.lower().startswith('i_ireid')])))
        if urban_barr_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, urban_barr_metrics, ['_ind_deg1', '_ind_deg2', '_ind_deg3'], ['Cities', 'Suburbs', 'Rural'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_barrier_label(x, "eID Non-Use: "))
            
            cols_to_drop = [c for c in ["Cities Avg (%)", "Suburbs Avg (%)", "Rural Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)

            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True)
        else:
            st.caption("No matching urbanization barrier variables mapped.")

    with st.expander("Age Cohorts Variance (Barriers)", expanded=False):
        age_barr_metrics = sorted(list(set([c.split('_y16')[0].split('_y20')[0].split('_y25')[0].split('_y35')[0].split('_y45')[0].split('_y55')[0].split('_y65')[0].lower() for c in df_filtered_gov.columns if any(sfx in c.lower() for sfx in DIMENSIONS["Age Cohorts"]["suffixes"]) and c.lower().startswith('i_ireid')])))
        if age_barr_metrics:
            df_results = funcs.run_friedman_multigroups(df_filtered_gov, age_barr_metrics, ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74'], baseline_labels)
            if "Indicator" in df_results.columns:
                df_results["Indicator"] = df_results["Indicator"].apply(lambda x: get_clean_barrier_label(x, "eID Non-Use: "))
            cols_to_drop = [c for c in ["16-19 Avg (%)", "20-24 Avg (%)", "25-34 Avg (%)", "35-44 Avg (%)", "45-54 Avg (%)", "55-64 Avg (%)", "65-74 Avg (%)"] if c in df_results.columns]
            df_results = df_results.drop(columns=cols_to_drop)

            st.dataframe(
                df_results, 
                column_config={
                    "Gap (Points)": st.column_config.NumberColumn(format="%.1f pts"),
                    "P-Value": st.column_config.NumberColumn(format="%.4f") 
                },
                use_container_width=True, hide_index=True)
        else: 
            st.caption("No matching age cohort barrier variables mapped.")



# ==============================================================================
# --- TAB: TRUST & E-GOVERNANCE USAGE CORRELATIONS ---
# ==============================================================================
# ==============================================================================
# --- TAB: TRUST & E-GOVERNANCE USAGE CORRELATIONS ---
# ==============================================================================
with tab_trust_correlations:
    st.header("Sociopolitical Drivers of Digital Statecraft")
    st.markdown("""
        This module evaluates the structural macro-level relationships between **Institutional Trust Vectors** and **e-Governance Adoption Rates** across EU member states.
    """)

    # --------------------------------------------------------------------------
    # 1. READ IN THE CLEAN MACRO BASELINE DATASET
    # --------------------------------------------------------------------------
    try:
        # Load the macro country-level baseline matrix directly
        df_trust, trust_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract macro baseline analysis layers: {e}")
        df_trust = pd.DataFrame()

    if df_trust.empty:
        st.warning("Baseline data table assets are currently unavailable.")
    else:
        # Filter down rows to the user's active sidebar country selections
        df_filtered_trust = df_trust[df_trust['clean_country_name'].isin(selected_countries)]

        # Group 1: Define your exact Eurobarometer trust and perception indicators (Y-Axis)
        TRUST_METRICS = {
            'tr_party': 'Trust: Political Parties',
            'tr_authority': 'Trust: Public Authorities',
            'tr_nat_gov': 'Trust: National Government',
            'tr_nat_par': 'Trust: National Parliament',
            'tr_eu': 'Trust: European Union',
            'tr_eu_par': 'Trust: European Parliament',
            'tr_press': 'Trust: Written Press',
            'tr_soc_netw_online': 'Trust: Social Networks Online',
            'nat_media_tr_info': 'Media: Trustworthy Info',
            'nat_media_free_pressure': 'Media: Free from Pressure',
            'tr_info_polit_on_soc_net': 'Trust: Political Info on Social Media',
            'eff_acc_to_tech': 'Perception: Effective Tech Access',
            'eff_improve_democr_life': 'Perception: Improves Democratic Life',
            'eff_improve_acc_pub_services': 'Perception: Improves Public Service Access',
            'eff_work_remote': 'Perception: Effectively Facilitates Remote Work'
        }
        
        # Group 2: Explicitly map your e-Gov digital metrics (X-Axis)
        EGOV_METRICS = {
            'i_iugov1': 'Interacting with Public Authorities',
            'i_igovapr': 'Online Scheduling Appointments',
            'i_igovtax2': 'Online Tax Declaration Submission',
            'i_iupdg': 'Submitting Official Forms Online',
            'i_iucpp': 'Accessing Personal Documents',
            'i_igovbe': 'Accessing Public Electronic Health Records',
            'i_igovrcc': 'Accessing Public Database/Registers',
            'i_igovrx': 'Using Request-Based Certificates',
            'i_ieid': 'Possessing/Using eID systems',
            'i_ireidno': 'Barriers: Lack of eID Possession',
            'i_iuai': 'Generative AI Tool Usage',
            'i_udi': 'Digital Exclusion Index'
        }

        # Filter dictionaries based on what columns actually exist in your database table
        available_trust = [c for c in TRUST_METRICS.keys() if c in df_filtered_trust.columns]
        available_egov = [c for c in EGOV_METRICS.keys() if c in df_filtered_trust.columns]

        if available_trust and available_egov:
            # ==============================================================================
            # COMPONENT 1: THE SPLIT GRID HEATMAP
            # ==============================================================================
            st.subheader("🔥 Macro Trust vs. Digital Interaction Split Grid")
            st.markdown("_Pearson Correlation Coefficients ($R$) comparing macro institutional sentiment variables with core e-Gov adoption actions._")

            # Calculate correlation matrix using only the relevant columns
            all_target_cols = available_trust + available_egov
            df_corr_matrix = df_filtered_trust[all_target_cols].corr(method='pearson')
            
            # Extract the cross-section slice: Trust on the Y-axis, e-Gov on the X-axis
            df_heatmap_slice = df_corr_matrix.loc[available_trust, available_egov]
            
            # Convert raw database handles to clean readable titles
            df_heatmap_slice.index = [TRUST_METRICS[c] for c in df_heatmap_slice.index]
            df_heatmap_slice.columns = [EGOV_METRICS[c] for c in df_heatmap_slice.columns]

            fig_corr = px.imshow(
                df_heatmap_slice,
                labels=dict(x="e-Governance / Digital Metric", y="Trust & Perception Vector", color="Pearson R"),
                x=df_heatmap_slice.columns,
                y=df_heatmap_slice.index,
                color_continuous_scale=styles.EU_CORNFLOWER,
                zmin=-1.0, zmax=1.0,
                text_auto='.2f',
                height=550
            )
            fig_corr.update_layout(
                margin=dict(t=10, b=25, l=10, r=10),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.write("---")

            # ==============================================================================
            # COMPONENT 2: INTERACTIVE OLS REGRESSION SCATTER MODEL
            # ==============================================================================
            st.subheader("📈 Macro Bivariate Scatter & Ordinary Least Squares (OLS) Model")
            st.markdown("_Pick any two indicators from your matrix above to fit a linear regression line across selected EU states._")

            col_input_x, col_input_y = st.columns(2)
            with col_input_x:
                chosen_x_col = st.selectbox(
                    "Select Sociopolitical Predictor (X Axis):",
                    options=available_trust,
                    format_func=lambda x: TRUST_METRICS[x]
                )
            with col_input_y:
                chosen_y_col = st.selectbox(
                    "Select Digital/e-Gov Outcome (Y Axis):",
                    options=available_egov,
                    format_func=lambda x: EGOV_METRICS[x]
                )

            # Drop missing rows to ensure clean pairwise calculations
            df_model_clean = df_filtered_trust[[chosen_x_col, chosen_y_col, 'clean_country_name']].dropna()

            if len(df_model_clean) >= 4:
                # Calculate OLS elements
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    df_model_clean[chosen_x_col], df_model_clean[chosen_y_col]
                )
                r_squared = r_value ** 2

                fig_reg = px.scatter(
                    df_model_clean, x=chosen_x_col, y=chosen_y_col,
                    hover_name='clean_country_name',
                    labels={chosen_x_col: TRUST_METRICS[chosen_x_col], chosen_y_col: EGOV_METRICS[chosen_y_col]},
                    trendline="ols",
                    trendline_color_override="#001f63"
                )
                fig_reg.update_traces(marker=dict(size=10, color="#498cdb", line=dict(width=1, color="White")))
                fig_reg.update_layout(
                    height=450,
                    margin=dict(t=15, b=15, l=15, r=15)
                )
                
                col_chart, col_stats = st.columns([3, 1])
                with col_chart:
                    st.plotly_chart(fig_reg, use_container_width=True)
                with col_stats:
                    st.markdown("### Model Diagnostics")
                    st.metric(label="R² (Explained Variance)", value=f"{r_squared:.3f}")
                    st.metric(label="β Coefficient (Slope)", value=f"{slope:.2f}")
                    st.metric(label="p-value (Significance)", value=f"{p_value:.4f}")
                    
                    if p_value < 0.05:
                        st.success("🟢 Statistically Significant")
                        st.caption("The observed linear relationship is unlikely to have occurred by chance.")
                    else:
                        st.info("⚪ Not Significant")
                        st.caption("No strong statistical support for a linear effect at this country-sample size.")
            else:
                st.warning("Insufficient valid pairwise country records available for the active geography filters.")
        else:
            st.error("Vector structural error: Mapped metric codes not found within your database baseline columns.")

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("Data Source Reference: Eurostat Digital Economy and Society Statistics (2025).")