
import pandas as pd
import nltk
import re
import html

from nltk.corpus import stopwords

# Download English stopwords
nltk.download("stopwords")

# Load the dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Get English stopwords
stop_words = set(stopwords.words("english"))

# Function to remove stopwords
def remove_stopwords(text):

    # Convert text to lowercase
    text = text.lower()

    # Decode HTML entities
    text = html.unescape(text)

    # Remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Split text into words
    words = text.split()

    # Remove stopwords
    filtered_words = [
        word for word in words
        if word not in stop_words
    ]

    # Join remaining words
    return " ".join(filtered_words)


# Apply stopword removal to descriptions
df["description"] = df["description"].apply(remove_stopwords)

# Display the cleaned description
print("\nDESCRIPTION AFTER STOPWORD REMOVAL:")
print(df["description"].iloc[0])

# Display total words remaining
print("\nTOTAL WORDS AFTER STOPWORD REMOVAL:")
print(len(df["description"].iloc[0].split()))
