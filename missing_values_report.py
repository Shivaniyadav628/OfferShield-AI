import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Calculate missing values
missing_count = df.isnull().sum()

# Calculate missing percentage
missing_percentage = (missing_count / len(df)) * 100

# Create report
missing_report = pd.DataFrame({
    "Missing Count": missing_count,
    "Missing Percentage": missing_percentage
})

# Sort columns by missing percentage
missing_report = missing_report.sort_values(
    by="Missing Percentage",
    ascending=False
)

print("\nMISSING VALUE REPORT:")
print(missing_report)