import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import funcs
import styles

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(layout="wide")
# ==========================================
# DATA LOADING
# ==========================================
try:
    # get the data + metadata
    df_baseline, baseline_labels = funcs.load_tab_data("mart_eu_baseline", "mart_indicators")
except Exception as e:
    st.error(f"Database connection or query failed: {e}")
    st.stop()

# --- HEADER & PRESENTATION CONTEXT ---
st.title("🇪🇺 Overview: Digital Skills, Internet Usage, & E-Governance")
st.markdown("""
    **Graduation Capstone Project** | An analysis of 27 EU Member States utilizing Eurostat & Eurobarometer data.\n
    This application investigates how structural digital baselines condition human trust and behavioral outcomes across Europe.
""")

# --- SIDEBAR GLOBAL FILTERS ---
st.sidebar.header("Geo Filter")
available_countries = sorted(df_baseline['clean_country_name'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries to Filter",
    options=available_countries,
    default=available_countries
)

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
    st.header("Intro to EU Digital Mapping | Main Metrics")

    display_name_to_code = {v: k for k, v in baseline_labels.items()}
    available_columns = df_filtered.columns.tolist()
    filtered_display_options = {
        proper_name: code 
        for proper_name, code in display_name_to_code.items() 
        if code in available_columns
    }

    filtered_display_options = dict(sorted(filtered_display_options.items()))
    
    # KPI Row
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
    
    st.markdown("---")

    col_map, col_key_insights = st.columns([2,1])


    # ---------------------------------
    # MAP
    # ---------------------------------

    with col_map:

        # select indicator for map:
        selected_title = st.selectbox(
            "Select Indicator:",
            options=list(filtered_display_options.keys())
        )
        chosen_indicator_code = filtered_display_options[selected_title]
            
        st.markdown(f"### {selected_title}") 
        
        # render the map:
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
        # fix Malta!
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

        # margins and borders
        fig.update_layout(
            title="",
            annotations=[],
            margin={"r":0, "t":0, "l":0, "b":0},
            paper_bgcolor="rgba(0,0,0,0)", # transparent map box
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)
    
    # --------------------
    # KEY INSIGHTS
    # --------------------
    with col_key_insights:
        st.subheader("Key Insights")
        with st.expander("**The Skills Ceiling Paradox**"):
            st.markdown(
                """
                While total digital exclusion is nearly extinct in the EU - with the "No Digital Skills" ceiling bottoming out at 
                a maximum of just **8.9%** - Europe faces a severe structural stagnation. The baseline average for at least basic digital skills 
                hovers at roughly 61% (combining basic and above-basic levels), leaving a massive 20-percentage-point deficit below 
                the official 2030 Digital Decade target of 80%. 
                The empirical reality is that the problem is no longer digital connection and access to the Internet, but a skills quality.
            """)
        with st.expander("**Access vs. Execution**"):
            st.markdown(
                """
                Universal connectivity is a solved problem across Europe, evidenced by a daily internet usage average of **90%** that pushes 
                up to **99.3%** in leading states. Because basic access is flat, stable, and universal, it cannot be a meaningful indicator 
                of socio-economic development. Instead, the true digital divide has shifted to frontier technology adoption: 
                AI usage sits at a **36.7%** average but shows a high variance between a minimum of **17.5%** and a maximum of **48.8%**,
                serving as the active indicator for regional digital development.
            """)
        with st.expander("**Institutional Fragmentation**"):
            st.markdown(
                """
                E-governance adoption in the EU is fundamentally bottlenecked by state-level administrative routines, not civic resistance. 
                While **64.5%** of citizens interact with public authorities online, deep systemic friction appears in many services: 
                online tax declaration averages **40%** but collapses to a near-zero floor of **0.36%** in some countries. This probably not a digital
                limitation but an institutional problem: access to online services needs to be provided and invested into. 
                Up to **56%** of citizens in certain member states completely lack access to a digital identity. 
                The data highlights that structural institutional barriers - and not cultural preferences — are actively forcing citizens 
                back onto analog ways.
            """)
        
    with st.expander("**Descriptive Statistics in Detail**"):
        if not df_filtered.empty:
    
            target_metrics = {
                'i_dsk2_bab': 'Basic and Above Basic Digital Skills',
                'i_dsk2_ab': 'Above Basic Digital Skills',
                'i_dsk2_x': 'No Digital Skills',
                'i_iday': 'Daily Internet Usage',
                'i_iuai': 'Generative AI Tools Usage',
                'i_igov': 'Online Authority Interaction',
                'i_igovapr': 'Online Appointments',
                'i_igovbe': 'Requesting Benefits Online',
                'i_igovtax2': 'Tax Declaration Online',
                'i_ireidno': 'Not Having eID'
            }

            available_columns = [col for col in target_metrics.keys() if col in df_filtered.columns]
    
            if available_columns:
                df_stats = df_filtered[available_columns].describe().loc[['mean', 'max', 'min', 'std']]
                df_stats = df_stats.T
                df_stats.index = df_stats.index.map(target_metrics)
                df_stats = df_stats.rename(columns={
                    'mean': 'EU Average (Mean)',
                    'max': 'Maximum State Score',
                    'min': 'Minimum State Score',
                    'std': 'Standard Deviation (σ)'
                })
                formatted_stats = df_stats.style.format("{:.1f}%")

                st.dataframe(
                    formatted_stats, 
                    use_container_width=True,
                    height=350
                )
                
                # Brief methodological context note
                st.caption(
                    "Note: Standard Deviation (σ) quantifies regional policy fragmentation. "
                    "Higher deviation scores indicate severe state-level "
                    "structural disparities across the Union."
                )
            else:
                st.warning("Specified metric columns were not discovered in the current data model layer.")
        else:
            st.warning("Unable to compute descriptive summary statistics due to an empty source dataframe.")



# ==============================================================================
# --- TAB 2: MACRO ARCHETYPES CLUSTERING ---
# ==============================================================================
with tab_clusters:
    st.header("European Archetypes: Data-Driven Country Profiles")
    st.info("""
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
            col_map, col_table = st.columns([3, 1], gap="small")

            with col_map:
                st.subheader("Geographic Archetype Footprint")
            

                fig_cluster_map = px.choropleth(
                    df_filtered_cluster,
                    locations='plotly_country_code',
                    locationmode='ISO-3',
                    color='cluster_profile',
                    hover_name='clean_country_name',
                    hover_data={'plotly_country_code': False, 'cluster_profile': True},
                    color_discrete_sequence=styles.EU_CLUSTERS,
                    height=700
                )

                fig_cluster_map.update_geos(              
                    projection_type="mercator", center=dict(lon=10, lat=52), projection_scale=4.5,         
                    visible=False, showframe=False, showcoastlines=True, coastlinecolor="LightGray", resolution=50,
                    bgcolor="rgba(0,0,0,0)",
                    
                    #fitbounds="locations"
                )

                fig_cluster_map.update_layout(
                    margin={"r":0, "t":0, "l":0, "b":0},
                    height=700,
                    legend=dict(
                        title=None, orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
                    ),
                    paper_bgcolor="rgba(0,0,0,0)", # transparent map box
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_cluster_map, use_container_width=True)


            with col_table:
                st.subheader("Member State Clusters")

                cluster_colors = {
                    0: "#005f73",  # Deep Teal
                    1: "#2a9d8f",  # Muted Sage
                    2: "#e9c46a",  # Soft Mustard
                    3: "#e76f51"   # Terracotta Orange
                }

                cluster_profiles = {
                    0: """
                    * **The Digital Footprint:** Robust, highly functional technical capacity. Over **30%** maintain advanced skills, **78%** use eID systems actively, and **69.6%** deal with state platforms online.
                    * **The Trust Paradox:** Despite high digital interaction, national political trust is low (Government trust rests at **27%**, Parliament at **25%**).
                    * **Strategic Synthesis:** Infrastructure is mature and citizens use it out of necessity, but digital capability has not translated into state institutional trust.
                    """,
                    1: """
                    * **The Digital Footprint:** Moderate skill baseline (**28.5%** above basic), but infrastructure friction causes adoption rates to sag. Only **41%** utilize eIDs, and government interactions drop to **59%**.
                    * **The Technical Barrier:** Up to **23%** of citizens actively face systemic or technical eID structural barriers.
                    * **Strategic Synthesis:** Citizens trust the system (Public Authority trust holds a solid **61.5%**), but they are hitting clear technical infrastructure walls.
                    """,
                    2: """
                    * **The Digital Footprint:** Exceptional baseline performance. Nearly half of the population (**47.4%**) holds advanced digital skills, eID adoption averages **89.7%**, and **83.5%** interact seamlessly with public authorities.
                    * **The Trust Anchor:** Institutional trust scores lead the EU block across all facets (Parliament trust sits at **55%**, Public Authorities at **70%**).
                    * **Strategic Synthesis:** A flawless digital ecosystem backed by high systemic and institutional trust.
                    """,
                    3: """
                    * **The Digital Footprint:** Severe digital divide crisis. Only **11.5%** reach above-basic literacy, entry-level exclusion scales up to almost **8%**, and eID usage craters to **11%**.
                    * **The Friction Metrics: ** Over half (**51.8%**) lack functional eID systems entirely, pulling electronic tax submissions down to a mere **11%**.
                    * **Strategic Synthesis:** Systemic digital alienation. Technical infrastructure is absent, civic skills are low, and institutional trust is relatively low.
                    """
                }
                
                if not df_filtered_cluster.empty:
                    # Explicit list of all 4 clusters to ensure every single card renders
                    for cl_idx in [0, 1, 2, 3]:
                        c_list = df_filtered_cluster[df_filtered_cluster['cluster_label'] == cl_idx]['clean_country_name'].tolist()
                        countries_str = ", ".join(c_list) if c_list else "No active countries"
                        
                        bg_color = cluster_colors.get(cl_idx, "#005f73")
                        text_color = "#FFFFFF" if bg_color == "#005f73" else "#000000"
                        
                        # Render the beautiful, standalone colorful country card using standard markdown
                        card_html = f"""
                        <div style="background-color: {bg_color}; border-radius: 12px; padding: 16px; margin-top: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <b style="font-size: 0.95rem; color: {text_color}; text-transform: uppercase; letter-spacing: 0.3px; display: block; margin-bottom: 8px;">🎯 {cluster_names[cl_idx]}</b>
                            <span style="font-size: 0.85rem; font-weight: 500; color: {text_color}; line-height: 1.4;">{countries_str}</span>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Use a clean, native Streamlit expander directly underneath each card
                        with st.expander("View Profile Characteristics"):
                            st.markdown(cluster_profiles[cl_idx])
                                
                else:
                    st.caption("No countries match your sidebar selections.")


            # ==============================================================================
            # LAYOUT SECTION 3: CLUSTER PROFILES (MATHEMATICAL VERIFICATION)
            # ==============================================================================
            st.write("---")
            with st.expander("View Cluster Empirical Profiles (Feature Averages Matrix)"):
                st.markdown("""
                    This verification matrix displays the raw mean percentages for each feature across the four clusters. 
                    The color gradient highlights where the highest concentration (`Deep Blue`) or structural deficits (`Light Blue`) sit for each archetype.
                """)

                # cluster avges:
                cluster_profiles = df_model_clean.groupby('cluster_label')[cluster_features].mean()

                # metrics and map
                cluster_profiles.index = [f"Cluster {i}: {cluster_names[i]}" for i in cluster_profiles.index]

                # clear headers for the table:
                RENAME_MAP = {
                    'i_dsk2_ab': 'Above Basic Skills %',
                    'i_ieid': 'eID Usage %',
                    'i_igovtax2': 'Tax Online %',
                    'i_igovapr': 'Appointments Online %',
                    'i_iugov1': 'Interaction with State %',
                    'i_dsk2_x': 'No Digital Skills %',
                    'i_ireidno': 'Barrier: No eID %',
                    'tr_nat_gov': 'Trust: Nat Gov',
                    'tr_nat_par': 'Trust: Nat Parl',
                    'tr_authority': 'Trust: Public Auth'
                }
                cluster_profiles = cluster_profiles.rename(columns=RENAME_MAP)

                # colored table:
                st.dataframe(
                    cluster_profiles.style.background_gradient(cmap='YlGnBu', axis=0).format("{:.2f}%"),
                    use_container_width=True,
                    height=220
                )


            # ==============================================================================
            # LAYOUT SECTION 4: SYSTEM METHODOLOGY NOTES (Appended at base)
            # ==============================================================================
            with st.expander("Methodology Note: Unsupervised Machine Learning Pipeline Specifications"):
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

st.warning(
    """
    **Strange indicators behavior**: Two indicators`i_imt12` (Individuals who used Internet more than a year ago or never) and `i_iux` (Individuals who 
    have never used Internet)) behave weirdly for Denmark. For this table, they are taken from the year 2024 instead of 2025. In original tables both
    marked as `:` for 2025, meaning "not available or missing". The main reason for it is that in Denmark in 2025 **99.7\\%** of population
    used Internet.
    """)
# ==============================================================================
# FOOTER SECTION
# ==============================================================================
funcs.add_authorship_footer()