import streamlit as st

# ==========================================
# PAGE SETTINGS & GLOBAL THEME
# ==========================================
st.set_page_config(layout="wide")

# Set the style for the tabs globally
st.markdown("""
    <style>
        button[data-baseweb="tab"] {
            background-color: #41748d !important;
            color: #83c5be !important;           
            border-radius: 4px 4px 0px 0px;       
            padding: 10px 20px !important;       
            margin-right: 4px !important;        
            transition: background-color 0.3s ease;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #005f73 !important; 
            color: #FFFFFF !important;           
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #005f73 !important; 
            color: #FFFFFF !important;           
            font-weight: bold !important;        
        }
        div[data-飛躍="stHorizontalBlock"] div[role="tablist"] div {
            background-color: transparent !important; 
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# NATIVE ROUTING MANAGEMENT
# ==========================================
# ⚡ CRITICAL FIX: The home page needs to point to a page file, NOT your main controller app.py!
overview_page = st.Page("pages/0_project_overview.py", title="Project Overview", icon="🇪🇺", default=True)
baseline = st.Page("pages/1_eu_baseline.py", title="EU Baseline & Clustering")
usage = st.Page("pages/2_internet_usage.py", title="Internet Usage")
digital_skills = st.Page("pages/3_digital_skills.py", title="Digital Skills")
e_gov = st.Page("pages/4_e_gov.py", title="E-Governance and eID")

# Declare and run the routing engine
pg = st.navigation([overview_page, digital_skills, usage, e_gov, baseline])
pg.run() # <--- Tells Streamlit to stop here and strictly run the selected page!