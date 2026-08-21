import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text

# Setup basic logging to see container progress in the terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_ingestion():
    # ---------------------------------------------------------
    # 1. Configuration & Security
    # Read database credentials from environment variables (.env)
    # instead of hardcoding passwords directly in the script.
    # ---------------------------------------------------------
    db_user = os.getenv("DB_USER", "admin")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "postgres_db")
    db_name = os.getenv("DB_NAME", "traffic_db")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    engine = create_engine(db_url)

    csv_path = "/app/data/brazilian_traffic.csv"
    logging.info("Starting batch ingestion process into PostgreSQL...")

    # ---------------------------------------------------------
    # 2. Idempotency Pattern
    # Drop the table before loading if it already exists.
    # This prevents accidental row duplication if the container restarts.
    # ---------------------------------------------------------
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS raw_traffic;"))
            conn.commit()
            logging.info("Clean slate: Dropped old 'raw_traffic' table if it existed.")
    except Exception as e:
        logging.warning(f"Could not drop existing table: {e}")

    # ---------------------------------------------------------
    # 3. Memory-Safe Chunking & ELT Loading
    # - chunksize=10000: Loads data in small batches to protect RAM (prevents OOM crashes)
    # - decimal=",": Converts Brazilian decimal commas into international dots
    # - dtype=str: Critical Data Engineering fix! Loads all raw columns as text (Bronze layer).
    #   This avoids crashes when a column contains unexpected text values (e.g. 'SPRF-MG').
    # ---------------------------------------------------------
    chunk_size = 10000
    total_rows = 0

    try:
        for chunk in pd.read_csv(
            csv_path, 
            encoding="utf-8", 
            sep=";", 
            decimal=",", 
            dtype=str, 
            chunksize=chunk_size
        ):
            # Append each chunk to the PostgreSQL table
            chunk.to_sql("raw_traffic", engine, if_exists="append", index=False)
            total_rows += len(chunk)
            logging.info(f"Loaded {total_rows:,} rows into PostgreSQL...")

        logging.info("Batch Ingestion completed successfully!")

    except FileNotFoundError:
        logging.error(f"Error: The dataset '{csv_path}' was not found in the container volume!")
    except Exception as e:
        logging.error(f"Ingestion failed with error: {str(e)}")

if __name__ == "__main__":
    run_ingestion()