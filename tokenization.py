import pandas as pd

# Load the dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Select the first job description
text = df["description"].iloc[0]

# Split the description into words
tokens = text.split()

# Display the tokens
print("\nFIRST 20 TOKENS:")
print(tokens[:20])

# Count total tokens
print("\nTOTAL NUMBER OF TOKENS:")
print(len(tokens))