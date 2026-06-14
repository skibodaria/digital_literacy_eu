import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


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
tab_baseline, tab_clusters = st.tabs([
    "Overview", 
    "Clustering"
])

# ==========================================
# TAB 1: PROJECT OVERVIEW
# ==========================================
with tab_baseline:
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


# ==============================================================================
# --- TAB 2: MACRO ARCHETYPES CLUSTERING ---
# ==============================================================================
with tab_clusters:
    st.header("European Archetypes: Data-Driven Country Profiles")
    st.markdown("""
        This workspace applies an unsupervised machine learning algorithm (**K-Means Clustering**) to group EU member states 
        not by geographic borders, but by structural intersections of **Digital Literacy, e-Gov Infrastructure Adoption**, and **Systemic Institutional Trust**.
    """)

    # --------------------------------------------------------------------------
    # 1. READ PIPELINE DATA & IMPORT SCALAR COMPLIANCE ENGINE
    # --------------------------------------------------------------------------
    try:
        # Load country-level baseline metrics matrix
        df_base_raw, cluster_labels_map = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract macro baseline for clustering modeling: {e}")
        df_base_raw = pd.DataFrame()

    if df_base_raw.empty:
        st.warning("Clustering baseline modeling frame is currently empty.")
    else:
        # Define the 10 distinct cross-domain features from your research strategy
        cluster_features = [
            'i_dsk2_ab', 'i_ieid', 'i_igovtax2', 'i_igovapr', 'i_iugov1', 
            'i_dsk2_x', 'i_ireidno', 
            'tr_nat_gov', 'tr_nat_par', 'tr_authority'
        ]

        # Verify which targeted tracking features exist in the table columns
        valid_features = [c for c in cluster_features if c in df_base_raw.columns]

        if len(valid_features) < len(cluster_features):
            st.error(f"Missing modeling components. Found only {len(valid_features)} of 10 attributes.")
        else:
            # Drop missing values and scale features natively using StandardScaler
            df_model_clean = df_base_raw.dropna(subset=cluster_features).copy()
            
            scaler = StandardScaler()
            scaled_matrix = scaler.fit_transform(df_model_clean[cluster_features])

            # Execute fixed K-Means modeling using your optimal K=4 solution
            optimal_k = 4
            kmeans_model = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            df_model_clean['cluster_label'] = kmeans_model.fit_predict(scaled_matrix)

            # Map cluster indices to your descriptive structural archetypes
            cluster_names = {
                0: "Digitally Engaged Sceptics",
                1: "Emerging Digital Transition",
                2: "Digital Frontrunners",
                3: "Digitally Excluded / Friction States"
            }
            df_model_clean['cluster_profile'] = df_model_clean['cluster_label'].map(cluster_names)

            # Build a lookup frame to cleanly apply cluster tags across your sidebar's country selections
            df_lookup = df_model_clean[['clean_country_name', 'cluster_label', 'cluster_profile', 'plotly_country_code'] + cluster_features]
            df_filtered_cluster = df_lookup[df_lookup['clean_country_name'].isin(selected_countries)].sort_values('cluster_label')

            # ==============================================================================
            # LAYOUT SECTION 1: SPLIT-VIEW (THE ARCHETYPE MAP & KEY METRIC SUMMARY)
            # ==============================================================================
            col_map, col_table = st.columns([7, 5])

            with col_map:
                st.subheader("🗺️ Geographic Archetype Footprint")
                
                # Custom discrete colors matching your interface styles
                color_palette = ["#498cdb", "#64748b", "#001f63", "#cbd5e1"] # Blue, Slate, Deep Blue, Light Slate

                fig_cluster_map = px.choropleth(
                    df_filtered_cluster,
                    locations='plotly_country_code',
                    locationmode='ISO-3',
                    color='cluster_profile',
                    hover_name='clean_country_name',
                    hover_data={'plotly_country_code': False, 'cluster_profile': True},
                    color_discrete_sequence=color_palette
                )

                fig_cluster_map.update_geos(              
                    projection_type="mercator", center=dict(lon=10, lat=52), projection_scale=4.5,         
                    visible=False, showframe=False, showcoastlines=True, coastlinecolor="LightGray", resolution=50
                )
                fig_cluster_map.update_layout(
                    margin={"r":0, "t":10, "l":0, "b":0},
                    height=500,
                    legend=dict(
                        title=None, orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
                    )
                )
                st.plotly_chart(fig_cluster_map, use_container_width=True)

            with col_table:
                st.subheader("📋 Member State Cluster Allocations")
                st.markdown("_Active countries categorized under their respective statistical archetypes based on your sidebar filters._")
                
                # Render clean, digestible markdown list boxes for each cluster block
                if not df_filtered_cluster.empty:
                    for cl_idx in sorted(cluster_names.keys()):
                        c_list = df_filtered_cluster[df_filtered_cluster['cluster_label'] == cl_idx]['clean_country_name'].tolist()
                        if c_list:
                            st.markdown(f"**🔹 {cluster_names[cl_idx]}**")
                            st.caption(", ".join(c_list))
                else:
                    st.caption("No countries match your sidebar selections.")

            st.write("---")

            # ==============================================================================
            # LAYOUT SECTION 2: INTERACTIVE PROFILE EXPLORER (The Core Insights)
            # ==============================================================================
            st.subheader("🔍 Archetype Strategic Balance Sheets")
            
            # Create 4 tabs for deep exploratory review of each structural profile
            tab_c2, tab_c0, tab_c1, tab_c3 = st.columns(4)
            
            with tab_c2:
                st.metric(label="🏆 Group Alpha", value="Digital Frontrunners")
                st.markdown("""
                    * **The Digital Footprint:** Exceptional baseline performance. Nearly half of the population (**47.4%**) holds advanced digital skills, eID adoption averages **89.7%**, and **83.5%** interact seamlessly with public authorities.
                    * **The Trust Anchor:** Institutional trust scores lead the EU block across all facets (Parliament trust sits at **0.55**, Public Authorities at **0.70**). 
                    * **Strategic Synthesis:** A flawless digital ecosystem backed by high systemic and institutional trust. 
                """)

            with tab_c0:
                st.metric(label="📊 Group Beta", value="Digitally Engaged Sceptics")
                st.markdown("""
                    * **The Digital Footprint:** Robust, highly functional technical capacity. Over **30%** maintain advanced skills, **78%** use eID systems actively, and **69.6%** deal with state platforms online.
                    * **The Trust Paradox:** Despite high digital interaction, national political trust is low (Government trust rests at **0.27**, Parliament at **0.25**).
                    * **Strategic Synthesis:** Infrastructure is mature and citizens use it out of necessity, but digital capability has not translated into state institutional trust.
                """)

            with tab_c1:
                st.metric(label="⚙️ Group Gamma", value="Emerging Transition")
                st.markdown("""
                    * **The Digital Footprint:** Moderate skill baseline (**28.5%** above basic), but infrastructure friction causes adoption rates to sag. Only **41.1%** utilize eIDs, and government interactions drop to **59.0%**.
                    * **The Technical Barrier:** Up to **22.9%** of citizens actively face systemic or technical eID structural barriers. 
                    * **Strategic Synthesis:** Citizens trust the system (Public Authority trust holds a solid **0.61**), but they are hitting clear technical infrastructure walls.
                """)

            with tab_c3:
                st.metric(label="⚠️ Group Delta", value="Digitally Excluded / Friction States")
                st.markdown("""
                    * **The Digital Footprint:** Severe digital divide crisis. Only **11.4%** reach above-basic literacy, entry-level exclusion scales up to **7.8%**, and eID usage craters to **11.1%**.
                    * **The Friction Metrics:** Over half (**51.8%**) lack functional eID systems entirely, pulling electronic tax submissions down to a mere **10.9%**.
                    * **Strategic Synthesis:** Systemic digital alienation. Technical infrastructure is absent, civic skills are low, and institutional trust is severely deflated.
                """)

            # ==============================================================================
            # LAYOUT SECTION 3: SYSTEM METHODOLOGY NOTES (Appended at base)
            # ==============================================================================
            st.write("---")
            with st.expander("🔬 Methodology Note: Unsupervised Machine Learning Pipeline Specifications"):
                st.markdown("""
                    **Model Implementation Blueprint:**
                    1. **Feature Engineering & Dimensional Selection:** The analysis isolates exactly 10 multi-domain dimensions per country, spanning Eurostat capabilities (skill levels, authentication barriers, transactional usage) and Eurobarometer sentiment markers (institutional trust tracks).
                    2. **Normalization Protocol:** Because percentage indicators and trust indexes operate on different scale boundaries, all parameters undergo **Standardization** ($Z$-score scaling) via standard scalar mapping:
                       $$Z = \\frac{x - \\mu}{\\sigma}$$
                       This guarantees that high-magnitude metrics don't bias cluster distance measurements.
                    3. **Hyperparameter Selection ($K$):** The partition configuration ($K=4$) was chosen via the **Elbow Method** (minimizing Within-Cluster Sum of Squares / Inertia) paired with Silhouette analysis maximization across testing ranges.
                    4. **Distance Optimization:** Optimization is performed iteratively using the standard **Euclidean Distance** vector cost formulation:
                       $$d(p, q) = \\sqrt{\\sum_{i=1}^{n} (q_i - p_i)^2}$$
                """)

# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025), [Eurobarometer Standard (104)](https://europa.eu/eurobarometer/surveys/detail/3378) and [Eurobarometer Special (sp566)](https://europa.eu/eurobarometer/surveys/detail/3362).
""")