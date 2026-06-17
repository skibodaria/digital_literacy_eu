import streamlit as st
import base64
import funcs

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        /* Target the exact inner layout div inside the container block */
        div[data-testid="stVerticalBlockBorder"] > div:first-child {
            background-color: #005f73 !important;  /* Pure white background card */
            border: 1px solid #005f73 !important;  /* Your primary teal accent color */
            border-radius: 12px !important;        /* Crisply rounded corners */
            padding: 24px !important;               /* Inner breathing room layout */
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important; /* Lifts it above the blue canvas */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🇪🇺 Digital Literacy, E-Governance Usage, Institutional Trust Inequality: Mapping the EU Digital Decade")
st.markdown(
    """
    Welcome to the EU Digital Baseline Workspace. This interface establishes a 
    macro-level diagnostic of digital literacy, Internet usage, and E-Governance and eID adoptions across the European Union. It helps to
    explore and understand the basic trends related to digital literacy in the EU member states and connect usage of E-Governance tools to
    institutionall trust, barriers, and inequality.
    """)

tab_short, tab_overview, tab_data, tab_methods = st.tabs([
    "Intro",
    "Project: Details",
    "Data & Sources",
    "Methods & Pipeline"
])
# ==========================================
# TAB 0: SHORT INTRO
# ==========================================
with tab_short:

    st.markdown("""
            <style>
            /* Define the structure for your solid color custom Insight Card */
            .insight-card {
                background-color: #007792;          /* Solid dark teal background block */
                border: 1px solid #007792;          /* Matching border color to make it flat */
                border-radius: 12px;                /* Modern curved corners */
                padding: 22px;                      /* Breathing room inside the card */
                box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* Soft drop shadow layer for subtle lift */
                margin-bottom: 15px;
                min-height: 390px;                  /* Keeps cards uniformly sized in the row */
            }
            
            /* High-contrast typography inside your solid dark cards */
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
            
            .insight-card ul {
                padding-left: 18px !important;
                color: #FFFFFF !important;          /* White bullet list items */
            }
            
            .insight-card li {
                margin-bottom: 10px;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            </style>
        """, unsafe_allow_html=True)
    
    st.header("Project Intro")
    st.caption("This pages helps to understand the core concepts of the project, its goals and hypotheses, data sources, pipeline. For more information," \
    "please explore additional tabs.")

    st.subheader("What I Wanted to Know: Research Questions")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        st.markdown("""
            <div class="insight-card">
                <h4>What are the levels of digital skills in the EU countries?</h4>
                <div class="card-caption">
                    Digital skills are measured in the EU on the following scale: above basic, basic, low, narrow, and limited. 
                    The methodology to estimate digital skills recently changed (2021)
                </div>
                <ul>
                    <li>What is the average level of digital skills?</li>
                    <li>What is the prospect for 2030?</li>
                    <li>Is EU going to reach the target of 80%?</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col_q2:
        st.markdown("""
            <div class="insight-card">
                <h4>What is the structure of digital skills literacy?</h4>
                <div class="card-caption">
                    To estimate digital skills, the EU survey uses several components: Information and Data Literacy, Communication and Collaboration,
                    Digital Content Creation, Safety and Security, and Problem Solving
                </div>
                <ul>
                    <li>Which skills are "stronger" and which are "weaker"?</li>
                    <li>What are the countries digital skills profiles?</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
            
    with col_q3:
        st.markdown("""
            <div class="insight-card">
                <h4>Do digital literacy and E-Governance vary across demographic groups?</h4>
                <div class="card-caption">Analyzing variance components across population segments</div>
                <ul>
                    <li>How gender, age, education, and urbanization levels correlate with digital skills?</li>
                    <li>Is there difference between those groups? Is it statistically significant?</li>
                    <li>How the groups differ in terms of E-Governance tools usage?</li>
                    <li>Are there any excluded groups?</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col_q4:
        st.markdown("""
            <div class="insight-card">
                <h4>Does active E-Governance usage foster higher trust in political institutions?</h4>
                <div class="card-caption">Empirical correlations between digital statecraft and institutional confidence layers</div>
                <ul>
                    <li>Is there correlation between E-Governance and eID usage and different metrics for institutional trust?</li>
                    <li>Is this correlation statistically significant?</li>
                    <li>What does it mean?</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)


    st.subheader("How Did I Do It: Project Pipeline")
    col1, arr1, col2, arr2, col3, arr3, col4, arr4, col5 = st.columns([3, 1, 3, 1, 3, 1, 3, 1, 3])
    st.markdown("""
        <style>
            .pipeline-arrow {
                font-size: 2rem;
                color: #005f73;          /* Matches your deep brand accent teal */
                font-weight: bold;
                text-align: center;
                line-height: 120px;       /* Vertically aligns arrow with the center of your cards */
                opacity: 0.7;
            }
        </style>
    """, unsafe_allow_html=True)

    with col1:
        st.markdown("**Data Retrieval**")
        st.image("assets/python.svg", width=40, use_container_width=False) 
        st.caption("Automated API bulk extraction & raw survey data ETL. Eurobarometer data clean-up and transformation")
    
    with arr1:
        st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)
    
    with col2: 
        st.markdown("**Modeling & Transformation**")
        st.image("assets/dbt.svg", width=40)
        st.caption("Prep, staging, and mart transformation. Merging complex data to clean DataFrames")

    with arr2:
        st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("**Storage Engine**")
        st.image("assets/postgresql.svg", width=40)
        st.caption("Locally hosted PostgreSQL database for source data and mart tables")
    
    with arr3:
        st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

    with col4:
        st.markdown("**EDA & Statistical Analysis**")
        m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
        with m1: st.image("assets/numpy.svg", width=40, use_container_width=False)
        with m2: st.image("assets/pandas.svg", width=40, use_container_width=False)
        with m3: st.image("assets/matplotlib.svg", width=40, use_container_width=False)
        with m4: st.image("assets/seaborn.svg", width=40, use_container_width=False)
        st.caption("Data exploration, first visualization, and data quality check. Correlations, regression, hypotheses testing")
    
    with arr4:
        st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

    with col5:
        st.markdown("**Presentation & App**")
        m5, m6 = st.columns([1, 1])
        with m5: st.image("assets/streamlit.svg", width=40, use_container_width=False)
        with m6: st.image("assets/plotly.svg", width=40, use_container_width=False)
        st.caption("Multi-panel application & dynamic SQL fetching.")

    st.subheader("Which Data Did I Use")
    col_stat, col_bar = st.columns(2)
    with col_stat:
        st.markdown("#### Eurostat Data")
        st.markdown(
            """
            **Eurostat** provides standardized, high-quality macro-statistics across Europe, 
            collected by national statistical agencies and harmonized at the EU level to ensure cross-country comparability.
            * **Base Tables:** 7 core Eurostat datasets integrated via API
            * **Key Tracking Vectors:** 15+ localized digital literacy, eID adoption, and internet usage indicators
            * **Geographic Scope:** 27 EU Member States
            * **Temporal Horizon:** baseline for **2025**
                * Digital Skills across Europe: 2015, 2016, 2017, 2019, 2021, 2023, 2025
            """
        )

    with col_bar:
        st.markdown("#### Eurobarometer Public Opinion Surveys")
        st.markdown(
            """
            The **Eurobarometer** is a unique cross-national public opinion survey conducted on behalf of the European Commission since the 1970s. 
            For this project I merged data from two Eurobarometer branches:
            """)
        st.markdown("##### 1. Standard Eurobarometer STD104, Autumn 2025")
        st.markdown(
            """
            * regular tracking surveys focusing on EU citizens' perceptions of institutional trust and public life
            * $n = 26,445$ respondents
            """)
        st.markdown("##### 2. Special Eurobarometer SP566 The Digital Decade 2025")
        st.markdown(
            """
            * targeted thematic surveys designed around specific economic and technological shifts (AI, digital technologies, Internet usage)
            * $n = 26,319$ respondents  
            """
        )






# ==========================================
# TAB 1: OVERVIEW
# ==========================================

with tab_overview:
    col_project, col_eu_targets = st.columns([4,2], gap="large")

    # ==============================================================================
    # COLUMN ON MAIN PROJECT CHARACTERISTICS
    # ==============================================================================
    with col_project: 
        st.header("The Strategic North Star: The 80% Target")
        st.markdown(
            """
            The analysis is fundamentally benchmarked against the European Commission’s 2030 Digital Decade Strategic Target, 
            which mandates that at least **80\\%** of all EU adults possess basic or above-basic digital skills by the end of the decade. 
            This metric serves as our foundational baseline, separating structural digital frontrunners from lagging regions facing 
            localized inequality.
            """)

        st.subheader("**Core Tracking Vectors**")
        st.markdown(
            """
            The dashboard aggregates critical macro-indicators to understand regional status and the most vulnerable demographic groups:
            - **Digital Literacy & Skills**: The levels of digital skills are defined inside [**DigComp Framework**](https://joint-research-centre.ec.europa.eu/projects-and-activities/education-and-training/digital-transformation-education/digital-competence-framework-digcomp_en).
            They change from from `I_DSK2_X` (No skills) up to `I_DSK2_AB` (Above-Basic Digital Skills). This lab also gives access to a deep-dive approach,
            looking into different type of skills - Data and Information Literacy; Digital Content Creation; Problem Solving; Safety; Communication and Collaboration.
            - **Internet Usage**: Series of metrics presenting wide range of online activities from `I_IUPDG` (Downloading and playing online games) to `I_IUCPP` (Civic and Political Participation Online).
            Other metrics also include Daily Internet Usage (`I_DAY`) and Adoption of Generative AI Tools (`I_IUAI`).
            - **E-Governance Engagement & eID Usage**: Quantifying direct interaction rates with public authorities (`I_IUGOV1`) and complex digital public services, such as online tax submissions (`I_IGOVTAX2`) or 
            Requesting Benefits Online (`I_IUGOBE`), including eID Adoption (`I_IEID`) or barriers in using this technology (`I_IREIDNA`, `I_IREIDNO`, `I_IREISEC` and other).
            """)

        st.subheader("**Scope & Indicators Types**")
        st.markdown(
            """
            For the scope of this research, the data is presented in two modes:
            - **Individuals** as the main unit of measurement for each metric. Since Eurostat and Eurobarometer both represent data _aggregated per country_, 
            all the metrics show the **total percentage of individuals** (`PC_IND` in the original database schemas). 
            - **Individual Types** vary depending on the active component and analytical layer:
                - **All Individuals:** Used uniformly across geographic maps, macro baseline matrices, and country-level clustering models (`IND_TOTAL` in the raw tables).
                - **Demographic Sub-groups:** Deployed dynamically across advanced statistical tests, cross-tabs, and boxplots to evaluate systemic internal variance. 
                These slices isolate populations by attributes such as gender (e.g., `_f` for female), age brackets (e.g., `_y16_24`), 
                education levels (e.g., `_i0_2` for high education), and urbanization levels (e.g., `_ind_deg1` for city populations).
            """)

        st.subheader("**Temporal Horizon**")
        st.markdown(
            """
            To ensure cross-national comparability, the indicators in this workspace are synchronized across fixed temporal baselines:
            - **Cross-Sectional Baseline (2025):** The vast majority of structural indicators—including eID adoption rates, E-Governance metrics, and all Eurobarometer institutional trust layers—reflect **2025**. 
            This provides a contemporary, post-pandemic snapshot of digital statecraft.
            - **"Longitudinal" Digital Skills Data (2021, 2023, 2025):** The **Digital Skills** domain features a dedicated macro time-series layer. 
            Because Eurostat updates these comprehensive literacy frameworks biennially, the workspace tracks these metrics across **2021, 2023, and 2025**, 
            allowing to evaluate structural progress toward the 2030 targets over time.
            """)
        
    # ==============================================================================
    # COLUMN ON EU TARGETS BY 2030
    # ==============================================================================
    with col_eu_targets:
        st.subheader("EU Digital Decade Targets 2030")
        st.markdown(
            """
            In 2022 the European Union adopted a policy establishing several goals for the Europe's digital transformation.
            The [Digital Decade Policy Programme 2030](https://eur-lex.europa.eu/eli/dec/2022/2481/oj) focuses on:
            """)
        with st.expander("Digitally Skilled Population and High-Skilled Professionals"):
            st.markdown(
                """
                - **Basic Digital Skills**: At least **80\\%** of all adults (16-74 years old) should possess *at least basic digital skills*; 
                - **ICT Specialists**: The EU aims to have **20 million employed ICT professionals**, with a significant focus on closing 
                the gender gap and increasing women's participation in the tech sector.
                """)
        with st.expander("Secure and Sustainable Digital Infrastructures"):
            st.markdown(
                """
                - **Connectivity**: 100\\% gigabit network coverage for all fixed locations and next-generation high-speed wireless networks 
                (at least equivalent to 5G) covering all populated areas;
                - **Semiconductors**: Boosting local fabrication so that the EU accounts for at least 20\\% of the world's semiconductor production by value; 
                - **Edge & Quantum Computing**: Deploying at least **10,000 highly secure, climate-neutral edge nodes** to guarantee low-latency data processing, 
                and securing cutting-edge quantum capabilities. 
                """)
        with st.expander("Digital Transformation of Businesses"):
            st.markdown(
                """
                - **Tech Adoption**: At least 75\\% of EU companies should adopt Cloud computing, Big Data/Data Analytics, and Artificial Intelligence;
                - **Small and Medium-size Enterprise Digitsation**: More than 90\\% of SMEs should reach at least a basic level of digital intensity;
                - **Innovation**: Fostering high-growth innovative startups to double their presence in Europe.
                """)
        with st.expander("Digitalisation of Public Services"):
            st.markdown(
                """ 
                - **eGovernment**: **100\\% online availability** of key public services for citizens and businesses;
                - **Digital Identity**: **100\\% of EU citizens** should have voluntary access to a secure, universally recognized electronic identification (eID) system;
                - **eHealth**: **100\\%** of citizens must have secure, electronic access to their personal electronic health records.
                """)
        st.write('---')

        st.subheader("Goals of the Project")
        with st.expander('**1. Mapping the "Digital Divide" Across the EU Counties:**'):
            st.write("""This goal focuses on identifying geographical disparities in digital infrastructure and 
            adoption across different Member States. By benchmarking regional progress, 
            the project highlights which countries are leading the transition and which regions risk falling behind 
            the EU’s 2030 uniformity targets.""")

        with st.expander('**2. Connecting E-Governance and eID Usage with Institutional Trust:**'):
            st.write("""This analysis investigates whether the digitization of essential public services actively improves 
            the relationship between citizens and the state. Specifically, it tests the hypothesis that seamless 
            interactions with tools like national eIDs and online public portals can statistically correlate with higher 
            levels of trust in national and EU institutions.""")

        with st.expander('**3. Investigating Correlations between Digital Skills and Key Demographic Characteristics:**'):
            st.write("""Instead of treating the population as a monolith, this objective digs into how structural factors 
            like gender, age, education, and urbanization level shape digital competence. 
            The goal is to isolate exactly which demographic groups face the highest barriers to entry, 
            revealing the socio-economic drivers behind digital exclusion.""")

        st.subheader("Limitations")
        with st.expander("Correlation vs. Causality"):
            st.write("""This analysis establishes **correlations, not causation**. Finding a statistical link between high 
                     eID usage and high institutional trust does not mean that using an eID causes someone to trust their government. 
                     It is highly likely that confounding variables—such as overall satisfaction with the economy, 
                     political stability, or pre-existing civic engagement—drive both tech adoption and trust simultaneously.""")
        
        with st.expander("Self-Reported Survey Bias"):
            st.write("""Because the Eurobarometer and Eurostat datasets rely on self-reported survey responses, the data is subject 
                     to inherent human biases. Respondents might overstate their "digital skills" due to social desirability bias, 
                     or their reported "trust" levels might reflect a temporary emotional reaction to current political events 
                     at the exact moment they took the survey, rather than a stable, long-term sentiment.""")
        
        with st.expander("Data Aggregation & Missing Granularity"):
            st.write("""Working with massive, pan-European datasets means some local nuances are inevitably lost in transposition. 
                     To maintain a clean data pipeline and handle missing values, certain row-level variables or niche demographic 
                     categories had to be aggregated. This macro-level view can sometimes mask sharp sub-regional and other inequalities 
                     within individual countries.""")
            
        with st.expander("Timeline"):
            st.write("""Surveys represent a specific snapshot in time. Because digital infrastructure and public sentiment shift rapidly, 
                     analyzing static historical datasets (even relatively "fresh" ones) makes it difficult to capture real-time trends 
                     or the immediate impact of very recent digital policy rollouts across the EU.""")

        st.subheader("**Future Research Vectors**")
        with st.expander("Intersectionality: Investigating Overlapping Inequalities"):
            st.write("""Future iterations of this project could move beyond analyzing demographic variables in isolation and 
                     instead adopt an intersectional approach. By examining how categories like age, gender, and education level overlap 
                     (e.g., analyzing the digital literacy rates of older women with lower educational attainment versus younger men with 
                     the same educational background), the research can uncover hidden barriers and identify the specific subgroups 
                     facing the most severe digital exclusion.""")
        with st.expander("Labor Market Dynamics: Employment Status and Occupation"):
            st.write("""Expanding the data pipeline to include labor market variables would allow for a deeper look into the economic 
                     drivers of digital literacy. Future research could analyze how digital skills and trust in digital governance 
                     vary across different employment statuses (unemployed, retired, self-employed) and occupational sectors 
                     (e.g., manual labor vs. knowledge-based industries), evaluating whether the workplace is 
                     the primary engine of tech fluency or a source of systemic disparity.""")
        with st.expander("Migration Experience and Civic Inclusion"):
            st.write("""Integrating data on migration backgrounds and citizenship status would provide critical insights 
                     into how digital public services affect marginalized or transitioning populations. This path would investigate 
                     whether platforms like eIDs and online immigration/residency portals serve as accessible tools for civic integration, 
                     or if linguistic, bureaucratic, and technical barriers increase the isolation of 
                     migrant communities from institutional support.""")
        with st.expander("Longitudinal Analysis: Tracking Trust Dynamics Over Time"):
            st.write("""While the current project offers a cross-sectional snapshot, a future longitudinal study could track the development of digital skills
                     and E-Governance tools adoption across multiple years.""")
        st.write('---')

        st.markdown("#### Hey! Nice to meet you!")
        with st.expander("**Meet the Author**"):
            with open("./.streamlit/author_pic.jpeg", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()

                col1, col2 = st.columns([1, 4], gap="small")

                with col1:
                    st.markdown(
                        f"""
                        <img src="data:image/jpeg;base64,{img_base64}" 
                            style="border-radius: 50%; width: 80px; height: 80px; object-fit: cover;">
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        """
                        Hey! I'm Dasha. I am a social scientist and also - now! - a data analyst.
                                \nThis entire project was born, raised, and heavily caffeinated within the walls of an **Data Analytics Bootcamp** at Spiced Academy. 
                                For me it's not only charts and metrics I'm presenting today, but also the deep-dive rabbit hole I happily fell into along the way,
                                tracking everything from casual gaming habits to general tech fluency just to see what makes the data fun. 
                                It turns out that wrangling massive EU datasets, untangling complex pipelines, and surviving a high-intensity bootcamp 
                                is the ultimate test of both data literacy and institutional trust!
                                \nIf you like the project, connect with me on [LinkedIn](https://www.linkedin.com/in/daria-skibo-56b9036a/).
            """)
                
            
# ==========================================
# TAB 2: DATA & SOURCES
# ==========================================
with tab_data:
    col_stat, col_bar = st.columns([1,1], gap="medium")
    
    # ----- EUROSTAT DATA -----
    with col_stat:
        st.subheader("Eurostat Data")
        st.markdown(
            """
            **Eurostat** (European Statistical Office) is a Directorate-General of the European Commission. 
            Its [primary mission](https://ec.europa.eu/eurostat/web/main/about-us/mission-values) is to provide high-quality, 
            standardized statistics across Europe, conducted under the unified framework of [the European Statistical System](https://ec.europa.eu/eurostat/web/european-statistical-system/overview).
            """
        )

        st.markdown("##### Main Tables Integrated into the Pipeline")
        eurostat_tables = [
            {"Table Code": "isoc_ci_ifp_iu", "Table Name": "Individuals - internet use", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/ISOC_CI_IFP_IU/default/table?lang=en)"},
            {"Table Code": "isoc_ci_ifp_fu", "Table Name": "Individuals - frequency of internet use", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_ci_ifp_fu/default/table?lang=en)"},
            {"Table Code": "isoc_ciegi_ac", "Table Name": "E-government - activities of individuals via websites", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_ciegi_ac/default/table?lang=en&category=isoc.isoc_i.isoc_ci_egi)"},
            {"Table Code": "isoc_ci_ac_i", "Table Name": "Individuals - internet activities", "Link":"[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_ci_ac_i/default/table?lang=en&category=isoc.isoc_i.isoc_iiu)"},
            {"Table Code": "isoc_eid_ieid", "Table Name": "Use of electronic identification (eID)", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_eid_ieid/default/table?lang=en&category=isoc.isoc_i.isoc_ci_egi)"},
            {"Table Code": "isoc_ai_iaiu", "Table Name": "Individuals - use of generative AI tools", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_ai_iaiu/default/table?lang=en&category=isoc.isoc_i.isoc_ai)"},
            {"Table Code": "isoc_sk_dskl_i21", "Table Name": "Individuals' level of digital skills (from 2021 onwards)", "Link": "[⛓️](https://ec.europa.eu/eurostat/databrowser/view/isoc_sk_dskl_i21/default/table?lang=en&category=isoc.isoc_sk.isoc_sku)"}
        ]
        st.table(eurostat_tables)
        st.caption("*Note: Table names and metrics can be updated on Eurostat side.*")

        with st.expander("**Data Trade-offs (Eurostat)**"):
            col1, col2 = st.columns(2)
            with col1:
                st.success("**The Pros**")
                st.markdown(
                    """
                    * **Harmonized Methodology:** Strict legal and statistical frameworks ensure that a metric like *"internet usage in the last 3 months"* is measured identically in Germany and France.
                    * **Massive Sample Sizes:** Because these metrics feed into direct EU policy and funding, they capture robust behavioral data across major national sample sizes.
                    * **Programmatic Access:** Excellent open-data infrastructure allows the pipeline to bypass manual file handling completely via the Python `eurostat` API package.
                    """)
            with col2:
                st.error("**The Cons**")
                st.markdown(
                    """
                    * **Publication Lags:** Consolidating data across 27 Member States creates an inherent lag of 12 to 24 months, making real-time tech tracking difficult.
                    * **The 'Break in Time Series' Trap:** Classification updates introduce database markers (`:b`) that can disrupt longitudinal analyses.
                    * **Regional Compliance Variance:** Capacity variations mean some Member States submit provisional data late, creating localized missing values.
                    """)

    # ----- EUROBAROMETER DATA -----
    with col_bar:
        st.subheader("Eurobarometer Public Opinion Surveys")
        st.markdown(
            """
            The **Eurobarometer** is a unique cross-national public opinion survey conducted on behalf of the European Commission since the 1970s. 
            This project merges data from two distinct Eurobarometer branches:
            """)
        st.markdown("##### Standard Eurobarometer")
        st.markdown(
            """
            Regular tracking surveys focusing on EU citizens' perceptions of institutional trust and public life.
            * **STD104 (Autumn 2025):** $n = 26,445$ respondents  
                [Documentation](https://europa.eu/eurobarometer/surveys/detail/3378) | [Data Repository](https://data.europa.eu/data/datasets/s3378_104_1_std104_eng?locale=en)
            """)
        st.markdown("##### Special Eurobarometer")
        st.markdown(
            """
            Targeted thematic surveys designed around specific economic and technological shifts.
            * **SP566: The Digital Decade 2025:** $n = 26,319$ respondents  
            Deep-dive metrics covering internet usage, digital identity awareness, and AI perception.  
            [Documentation](https://europa.eu/eurobarometer/surveys/detail/3362) | [Data Repository](https://data.europa.eu/data/datasets/s3362_103_2_sp566_eng?locale=en)
            """
        )
        with st.expander("**Data Trade-offs (Eurobarometer)**"):
            col3, col4 = st.columns(2)
            with col3:
                st.success("**The Pros**")
                st.markdown(
                    """
                    * **Rich Behavioral Insights:** Captures qualitative variables regarding digital trust and citizen sentiments that hard metrics miss.
                    * **Faster Release Cycles:** Published significantly faster than traditional academic panel surveys, allowing access to fresher data.
                    * **Unified Framework:** Fully synchronized and standardized across all EU countries from day one.
                    """
                )
            with col4:
                st.error("**The Cons**")
                st.markdown(
                    """
                    * **Human-Centric Formats:** Raw data is heavily distributed via formatted `.xlsx` sheets, requiring extensive programmatic parsing and reshaping.
                    * **Cultural Translation Shifts:** Nuances in wordings across dozens of languages can lead to subtle variations in how "trust" is interpreted.
                    * **Broad Demographic Grouping:** Key variables (age, income) are pre-aggregated into rigid intervals, restricting hyper-specific micro-modeling.
                    """
                )
        
    # ----- INDICATORS -----
    st.subheader("The Project Indicator Map")
    st.markdown(
        "To execute the statistical and correlation analysis, variables across both repositories were extracted, filtered, and mapped into three core groups:"
    )
    
    expander_iv = st.expand_or_collapse = st.expander("Independent Variables (The Drivers)", expanded=True)
    with expander_iv:
        st.markdown(
            """
            * **E-Governance & eID Adoption:** Frequency of website interaction with public authorities (`isoc_ciegi_ac`) and utilization of electronic IDs (`isoc_eid_ieid`).
            * **Digital Literacy & Fluency:** Baseline digital skills scores (`isoc_sk_dskl_i21`) and everyday internet consumption habits (`i_day`).
            """
        )
        
    expander_dv = st.expander("Dependent Variables (The System Outcomes)", expanded=True)
    with expander_dv:
        st.markdown(
            """
            * **Institutional Trust:** Scaled metrics for citizens' expressed level of confidence in National Parliaments, National Governments, and the European Union (`Eurobarometer 104`).
            * **Digital Rights Sentiments:** Public agreement levels regarding digital environment protections and digital principles safety nets (`Eurobarometer 104`).
            """
        )
        with st.expander("**Example of a question on trust**"):
            st.write("**QA6.1.** How much trust do you have in certain institutions? For each of the following institutions, " \
                "do you tend to trust it or tend not to trust it?:-Political Parties" \
                "\n- Tend to trust" \
                "\n- Tend not to trust" \
                "\n- Don't know")
        with st.expander("**Example of a question about digital usage / expectations**"):
            st.write("**QE1.10.** How important do you think digital technologies will be for the following areas of your daily life " \
                "by 2030?:-Accessing public services online" \
                "\n* Very important" \
                "\n* Fairly important" \
                "\n* Not very important" \
                "\n* Not at all important" \
                "\n* Don't know")
        
    expander_cov = st.expander("Socio-Demographic Dimensions", expanded=True)
    with expander_cov:
        st.markdown(
            """
            * Age groups: `16-19`, `20-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`,
            * Education levels: `Low`, `Medium`, `High`, 
            * Urbanization levels: `Cities`, `Towns/Suburbs`, `Rural`,
            * Gender: `Female` and `Male` of age 16-74.
            """
        )
        
    st.info(
        "**Data Cleaning Highlight:** In order to avoid presenting data mismatched by year, '**latest available year**' technique was implemented with the control for that year to be 2025."
    )


# ==========================================
# TAB 3: PIPELINE & METHODS
# ==========================================
with tab_methods:

    col_core, col_pipeline, col_analytics = st.columns ([1,1,1], gap="small")

    # ----- Core Methodology & Research Design -----
    with col_core:
        st.markdown("#### Framework & Objectives")
        st.write(
            """
            Using macro-level and individual-level survey data in 2025-2026, this study investigates the existence of a 
            "Second-Level Digital Divide" across the 27 European Union member states. Moving beyond basic internet access, 
            the project explores how an individual's actual digital capability maps against demographic inequality lines, 
            affects their vulnerability to fake news/disinformation, and correlates with their overall trust in national and 
            European governance.
        """)

        st.markdown("#### Core Research Questions")
        st.write(
            """ 

            **1. The Macro Overview**: What is the current state baseline of internet usage frequency and overall digital 
            skill levels across the EU-27?

            **2. The Sociodemographic Split**: Does the Digital Divide match traditional socio-demographic inequality lines 
            (e.g., age, gender, education level, type of settlement)?

            **3. Institutional Trust**: How does an individual’s digital literacy correlate with their trust in national governments and EU-level institutions?  

        """)
    
    with col_pipeline:
        st.markdown("#### The Data Pipeline Architecture")
        with st.expander("**Phase A | Data Retrieving and Seeding**"):
            st.write(
                """
                ##### Multi-Source Extraction & Ingestion Architecture
                
                Before any data could enter our transformation pipeline, we designed an acquisition strategy to bridge programmatically open public data registries with complex, survey-based institutional datasets.
                
                ---

                **1. Data Ingestion Pathways**
                We executed two distinct retrieval methodologies tailored to the infrastructure of our source institutions:
                * **Programmatic Bulk Extraction (Eurostat):** To capture the comprehensive digital skills timelines and e-governance metrics, we bypassed manual downloads and built an automated extraction script utilizing the `eurostat` Python library. This interacted directly with the Eurostat API to pull raw, high-density bulk database sheets, ensuring programmatic reproducibility and caching optimization.
                * **Targeted Manual Retrieval (Eurobarometer):** Because Eurobarometer institutional trust matrices are delivered as dense, highly segmented research structures, these files were manually retrieved. This ensured precise cohort isolation before entering our custom ingestion framework.

                **2. Custom Python Pre-Processing & ETL Pipeline**
                The raw Eurobarometer data contained severe structural irregularities that made it entirely incompatible with database tables. To solve this, we engineered a dedicated Python cleaning script to run complex pre-processing routines:
                * **Deduplication & Language Pruning:** The raw source files contained parallel French and English string duplications for survey questions. We engineered string filtering logic to completely purge the secondary language copies, standardizing the text layers.
                * **Normalization of Metrics:** We systematically isolated and removed absolute numbers (raw respondent counts), transforming the metrics exclusively into normalized, cross-nationally comparable percentages.
                * **Schema & Meta-Label Preservation:** To ensure we did not lose granular structural insights, our script systematically renamed raw, cryptic column headers into clear, legible semantic metrics, while preserving the underlying row-level metadata context for every tracked indicator.

                **3. The `dbt Seed` Layer**
                Once both datasets were clean and structured into optimized, flat `.csv` data files, we loaded them into our localized environment. Using the **`dbt seed`** command, these static, raw historical frameworks were natively compiled and inserted directly into our local database warehouse as version-controlled relations. This established an immutable, repeatable foundation for all downstream analytical models.
                """
            )
            
        with st.expander("**Phase B | Transformation & Modeling**"):
            st.markdown(
                """
                ##### The dbt Transformation Architecture
                To handle our high-volume datasets with absolute pipeline integrity, we structured our **dbt (Data Build Tool)** architecture into a tailored, three-tiered data modeling system. This decoupled our heavy architectural restructuring from our research-specific slicing logic.
                
                ---

                **1. The Preparation Layer (`prep_`)**
                This layer served as our heavy structural engineering gate, handling data from over 35+ disparate Eurostat tables alongside country metadata:
                * **The 2-Million-Row Melt Operations:** The raw Eurostat inputs were structurally wide and fragmented. We executed comprehensive melting and reshaping operations to transform the data layout. We unpivoted the separate yearly columns into a single longitudinal `time_period` vector and consolidated all disparate metrics into a unified `indicator` column—generating a massive, normalized core table exceeding 2 million rows.
                * **Geospatial & Reference Harmonization:** We engineered our core country reference model (`prep_countries`). This layer cleaned country-level strings and established a master lookup map to resolve standard administrative geocode inconsistencies.

                **2. The Staging Layer (`stg_`)**
                Once the data was normalized into a massive, centralized core matrix, our staging layer acted as a specialized filtering gate to isolate our distinct research components:
                * **Research Vector Extraction:** Instead of passing the entire 2-million-row table downstream, we built dedicated staging models to extract precise subsets of data tailored to our specific research questions (e.g., isolating Digital Skills metrics independently from E-Governance variables).
                * **Demographic Slicing & Metric Refinement:** In this layer, we performed targeted data cleaning on the metrics and isolated the granular demographic cross-sections (such as isolating male vs. female performance bands) required for our non-parametric statistical testing.

                **3. The Mart Layer (`mart_`)**
                Our final modeling layer produces highly optimized, lean tables designed specifically to feed our Streamlit app without runtime computational lag:
                * **Label Enrichment & ISO Mapping:** This layer joins our clean research vectors with definitive country boundary handles (`plotly_country_code`) and appends readable descriptive text labels to our abstract Eurostat indicator handles.
                * **EU Baseline Aggregations:** The primary output of this tier is our definitive main metrics table (`mart_eu_baseline`), which provides pre-aggregated, sorted, and spatially mapped values ready for instant rendering on our dashboard maps and statistical modules.
            """)

        with st.expander("**Phase C | EDA, First Visualizations, & Testing Hypotheses**"):
            st.write("""
                ##### Exploratory Data Analysis & Statistical Iteration
                Before building our production application, we utilized Jupyter Notebooks (`.ipynb`) as an agile sandbox environment to perform 
                Exploratory Data Analysis (EDA), profile our distributions, and validate our initial statistical assumptions. 
                
                ---

                **1. Data Profiling & Finding Anomaly Triggers**
                Our initial EDA uncovered several structural vulnerabilities in the raw ingestion files that required immediate intervention:
                * **Identifying Missing Vectors:** We mapped out the missing data footprints across countries. This revealed that certain critical historical years were completely absent for specific indicators, which forced us to go back to the pipeline, retrieve entirely new data sheets, and engineer a more resilient data strategy.
                * **Exposing the Methodology Break:** It was during this exploratory phase that we visualized the sharp drop-off in scores between 2019 and 2021. By digging into the metadata, we caught the Eurostat framework overhaul, allowing us to proactively design the "Framework Bridge" before writing production code.

                **2. The Statistical Evolution**
                Our statistical architecture underwent an iterative design evolution as we refined our research questions:
                * **Initial Explorations (Correlations & T-Tests):** We began by mapping basic linear correlations and running standard independent t-tests to compare groups. 
                * **The Non-Parametric Shift:** Realizing that our survey-based percentage distributions violated the assumption of normality required by parametric tests, we pivoted to more robust methods. We deployed the **Friedman Test** to evaluate multi-year macro trends across the EU blocks, and switched our demographic comparisons to the **Wilcoxon Signed-Rank Test** to accurately handle paired, non-normal cohorts (e.g., female vs. male performance within the same country).

                **3. Notebook Refactoring & Productionization**
                Moving from an experimental sandbox to an analytics-ready application required strict code refactoring:
                * **Code Reuse & Adaptation:** We successfully extracted the working SQL queries, data filtering blocks, and statistical routines 
                (like the Friedman and Wilcoxon calculations) directly from our `.ipynb` exploratory notebooks and integrated them straight into 
                the Streamlit application framework to make the dashboard instantly operational.
                """)

        with st.expander("**Phase D | App Layer & Final Presentation**"):
            st.write("""
                ##### App Delivery, Database Integration, & Version Control
                The final phase of our lifecycle focused on translating our transformed data models into a secure, interactive, and production-ready web application.
        
                ---

                * **The Streamlit Frontend:** We engineered an interactive dashboard using **Streamlit**, deploying a multi-panel layout to present our 
                findings cleanly.
                * **PostgreSQL Infrastructure:** The application does not rely on static flat files; instead, it creates a live 
                secure connection to the localized **PostgreSQL data warehouse**. Streamlit interacts directly with our dbt-generated mart layer via 
                SQL queries, ensuring dynamic data retrieval. The PostgreSQL database tables can be updated at any moment.
                * **Version Control & Lineage:** To guarantee project reproducibility, the entire repository—including our dbt schemas, 
                SQL transformations, seed datasets, and frontend scripts—is managed under Git version control. This establishes a history of the changes 
                and protects the structural integrity of the deployment pipeline.
                """)
    
    with col_analytics:
        st.markdown("#### Analytical Approaches")
        with st.expander("Friedman Test"):
            st. write(""" 
                Macro-Level Multi-Year Comparison): We used this non-parametric test to evaluate whether digital 
                literacy and trust scores shifted significantly across the entire European Union over time. 
                It treats each country as a block and looks across multiple years to prove if the overall EU trajectory 
                is changing or stagnant.
            """)
        with st.expander("Wilcoxon Signed-Rank Test"):
            st.write(""" 
                (Paired): We deployed this non-parametric test to evaluate structural inequalities within countries. 
            By treating each Member State as its own baseline, we directly compared paired demographic cohorts 
            (specifically female vs. male digital proficiency scores) to determine if the gender capability gap 
            is statistically significant across the EU.
            """)
        with st.expander("K-Means Clustering"):
            st.write("""
                (Unsupervised Performance Grouping): Instead of relying on traditional, arbitrary geographic definitions (like "Eastern Europe"), 
                we put our multi-dimensional indicators (skills, trust, eID friction) into a clustering algorithm. This grouped the Member States 
                into distinct, empirical archetypes based on their actual digital maturity and institutional readiness.
            """)




# ==============================================================================
# FOOTER SECTION
# ==============================================================================
funcs.add_authorship_footer()