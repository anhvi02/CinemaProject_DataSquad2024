import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns 
import matplotlib.pyplot as plt
import pyodbc
import streamlit as st
import datetime 

###### STREAMLIT SETTINGS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
st.set_page_config(layout = 'wide', page_title='Cinema Dashboard', page_icon='🍿')
color_1 = '#fb6f92'
# ffc300
color_2 = '#ffc2d1'


##### DATABASE CONNECTING >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Connection details
server = st.secrets["server"]
database = st.secrets["database"]
username = st.secrets["username"]
password = st.secrets["password"]
driver = "{ODBC Driver 18 for SQL Server}" 

# Connection string
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
# st.write(conn_str)
# Connect to the database
conn = pyodbc.connect(conn_str)




###### TABS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
sale_db, customer_db, about = st.tabs(["Doanh thu", "Khách hàng", "Giới thiệu"])



##### SALES DASHBOARD>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#### DATA PREPRARING  -------------------------->
### Film Data
query_film = 'SELECT * FROM Film'
df_film = pd.read_sql(query_film, conn)

### Ticket Data
query_tick = 'SELECT * FROM Ticket'
df_tick = pd.read_sql(query_tick, conn)

### Order Data
df_order = df_tick.drop_duplicates(subset=['orderid'])

#### DISPLAYING SALES DASHBOARD  -------------------------->
with sale_db:
    st.markdown("<h3 style='text-align: center;'>Chuyển qua tab Khách hàng giùm chứ đây chưa có mẹ gì hết đâu</h3>", unsafe_allow_html=True)
    st.write('##')

    # ### Sales Data Metrics
    # # Total sale
    # total_sale = df_order['total'].sum()
    # # total_sale = '{:,.0f}'.format(total_sale)
    # st.metric('Tổng doanh thu (VNĐ)', total_sale)

    # # Total order
    # total_order = len(df_order['orderid'])
    # st.metric('Số lượng order', total_order)

    # # Total film
    # total_film = len(df_order['film'].unique())
    # st.metric('Số phim được chiếu', total_film)

    # ### Display data
    # showdata = st.checkbox("Display Data")
    # if showdata:
    #     st.dataframe(df_cust, use_container_width=True)



##### CUSTOMER DASHBOARD >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#### DATA PREPARING -------------------------->
### Customer Data
query_cust = 'SELECT * FROM Customer'
df_cust = pd.read_sql(query_cust, conn)
def extract_age(birthday):
    today = datetime.datetime.now().year
    age = today - birthday.year
    return age
df_cust['age'] = df_cust['DOB'].apply(extract_age)

### Order data
df_order = df_tick.drop_duplicates(subset=['orderid'])

### Sale data by customer
df_order_cust = pd.merge(df_order, df_cust, how='left', on='customerid')

#### CHARTS PREPARING -------------------------->
### Histogram: Age Distribution
def visualize_histogram_age():
    chart_histo_age = px.histogram(df_cust, 
                                x='age', 
                                title='Phân bố tuổi khách hàng',
                                labels={'age': 'Độ tuổi'},
                                color_discrete_sequence=[color_1],
                                height=445)
    chart_histo_age.update_layout(
                            # paper_bgcolor='rgb(255,255,255)',
                            # xaxis_title='Tuổi',
                            yaxis_title='Số lượng khách hàng',
                            bargap=0.1, 
                            # margin=dict(l=10, r=10, t=30, b=10),  
                            title_x=0.5,  
                            title_xanchor='center',
                            showlegend=False,) 
    st.plotly_chart(chart_histo_age, use_container_width=True)

### Pie chart Gender proportion
def visualize_pie_gender():
    df_gender = pd.DataFrame((df_cust['gender'].value_counts()/len(df_cust))*100).reset_index(False)
    color_mapping_gender = {
        # 'Nữ': '#ffc300',
        'Nữ': color_1,
        'Nam': color_2,
    }
    df_gender['color'] = df_gender['gender'].map(color_mapping_gender)

    chart_pie_gender = px.pie(df_gender, 
                            names='gender', 
                            values='count',
                            title='Tỉ lệ giới tính Khách hàng', 
                            color_discrete_sequence=df_gender['color'],
                            labels={'gender': 'Giới tính', 'count': 'Tỉ lệ'},
                            hole=0.4, 
                            height=225)
    chart_pie_gender.update_layout(
                            # paper_bgcolor='rgb(255,255,255)',
                            showlegend=False,
                            margin=dict(l=10, r=10, t=30, b=0),
                            autosize=False,
                            width=100,
                            title_x=0.5,
                            title_xanchor='center')
    chart_pie_gender.update_traces(text=df_gender['gender'], textposition='outside')
    st.plotly_chart(chart_pie_gender, use_container_width=True)

### Bar chart: number of customer by job and industry
def visualize_bar_jobindust(column, label, title_chart):
    df_jobindust = pd.DataFrame(df_cust[column].value_counts()).reset_index().sort_values(by='count', ascending=False)
    chart_bar_jobindust  = px.bar(x=df_jobindust[column], y=df_jobindust['count'], 
                                labels={'x': label, 'y': 'Số lượng khách hàng'},
                                color_discrete_sequence=[color_1],
                                title=title_chart,
                                height=415)
    chart_bar_jobindust.update_layout(
            # paper_bgcolor='rgb(255,255,255)',
            xaxis_title=label,
            yaxis_title='Số lượng khách hàng',
            title_x=0.5,
            title_xanchor='center',
            showlegend=False)
    st.plotly_chart(chart_bar_jobindust, use_container_width=True)

### Pareto chart: sales contribution by customer
def visualize_pareto_sales(number_of_customer):
    df_sale_cust_pareto = df_order_cust.copy()
    df_sale_cust_pareto = pd.DataFrame(df_sale_cust_pareto.groupby('customerid')['total'].sum()).reset_index().sort_values(by='total', ascending=False)

    # Calculate cumulative sum
    df_sale_cust_pareto['cumulative_sum'] = df_sale_cust_pareto['total'].cumsum()
    # Calculate total sum
    total_sum = df_sale_cust_pareto['total'].sum()
    # Calculate cumulative percentage
    df_sale_cust_pareto['cumulative_percentage'] = round((df_sale_cust_pareto['cumulative_sum'] / total_sum) * 100,2)

    # filter by number of customer to display
    df_sale_cust_pareto = df_sale_cust_pareto.head(number_of_customer)

    # bar chart for sales
    chart_pareto_sale = px.bar(df_sale_cust_pareto, x='customerid', y='total', 
                            title='Biểu đồ pareto doanh thu bởi khách hàng',
                            labels={'customerid': 'Mã khách hàng', 'total': 'Tổng chi tiêu'},
                            hover_data=['total'],
                            color_discrete_sequence=[color_1], 
                            height=488)

    
    # line chart for cumulative percentage
    chart_pareto_sale.add_scatter(x=df_sale_cust_pareto['customerid'], y=df_sale_cust_pareto['cumulative_percentage'], 
                        mode='lines', 
                        name='Phần trăm doanh thu tích lũy', 
                        yaxis='y2', 
                        line=dict(color=color_2), 
                        hoverinfo='y')
    
    chart_pareto_sale.update_layout(
                        yaxis2=dict(
                            title='Phần trăm doanh thu tích lũy',
                            overlaying='y', # important
                            side='right',
                            range=[0, df_sale_cust_pareto['cumulative_percentage'].head(number_of_customer).tail(1)]),
                        title_x=0.5,
                        title_xanchor='center',
                        xaxis_type='category', # making sure plotly interpret customerid as categorical data
                        showlegend=False,
                        # legend=dict(
                        #     yanchor="top",
                        #     xanchor="right", )
                        )
    st.plotly_chart(chart_pareto_sale, use_container_width=True)

#### DISPLAYING CUSTOMER DASHBOARD -------------------------->
with customer_db:
    st.markdown("<h3 style='text-align: center;'>Dashboard thông tin khách hàng tháng 5</h3>", unsafe_allow_html=True)
    st.write('##')

    ### Column1: metrics + pareto | Column2: pie histo filter bar
    column1, column2 = st.columns([4,6]) 

    with column2:
        # Column3: pie + histo | Column4: filter + bar
        column3, column4 = st.columns([5,5])
        with column4:
            # filter gender
            filter_gender = st.selectbox(label='Giới tính',options=('Tất cả','Nam','Nữ'), index=0)
            if filter_gender != 'Tất cả':
                df_cust = df_cust[df_cust['gender'] == filter_gender]
                df_order_cust = df_order_cust[df_order_cust['gender'] == filter_gender]

            # filter job industry bar
            filter_job_industry = st.selectbox(label='Biểu đồ cột: lọc dữ liệu',options=('Job','Industry'), index=1)
            
            # filter sale preto
            max_customer = len(df_order_cust['customerid'].unique())
            display_customer = st.number_input(f'Biểu đồ pareto: số lượng khách hiển thị (tối đa {max_customer})', 
                                        min_value= 5, max_value= max_customer, step = 1,
                                        value= 15)

            # Bar Chart: job and industry
            if filter_job_industry == 'Job':
                visualize_bar_jobindust('job', 'Nghề nghiệp', 'Số lượng khách hàng theo nghề nghiệp')
            else:
                visualize_bar_jobindust('industry', 'Lĩnh vực', 'Số lượng khách hàng theo lĩnh vực chuyên môn')

        with column3:
            # Pie chart: gender proportion
            visualize_pie_gender()
            # Histogram: age distribution
            visualize_histogram_age()


    ### Customer Data Metrics
    with column1:
        metric1, metric2 = st.columns([5,5])
        with metric1:
            total_customer = len(df_cust['customerid'].unique())
            st.metric('Tổng số Khách hàng', total_customer)
        
        with metric2:
            average_age = round(df_cust['age'].mean())
            # total_sale = '{:,.0f}'.format(total_sale)
            st.metric('Độ tuổi trung bình', average_age)
        
        # Metric: average spending
        df_sale_metric = pd.DataFrame(df_order_cust.groupby('customerid')['total'].sum()).reset_index().sort_values(by='total', ascending=False)
        average_spending = round(df_sale_metric['total'].median())
        st.metric('Mức chi tiêu trung bình trong tháng',average_spending)


        # Pareto chart: sales
        visualize_pareto_sales(display_customer)

with about:
    st.header("👑 BY KING HENRY 👑")





        
    






