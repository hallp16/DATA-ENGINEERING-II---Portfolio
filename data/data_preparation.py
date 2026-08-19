import os
import glob
import pandas as pd

# ---------------------------------------------------------
# Step 1: Directory Setup
# Ensure the script runs in its current folder so it reliably
# finds the downloaded CSV files regardless of where it is executed.
# ---------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Find all annual Brazilian traffic files (Dados_PRF_*.csv)
file_list = sorted(glob.glob("Dados_PRF_*.csv"))
print(f"Found {len(file_list)} raw yearly files. Starting data consolidation...")

dataframes = []

# ---------------------------------------------------------
# Step 2: Extraction & Encoding Fix
# Note: Brazilian governmental datasets use Latin-1 (ISO-8859-1)
# due to special Portuguese characters (like 'ç', 'ã', 'é').
# Reading directly as UTF-8 throws decoding errors.
# ----------------------------------------------------------
for file in file_list:
    try:
        # Semicolon is used as the standard CSV separator in this dataset
        df = pd.read_csv(file, encoding="latin-1", sep=";", low_memory=False)
        dataframes.append(df)
        print(f" -> Successfully read: {os.path.basename(file)} ({len(df):,} rows)")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Combine all individual yearly dataframes into one master dataframe
print("Merging all years into a single master dataset...")
combined_df = pd.concat(dataframes, ignore_index=True)
print(f"Total consolidated rows: {len(combined_df):,}")

# ---------------------------------------------------------
# Step 3: Date Standardization & Chronological Sorting
# The raw data has inconsistent date formats:
# - Older years often use 'DD/MM/YYYY'
# - Newer years use 'YYYY-MM-DD'
# ---------------------------------------------------------
if 'data_inversa' in combined_df.columns:
    print("Standardizing inconsistent date formats...")
    
    # Let pandas infer and parse mixed date formats into real datetime objects
    combined_df['data_inversa'] = pd.to_datetime(
        combined_df['data_inversa'], 
        format='mixed', 
        errors='coerce'
    )
    
    # Sort chronologically from oldest to newest accident record
    combined_df = combined_df.sort_values(by='data_inversa')
    
    # Convert to standard ISO format (YYYY-MM-DD) which PostgreSQL understands best
    combined_df['data_inversa'] = combined_df['data_inversa'].dt.strftime('%Y-%m-%d')

# ---------------------------------------------------------
# Step 4: Export Clean Consolidated Data
# Save as a clean UTF-8 file with semicolon separator for the ingestion pipeline
# ---------------------------------------------------------
output_file = "brazilian_traffic.csv"
combined_df.to_csv(output_file, index=False, encoding="utf-8", sep=";")
print(f"Done! Clean dataset saved as '{output_file}'. Ready for database ingestion.")