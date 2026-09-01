import os
import glob
import sys
import pandas as pd

# csv files are mounted at /app/data inside the container

data_dir = "/app/data"
os.chdir(data_dir)

# all yearly files follow the pattern Dados_PRF_*.csv
file_list = sorted(glob.glob("Dados_PRF_*.csv"))
print(f"Found {len(file_list)} raw yearly files. Starting data consolidation...")

if not file_list:
    print("No Dados_PRF_*.csv files found in /app/data — aborting.")
    sys.exit(1)

dataframes = []

# Read each file with Latin-1 encoding (brazilian portuguese special characters)
# the files use semicolon as separator

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

# brazilian dates are DD/MM/YYYY; pandas assumes month first by default

if 'data_inversa' in combined_df.columns:
    combined_df['data_inversa'] = pd.to_datetime(
        combined_df['data_inversa'], 
        format='mixed', 
        dayfirst=True,
        errors='coerce'
    )
    combined_df = combined_df.sort_values(by='data_inversa')
    combined_df['data_inversa'] = combined_df['data_inversa'].dt.strftime('%Y-%m-%d') 
    
#  output file ready  for the ingestion
output_file = "brazilian_traffic.csv"
combined_df.to_csv(output_file, index=False, encoding="utf-8", sep=";")
print(f"Done! Clean dataset saved as '{output_file}'. Ready for database ingestion.")