import pandas as pd

# Load the dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Display first 5 rows
print("\nFIRST 5 JOB POSTINGS:")
print(df.head())

# Display total rows and columns
print("\nDATASET SHAPE:")
print(df.shape)

# Display all column names
print("\nCOLUMN NAMES:")
print(df.columns)

# Display dataset information
print("\nDATASET INFORMATION:")
df.info()