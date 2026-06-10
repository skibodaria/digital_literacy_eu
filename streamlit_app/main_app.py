if __name__ == '__main__':
    import streamlit as st
    import plotly.express as px

    st.title("EU Analysis Dashboard")

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

    eurobarometer_columns = ['country_name','country_code', 'tr_party', 'tr_authority', 'tr_nat_gov', 'tr_nat_par',
       'tr_eu', 'tr_eu_par', 'tr_press', 'tr_soc_netw_online',
       'nat_media_tr_info', 'nat_media_free_pressure',
       'tr_info_polit_on_soc_net', 'eff_acc_to_tech',
       'eff_improve_democr_life', 'eff_improve_acc_pub_services',
       'eff_work_remote']
    eurostat_indicators = ['country_name','country_code','i_dsk2_ab', 'i_dsk2_b', 'i_dsk2_x', 'i_iday',
       'i_ieid', 'i_igovapr', 'i_igovtax2', 'i_imt12', 'i_iuai', 'i_iugov1',
       'i_iupol2', 'i_iux', 'i_maps', 'i_tic', 'i_udi', 'i_ireidno',
       'i_ireidna', 'i_ireidsec', 'i_ireidtec', 'i_ireidnn', 'i_ireiddev',
       'i_ireidoth']
    

    # and their titles to be able to print it nicely:
    eurostat_indicators_titles = {
        'i_iday':'Frequency of internet access: daily',
        'i_iupol2': 'Internet use: expressing opinions on civic or political issues on websites or in social media (e.g. Facebook, Twitter, Instagram, YouTube)',
        'i_iugov1': 'Internet use: interaction with public authorities (last 12 months)',
        'i_igovapr':'Internet use: making an appointment or a reservation (last 12 months)',
        'i_imt12':'Last internet use: more than a year ago or never',
        'i_iux':'Internet use: never',
        'i_maps':'Individuals manage access to personal data on the internet (3 months)',
        'i_udi':'Individuals have seen untrue or doubtful information or content on the internet news sites or social media (3 months)',
        'i_tic':'Individuals have checked the truthfulness of the information or content they found on the internet news sites or social media (3 months)',
        'i_dsk2_ab':'Individuals with above basic overall digital skills (highest)',
        'i_dsk2_b':'Individuals with basic overall digital skills (high)',
        'i_dsk2_x':'Individuals with no overall digital skills',
        'i_ieid':	'Individuals who have used their eID to access online services for private purpose in the last 12 months',
        'i_ireidno':"Individuals not using their eID in the last 12 months because they didn’t have one",
        'i_ireidna':"Individuals not using their eID in the last 12 months because they were not aware of its existence",
        'i_ireidsec': "Individuals not using their eID in the last 12 months because they didn’t feel safe using it",
        'i_ireidtec': "Individuals not using their eID in the last 12 months because they could not use it due to usability/technical issues",
        'i_ireidnn': "Individuals not using their eID in the last 12 months because they didn’t need to access any online services requiring it",
        'i_ireiddev':"Individuals not using their eID in the last 12 months because they could not use it to access the service via a smartphone or tablet",
        'i_ireidoth': "Individuals not using their eID in the last 12 months because of other reasons",
        'i_igovtax2':'Internet use: submitting my tax declaration (in the last 12 months)',
        'i_iuai':'Use of generative AI tools: in the last 3 months'
    }
    
    df_eurostat = df_data[eurostat_indicators]
    df_eurobar = df_data[eurobarometer_columns]

    st.subheader("Descriptive Statistics for Main Eurostat Metrics, 2025")
    st.dataframe(df_eurostat.describe())

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

