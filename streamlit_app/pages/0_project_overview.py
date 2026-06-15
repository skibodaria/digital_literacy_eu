import streamlit as st
import base64

st.set_page_config(layout="wide")

st.header("Digital Literacy, E-Governance Usage, & Inequality: Mapping the EU Digital Decade")
st.markdown(
    """
    Welcome to the EU Digital Baseline Workspace. This core interface establishes an objective, 
    macro-level diagnostic of digital literacy, Internet usage, and e-governance adoptions across the European Union.
    """)
st.write("---")

tab_overview, tab_data, tab_methods, tab_rec = st.tabs([
    "Project Intro",
    "Data & Sources",
    "Methods & Pipeline",
    "Key Insights & Recommendations"
])

# ==========================================
# TAB 1: OVERVIEW
# ==========================================

with tab_overview:
    col_project, col_eu_targets = st.columns([4,2], gap="large")

    # ==============================================================================
    # COLUMN ON MAIN PROJECT CHARACTERISTICS
    # ==============================================================================
    with col_project: 
        st.subheader("The Strategic North Star: The 80% Target")
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
        with st.expander("**From Author**"):
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
    st.header("Data Sources & Indicators Blueprint")
    st.markdown("""The analytical process of this project relies on official, well-established, and publicly available macro-statistics provided
    by the European Commission."""
)
    # ----- EUROSTAT DATA -----
    st.subheader("Eurostat Data")
    st.markdown(
        """
        **Eurostat** (European Statistical Office) is a Directorate-General of the European Commission. 
        Its [primary mission](https://ec.europa.eu/eurostat/web/main/about-us/mission-values) is to provide high-quality, 
        standardized statistics across Europe, conducted under the unified framework of [the European Statistical System](https://ec.europa.eu/eurostat/web/european-statistical-system/overview).
        """
    )

    st.markdown("#### Main Tables Integrated into the Pipeline")
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
    st.caption("*Note: Table registry is dynamically updated via the data pipeline.*")

    st.markdown("#### Data Pipeline Trade-offs (Eurostat)")
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
    st.subheader("Eurobarometer Public Opinion Surveys")
    st.markdown(
        """
        The **Eurobarometer** is a unique cross-national public opinion survey conducted on behalf of the European Commission since the 1970s. 
        This project merges individual microdata from two distinct Eurobarometer branches:
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
    st.markdown("#### Data Pipeline Trade-offs (Eurobarometer)")
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
        "**Data Cleaning Highlight:** In order to avoid presenting data mismatched by year, '**latest available year**' technique was implemented."
    )



# ==========================================
# TAB 3: PIPELINE & METHODS
# ==========================================
with tab_methods:
    st.subheader("Info about methods and process")

# ==========================================
# TAB 4: FINDINGS & RECOMMENDATIONS
# ==========================================
with tab_rec:
    st.subheader("Main Insights and Recommendations")


# ==============================================================================
# FOOTER SECTION
# ==============================================================================
st.write("---")
st.caption("""
    **Data Source Reference:** Eurostat Digital Economy and Society Statistics (2025), [Eurobarometer Standard (104)](https://europa.eu/eurobarometer/surveys/detail/3378) 
    and [Eurobarometer Special (sp566)](https://europa.eu/eurobarometer/surveys/detail/3362).
""")