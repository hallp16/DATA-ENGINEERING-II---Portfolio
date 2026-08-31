import os
import logging
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# setup logs output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_spark_job():
    logging.info("Starting Apache Spark transformation job...")
       
    spark = SparkSession.builder \
        .appName("BrazilianTrafficAnalytics") \
        .getOrCreate()

    # load credentials from env
    db_user = os.environ.get("DB_USER", "admin")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST", "postgres_db")
    db_name = os.environ.get("DB_NAME", "traffic_db")
    
    jdbc_url = f"jdbc:postgresql://{db_host}:5432/{db_name}"
    connection_properties = {
        "user": db_user,
        "password": db_password,
        "driver": "org.postgresql.Driver"
    }    
   
    logging.info("Reading raw text data from PostgreSQL table 'raw_traffic'...")
    df_raw = spark.read.jdbc(url=jdbc_url, table="raw_traffic", properties=connection_properties)

    # conversion of str column to adequate types;
    #rows without a valid date are dropped, as this is part of the cleaning process   
    
    logging.info("Applying schema casting and cleansing rules...")
    
    df_clean = df_raw.withColumn("data_inversa", F.to_date(F.col("data_inversa"), "yyyy-MM-dd")) \
                     .withColumn("mortos", F.col("mortos").cast("integer")) \
                     .withColumn("feridos", F.col("feridos").cast("integer"))           
   
    df_clean = df_clean.filter(F.col("data_inversa").isNotNull())  
    # usecase: how many accidents, deaths, and injuries per state and year?
   
    logging.info("Computing business aggregations (Accidents & Casualties by State/Year)...")
    
    df_analytics = df_clean.withColumn("year", F.year(F.col("data_inversa"))) \
                           .groupBy("uf", "year") \
                           .agg(
                               F.count("*").alias("total_accidents"),
                               F.sum("mortos").alias("total_deaths"),
                               F.sum("feridos").alias("total_injuries")
                           )
    
    # Write the analytics table back to PostgreSQL
    
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