import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Analyse remote job postings
remote_analysis = pd.crosstab(
    df["telecommuting"],
    df["fraudulent"]
)

print("\nTELECOMMUTING ANALYSIS:")
print(remote_analysis)

# Calculate percentages
remote_percentage = pd.crosstab(
    df["telecommuting"],
    df["fraudulent"],
    normalize="index"
) * 100

print("\nTELECOMMUTING PERCENTAGES:")
print(remote_percentage)