import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns 
import matplotlib.pyplot as plt
import pyodbc
import streamlit as st

###### STREAMLIT SETTINGS ----------------------------------------->
st.set_page_config(layout = 'wide', page_title='Cinema Dashboard', page_icon='🍿')
# 🎬🍿
###### TABS ----------------------------------------->
sale_db, customer_db, about = st.tabs(["Doanh thu", "Khách hàng", "Giới thiệu"])

##### IMPORT DATA ----------------------------------------->
# Connection details
server = 'projectcinemaserver.database.windows.net'
database = 'cinemadatabase'
username = 'datasquad'
password = 'Homies@2024'
driver = '{ODBC Driver 18 for SQL Server}'  # Adjust driver based on your environment
# Connection string
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
# Connect to the database
conn = pyodbc.connect(conn_str)

# Customer Data
query_cust = 'SELECT * FROM Customer'
df_cust = pd.read_sql(query_cust, conn)

# Film Data
query_film = 'SELECT * FROM Film'
df_film = pd.read_sql(query_film, conn)

# Customer Data
query_tick = 'SELECT * FROM Ticket'
df_tick = pd.read_sql(query_tick, conn)
df_order = df_tick.drop_duplicates(subset=['orderid'])
# df_tick = pd.read_csv('Ticket.csv')
# df_order = df_tick.drop_duplicates(subset=['orderid'])

#### Sale Dashboard ------------------->
with sale_db:
    st.markdown("<h3 style='text-align: center;'>Dashboard báo cáo doanh thu</h3>", unsafe_allow_html=True)
    st.write('##')

    ### Data Metrics

    # Total sale
    total_sale = df_order['total'].sum()
    # total_sale = '{:,.0f}'.format(total_sale)
    st.metric('Tổng doanh thu (VNĐ)', total_sale)

    # Total order
    total_order = len(df_order['orderid'])
    st.metric('Số lượng order', total_order)

    # Total film
    total_film = len(df_order['film'].unique())
    st.metric('Số phim được chiếu', total_film)




    ### Display data
    showdata = st.checkbox("Display Data")
    if showdata:
        st.dataframe(df_cust, use_container_width=True)



