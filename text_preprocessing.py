import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Select job descriptions
text = df["description"]

# Convert text into lowercase
df["description"] = df["description"].str.lower()

# Display original and processed text
print("\nORIGINAL DESCRIPTION:")
print(text.iloc[0])

print("\nLOWERCASE DESCRIPTION:")
print(df["description"].iloc[0])