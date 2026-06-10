import streamlit as st
import plotly.express as px

@st.cache_data
def load_and_clean_data():
    conn = st.connection("postgresql", type="sql")
    df_data = conn.query("SELECT * FROM public.mart_eu_baseline", ttl="10m")

    year_to_check = ['i_dsk2_ab_source_year', 'i_dsk2_b_source_year',
       'i_dsk2_x_source_year', 'i_iday_source_year', 'i_ieid_source_year',
       'i_igovapr_source_year', 'i_igovtax2_source_year',
       'i_imt12_source_year', 'i_iuai_source_year', 'i_iugov1_source_year',
       'i_iupol2_source_year', 'i_iux_source_year', 'i_maps_source_year',
       'i_tic_source_year', 'i_udi_source_year', 'i_ireidno_source_year',
       'i_ireidna_source_year', 'i_ireidsec_source_year',
       'i_ireidtec_source_year', 'i_ireidnn_source_year',
       'i_ireiddev_source_year', 'i_ireidoth_source_year']
    
    df_data = df_data.drop(columns=year_to_check)
    df_data = df_data.drop(columns=['lat','lon'])

    eurostat_indicators = ['country_name','country_code','i_dsk2_ab', 'i_dsk2_b', 'i_dsk2_x', 'i_iday',
       'i_ieid', 'i_igovapr', 'i_igovtax2', 'i_imt12', 'i_iuai', 'i_iugov1',
       'i_iupol2', 'i_iux', 'i_maps', 'i_tic', 'i_udi', 'i_ireidno',
       'i_ireidna', 'i_ireidsec', 'i_ireidtec', 'i_ireidnn', 'i_ireiddev',
       'i_ireidoth']
    
    df = df_data[eurostat_indicators]

    return df



if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("EU Digital Litercay Overview")
    st.write("---")

    left_layout_col, right_layout_col = st.columns([1, 2], gap="large")

    df_eurostat = load_and_clean_data()
    eurostat_indicators_titles = {
        'i_iday':'Access Internet Daily',
        'i_iugov1': 'Use Internet to Interact with Authorities',
        'i_dsk2_ab':'Have Above Basic Digital Skills',
        'i_dsk2_b':'Have Basic Digital Skills',
        'i_dsk2_x':"Don't Have Any Digital Skills",
        'i_ieid': 'Using eID to Access Online Services',
        'i_ireidno':"Do Not Use eID and Don't Have One",
        'i_igovtax2':'Submit Tax Declaration Online',
        'i_iuai':'Use Generative AI'
    }

    with left_layout_col:
        st.subheader("Indicators & Benchmarks")
        selected_title = st.selectbox("Select Metric:", options=list(eurostat_indicators_titles.values()))
        selected_indicator = next(k for k, v in eurostat_indicators_titles.items() if v == selected_title)
        st.write("---")
    

        st.metric(label="EU Average", value=f"{df_eurostat[selected_indicator].mean():.1f}%")
        st.metric(label="Std. Deviation", value=f"{df_eurostat[selected_indicator].std():.1f}")
        st.metric(label="Min Country", value=f"{df_eurostat[selected_indicator].min():.1f}%")
        st.metric(label="Max Country", value=f"{df_eurostat[selected_indicator].max():.1f}%")

    metrics_to_show = [
        'i_dsk2_ab','i_dsk2_b','i_dsk2_x', 'i_iday',
        'i_ieid', 'i_igovtax2', 'i_iuai', 'i_iugov1', 
        'i_ireidno'
    ]


    with right_layout_col:
        st.subheader("Geographic Distribution")
        st.write("Select an indicator below to explore it's geographic distribution across the EU.")

        selected_title = st.selectbox(
            "Choose a metric to visualize:",
            options=eurostat_indicators_titles.values()
        )

        selected_indicator = next(
            key for key, val in eurostat_indicators_titles.items() if val == selected_title
        )

        fig = px.choropleth(
            df_eurostat,
            locations='country_name',          
            locationmode='country names',      
            color=selected_indicator,
            hover_name='country_name',         
            hover_data=[selected_indicator], 
            color_continuous_scale='haline',
            title=selected_title, 
            width=1000,
            height=700
        )

        fig.update_geos(
            projection_type="mercator",   
            center=dict(lon=10, lat=52),  
            projection_scale=4.5,         
            visible=False,                
            showframe=False,              
            showcoastlines=True,          
            coastlinecolor="LightGray"
        )

        fig.update_layout(
            margin={"r":0,"t":50,"l":0,"b":0}, 
            title_font_size=16,           
            title_x=0.5 
        )

        st.plotly_chart(fig, use_container_width=True)
    
    
        st.divider()

