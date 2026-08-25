FROM python:3.9.18-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingest.py .
COPY data_preparation.py .

# Data preparation runs FIRST, then ingestion
CMD ["sh", "-c", "python data_preparation.py && python ingest.py"]