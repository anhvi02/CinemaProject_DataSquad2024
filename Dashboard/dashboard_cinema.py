import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns 
import matplotlib.pyplot as plt
import pyodbc
import streamlit as st
import datetime 
import smtplib

###### STREAMLIT SETTINGS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
st.set_page_config(layout = 'wide', page_title='Cinema Dashboard', page_icon='🍿')
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
color_1 = '#14213d'
# 14213d: xanh ghi
# fb6f92: vang
color_2 = '#fca311'
# a3b18a
#fca311: vang



##### DATABASE CONNECTING >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Connection details
try:
    server = st.secrets["server"]
    database = st.secrets["database"]
    username = st.secrets["username"]
    password = st.secrets["password"]
    driver = st.secrets["driver"] 

    # Connection string
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    # st.write(conn_str)
    # Connect to the database
    conn = pyodbc.connect(conn_str)

except Exception as e:
    reciever_emails = ['huynhthong02042002@gmail.com', 'trungthien09503@gmail.com','anhvi09042002@gmail.com']
    sender_gmail = st.secrets["sender_gmail"]
    sender_apppass = st.secrets["sender_apppass"]
    subject = st.secrets["subject"]
    message = st.secrets["message"]

    def sendemail(sender_gmail, sender_apppass, reciever, subject, message):
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()

        server.login(sender_gmail,sender_apppass)
        server.sendmail(sender_gmail, reciever,f'Subject: {subject}\n{message}')
        server.quit()
        print(f'Mail sent to {reciever}') 

    for mail in reciever_emails:
        sendemail(sender_gmail, sender_apppass, mail, subject, message)


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
df_tick['showtime'] = pd.to_datetime(df_tick['showtime'])

def extract_week(data):
    data = data.isocalendar()[1]
    return data

df_tick['date'] = df_tick['showtime'].dt.date
df_tick['hour'] = df_tick['showtime'].dt.hour
df_tick['weekinyear'] = df_tick['showtime'].apply(extract_week)
df_tick['dayinweek'] = df_tick['showtime'].dt.day_name()

### Order Data
df_order = df_tick.drop_duplicates(subset=['orderid'])

#### CHART PREPRARING  -------------------------->
# LINE CHART: sales by day in week
def visualize_line_salesbywwek():
    df_sale_time = df_order.copy()
    
    # week = []
    # # Extract date and hour from 'showtime'
    # for ele in  df_sale_time['showtime']:
    #     week.append(ele.isocalendar()[1])
    # df_sale_time['dayinweek'] = df_sale_time['showtime'].dt.day_name()
    # df_sale_time['weekinyear'] = week

    sale_by_dayinweek = pd.DataFrame(df_sale_time.groupby(['dayinweek','weekinyear'])['total'].sum()).reset_index()
    # Mapping days of the week to numbers
    day_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

    sale_by_dayinweek['numbered_dayinweek']=sale_by_dayinweek['dayinweek'].map(day_mapping)
    sale_by_dayinweek  = sale_by_dayinweek.sort_values(by='numbered_dayinweek')

    # color_mapping_price = {'Sealand': '#ffc300', 'Non-Sealand': '#0466c8'}

    chart_line_salesbyweek = px.line(sale_by_dayinweek,
                    x="dayinweek",
                    y="total",
                    labels={'dayinweek': 'Thứ', 'weekinyear':'Tuần', 'total': 'Doanh thu'},
                    title='Averge price per night changes over time',
                    color="weekinyear",
                    # color_discrete_map=color_mapping_price,
                    # width=700,
                    height=430,)
    chart_line_salesbyweek.update_layout(title_x=0.3,
                        title_xanchor='center')
    st.plotly_chart(chart_line_salesbyweek, use_container_width=True)



def visualize_line_salebyweekandhour(week = 0):
    df_sale_time = df_order.copy()
    df_sale_time['showtime'] = pd.to_datetime(df_sale_time['showtime'])


    if week != 0:
        df_sale_time = df_sale_time[df_sale_time['weekinyear'] == week]

    df_visualize_salebyweek = pd.DataFrame(df_sale_time.groupby(['hour','dayinweek'])['total'].sum()).reset_index()
    chart_line_salesbyweekandhour = px.line(df_visualize_salebyweek,
                    x="hour",
                    y="total",
                    labels={'hour': 'Khung giờ', 'total': 'Doanh thu'},
                    title=f'Doanh thu của tuần {week} theo khung giờ',
                    color="dayinweek",
                    # color_discrete_map=color_mapping_price,
                    # width=700,
                    height=430,)
    chart_line_salesbyweekandhour.update_layout(title_x=0.3,
                        title_xanchor='center')
    
    st.plotly_chart(chart_line_salesbyweekandhour, use_container_width=True)




#### DISPLAYING SALES DASHBOARD  -------------------------->
with sale_db:
    st.markdown("<h3 style='text-align: center;'>Dashboard doanh thu tháng 5</h3>", unsafe_allow_html=True)

    column1, column2 = st.columns([5,5])
    with column1:
        
        list_week = list(df_order['showtime'].apply(extract_week).unique())
        list_week.insert(0, 'Tất cả các tuần')
        filter_week = st.selectbox('Tuần',list_week, index = 0)
        if filter_week != 'Tất cả các tuần':
            visualize_line_salebyweekandhour(week = filter_week)
        else:
            visualize_line_salebyweekandhour()
        
        

    ### Sales Data Metrics
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
            default_customer = 15
            if max_customer < 15:
                default_customer = max_customer -1
            display_customer = st.number_input(f'Biểu đồ pareto: số lượng khách hiển thị (tối đa {max_customer})', 
                                        min_value= 5, max_value= max_customer, step = 1,
                                        value= default_customer)

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





        
    






