import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Count duplicate rows
duplicate_count = df.duplicated().sum()

print("\nDUPLICATE ROWS:")
print(duplicate_count)

# Check duplicate job IDs
duplicate_ids = df["job_id"].duplicated().sum()

print("\nDUPLICATE JOB IDs:")
print(duplicate_ids)

# Display dataset size
print("\nTOTAL ROWS:")
print(len(df))