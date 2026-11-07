import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Find the row with missing description
missing_description = df[df["description"].isnull()]

print("\nJOB POSTING WITH MISSING DESCRIPTION:")
print(missing_description.T)