import pandas as pd

# Load the dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Count missing values in each column
missing_count = df.isnull().sum()

# Calculate missing percentage
missing_percentage = (missing_count / len(df)) * 100

# Create a summary table
missing_data = pd.DataFrame({
    "Missing Values": missing_count,
    "Missing Percentage": missing_percentage
})

# Display only columns having missing values
print("\nMISSING VALUES ANALYSIS:")
print(missing_data[missing_data["Missing Values"] > 0])