import pandas as pd

# Load original dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Display missing values before cleaning
print("MISSING VALUES BEFORE CLEANING:")
print(df.isnull().sum().sum())

# Find all text columns
text_columns = df.select_dtypes(
    include=["object"]
).columns

# Replace missing text values
df[text_columns] = df[text_columns].fillna("Not Specified")

# Display missing values after cleaning
print("\nMISSING VALUES AFTER CLEANING:")
print(df.isnull().sum().sum())

# Save cleaned dataset
df.to_csv(
    "data/processed/jobs_cleaned.csv",
    index=False
)

print("\nCleaned dataset saved successfully!")