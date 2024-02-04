import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns 
import matplotlib.pyplot as plt
import pyodbc
import streamlit as st
import datetime 
import smtplib
from email.mime.text import MIMEText

###### STREAMLIT SETTINGS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
st.set_page_config(layout = 'wide', page_title='Cinema Dashboard', page_icon='🍿')
# st.markdown("""
#     <style>
#         .reportview-container {
#             margin-top: -2em;
#         }
#         #MainMenu {visibility: hidden;}
#         .stDeployButton {display:none;}
#         footer {visibility: hidden;}
#         #stDecoration {display:none;}
#     </style>
# """, unsafe_allow_html=True)
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
    # Connect to the database
    conn = pyodbc.connect(conn_str)

except Exception as e:
    error_info = str(e)
    print(error_info)

    reciever_emails = ['huynhthong02042002@gmail.com', 'trungthien0503@gmail.com','anhvi09042002@gmail.com','tuan.tn01012002@gmail.com']
    sender_gmail = st.secrets["sender_gmail"]
    sender_apppass = st.secrets["sender_apppass"]
    subject = st.secrets["subject"]
    message = f'Streamlit App IP updated. \n Error details: {str(error_info)}'

    def sendemail(sender_gmail, sender_apppass, reciever, subject, message):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender_gmail
        msg['To'] = reciever

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_gmail, sender_apppass)
        server.sendmail(sender_gmail, reciever, msg.as_string())
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

### Cutomer Data
query_cust = 'SELECT * FROM Customer'
df_cust = pd.read_sql(query_cust, conn)

### Ticket Data
query_tick = 'SELECT * FROM Ticket'
df_tick = pd.read_sql(query_tick, conn)
df_tick = pd.merge(df_tick, df_cust, how='left', on='customerid')
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
def visualize_line_salebyweekandhour(week):
    df_sale_time = df_order.copy()
    # preparing data
    df_sale_time['showtime'] = pd.to_datetime(df_sale_time['showtime'])

    # filtering
    week_title = 'tất cả các tuần'
    if week != 'Tất cả các tuần':
        week_title = f'tuần {week}'

    df_visualize_salebyweek = pd.DataFrame(df_sale_time.groupby(['hour','dayinweek'])['total'].sum()).reset_index()

    # coloring
    # color_mapping_day = ['#FCA311', '#D58D18', '#AF7820','#886227', '#614C2E','#3B3736', '#14213D']
    color_mapping_day = ['#FCA311', '#B59245', '#4B7794','#0466C8', '#0952A0','#0F3565', '#14213D']
    dict_color = {}
    for ind, date in enumerate(df_visualize_salebyweek['dayinweek'].unique()):
        dict_color[date] = color_mapping_day[ind]

    chart_line_salesbyweekandhour = px.line(df_visualize_salebyweek,
                    x="hour",
                    y="total",
                    labels={'hour': 'Khung giờ', 'total': 'Doanh thu', 'dayinweek': 'Ngày trong tuần'},
                    title=f'Doanh thu của {week_title} theo khung giờ',
                    color="dayinweek",
                    color_discrete_map=dict_color,
                    markers = True,
                    # width=700,
                    height=400)
    chart_line_salesbyweekandhour.update_layout(
                                        # paper_bgcolor='rgb(255,255,255)',
                                        margin=dict(l=0, r=10, t=40, b=30),
                                        xaxis=dict(tickmode='linear', dtick=2),
                                        title_x=0.5,
                                        title_xanchor='center')

    
    st.plotly_chart(chart_line_salesbyweekandhour, use_container_width=True)


def visualize_pareto(column, number_to_display, title, x_label, y_label, y2_label):
    df_pareto = df_order.copy()

    df_pareto = pd.DataFrame(df_pareto.groupby(column)['total'].sum()).reset_index().sort_values(by='total', ascending=False)

    # Calculate cumulative sum
    df_pareto['cumulative_sum'] = df_pareto['total'].cumsum()
    # Calculate total sum
    total_sum = df_pareto['total'].sum()
    # Calculate cumulative percentage
    df_pareto['cumulative_percentage'] = (df_pareto['cumulative_sum'] / total_sum) * 100
    df_pareto = df_pareto.head(number_to_display)

    # bar chart for sales
    chart_pareto_sale = px.bar(df_pareto, x=column, y='total', 
                            title=title,
                            labels={column: x_label, 'total': y_label},
                            hover_data=['total'],
                            color_discrete_sequence=[color_1], 
                            height=600)
        # line chart for cumulative percentage
    chart_pareto_sale.add_scatter(x=df_pareto[column], y=df_pareto['cumulative_percentage'], 
                        mode='lines', 
                        name='Phần trăm doanh thu tích lũy', 
                        yaxis='y2', 
                        line=dict(color=color_2), 
                        hoverinfo='y')
    
    chart_pareto_sale.update_layout(
                        yaxis2=dict(
                            title=y2_label,
                            overlaying='y', # important
                            side='right',
                            range=[0, df_pareto['cumulative_percentage'].head(number_to_display).tail(1)]),
                        title_x=0.5,
                        title_xanchor='center',
                        xaxis_type='category', # making sure plotly interpret customerid as categorical data
                        showlegend=False,
                        # legend=dict(
                        #     yanchor="top",
                        #     xanchor="right", )
                        )
    st.plotly_chart(chart_pareto_sale, use_container_width=True)


def visualize_line_salebydate():
    df_sale_by_date = df_order.sort_values(by= 'saledate')
    df_sale_by_date['date'] = df_sale_by_date['date'].astype(str)
    df_sale_by_date = df_sale_by_date.groupby('date')['total'].sum().reset_index()

    # color_mapping_price = {'Sealand': '#ffc300', 'Non-Sealand': '#0466c8'}

    chart_line_sale = px.line(df_sale_by_date,
                    x="date",
                    y="total",
                    title='Doanh thu theo các ngày trong tháng 5',
                    markers = True,
                    # width=700,
                    height=400,
                    labels={'date': 'Ngày', 'total':'Doanh thu'})
    chart_line_sale.update_traces(line_color= color_2, line_width=3)
    chart_line_sale.update_layout(title_x=0.5, 
                                  title_xanchor='center',
                                #   paper_bgcolor='rgb(255,255,255)',
                                  margin=dict(l=0, r=10, t=40, b=30),
                                  xaxis_type='category',
                                  xaxis=dict(tickmode='linear', dtick=2))
    st.plotly_chart(chart_line_sale, use_container_width=True)
    

def visualize_pie(column, chart_title):
    pie_ratio = round((df_tick[column].value_counts()/len(df_tick))*100,2)
    df_pie = pd.DataFrame(pie_ratio).reset_index().sort_values(by='count', ascending=False)

    list_color = [color_1, color_2]
    # df_pie['color'] = df_pie[column].map(list_)

    chart_pie = px.pie(df_pie, 
                        names=column, 
                        values='count',
                        title=chart_title,
                        # color = column, 
                        color_discrete_sequence= list_color,
                        hole=0.4, 
                        height=320)

    chart_pie.update_layout(showlegend=False,
                                # paper_bgcolor='rgb(255,0,255)',
                                margin=dict(l=0, r=10, t=70, b=40),
                                title_x=0.5,
                                title_xanchor='center',
                                autosize=False,
                                width=300)
    chart_pie.update_traces(text=df_pie[column], textposition='outside')

    st.plotly_chart(chart_pie, use_container_width=True)


### Histogram: Seat row distribution
def visualize_histogram_seat():
    df_seat = df_tick.copy()
    def extract_seatrow(data):
        return data[:1]

    # extract seat_row
    df_seat['seat_row'] = df_seat['slot'].apply(extract_seatrow)
    df_seat = df_seat.sort_values(by='seat_row')
    
    chart_histo_seat = px.histogram(df_seat, 
                                x='seat_row', 
                                title='Phân bố số lượng vé ở mỗi hàng ghế',
                                labels={'seat_row': 'Hàng ghế'},
                                color_discrete_sequence=[color_1],
                                height=400)
    chart_histo_seat.update_layout(
                            # paper_bgcolor='rgb(255,255,255)',
                            # margin=dict(l=10, r=10, t=30, b=0), 
                            # xaxis_title='Tuổi',
                            yaxis_title='Số lượng vé',
                            bargap=0.1,  
                            title_x=0.55,  
                            title_xanchor='center',
                            showlegend=True,) 
    st.plotly_chart(chart_histo_seat, use_container_width=True)
    
def visualize_pie_room():
    df_sale_by_room = df_order.copy()
    df_sale_by_room = df_sale_by_room.groupby('room')['total'].sum().reset_index().sort_values(by='total', ascending=False)

    color_mapping_room = ['#14213D', '#614C2E', '#AF7820', '#FCA311']

    # Convert 'room' column to categorical
    df_sale_by_room['room'] = pd.Categorical(df_sale_by_room['room'])
    df_sale_by_room['proportion'] = (df_sale_by_room['total']/sum(df_sale_by_room['total']))*100

    # chart_bar_room = px.bar(
    #     df_sale_by_room,
    #     x='room',
    #     y='total',
    #     color='room',  # Set the color parameter to the 'room' column
    #     color_discrete_sequence=color_mapping_room,  # Specify the color sequence
    #     labels={'room': 'Phòng', 'total': 'Doanh thu'},
    #     title='Doanh thu theo các phòng chiếu',
    #     height=475
    # )
    # chart_bar_room.update_layout(
    #     title_x=0.5,
    #     title_xanchor='center',
    #     xaxis_type='category'
    # )

    # st.plotly_chart(chart_bar_room, use_container_width=True)

    chart_pie_room = px.pie(df_sale_by_room, 
                        names='room', 
                        values='proportion',
                        title='Doanh thu theo phòng chiếu',
                        labels = {'room': 'Phòng chiếu', 'proportion': 'Phần trăm doanh thu'},
                        # color = column, 
                        color_discrete_sequence = color_mapping_room,
                        hole=0.4, 
                        height=320)

    chart_pie_room.update_layout(showlegend=True,
                                # paper_bgcolor='rgb(255,0,255)',
                                margin=dict(l=0, r=10, t=70, b=40),
                                title_x=0.5,
                                title_xanchor='center',
                                autosize=False,
                                width=300,
                                )
    chart_pie_room.update_traces(text=df_sale_by_room['room'], textposition='outside')

    st.plotly_chart(chart_pie_room, use_container_width=True)

#### DISPLAYING SALES DASHBOARD  -------------------------->
with sale_db:
    st.markdown("<h3 style='text-align: center;'>Dashboard doanh thu tháng 5</h3>", unsafe_allow_html=True)

    metric, filter_pie = st.columns([4.5,5.5]) 

    with filter_pie:
        # Column3: pie + histo | Column4: filter + bar
        pie, all_filters = st.columns([6,4])
        with all_filters:
            # MULTIPLE EFFECT FIlTER: week
            list_week = sorted(list(df_order['weekinyear'].unique()))
            list_week.insert(0, 'Tất cả các tuần')
            filter_week = st.selectbox('Tuần',list_week, index = 0)
            if filter_week != 'Tất cả các tuần':
                df_tick = df_tick[df_tick['weekinyear'] == filter_week]
                df_order = df_tick.drop_duplicates(subset=['orderid'])

            st.write('---')
            # SINGLE EFFECT FILTER: measurement for pie chart
            measurements_pie = ['Slot type', 'Ticket Type']
            filter_slot_for_ticket = st.selectbox('Biểu đồ tròn: lọc dữ liệu', measurements_pie, index = 0)


            # SINGLE EFFECT FILTER: measurement for pareto
            measurements_pareto = ['Film', 'Khách hàng', 'Job', 'Industry']
            filter_slot_or_ticket = st.selectbox('Biểu đồ Pareto: lọc dữ liệu', measurements_pareto, index = 0)
            list_columns = ['film', 'customerid', 'job', 'industry']
            column_for_pareto = list_columns[measurements_pareto.index(filter_slot_or_ticket)]

        with pie:
            # PIE: Slot type and Ticket_type ratio
            if filter_slot_for_ticket == 'Slot type':
                visualize_pie(column= 'slot_type', chart_title= 'Tỉ lệ vé của các loại ghế')
            else:
                visualize_pie(column= 'ticket_type', chart_title= 'Tỉ lệ vé của thành viên')

        visualize_line_salebyweekandhour(week = filter_week)
        # PARETO: film, industry, job
        visualize_pareto(column= column_for_pareto, 
                        number_to_display= 15, 
                        title= f'Doanh thu tích lũy theo {filter_slot_or_ticket}', 
                        x_label= filter_slot_or_ticket,
                        y_label= 'Doanh thu',
                        y2_label= 'Tích lũy doanh thu')
        
        
    with metric:
        metric1, metric2 = st.columns([7,3])
        with metric1:
            # Total sale
            total_sale = df_order['total'].sum()
            total_sale = '{:,.0f}'.format(total_sale)
            st.metric('Tổng doanh thu (VNĐ)', total_sale)
        with metric2:
            # Total film
            total_film = len(df_order['film'].unique())
            st.metric('Số phim được chiếu', total_film)

        # Total order
        total_order = len(df_order['orderid'])
        st.metric('Số lượng order', total_order)

        # LINE: sale by date
        visualize_line_salebydate()

        # HISTOGRAM: seat
        visualize_histogram_seat()

        # PIE: sales by room
        visualize_pie_room()





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





        
    






