FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies + FreeTDS for SQL Server 2008 R2
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    freetds-dev \
    tdsodbc \
    && rm -rf /var/lib/apt/lists/*

# Register FreeTDS as ODBC driver
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" > /etc/odbcinst.ini

# Configure FreeTDS for SQL Server 2008 R2
RUN echo "[global]\n\
tds version = 7.2\n\
client charset = UTF-8\n\
text size = 20971520" > /etc/freetds/freetds.conf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
