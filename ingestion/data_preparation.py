import os
import glob
import pandas as pd

# ---------------------------------------------------------
# Step 1: Directory Setup – FIXED for Docker container
# The data is mounted at /app/data inside the container
# ---------------------------------------------------------
data_dir = "/app/data"
os.chdir(data_dir)

# Find all annual Brazilian traffic files (Dados_PRF_*.csv)
file_list = sorted(glob.glob("Dados_PRF_*.csv"))
print(f"Found {len(file_list)} raw yearly files. Starting data consolidation...")

dataframes = []

# ---------------------------------------------------------
# Step 2: Extraction & Encoding Fix
# ---------------------------------------------------------
for file in file_list:
    try:
        df = pd.read_csv(file, encoding="latin-1", sep=";", low_memory=False)
        dataframes.append(df)
        print(f" -> Successfully read: {os.path.basename(file)} ({len(df):,} rows)")
    except Exception as e:
        print(f"Error reading {file}: {e}")

print("Merging all years into a single master dataset...")
combined_df = pd.concat(dataframes, ignore_index=True)
print(f"Total consolidated rows: {len(combined_df):,}")

# ---------------------------------------------------------
# Step 3: Date Standardization & Chronological Sorting
# ---------------------------------------------------------
if 'data_inversa' in combined_df.columns:
    print("Standardizing inconsistent date formats...")
    combined_df['data_inversa'] = pd.to_datetime(
        combined_df['data_inversa'], 
        format='mixed', 
        errors='coerce'
    )
    combined_df = combined_df.sort_values(by='data_inversa')
    combined_df['data_inversa'] = combined_df['data_inversa'].dt.strftime('%Y-%m-%d')

# ---------------------------------------------------------
# Step 4: Export Clean Consolidated Data
# Saves to /app/data/brazilian_traffic.csv (same directory as input)
# ---------------------------------------------------------
output_file = "brazilian_traffic.csv"
combined_df.to_csv(output_file, index=False, encoding="utf-8", sep=";")
print(f"Done! Clean dataset saved as '{output_file}'. Ready for database ingestion.")