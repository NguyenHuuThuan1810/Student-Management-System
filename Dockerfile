# 1. Sử dụng Python bản lightweight làm nền
FROM python:3.10-slim

# 2. Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# 3. Cài đặt các thư viện hệ thống cần thiết (nếu mysql-connector cần build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy file requirements.txt vào trước để tối ưu hóa cache
COPY requirements.txt .

# 5. Cài đặt các thư viện Python (Flask, mysql-connector-python,...)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy toàn bộ mã nguồn của dự án vào container
COPY . .

# 7. Mở cổng 5000 (cổng chạy Flask mặc định)
EXPOSE 5000

# 8. Lệnh chạy ứng dụng khi container khởi động
CMD ["python", "main.py"]