import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Display one genuine job description
print("\nGENUINE JOB DESCRIPTION:")
print(df[df["fraudulent"] == 0]["description"].iloc[0])

# Display one fraudulent job description
print("\nFRAUDULENT JOB DESCRIPTION:")
print(df[df["fraudulent"] == 1]["description"].iloc[0])