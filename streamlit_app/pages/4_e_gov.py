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

# formatting for KPIs:
st.markdown("""
    <style>
    /* Define the structure for custom metric card */
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

# ==============================================================================
# 2. DATA INGESTION & DICTIONARY RUNTIME INITIALIZATION
# ==============================================================================
try:
    df_gov, gov_labels = funcs.load_tab_data('stg_gov_demog_2025', 'mart_indicators')
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# build the custom structured column mapping dictionary using helper function
gov_maps = funcs.extract_demographic_metrics(df_gov)

# helper map to bypass case-sensitivity when checking for dataframes
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
st.title("Modern E-Government Demographics Workspace")
st.caption("""
    **Examining the Socio-Demographic Layers of European eID & E-Gov Services**: 
    This workspace uses structured significance metrics to isolate digital governance variance across the selected countries.
""")

# ==============================================================================
# 5. MAIN HIGH-LEVEL TABS ARCHITECTURE
# ==============================================================================
tab_usage, tab_barriers, tab_trust_correlations, tab_skills_vs_egov = st.tabs([
    "E-Government Usage & Engagement", 
    "Barriers & Reasons for Non-Usage",
    "Institutional Trust & E-Government",
    "Digital Skills vs E-Government Tools Usage"
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
    st.header("Macro Trends & National Baselines | E-Gov & eID")
    st.caption("The KPIs below represent _online_ interactions with authorities and usage of digital tools, like E-Government and eIDs.")

    # data for KPIs:
    metrics_data = [
        ("Using eIDs", df_filtered_baseline['i_ieid'].mean().round(2)),
        ("Don't Have eIDs", df_filtered_baseline['i_ireidno'].mean().round(2)),
        ("Use Public Services", df_filtered_baseline['i_iugov1'].mean().round(2)),
        ("Pay Taxes", df_filtered_baseline['i_igovtax2'].mean().round(2)),
        ("Request Benefits", df_filtered_baseline['i_igovbe'].mean().round(2)),
        ("Make Appointments", df_filtered_baseline['i_igovapr'].mean().round(2))
    ]

    # the KPIs:
    cols = st.columns(6)
    for i, col in enumerate(cols):
        label, val = metrics_data[i]
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

    col_map_tab1, col_key_insights_tab1 = st.columns([4,2])

    with col_map_tab1:
        # --- MAP INSERTION ---
        # create dictionary to map specific 7 usage metrics to their descriptive titles
        tab1_display_options = {
            baseline_labels.get(code, code).replace("e-Gov: ", "").replace("eID", "").replace(": ",""): code 
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
                height=700
            )
            fig.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Value: %{z:.2f}%<extra></extra>")
            fig.update_geos(
                projection_type="mercator", center=dict(lon=10, lat=52), projection_scale=4.5,         
                visible=False, showframe=False, showcoastlines=True, coastlinecolor="LightGray",
                resolution=50, bgcolor="rgba(0,0,0,0)"                 
            )
            fig.update_layout(
                margin={"r":0, "t":0, "l":0, "b":0}, 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                coloraxis_colorbar=dict(
                    title="Percent"
                ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data columns located for this indicator setup.")
        
    with col_key_insights_tab1:
        st.markdown("##### Key Insights")
        st.warning(""" 
            **The Urban Divide**: Living in different types of areas creates a statistically significant gap in using online services. 
            Geography is a persistent **barrier** to accessing online services and interacting with authorities
        """)
        st.info("""
            **The Age Factor**: The data highlights that age cohorts exhibit massive disparities in usage, with gaps as high as **37.4** points 
            in areas like tax declarations. These results are significant across all the age cohorts. Age strongly influences how populations navigate the digital landscape
        """)
        st.warning("""
            **The Education Gap**: Education is a much stronger driver of digital engagement, with significant gaps appearing across every single category E-Government tools
        """)
        st.info("""
            **The Gender Perspective**: Gender differencesare relatively small and inconsistent, with several key areas showing no statistically significant gap
        """)

    st.write("---")


    # ------------------ DYNAMIC BOXPLOT STUDIO ------------------
    st.subheader("Dynamic Boxplot Lab")
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

        dim_options = list(DIMENSIONS.keys())
        default_idx = dim_options.index("Age Cohorts")

        with b_col2:
            selected_dim = st.selectbox("Select Demographic Dimension Breakout", options=dim_options, key="usage_dim",index=default_idx)
            
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
            
            # dynamic clean plot header title using clean baseline dictionary
            clean_plot_title = baseline_labels.get(selected_metric.lower(), selected_metric.upper())
            clean_plot_title = clean_plot_title.replace("e-Gov: ", "").replace("eID: ", "")

            fig_box = px.box(
                df_melted, 
                x="Demographic Slice", 
                y="Percentage", 
                color="Demographic Slice",
                points="all", 
                hover_data=[country_col],
                title=f"Distribution Matrix: {clean_plot_title}"
            )
            fig_box.update_layout(height=400, showlegend=False, margin={"t":40, "b":40})
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.caption("The selected demographic combination is not completely mapped for this metric in the database tables.")

    funcs.read_boxplot()        
    
    # ------ Significance of Demographic Dimensions --------
    st.subheader("Comparative Demographic Analysis")
    
    # advanced helper that handles both raw code strings and pre-labeled strings safely
    def get_clean_table_label(raw_string, prefix_to_strip):
        raw_str_clean = str(raw_string).strip()
        
        # scenario A: If the string is already a descriptive title containing a system prefix,
        # skip the complex matching entirely and just strip the headers!
        if any(p in raw_str_clean for p in ["e-Gov:", "eID:", "eID Non-Use:", "eID Barriers:"]):
            return (raw_str_clean
                    .replace("e-Gov: ", "")
                    .replace("eID: ", "")
                    .replace("eID Non-Use: ", "")
                    .replace("eID Barriers: ", "")
                    .replace("e-Gov : ", "")
                    .strip())
            
        # scenario B: It's a mangled key token from a t-test (e.g., "I Igovrx F")
        normalized_target = raw_str_clean.replace(" ", "").lower()
        if normalized_target.endswith('f') and not normalized_target.startswith('i_ireidf'):
            normalized_target = normalized_target[:-1]

        for k, v in baseline_labels.items():
            # remove spaces and underscores from the dictionary key to ensure a structural match
            normalized_key = k.replace("_", "").replace(" ", "").lower()
            if normalized_key in normalized_target or normalized_target in normalized_key:
                return (v.replace("e-Gov: ", "")
                        .replace("eID: ", "")
                        .replace("eID Non-Use: ", "")
                        .replace("eID Barriers: ", "")
                        .replace("e-Gov : ", "")
                        .strip())
        return raw_str_clean
    
    # ------- GENDER ---------

    with st.expander("Gender Gaps Significance (Wilcoxon Signed-Rank)", expanded=False):
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
    
    # ------- EDUCATION ---------
    with st.expander("Education Level Variance (Friedman Multi-Group)", expanded=False):
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

    # ------- URBANIZATION ---------
    with st.expander("Urbanization Split Variance (Friedman Multi-Group)", expanded=False):
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

    # ------- AGE ---------
    with st.expander("Age Cohorts Variance (Friedman Multi-Group)", expanded=False):
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

    st.header("Main Reasons of Not Using E-Government Tools and eIDs")
    barriers_data = [
        ("No Awareness", df_filtered_baseline['i_ireidna'].mean().round(2)),
        ("No Posession", df_filtered_baseline['i_ireidno'].mean().round(2)),
        ("No Need", df_filtered_baseline['i_ireidnn'].mean().round(2)),
        ("Security", df_filtered_baseline['i_ireidsec'].mean().round(2)),
        ("Technical Problems", df_filtered_baseline['i_ireidtec'].mean().round(2)),
        ("No Compatible Device", df_filtered_baseline['i_ireiddev'].mean().round(2))
    ]

    # the KPIs:
    cols = st.columns(6)
    for i, col in enumerate(cols):
        label, val = barriers_data[i]
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

    col_map_tab2, col_key_insights_tab2 = st.columns([3,2])

    
    with col_map_tab2:
    # --- MAP (BARRIERS) ---
        barrier_options_map = {}
        for metric_code in map_tab2_no_eid_metrics:

            matched_col = next((c for c in df_tab2_map.columns if c.lower() == metric_code.lower()), None)
            
            if matched_col:
                raw_label = baseline_labels.get(metric_code, metric_code)
                
                clean_label = (raw_label
                            .replace("eID Non-Use: ", "")
                            .replace("eID Barriers: ", "")
                            .replace("e-Gov: ", "")
                            .replace("eID: ", "")
                            .strip())
                
                barrier_options_map[clean_label] = matched_col

        # alphabetical order:
        barrier_options_map = dict(sorted(barrier_options_map.items()))

        if barrier_options_map:

            # selection of a metric:
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
                height=700
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
        

    with col_key_insights_tab2:
        st.markdown("##### Key Insights")
        st.info("""
            **Gender Neutrality in Adoption Barriers**: For almost all reasons why people don't use eIDs
            there is no significant difference between men and women. While there is a slight, statistically significant gap regarding 
            "security concerns," overall, gender is not a major factor in explaining why individuals struggle to adopt eID services
        """)
        st.warning("""
            **Education level** creates significant, measurable gaps in eID adoption. The largest barriers for less-educated groups are 
            lack of awareness and not having an eID account. Digital literacy initiatives are more effective when targeted at educational 
            gaps
        """)
        st.warning("""
            **The Urban-Rural Knowledge Gap**: Geographical location (specifically living in more rural or isolated areas) creates a significant 
            information barrier. Improving awareness campaigns in these areas could be a highly effective way to bridge the gap
        """)
        st.info("""
            **Age as a Primary Driver of Complexity**: Age cohorts show a high number of significant disparities across multiple barriers to eID adoption.
            Age significantly influence awareness, perceived need, actual ownership, security concerns, and technical difficulties
        """)


    st.write("---")

    # ------------------ DYNAMIC BOXPLOT STUDIO ------------------
    st.subheader("Dynamic Boxplot Lab")
    barr_base_metrics = [m for m in gov_maps["education"]["base_metrics"] if m.lower().startswith('i_ireid')]

    if barr_base_metrics:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            def format_tab2_boxplot(x):
                raw_label = baseline_labels.get(x.lower(), x.upper())
                clean_label = raw_label.replace("eID Non-Use: ", "").replace("eID Barriers: ", "")
                return clean_label
            
            metric_index = barr_base_metrics.index("i_ireidna")

            selected_metric_b = st.selectbox(
                "Select Metric for Distribution Analysis", 
                options=barr_base_metrics, 
                format_func=format_tab2_boxplot,
                key="t2_boxplot_metric_dropdown",
                index=metric_index
            )

        dim_options_tab2 = list(DIMENSIONS.keys())
        default_idx_tab2 = dim_options_tab2.index("Age Cohorts")
        with b_col2:
            selected_dim_b = st.selectbox(
                "Select Demographic Dimension Breakout", 
                options=list(DIMENSIONS.keys()), 
                key="barr_dim",
                index=default_idx_tab2)
            

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
            
    funcs.read_boxplot()

    # ------------------ SIGNIFICANCE MATRICES ------------------
    st.subheader("Analyzing Barriers to eID Adoption")

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
    
    # ----- GENDER ----
    with st.expander("Gender Gaps Significance (Wilcoxon Signed-Rank)", expanded=False):
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

    # ----- EDUCATION ----
    with st.expander("Education Level Variance (Friedman Multi-Group)", expanded=False):
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

    # ---- URBANIZATION -----
    with st.expander("Urbanization Split Variance (Friedman Multi-Group)", expanded=False):
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

    # ----- AGE ---- 
    with st.expander("Age Cohorts Variance (Friedman Multi-Group)", expanded=False):
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


    st.warning("""
        **Sample Size**: The reduction of the statistical sample size from 27 to 15 or 16 needed further investigation.
            """)
    st.info("""
        **Low Reliablity**: Additional check with the data source [Eurostat | Use of electronic identification (eID) `isoc_eid_ieid` Table](https://ec.europa.eu/eurostat/databrowser/view/isoc_eid_ieid/default/table?lang=en&category=isoc.isoc_i.isoc_ci_egi)
        confirmed that several countries (**Denmark**, **Estonia**, **Greece**, **Finland**, **Sweden**, and **Norway**)
        missing data on multiple metrics (e.g., "Indiciduals not using their eID in the last 12 months because they were not aware of its existance", `i_ireidna`)
        for several age cohorts. For some other countries (e.g., **Belgium**, **Ireland**, **France**, **Netherlands**, **Latvia**, and **Lithuania**)
        the existing data marked with the flag `:u`, signaling "low reliability".
        \nLow reliability in the context of the Eurostat data means that the values are based on small samples or do not meet standard Eurostat criteria
        for statistical analysis.""")



# ==============================================================================
# --- TAB 3: TRUST & E-Government USAGE CORRELATIONS ---
# ==============================================================================
with tab_trust_correlations:
    st.header("Institutional Trust & E-Government Tools Usage | Are There Correlations?")

    # get the data:
    try:
        df_trust, trust_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract macro baseline analysis layers: {e}")
        df_trust = pd.DataFrame()


    if df_trust.empty:
        st.warning("Baseline data table assets are currently unavailable.")
    else:
        df_filtered_trust = df_trust[df_trust['clean_country_name'].isin(selected_countries)]

    trust_data = [
        ("National Government", df_filtered_trust['tr_nat_gov'].mean().round(2)),
        ("National Parliament", df_filtered_trust['tr_nat_par'].mean().round(2)),
        ("Political Parties", df_filtered_trust['tr_party'].mean().round(2)),
        ("The EU", df_filtered_trust['tr_eu'].mean().round(2)),
        ("Public Authorities", df_filtered_trust['tr_authority'].mean().round(2)),
        ("National Press", df_filtered_trust['tr_press'].mean().round(2))
    ]

    # the KPIs:
    cols_barr = st.columns(6)
    for i, col in enumerate(cols_barr):
        label, val = trust_data[i]
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)


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
        'tr_info_polit_on_soc_net': 'Trust: Political Info on Social Media'
    }
        
    EGOV_METRICS = {
        'i_iugov1': 'General Interaction with Authorities',
        'i_igovapr': 'Making Appointments Online',
        'i_igovtax2': 'Submitting Tax Declaration Online',
        'i_igovbe': 'Requesting Benefits Online',
        'i_igovrcc': 'Other Requests and Complaints Online',
        'i_igovrx': 'No Requests Online',
        'i_ieid': 'Have eID',
        'i_ireidno': "Don't Have eID"
    }

    col_correlation, col_insights_corr = st.columns([4,1])

    available_trust = [c for c in TRUST_METRICS.keys() if c in df_filtered_trust.columns]
    available_egov = [c for c in EGOV_METRICS.keys() if c in df_filtered_trust.columns]

    if available_trust and available_egov:
        # ==============================================================================
        # COMPONENT 1: THE SPLIT GRID HEATMAP (Trust on Y, e-Gov on X)
        # ==============================================================================
        with col_correlation:
            st.subheader("Macro Trust vs. Digital Interaction Matrix")
            funcs.read_pearson()

            all_target_cols = available_trust + available_egov
            df_corr_matrix = df_filtered_trust[all_target_cols].corr(method='pearson')
            
            df_heatmap_slice = df_corr_matrix.loc[available_trust, available_egov]
            
            df_heatmap_slice.index = [TRUST_METRICS[c] for c in df_heatmap_slice.index]       # Rows = Trust
            df_heatmap_slice.columns = [EGOV_METRICS[c] for c in df_heatmap_slice.columns]   # Columns = e-Gov

            fig_corr = px.imshow(
                df_heatmap_slice,
                labels=dict(x="e-Government / Digital Metric", y="Trust & Perception Vector", color="Pearson R"),
                x=df_heatmap_slice.columns,
                y=df_heatmap_slice.index,
                color_continuous_scale="RdBu",
                zmin=-1.0, zmax=1.0,
                text_auto='.2f',
                height=800
            )
            fig_corr.update_layout(
                margin=dict(t=10, b=25, l=10, r=10),
                xaxis_tickangle=-45,
                yaxis=dict(tickfont=dict(size=18)), # increase the font on Y
                xaxis=dict(tickfont=dict(size=18)), # increade the font on X
                coloraxis_showscale=False # ommit the legend
            )
            fig_corr.update_traces(textfont_size=16)

        
            st.plotly_chart(fig_corr, use_container_width=True)
            
        with col_insights_corr:
            st.markdown("##### Key Insights")
            st.warning(
                """
                **The Social Media Paradox**: Trust to Social Media Networks had strong negative correlation with active E-Government usage and 
                strong positive correlation with not having eID. Individuals who place high trust in social media as an information source are 
                significantly less likely to engage with formal E-Government services and more likely to lack an eID
                """
            )
            st.info(
                """
                **Convenience as a Proxy for Trust**: Users often adopt e-Government tools because they offer immediate, tangible benefits
                (time savings, 24/7 access, reduced bureaucracy). "Digital Adoption" is increasingly becoming a pragmatic behavior rather than a political one. 
                Even individuals with low trust in public authorities or the national government will use digital services if those services reliably reduce 
                the friction of daily life.
                """
            )

        # ==============================================================================
        # COMPONENT 2: INTERACTIVE OLS REGRESSION SCATTER MODEL
        # ==============================================================================
        st.subheader("Macro Bivariate Scatter & Ordinary Least Squares (OLS) Model")
        st.markdown("_Pick any two indicators from your matrix above to fit a linear regression line across selected EU states._")

        col_input_x, col_input_y = st.columns(2)
        with col_input_x:

            chosen_x_col = st.selectbox(
                "Select Digital/e-Gov Predictor (X Axis):",
                options=available_egov,    
                format_func=lambda x: EGOV_METRICS[x]  ,
                index=2 # defaults to tax declarations
            )
        with col_input_y:
            # Y-Axis selectbox should display and handle Trust metrics
            chosen_y_col = st.selectbox(
                "Select Institutional Trust Outcome (Y Axis):",
                options=available_trust, 
                format_func=lambda x: TRUST_METRICS[x],
                index=1 # defaults to trust to public authority
            )

        df_model_clean = df_filtered_trust[[chosen_x_col, chosen_y_col, 'clean_country_name']].dropna()

        if len(df_model_clean) >= 4:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_model_clean[chosen_x_col], df_model_clean[chosen_y_col]
            )
            r_squared = r_value ** 2

            fig_reg = px.scatter(
                df_model_clean, x=chosen_x_col, y=chosen_y_col,
                hover_name='clean_country_name',
                labels={chosen_x_col: EGOV_METRICS[chosen_x_col], chosen_y_col: TRUST_METRICS[chosen_y_col]},
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
                else:
                    st.info("⚪ Not Significant")
        else:
            st.warning("Insufficient valid pairwise country records available for the active geography filters.")



# ==============================================================================
# --- TAB: DIGITAL SKILLS VS. E-GOVERMENT ADOPTION ---
# ==============================================================================
with tab_skills_vs_egov:
    st.header("Digital Literacy and E-Government Tools | More Literacy Boosts the Usage?")

    try:
        df_pipeline, pipeline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract macro baseline for capability modeling: {e}")
        df_pipeline = pd.DataFrame()

    if df_pipeline.empty:
        st.warning("Baseline data table assets are currently unavailable.")
    else:
        df_filtered_pipe = df_pipeline[df_pipeline['clean_country_name'].isin(selected_countries)]

        # Group 1: The Core Digital Competence Brackets (X-Axis)
        SKILL_BRACKETS = {
            'i_dsk2_ab': 'Above Basic Digital Skills',
            'i_dsk2_b': 'Basic Digital Skills',
            'i_dsk2_lw': 'Low Digital Skills',
            'i_dsk2_lm': 'Limited Digital Skills',
            'i_dsk2_n': 'Narrow Digital Skills',
            'i_dsk2_x': 'No Digital Skills (Exclusion Baseline)'
        }
        
        ADOPTION_ACTIONS = {
            'i_ieid': 'Possessing/Using eID Systems',
            'i_ireidno': 'Barrier: Lack of eID Possession',
            'i_iugov1': 'Interacting Online with Public Authorities',
            'i_iucpp': 'Civic and Political Participation Online',
            'i_igovtax2': 'Online Tax Declaration Submission',
            'i_igovbe': 'Requesting Benefits Online',
            'i_igovrcc': 'Other Complains and Requests Online'
        }

        col_heatmap_tab3, col_insights_tab3 = st.columns([4,1])
        available_skills = [c for c in SKILL_BRACKETS.keys() if c in df_filtered_pipe.columns]
        available_actions = [c for c in ADOPTION_ACTIONS.keys() if c in df_filtered_pipe.columns]

        if available_skills and available_actions:
            # ==============================================================================
            # COMPONENT 1: THE SPLIT GRID HEATMAP
            # ==============================================================================
            with col_heatmap_tab3:
                st.subheader("Digital Skills vs E-Government Usage Correlation Matrix")
                funcs.read_pearson()

                all_target_cols = available_skills + available_actions
                df_pipe_corr = df_filtered_pipe[all_target_cols].corr(method='pearson')
                
                df_pipe_heatmap = df_pipe_corr.loc[available_actions, available_skills]
                
                df_pipe_heatmap.index = [ADOPTION_ACTIONS[c] for c in df_pipe_heatmap.index]
                df_pipe_heatmap.columns = [SKILL_BRACKETS[c] for c in df_pipe_heatmap.columns]

                fig_pipe_corr = px.imshow(
                    df_pipe_heatmap,
                    labels=dict(x="Digital Skills Levels", y="e-Gov / eID Action", color="Pearson R"),
                    x=fig_pipe_corr.data[0].x if 'fig_pipe_corr' in locals() else df_pipe_heatmap.columns,
                    y=df_pipe_heatmap.index,
                    color_continuous_scale="RdBu",
                    zmin=-1.0, zmax=1.0,
                    text_auto='.2f',
                    height=700
                )
                fig_pipe_corr.update_layout(
                    margin=dict(t=10, b=25, l=10, r=10),
                    xaxis_tickangle=-30,
                    coloraxis_showscale=False,
                    yaxis=dict(tickfont=dict(size=18)),
                    xaxis=dict(tickfont=dict(size=18))
                )

                fig_pipe_corr.update_traces(textfont_size=18)
                st.plotly_chart(fig_pipe_corr, use_container_width=True)
            
            with col_insights_tab3:
                st.markdown("##### Key Insights")
                st.warning(
                    """ 
                    **The Digital Divide Trap**: There is a strong negative correlation (as low as $-0.82$) between lower skill levels ("Limited," "Narrow," and "No Digital Skills") 
                    and interacting online with public authorities. This confirms that the EU’s goal of 100\\% service availability will likely fail if it 
                    does not achieve the target of 80\\% of citizens having "above basic" digital skills. Those with lower skills are effectively **excluded from the digital ecosystem**.
                """)
                st.info(
                    """
                    **The "Above Basic" Digital Skills Threshold is the Key Driver**: There is a (moderate) strong, positive correlation ($0.57$ to $0.74$) between having "Above Basic" 
                    digital skills and active usage of all E-Government tools. This skill level also has a strong negative correlation ($-0.64$) with the barrier of lacking an eID
                """)


            st.write("---")

            # ==============================================================================
            # COMPONENT 2: INTERACTIVE BIVARIATE OLS SCATTER MODEL
            # ==============================================================================
            st.subheader("The Linear Regression Model")
            st.markdown("_Isolate specific digital skills levels to see country-by-country slopes ($β$) and model significance ($p$)._")

            col_sel_x, col_sel_y = st.columns(2)
            with col_sel_x:
                chosen_skill_x = st.selectbox(
                    "Select Literacy Predictor (X Axis):",
                    options=available_skills,
                    format_func=lambda x: SKILL_BRACKETS[x],
                    index=5
                )
            with col_sel_y:
                chosen_action_y = st.selectbox(
                    "Select Platform Outcome (Y Axis):",
                    options=available_actions,
                    format_func=lambda x: ADOPTION_ACTIONS[x],
                    index=2
                )

            df_reg_clean = df_filtered_pipe[[chosen_skill_x, chosen_action_y, 'clean_country_name']].dropna()

            if len(df_reg_clean) >= 4:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    df_reg_clean[chosen_skill_x], df_reg_clean[chosen_action_y]
                )
                r_squared = r_value ** 2

                fig_pipe_reg = px.scatter(
                    df_reg_clean, x=chosen_skill_x, y=chosen_action_y,
                    hover_name='clean_country_name',
                    labels={chosen_skill_x: SKILL_BRACKETS[chosen_skill_x], chosen_action_y: ADOPTION_ACTIONS[chosen_action_y]},
                    trendline="ols",
                    trendline_color_override="#001f63"
                )
                fig_pipe_reg.update_traces(marker=dict(size=10, color="#498cdb", line=dict(width=1, color="White")))
                fig_pipe_reg.update_layout(
                    height=450,
                    margin=dict(t=15, b=15, l=15, r=15)
                )
                
                col_reg_chart, col_reg_stats = st.columns([3, 1])
                with col_reg_chart:
                    st.plotly_chart(fig_pipe_reg, use_container_width=True)
                with col_reg_stats:
                    st.markdown("### Model Diagnostics")
                    st.metric(label="R² Value", value=f"{r_squared:.3f}")
                    st.metric(label="β (Slope)", value=f"{slope:.2f}")
                    st.metric(label="p-value", value=f"{p_value:.4f}")
                    
                    if p_value < 0.05:
                        st.success("🟢 Statistically Significant")
                        st.caption("Changes in national digital literacy tiers act as a strong statistical predictor for this E-Governmnet metric.")
                    else:
                        st.info("⚪ Not Significant")
                        st.caption("The variations are likely distributed across non-linear paths or infrastructural friction points independent of basic user skills.")
            else:
                st.warning("Insufficient valid paired country profiles are active for the filtered region.")
        else:
            st.error("Schema lookup breakdown: Required indicators missing inside your database baseline table columns.")


# ==============================================================================
# FOOTER SECTION
# ==============================================================================
funcs.add_authorship_footer()