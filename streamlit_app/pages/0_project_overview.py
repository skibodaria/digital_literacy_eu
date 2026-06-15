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
        st.markdown(
            """
            1. Mapping the "Digital Divide" Across the EU Counties
            2. Connecting E-Governance and eID Usage with Institutional Trust
            3. Investigating Correlations between Digital Skills and Key Demographic Characteristics"""
        )
    
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
    st.subheader("Information about Data")



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