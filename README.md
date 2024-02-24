# DỰ ÁN: PHÂN TÍCH DỮ LIỆU RẠP PHIM
Với bộ dữ liệu về một rạp phim được cung cấp bởi ban tổ chức cuộc thi Data GotTalent 2024, đội ngũ DataSquad đã xử lý, phân tích và đưa ra những đề xuất nhằm tối ưu hóa hoạt động kinh doanh.  
Bên cạnh đó, DataSquad còn xây dựng một database với nền tảng Azure nhằm lưu trữ dữ liệu cùng với một data pipeline để thực hiện quá trình ETL bao gồm extract dữ liệu từ file spreadsheet, transform dữ liệu và load vào database.  
Sau cùng, một dashboard được xây dựng với Streamlit để báo cáo kinh doanh.

# WORKFLOW
![alt text] ([https://github.com/anhvi02/CinemaProject_DataSquad2024/blob/main/workflow.png?raw=true](https://raw.githubusercontent.com/anhvi02/CinemaProject_DataSquad2024/main/workflow.png))

# FILE DESCRIPTION
1. analysis_cinema.ipynb:
    - Giai đoạn 1: Làm sạch và khám phá dữ liệu
    - Giai đoạn 2: Nạp dữ liệu
        + Tạo server, database trên Azure:
            * Sử dụng pyodbc để connect db trên azure
            * Thiết kế database: Cấu hình các trường dữ liệu, tạo ràng buộc(FK) giữa các bảng.
            * Đẩy dữ liệu lên database
    - Giai đoạn 3: Phân tích dữ liệu
        + Phân tích doanh thu
        + Phân tích khách hàng
2. dashboard_cinema.py
    - Sales dashboard
    - Customer dashboard
    - Giới thiệu
3. report_cinema.pdf
    - Tổng hợp nội dung phân tích
    - Tiền xử lý và khám phá dữ liệu
    - Phân tích dữ liệu
4. cleaned_data_cinema.xlsx
    - Customer
    - Ticket
    - Film
5. requirements.txt
    - Môi trường để lập trình

# Thành viên
1. Phạm Anh Vĩ
    - Xây dựng database và data pipeline
    - Xây dựng dashboard
    - Phân tích dữ liệu
    - Quản lý dự án
2. Phù Trung Thiện
    - Phân tích dữ liệu
    - Data storytelling
3. Huỳnh Thông
    - Khám phá, tiền xử lý dữ liệu
    - Phân tích dữ liệu
4. Trần Ngọc Tuấn
    - Phân tích dữ liệu
    - Tiền xử lý dữ liệu
