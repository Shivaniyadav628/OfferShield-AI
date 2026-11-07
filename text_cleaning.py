import pandas as pd
import re
import html

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Function to clean text
def clean_text(text):

    # Convert text to lowercase
    text = text.lower()

    # Decode HTML entities
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove special characters and punctuation
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Apply cleaning to descriptions
df["description"] = df["description"].apply(clean_text)

# Display original example from cleaned dataset
print("\nCLEANED JOB DESCRIPTION:")
print(df["description"].iloc[0])