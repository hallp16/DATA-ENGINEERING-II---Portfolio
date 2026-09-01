# Brazilian Traffic Incidents – Data Engineering Portfolio Project

Master's Portfolio Project – Data Engineering

Batch data pipeline for processing Brazilian traffic accident data (~2 million records).

## Dataset
- **Source:** [Kaggle – Brazilian Traffic Incidents (2007–2023)](https://www.kaggle.com/datasets/pedrogoncalv/brazilian-traffic-incidents-2007-to-2023)
- **Files:** 17 annual CSV files (`Dados_PRF_2007.csv` to `Dados_PRF_2023.csv`)

## Architecture
- **Data Preparation:** Python (Pandas) – automatic consolidation of 17 CSV files with Latin-1 encoding (runs inside the container on startup)
- **Ingestion:** Python (Pandas + SQLAlchemy) – chunked CSV reading with idempotent full-reload pattern (`DROP` + batch `INSERT`)
- **Storage:** PostgreSQL – stores raw data (`raw_traffic`) and analytics tables (`analytics_state_yearly`)
- **Processing:** Apache Spark (PySpark) – schema casting, null-cleansing, and aggregations
- **Reproducibility:** Pinned Docker base images (`python:3.9.18-slim`, `postgres:14.12`, `apache/spark:3.5.1`)

## Architecture Diagram

<img width="8192" height="1502" alt="Brazilian Traffic Incident batch project" src="https://github.com/user-attachments/assets/1ffb1911-8b31-4deb-ad1f-d0b856359617" />


## Repository Structure

```text
DATA-ENGINEERING-II---Portfolio/
├── data/                              # Raw Kaggle CSV files (git-ignored)
│   └── Dados_PRF_*.csv                # 17 annual CSV files (2007-2023)
├── ingestion/                         # Data consolidation & ingestion service
│   ├── Dockerfile                     # Python 3.9.18-slim container definition
│   ├── ingest.py                      # Batch ingestion worker (Pandas + SQLAlchemy)
│   ├── data_preparation.py            # Merges 17 CSV files into one dataset
│   └── requirements.txt               # Python dependencies
├── init_db/                           # DB init scripts
│   └──roles.sql                      # Creates read-only ml_reader role
├── spark_job/                         # PySpark transformation & aggregation
│   └── process_data.py                # Data cleaning, null-filtering & Gold-layer aggregation
├── .env.example                       # Template for database environment variables
├── .gitignore                         # Excludes .env, *.csv, and Python cache
├── docker-compose.yml                 # Multi-container orchestration (PostgreSQL, Ingestion, Spark)
└── README.md                          # Project documentation

``` 

## Quick Start
### 1. Environment Setup 
```bash
# Copy environment configuration
cp .env.example .env
```

### 2. Prepare Data
```bash
# Create the data folder if it doesn't exist
mkdir -p data

# Place the 17 downloaded Kaggle CSV files (Dados_PRF_*.csv) inside the data/ folder.
# The ingestion container will automatically consolidate and format them on startup.
```

### 3. Start Storage & Ingestion
```bash
# Build and run PostgreSQL and the automated Ingestion service
docker-compose up --build -d

# Follow container logs to observe automated CSV consolidation and batch ingestion progress.
# Loads ~2 million records in PostgreSQL, may take some minutes, please wait completion.
docker logs -f traffic_ingestion

```

### 4. Run Spark Processing
```bash
# Execute PySpark batch transformation (Silver & Gold Layer)
docker-compose run -u root --rm spark_processing /opt/spark/bin/spark-submit --packages org.postgresql:postgresql:42.7.13 /app/process_data.py
```

### 5. Verify Analytics Results
```bash
# Default credentials from .env.example; adjust if you changed DB_USER/DB_NAME in your .env
docker-compose exec postgres_db psql -U admin -d traffic_db -c "SELECT * FROM analytics_state_yearly ORDER BY total_accidents DESC LIMIT 10;"
```

## Results
- **2,013,757** raw records ingested; rows with invalid or missing timestamps were filtered during Silver-layer cleansing prior to aggregation.
- **Analytics table:** analytics_state_yearly (aggregations of accidents, fatalities, and injuries grouped by state and year).

