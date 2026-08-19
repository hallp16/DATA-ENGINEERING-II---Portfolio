import os
import logging
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Setup logging output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_spark_job():
    logging.info("Starting Apache Spark transformation job...")

    # ---------------------------------------------------------
    # 1. Initialize Spark Session
    # Using PySpark to demonstrate horizontal scalability for large datasets.
    # ---------------------------------------------------------
    spark = SparkSession.builder \
        .appName("BrazilianTrafficAnalytics") \
        .getOrCreate()

    # Load connection details from environment variables
    db_user = os.environ.get("DB_USER", "admin")
    db_password = os.environ.get("DB_PASSWORD", "masterpassword123")
    db_host = os.environ.get("DB_HOST", "postgres_db")
    db_name = os.environ.get("DB_NAME", "traffic_db")
    
    jdbc_url = f"jdbc:postgresql://{db_host}:5432/{db_name}"
    connection_properties = {
        "user": db_user,
        "password": db_password,
        "driver": "org.postgresql.Driver"
    }

    # ---------------------------------------------------------
    # 2. EXTRACT (Bronze Layer)
    # Read the raw text data directly from the PostgreSQL database via JDBC
    # ---------------------------------------------------------
    logging.info("Reading raw text data from PostgreSQL table 'raw_traffic'...")
    df_raw = spark.read.jdbc(url=jdbc_url, table="raw_traffic", properties=connection_properties)

    # ---------------------------------------------------------
    # 3. TRANSFORM (Silver Layer - Data Cleansing & Schema Casting)
    # Convert string columns into real analytical types (Dates, Integers)
    # and filter out invalid/corrupted records.
    # ---------------------------------------------------------
    logging.info("Applying schema casting and cleansing rules...")
    
    df_clean = df_raw.withColumn("data_inversa", F.to_date(F.col("data_inversa"), "yyyy-MM-dd")) \
                     .withColumn("mortos", F.col("mortos").cast("integer")) \
                     .withColumn("feridos", F.col("feridos").cast("integer"))
                     
    # Safety filter: remove rows without a valid parsed date
    df_clean = df_clean.filter(F.col("data_inversa").isNotNull())

    # ---------------------------------------------------------
    # 4. BUSINESS LOGIC & AGGREGATION (Gold Layer)
    # Business Question: How many accidents, fatalities, and injuries 
    # occurred per state (UF) and per year?
    # ---------------------------------------------------------
    logging.info("Computing business aggregations (Accidents & Casualties by State/Year)...")
    
    df_analytics = df_clean.withColumn("year", F.year(F.col("data_inversa"))) \
                           .groupBy("uf", "year") \
                           .agg(
                               F.count("*").alias("total_accidents"),
                               F.sum("mortos").alias("total_deaths"),
                               F.sum("feridos").alias("total_injuries")
                           )

    # ---------------------------------------------------------
    # 5. LOAD (Gold Layer Export)
    # Write the high-value analytics table back into PostgreSQL for BI dashboards
    # ---------------------------------------------------------
    logging.info("Writing final Gold table 'analytics_state_yearly' to PostgreSQL...")
    df_analytics.write.jdbc(
        url=jdbc_url, 
        table="analytics_state_yearly", 
        mode="overwrite", 
        properties=connection_properties
    )

    logging.info("Spark transformation completed successfully!")
    spark.stop()

if __name__ == "__main__":
    run_spark_job()