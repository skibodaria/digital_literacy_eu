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

st.markdown("""
            <style>
            /* Define the structure for solid color custom Insight Card */
            .insight-card {
                background-color: #007792;          /* Solid dark teal background block */
                border: 1px solid #007792;          /* Matching border color to make it flat */
                border-radius: 12px;                /* Modern curved corners */
                padding: 22px;                      /* Breathing room inside the card */
                box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* Soft drop shadow layer for subtle lift */
                margin-bottom: 15px;
                min-height: 280px;                  /* Keeps cards uniformly sized in the row */
            }
            
            /* High-contrast typography inside solid dark cards */
            .insight-card h4 {
                color: #FFFFFF !important;          /* Crisp white title headers */
                font-weight: 700 !important;
                margin-top: 0px !important;
                font-size: 1.15rem !important;
            }
            
            .insight-card .card-caption {
                font-size: 0.85rem;
                color: #caf0f8;                     /* Light blue tint color for high-contrast context text */
                font-style: italic;
                margin-bottom: 14px;
                line-height: 1.4;
            }

            .insight-card p {
                color: #e0e0e0 !important; /* Soft light gray for better readability */
                font-size: 1.0rem !important;
                line-height: 1.5;
                margin-top: 10px !important;
            }
            
            .insight-card ul {
                padding-left: 18px !important;
                color: #FFFFFF !important;          /* White bullet list items */
            }
            
            .insight-card li {
                color: #FFFFFF !important;
                margin-bottom: 10px;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            </style>
        """, unsafe_allow_html=True)

# ==============================================================================
# DATA LOADING
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

DIMENSIONS = {
    "Gender": {"suffixes": ['_f_y16_74', '_m_y16_74'], "labels": ['Female', 'Male']},
    "Education Level": {"suffixes": ['_i0_2', '_i3_4', '_i5_8'], "labels": ['Low Edu', 'Med Edu', 'High Edu']},
    "Urbanization Level": {"suffixes": ['_ind_deg1', '_ind_deg2', '_ind_deg3'], "labels": ['Cities', 'Suburbs', 'Rural']},
    "Age Cohorts": {"suffixes": ['_y16_19', '_y20_24', '_y25_34', '_y35_44', '_y45_54', '_y55_64', '_y65_74'], "labels": ['16-19', '20-24', '25-34', '35-44', '45-54', '55-64', '65-74']}
}

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.title("🇪🇺 Digital Skills Analysis")
st.caption("""
    **Examining the Socio-Demographic Layers of European Digital Literacy**: This workspace breaks down the digital skill distributions 
    across stratified population segments in the EU. The main demographic dimensions used here
    are: gender, age, level of education, and urbanization level. Explore tha tabs to learn more about
    macro trends and inequality in relation to digital skills, or dive deeper in an individual countries'
    digital skills profiles.
""")


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
    
    st.header("Macro Trends & National Baselines")
    
    # --------------------------------------------------------------------------
    # 6 KPI METRIC COLUMNS (do not change with country selection!)
    # --------------------------------------------------------------------------
    cols = st.columns(6)

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

    metrics_data = [
        ("Above Basic", df_filtered_baseline['i_dsk2_ab'].mean()),
        ("Basic Skills", df_filtered_baseline['i_dsk2_b'].mean()),
        ("Low Skills", df_filtered_baseline['i_dsk2_lw'].mean()),
        ("Limited Skills", df_filtered_baseline['i_dsk2_lm'].mean()),
        ("Narrow Skills", df_filtered_baseline['i_dsk2_n'].mean()),
        ("No Skills", df_filtered_baseline['i_dsk2_x'].mean())
    ]
    
    for i, col in enumerate(cols):
        label, val = metrics_data[i]
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # --------------------------------------------------------------------------
    # TWO COLUMN LAYOUT: MAP (LEFT) & TEXT EXPLANATION (RIGHT)
    # --------------------------------------------------------------------------
    col_map, col_text = st.columns([4, 2])

    with col_map:
        
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

        st.markdown(f"### Geographic Distribution: {chosen_label}")
        chosen_indicator_code = map_radio_options[chosen_label]
        
        fig = px.choropleth(
            df_filtered_baseline,                           
            locations='plotly_country_code',   
            locationmode='ISO-3',               
            color=chosen_indicator_code,                    
            hover_name='clean_country_name',  
            color_continuous_scale=styles.EU_CORNFLOWER,
            height=700
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
            coloraxis_colorbar=dict(title="Percent")
        )
        
        st.plotly_chart(fig, use_container_width=True)        
        
    with col_text:
        st.markdown("### What's About Your Digital Skills?")
        st.link_button(
            label="🔗 Test Yourself and Learn More", 
            url="https://europa.eu/europass/digitalskills/screen/home",
            use_container_width=False,
            help="Official EU Digital Skills Assessment Tool"
        )


        with st.container():
            st.markdown("### Key Insights")
            st.warning("""
                **Persistent Polarization**: A significant gap remains between those with advanced digital literacy and those left in the 
                "digital tail," proving that basic access alone cannot solve these deep-seated disparities
                       """)

            st.info("""
                **Growth Mismatch**: Digital adoption is growing, but it is moving at a steady. To meet the EU’s 2030 targets the EU countries need
                to shift to targeting and direct upskilling policies""")

            st.warning("""
                **Quality over Connectivity**: Having the tools and the connection is no longer the bottleneck; 
                the true challenge is to overcome the growing distance between hardware access and actual digital competence.
                """)

        with st.expander("**What Is Being Measured?**"):
            st.markdown(
                """
                Eurostat measures citizens' digital proficiency via the Digital Skills Indicator (DSI), which is based 
                on [the European Commission's DigComp 2.0 framework](https://ec.europa.eu/eurostat/cache/metadata/en/isoc_sk_dskl_i21_esmsip2.htm#indicatorDisseminated). The methodology tracks a user's activities across five domains.

                **What Are Those Domains?**
                1. **Information & Data Literacy**:	Searching for information, reading news, health research, and online fact-checking.
                2. **Communication & Collaboration**: Emails, video calls, social media, messaging, and online civic voting/political expression.
                3. **Digital Content Creation**: Word processing, spreadsheets (basic & advanced), photo/video editing, file management, and programming.
                4. **Safety & Privacy**: Checking website security, reading privacy rules, disabling location services, and blocking cookies.
                5. **Problem Solving**: Installing apps, changing settings, online shopping/banking, selling items, or using online learning resources.
            """)
                
                
        with st.expander("**How the Overall Score is Calculated?**"):
            st.markdown(
                """
                The final composite score groups individuals based on how many of the five sub-areas they successfully master:

                - *Above Basic Skills*: Scored "Above Basic" in all 5 areas.
                - *Basic Skills*: Scored "At least Basic" in all 5 areas (but didn't hit maximum in all 5).
                - *Low Skills*: Scored "At least Basic" in 4 areas (0 skills in 1 area).
                - *Narrow Skills*: Scored "At least Basic" in 3 areas (0 skills in 2 areas).
                - *Limited Skills*: Scored "At least Basic" in 2 areas (0 skills in 3 areas).
                - *No Digital Skills*: Scored "0 skills" in 4 or all 5 areas (despite recent Internet use).
                - *Not Applicable / Assessed*: Individuals who have not used the Internet at all in the past 3 months.
                
                """)
    
    col_explain, col_time = st.columns([2,3])

    # ------------------------------------------------------------------------------
    # --- MODULE: 2030 DIGITAL DECADE FORECAST PANELS (HISTORICAL BRIDGE OVERHAUL) ---
    # ------------------------------------------------------------------------------
    with col_time:
        st.markdown('#### Historical Progression of "At Least Basic Digital Skills"')

        st.markdown("""
                _This predictive model uses an Ordinary Least Squares (OLS) linear regression to project historical Eurostat growth rates 
                into the next decade, accounting for the structural framework adjustments in 2021_
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
            from scipy import stats
            import numpy as np
            
            # Compute core linear regression attributes across the historic baseline
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_eu_avg['reporting_year'], df_eu_avg['indicator_value']
            )
            
            # append 2030 to the timeline array to plot the extended trendline
            full_years = np.append(df_eu_avg['reporting_year'].values, [2030])
            
            df_proj = pd.DataFrame({
                'reporting_year': full_years,
                'regression_value': slope * full_years + intercept
            })

            # Base line chart modeling the empirical historical data
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

            # Style the historical trajectory
            fig_line.update_traces(
                line=dict(color='#41748d', width=4),
                marker=dict(size=9, color='#005f73'),
                textposition='top center',
                name='Historical Reality'
            )

            # Extract the precise 2030 OLS forecast value
            val_2030 = df_proj[df_proj['reporting_year'] == 2030]['regression_value'].values[0]

            # Overlay the formal linear projection path out to 2030
            fig_line.add_scatter(
                x=df_proj['reporting_year'],
                y=df_proj['regression_value'],
                mode='lines+markers',
                line=dict(color='crimson', width=2, dash='dash'),
                marker=dict(
                    size=[10 if y == 2030 else 0 for y in df_proj['reporting_year']],
                    color='crimson'
                ),
                name='OLS Linear Trendline'
            )

            # Context Annotation: Precise 2030 Forecast Node
            fig_line.add_annotation(
                x=2030,
                y=val_2030,
                text=f"2030 Forecast: {val_2030:.1f}%",
                showarrow=True,
                arrowhead=1,
                ax=-75, 
                ay=35,  
                font=dict(color="crimson", size=11, family="sans-serif"),
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="crimson",
                borderwidth=1
            )
            
            # Context Annotation: Official Policy Targets
            fig_line.add_annotation(
                x=2017, y=82,
                text="Official EU 2030 Goal: 80%",
                showarrow=False,
                font=dict(color="#2a9d8f", size=11, family="sans-serif")
            )

            # Context Structural Element: 2021 Eurostat Methodology Shift
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

            # Layout canvas presentation configuration
            fig_line.update_layout(
                height=500,
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

    # ensure data is sorted
    df_eu_avg = df_eu_avg.sort_values('reporting_year')

    # get the baseline values
    year_min = int(df_eu_avg['reporting_year'].min())
    year_max = int(df_eu_avg['reporting_year'].max())
    val_min = df_eu_avg[df_eu_avg['reporting_year'] == year_min]['indicator_value'].values[0]
    val_max = df_eu_avg[df_eu_avg['reporting_year'] == year_max]['indicator_value'].values[0]

    # 3. Perform the OLS Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_eu_avg['reporting_year'], df_eu_avg['indicator_value']
    )

    # calculate the forecasted numbers:
    annual_growth = slope
    projected_2030 = (slope * 2030) + intercept
    structural_deficit = 80.0 - projected_2030
    
with col_explain:
    st.subheader("Is the EU Going to Meet the 2030 Goal?")

    with st.expander("Methodology & Limitations Comments"):
        st.markdown("""
            To build a 10-year outlook, I combined older Eurostat data (2015–2019) with updated metrics (2021–2025). 
            I used **Linear Regression (OLS)** to determine the average annual growth rate. This mathematical approach 
            focuses on the long-term historical trend rather than specific yearly ups or downs
        """)
    
    st.info(
        "**Important Note**: This is a mathematical projection, not a formal prediction. A true forecast would "
        "also need to account for future government investment, digital policy changes, and specific "
        "national training initiatives"
    )

    st.markdown(f"""
        **Key Findings**
        * **Historical Growth:** Between 2015 and 2025, the percentage of the EU population with at least basic digital skills grew from **{val_min:.1f}%** to **{val_max:.1f}%**.
        * **Annual Pace:** The historical trend indicates a steady improvement of **{annual_growth:.2f}%** per year.
        * **2030 Outlook:** If this pace continues, the EU will reach an estimated **{projected_2030:.1f}%** digital literacy by 2030.
    """)
    st.warning(f"**The Gap:** To hit the official **80% target**, we face a structural deficit of **{structural_deficit:.1f}%**.")

    
# ==============================================================================
# --- TAB 2: DEMOGRAPHIC DIMENSIONS (BOXPLOT STUDIO) ---
# ==============================================================================

with tab_demog:
    st.header("Digital Skills and Social Groups | Possible Exclusion Patterns")

    cards = [
            ("The Age Gap Persists", "People aged 65 and over remain the most vulnerable group, facing the highest barriers to digital inclusion"),
            ("The Power of Education", "Education is a primary driver of digital literacy"),
            ("The Gender Perspective", "The gap exists in advanced usage, basic entry-level knowledge is balanced"),
            ("Urban vs. Rural Divide", "Geography creates a significant barrier: rural communities often lack the same level of digital support as in cities"),
            ("To Research:", "The most important insights emerge where age, education, and location overlap")
        ]

    cols = st.columns(5)

    for i, (title, content) in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
                <div class="insight-card">
                    <h4>{title}</h4>
                    <p>{content}</p>
                </div>
            """, unsafe_allow_html=True)

    # ensure skills_map is available + ensure extract_demographic_metrics is returning keys that exist in  df
    skills_map = funcs.extract_demographic_metrics(df_skills)
    
    # ensure this matches specific skill metric naming convention
    # if 'education' isn't the right key for skills, check other funcs.extract output
    skills_base_metrics = [m for m in skills_map.get("education", {}).get("base_metrics", [])]

    st.write('---')
    st.header("Dynamic Boxplot Lab")
    
    if skills_base_metrics:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            def format_tab2_boxplot(x):
                full_key = next((k for k in skills_labels.keys() if x in k), None)
    
                if full_key:
                    raw_label = skills_labels[full_key]
                    # extract only the part before the first '('
                    # "Digital Skills: Above Basic (% of individuals) - ..." -> "Digital Skills: Above Basic "
                    clean_label = raw_label.split('(')[0].strip()
                    return clean_label
                
                return x.upper()

            selected_metric_b = st.selectbox(
                "Select Metric for Distribution Analysis", 
                options=skills_base_metrics, 
                format_func=format_tab2_boxplot,
                key="t2_boxplot_metric_dropdown"
            )
        with b_col2:
            dim_options = list(DIMENSIONS.keys())
            selected_dim_b = st.selectbox(
                "Select Demographic Dimension Breakout", 
                options=dim_options, 
                key="barr_dim",
                index=dim_options.index("Age Cohorts") # opens the Age Cohorts box plot automatically!
                )

        dim_cfg_b = DIMENSIONS[selected_dim_b]
        
        # build target columns based on selected_metric_b + suffixes
        target_cols_b = [f"{selected_metric_b}{sfx}" for sfx in dim_cfg_b["suffixes"]]
        
        # find columns that exist in df_skills (case-insensitive)
        df_cols_lower = [c.lower() for c in df_skills.columns]
        real_cols_b = [c for c in df_skills.columns if c.lower() in [tc.lower() for tc in target_cols_b]]
        
        # verify that all columns are there:
        if len(real_cols_b) == len(target_cols_b):
            # 4. Melt
            df_melted_b = df_skills.melt(
                id_vars=[country_col], 
                value_vars=real_cols_b, 
                var_name="Demographic Slice", 
                value_name="Percentage"
            )
            
            # map column names to clean labels from DIMENSIONS
            # ensure the order of real_cols_b corresponds to dim_cfg_b["labels"]
            suffix_to_label_b = dict(zip([rc.lower() for rc in real_cols_b], dim_cfg_b["labels"]))
            df_melted_b["Demographic Slice"] = df_melted_b["Demographic Slice"].str.lower().map(suffix_to_label_b)
            
            #clean_plot_title_b = skills_labels.get(selected_metric_b.lower(), selected_metric_b.upper()) 

            fig_box_b = px.box(
                df_melted_b, 
                x="Demographic Slice", 
                y="Percentage", 
                color="Demographic Slice",
                points="all", 
                hover_data=[country_col],
                title=""
            )
            fig_box_b.update_layout(height=400, showlegend=False, margin={"t":40, "b":40})
            st.plotly_chart(fig_box_b, use_container_width=True)
        else:
            st.caption(f"Missing data: Found {len(real_cols_b)}/{len(target_cols_b)} expected columns for this metric.")

    funcs.read_boxplot()       

    # ========================================================
    # STATISTICAL TESTS
    # ========================================================

    st.subheader("Global EU Significance Tests (Fixed Sample Baselines)")
    
    # ---------- GENDER ----------
    with st.expander("Gender Gaps Significance (Wilcoxon Signed-Rank)", expanded=False):
        col_tbl, col_ins = st.columns([3, 2])

        with col_tbl:
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

    # ----------- AGE ----------
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

    # ---------- EDUCATION ----------
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

    # ----------- URBANIZATION ----------
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
# --- TAB 3: SKILL METRIC DEEP DIVE ---
# ==============================================================================
with tab_deep_dive:
    st.header("Digital Skills Deep Dive | Cross-Dimensional Fingerprint")
    st.caption("""
        This section breaks down digital skills into the five core areas defined by the European Commission. 
        Instead of just showing one general score, this tool lets you compare how different groups of people perform in each area 
        to see exactly where the biggest gaps are.
    """)

    # --------------------------------------------------------------------------
    # DATABASE DATA EXTRACTION & CONFIGURATION
    # --------------------------------------------------------------------------
    try:
        # load the newly created dbt mart table and its metadata indicators
        df_deep, deep_labels = funcs.load_tab_data("stg_skills_deep_dive", "mart_indicators")
    except Exception as e:
        st.error(f"Failed to extract deep dive dimension data: {e}")
        df_deep = pd.DataFrame()

    if df_deep.empty:
        st.warning("Deep Dive data asset pipeline empty. Verify your 'stg_skills_deep_dive' table status.")
    else:
        # filter deep dive frame down to the user's active sidebar geographic choices
        df_filtered_deep = df_deep[df_deep['clean_country_name'].isin(selected_countries)]

        # human-readable mapping dictionary for the 5 Core Framework Dimension prefixes
        DIMENSION_MAP = {
            'i_dsk2_il_bab': 'Information & Data Literacy',
            'i_dsk2_cc_bab': 'Communication & Collaboration',
            'i_dsk2_dcc_bab': 'Digital Content Creation',
            'i_dsk2_sf_bab': 'Safety & Privacy Competence',
            'i_dsk2_ps_bab': 'Technical Problem Solving'
        }

        # ==============================================================================
        # COMPONENT 1: COUNTRY GEOGRAPHIC SIGNATURE FINGERPRINT (Radar Map Matrix)
        # ==============================================================================

        # one country to take a closer look -- I want Romania to be a default:
        countries = sorted(df_filtered_deep['clean_country_name'].unique())
        default_index = countries.index("Romania") if "Romania" in countries else 0

        fingerprint_country = st.selectbox(
            "Select Target Country for Fingerprint Analysis:",
            options=countries,
            index=default_index
        )

        df_country_fingerprint = df_filtered_deep[df_filtered_deep['clean_country_name'] == fingerprint_country]
        df_eu_fingerprint = df_deep.copy() # need a full copy to get EU metrics

        fingerprint_rows = []
        for prefix, label in DIMENSION_MAP.items():
            # get the national data for men and women (two groups together -> the whole adult population)
            f_col = f"{prefix}_f_y16_74"
            m_col = f"{prefix}_m_y16_74"
            
            if f_col in df_country_fingerprint.columns and m_col in df_country_fingerprint.columns:
                # national average for total baseline
                country_avg = (df_country_fingerprint[f_col].mean() + df_country_fingerprint[m_col].mean()) / 2
                eu_avg = (df_eu_fingerprint[f_col].mean() + df_eu_fingerprint[m_col].mean()) / 2
                
                fingerprint_rows.append({
                    "Dimension": label,
                    f"{fingerprint_country} (%)": round(country_avg, 1) if not pd.isna(country_avg) else 0,
                    "EU Average (%)": round(eu_avg, 1) if not pd.isna(eu_avg) else 0
                })

        if fingerprint_rows:
            df_radar = pd.DataFrame(fingerprint_rows)
            
            fig_radar = go.Figure()
            
            # line 1: target country
            fig_radar.add_trace(go.Scatterpolar(
                r=df_radar[f"{fingerprint_country} (%)"],
                theta=df_radar['Dimension'],
                fill='toself',
                name=fingerprint_country,
                line_color='#001f63',
                fillcolor='rgba(0, 31, 99, 0.2)'
            ))
            
            # line 2: EU average
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
                st.markdown(f"### {fingerprint_country} Digital Skills Balance Sheet")
                with st.expander("**How to read this chart:**", expanded=True):
                    st.markdown("""
                        * A perfectly symmetrical web indicate well-rounded national educational and "digital-skills-promotional" strategies
                        * Sharp peaks point out targeted national specializations and "wow" moments
                        * Inward sharp "gaps" signal strategic bottlenecks and problems
                    """)
                
                # dynamic key insights:
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
        st.caption("This matrix is _not_ sensitive to the country selection tool: it represents the digital skills components" \
        "vs demographic dimensions for **all** countries in the dataset")

        col_matrix, col_matrics_comments = st.columns([3,1])
        with col_matrix: 
        
            deep_demo_choice = st.selectbox(
                "Select Demographic Stratification Layer:",
                options=["Age Cohorts", "Education Levels", "Urbanization Levels"],
                key="deep_demo_selectbox"
            )

            if deep_demo_choice == "Age Cohorts":
                slice_mapping = {'y16_19': '16-19', 'y20_24': '20-24', 'y25_34': '25-34', 'y35_44': '35-44', 'y45_54': '45-54', 'y55_64': '55-64', 'y65_74': '65-74'}
            elif deep_demo_choice == "Education Levels":
                slice_mapping = {'i0_2': 'Low Edu', 'i3_4': 'Medium Edu', 'i5_8': 'High Edu'}
            else:
                slice_mapping = {'ind_deg1': 'Cities', 'ind_deg2': 'Suburbs', 'ind_deg3': 'Rural'}

            heatmap_data = []

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
                
                df_heat_pivot = df_heat.pivot(
                    index="Core Dimension", 
                    columns="Socio-Demographic Group", 
                    values="Mean Proficiency (%)"
                )
                
                df_heat_pivot = df_heat_pivot[list(slice_mapping.values())]

                fig_heat = px.imshow(
                    df_heat_pivot,
                    labels=dict(x="Demographic Group Segment", y="Competence Dimension", color="Avg %"),
                    x=df_heat_pivot.columns,
                    y=df_heat_pivot.index,
                    color_continuous_scale=styles.EU_CORNFLOWER,
                    text_auto='.1f',
                    height=600
                )

                fig_heat.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    margin=dict(t=10, b=20, l=10, r=10),
                    font=dict(size=14),
                    coloraxis_colorbar=dict(
                        tickfont=dict(size=12),
                        title_font=dict(size=14)
                    ),
                    yaxis=dict(
                        tickfont=dict(size=18)
                    ),
                    
                    # force X-axis (age cohorts) labels to be larger
                    xaxis=dict(
                        tickfont=dict(size=18)
                    )
                )

                st.plotly_chart(fig_heat, use_container_width=True)

            else:
                st.warning("Matching metric matrix blocks could not be constructed for this segment setup.")
        
        with col_matrics_comments:
            st.markdown("##### Key Insights:")
            
            max_val = df_heat["Mean Proficiency (%)"].max()
            min_val = df_heat["Mean Proficiency (%)"].min()
            top_seg = df_heat.loc[df_heat["Mean Proficiency (%)"].idxmax()]
            bot_seg = df_heat.loc[df_heat["Mean Proficiency (%)"].idxmin()]
            
            st.markdown(f"""
                * **Peak Adoption Concentration:** Maximum digital proficiency is reached inside the **{top_seg['Socio-Demographic Group']}** subgroup evaluating **{top_seg['Core Dimension']}** at **{max_val}%**.
                * **Core Exclusion Point:** Structural friction is concentrated mainly in the **{bot_seg['Socio-Demographic Group']}** cohort assessing **{bot_seg['Core Dimension']}**, dropping to **{min_val}%**.
            """)
            st.info(f"**Horizontal Line Check:** Scan the heatmap horizontally. The colors transition rapidly from dark to light, it shows that **{deep_demo_choice}** has the most powerful influence on digital skill levels, regardless of the specific type of skill being measured.")



# ==============================================================================
# FOOTER SECTION
# ==============================================================================
funcs.add_authorship_footer()