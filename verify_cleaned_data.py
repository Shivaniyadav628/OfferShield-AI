import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Check dataset dimensions
print("\nCLEANED DATASET SHAPE:")
print(df.shape)

# Check missing values
print("\nTOTAL MISSING VALUES:")
print(df.isnull().sum().sum())

# Check first five records
print("\nFIRST FIVE CLEANED RECORDS:")
print(df.head())

# Check target distribution
print("\nFRAUD DISTRIBUTION:")
print(df["fraudulent"].value_counts())