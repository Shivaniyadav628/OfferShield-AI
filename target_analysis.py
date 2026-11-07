import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Count genuine and fraudulent jobs
target_counts = df["fraudulent"].value_counts()

print("\nJOB POSTING DISTRIBUTION:")
print(target_counts)

# Calculate percentages
target_percentages = df["fraudulent"].value_counts(normalize=True) * 100

print("\nJOB POSTING PERCENTAGES:")
print(target_percentages)

# Display category names
print("\nCATEGORY MEANING:")
print("0 = Genuine job posting")
print("1 = Fraudulent job posting")