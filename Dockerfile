FROM apache/airflow:3.1.5

USER root

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*



USER airflow

WORKDIR /opt/airflow

COPY requirements.txt .

RUN pip install -r requirements.txt

