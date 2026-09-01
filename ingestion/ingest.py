import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text

# log function to see the progress on terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_ingestion():
            
    # read credentials from env    
    db_user = os.getenv("DB_USER", "admin")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "postgres_db")
    db_name = os.getenv("DB_NAME", "traffic_db")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    engine = create_engine(db_url)

    csv_path = "/app/data/brazilian_traffic.csv"
    logging.info("Starting batch ingestion process into PostgreSQL...")    
    
    # always fresh start; ensures idempotency 
   
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS raw_traffic;"))
            conn.commit()
            logging.info("Clean slate: Dropped old 'raw_traffic' table if it existed.")
    except Exception as e:
        logging.warning(f"Could not drop existing table: {e}")
   
    # load data in smaller batches to avoid memory issues        
   
    chunk_size = 10000
    total_rows = 0

    try:
         # load all columns as text first to avoid type errors; bronze layer approach
        for chunk in pd.read_csv(
            csv_path, 
            encoding="utf-8", 
            sep=";",             
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