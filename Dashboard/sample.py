import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns 
import streamlit as st
import matplotlib.pyplot as plt


### STREAMLIT SETTINGS
st.set_page_config(layout = 'wide', page_title='AirBnb Project', page_icon='🏠')

### TABS
dashboard, model, about = st.tabs(["Dashboard", "Model",'About'])

### DASHBOARD -----------------------------------------------------------------
with dashboard:
    #### DASHBOARD
    st.markdown("<h2 style='text-align: center;'>AIRBNB: DENMARK PROPERTIES DASHBOARD</h1>", unsafe_allow_html=True)
    st.write('##')
    ### IMPORT DATA
    df = pd.read_csv('data_airbnb.csv', encoding='latin-1')

    ### DATA CLEANING
    # handling missing values
    df = df.dropna(subset=['accommodates', 'price_USD','longitude'])
    # specify properties in Sealand
    df['location'] = 'Non-Sealand'
    df.loc[(df['latitude']<=55.78) & (df['longitude']>=10.994) & (df['longitude']<=12.672), 'location'] = 'Sealand'
    # calculate price 
    df['price_per_night'] = df['price_USD']/df['minstay']
    # transform first_listed to datetime data (year-month)
    df['first_listed'] = pd.to_datetime(df['first_listed'], format='%d/%m/%Y')
    # transform to year-month format
    df['month_year'] = df['first_listed'].dt.to_period('M')
    # sort values
    df = df.sort_values(by='month_year')


    ### SPLITTING COLUMNS
    block1, block2= st.columns([5,5])

    # COLUMN 3
    with block2: 
        block2_chart, block2_filter= st.columns([7,3])
        with block2_filter:
            ### Filter
            # locations
            filter_location = st.selectbox(
                'Location',
                ('All','Sealand',' Non-Sealand'), index=0)
            if filter_location != 'All':
                df = df[df['location'] == filter_location]

            # period of time
            from datetime import datetime
            point_of_time = st.slider(
                "Period of time",
                value=datetime(2019, 10, 1),
                min_value = datetime(2016, 11, 1),
                format="Y-M")
            point_of_time = pd.to_datetime(point_of_time).to_period('M')

            df = df[df['month_year'] <= point_of_time]
        with block2_chart:
            #  PIE CHART: room type
            room_type_counts = round((df['prop_room_type'].value_counts()/len(df))*100,2)
            df_roomtype = pd.DataFrame(room_type_counts).reset_index()
            df_roomtype.columns = ['Room Type', 'Percentage']

            color_mapping_roomtype = {
            'Entire home/apt': '#ffc300',
            'Private room': '#fcefb4',
            'Shared room': '#0466c8',}

            df_roomtype['color'] = df_roomtype['Room Type'].map(color_mapping_roomtype)
            pie_roomtype = px.pie(df_roomtype, 
                                names='Room Type', 
                                values='Percentage',
                                title='Percentage of Room types', 
                                color_discrete_sequence=df_roomtype['color'],
                                hole=0.4, 
                                height=200)
            
            pie_roomtype.update_layout(showlegend=False,
                                        # paper_bgcolor='rgb(255,255,255)',
                                        margin=dict(l=10, r=10, t=30, b=0),
                                        title_x=0.3,
                                        autosize=False,
                                        width=100)
            pie_roomtype.update_traces(text=df_roomtype['Room Type'], textposition='outside')

            st.plotly_chart(pie_roomtype, use_container_width=True)


        # LINE CHART: price changes overtime
        # group data to aggregate
        gr_time = df.groupby(['month_year','location'])['price_per_night'].mean().reset_index().sort_values(by='month_year')
        gr_time['month_year'] = gr_time['month_year'].astype(str)
        gr_time.columns = ['Period of time', 'Location', 'Average price per night']

        color_mapping_price = {'Sealand': '#ffc300', 'Non-Sealand': '#0466c8'}

        fig = px.line(gr_time,
                        x="Period of time",
                        y="Average price per night",
                        title='Averge price per night changes over time',
                        color="Location",
                        color_discrete_map=color_mapping_price,
                        # width=700,
                        height=430,
                        labels={'Location': 'Location'})
        fig.update_layout(title_x=0.3)
        st.plotly_chart(fig, use_container_width=True)


    # COLUMN 1
    with block1:
        metric_1, metric_2 = st.columns([5,5])
        with metric_1:
            # number of properties
            no_prop = len(df)
            st.metric('Number of properties', no_prop,label_visibility="visible")

            # average satisfaction score
            average_satisfaction = round((df['overall_satisfaction']).mean(),1)
            st.metric('Average satisfaction score',average_satisfaction)
        with metric_2:
            # number of hosts
            no_host = len(df['host_id'].unique())
            st.metric('Number of hosts', no_host)
            # average price per_night
            avg_price = round((df['price_per_night']).mean(),2)
            st.metric('Average price per night ($)', avg_price)

        # BAR CHART: satisfaction score

        satis_counts = df.groupby(['overall_satisfaction', 'location']).size()
        df_satis = pd.DataFrame(satis_counts).reset_index()
        df_satis.columns = ['Satisfaction score', 'Location', 'Number of reviews']
        df_satis.sort_values(by='Satisfaction score', inplace=True)

        # Create a bar chart with blended bars using plotly express
        color_mapping_satis = {'Sealand': '#ffc300', 'Non-Sealand': '#0466c8'}
        fig = px.bar(
            df_satis,
            x='Satisfaction score',
            y='Number of reviews',
            color='Location',
            color_discrete_map=color_mapping_satis,
            labels={'Number of reviews': 'Number of Reviews'},
            title='Satisfaction Score Distribution',
            barmode='group',  # Use barmode='group' for blended bars
            height=475
        )
        fig.update_layout(title_x=0.3)

        # st.markdown("<h5 style='text-align: center;'>Satisfaction Score Distribution</h5>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    ### Display data
    showdata = st.checkbox("Display Data")
    if showdata:
        st.dataframe(df, width=1920)


### MODEL -----------------------------------------------------------------
with model:
    ### DATA INPUT INTERFACE	
    st.markdown("<h2 style='text-align: center;'>PREDICTION MODEL: SEALAND BUDGET PROPERTIES CLASSIFIER</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><i>This predictive model can be utilized by Airbnb to identify properties categorized as budget-friendly, facilitating the application of distinct marketing strategies. <br> Additionally, customers can use it to reference property prices.</i></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><b>Developed by Vi Pham - Henry</b></div>", unsafe_allow_html=True)


    # CONTENT ALIGNMENT WITH COLUMNS
    st.write('##')
    empty, model_input, empty = st.columns([1,8,1])
    with model_input:
        # SPLIT COLUMN
        input_col1, input_col2 = st.columns(2)
        # COLUMN 1
        with input_col1:

            import json
            # Load encoding mapping from JSON file
            with open('encoding_mapping.json', 'r') as json_file:
                categoricaldata_mapping = json.load(json_file)

            ## prop_room_type
            list_roomtypes = []
            for roomtype, code in categoricaldata_mapping['prop_room_type'].items():
                list_roomtypes.append(roomtype)

            input_roomtype = st.selectbox(
                'Room Type',list_roomtypes)
            
            input_model_roomtype = categoricaldata_mapping['prop_room_type'][input_roomtype]
            # st.write('Encoded roomt type:', input_model_roomtype)


            ## reviews
            input_model_reviews= int(st.number_input('Number of reviews', step=1))

            ## latitude
            input_model_latitude = st.number_input("Properties's latitude", format="%f")
        # COLUMN 2
        with input_col2:
            ## neighborhood
            list_neighborhoods = []
            for neighborhood, code in categoricaldata_mapping['neighborhood'].items():
                list_neighborhoods.append(neighborhood)

            input_neighborhood = st.selectbox(
                'Neighborhood',list_neighborhoods)
            
            input_model_neighborhood = categoricaldata_mapping['neighborhood'][input_neighborhood]
            # st.write('Encoded neighborhood:', input_model_neighborhood)

            ## accommodates
            input_model_accommodates = int(st.number_input('Number of accommodates', step=1))

            ## longitude
            input_model_longitude = st.number_input("Properties's longitude", format="%f")
        
        ## overall_satisfaction
        empty, satis_slider, empty = st.columns([3, 4, 3])
        with satis_slider:
            input_model_satisfaction = st.slider('Overall satisfaction score of property', 0, 5)

    ### SUBMIT TO PREDICT
    # Create a container for alignment
    empty, button_align, empty = st.columns([4, 2, 4])
    with button_align:
        button_predict = st.button("PREDICT", type="primary", key="predict_button", use_container_width=True)
        st.markdown("""
                <style>
                div.stButton > button:first-child {
                    background-color: #ffc300;
                    color:black;
                    font-weight:bold;
                }
                </style>""", unsafe_allow_html=True)
        
        if button_predict:
            input_model_final = np.array([input_model_roomtype, input_model_neighborhood,
                                        input_model_reviews, input_model_satisfaction,
                                        input_model_accommodates,
                                        input_model_latitude, input_model_longitude])

            # Reshape the input to have a single row and 7 columns
            input_model_final = input_model_final.reshape(1, -1)
            print(input_model_final)

            ### Load the model
            import joblib
            model = joblib.load('model.joblib')
            result = model.predict(input_model_final)

            ## Display result
            if result == 1:
                st.success("Budget Property!")
            else:
                st.error("Non-Budget Property!")

### ABOUT -----------------------------------------------------------------

with about:
    with st.container():
        st.title("Hi there, I'm Vi Pham - Henry :wave:")
        st.subheader("A data nerd from Vietnam")
        st.write(
            "I am passionate about the field of data science and have 3 years of experience in this domain. I hope this project will spark an interest in you, just like it has for me."
        )
        st.write("[Learn more about my other projects on GitHub](https://pythonandvba.com)")

    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("What else I can do?")
            st.write("##")
            st.write(
                """
                Over the course of the past 3 years, my learning journey has equipped me with the following data science skills:
                -  Data Wrangling
                -  Data Visualization
                -  Machine Learning, Statistics
                -  Database, Data Warehouse
                -  Django, Streamlit
                -  Python, SQL, Tableau, PowerBI
                -  Cloud Computing: Azure
                -  Data Scraping
                """
            )

        with right_column:
            st.header("Thank you for reading")
            st.write("##")
            st.write(
                """
                I sincerely appreciate your time in following and reading the results of this project. If you have any questions, opinions, or would like to share your thoughts, I warmly welcome and are open to receiving them.  
                To get in touch with me or to obtain more detailed information, please use the following means:  

                Email: anhvi09042002@gmail.com  

                LinkedIn: https://www.linkedin.com/in/anh-vi-pham/  

                Github: https://github.com/anhvi02

                Kaggle: https://www.kaggle.com/nobit02  

                I highly value all contributions and feedback, and will endeavor to respond at the earliest opportunity. Thank you once again, and I look forward to hearing from you!""")
