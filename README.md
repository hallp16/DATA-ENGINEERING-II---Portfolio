# Brazilian Traffic Incidents - Data Engineering Pipeline

Batch data pipeline for processing Brazilian traffic accident data (~1.8M records).

## Dataset
- **Source:** [Kaggle – Brazilian Traffic Incidents (2007–2023)](https://www.kaggle.com/datasets/pedrogoncalv/brazilian-traffic-incidents-2007-to-2023)

## Architecture
- *Ingestion:* Python (Pandas) - loads raw CSV data into PostgreSQL
- *Storage:* PostgreSQL - stores raw data and analytics tables
- *Processing:* Apache Spark (PySpark) - data cleaning and aggregation

## Quick Start

```
bash
# 1. Setup environment
cp .env.example .env

# 2. Start database & ingestion
docker-compose up --build -d

# 3. Run Spark transformation
docker-compose run -u root --rm spark_processing /opt/spark/bin/spark-submit --packages org.postgresql:postgresql:42.7.13 /app/process_data.py
```

## Results
- *~1.8M records processed*
- *Analytics table*: analytics_state_yearly (accidents, deaths, injuries per state/year)

## Repository Structure
- *ingestion/* - Python ingestion service
- *spark_job/* - PySpark processing script
- *docker-compose.yml* - Container orchestration
