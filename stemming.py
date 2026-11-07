
import pandas as pd
import nltk
import re

from nltk.stem import PorterStemmer

# Load the dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Create a stemming object
stemmer = PorterStemmer()

# Function to perform stemming
def perform_stemming(text):

    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Split text into individual words
    words = text.split()

    # Apply stemming to each word
    stemmed_words = [stemmer.stem(word) for word in words]

    # Join stemmed words into a sentence
    return " ".join(stemmed_words)


# Apply stemming to job descriptions
df["description"] = df["description"].apply(perform_stemming)

# Display original description
print("\nORIGINAL DESCRIPTION:")
print(pd.read_csv("data/processed/jobs_cleaned.csv")["description"].iloc[0])

# Display stemmed description
print("\nSTEMMED DESCRIPTION:")
print(df["description"].iloc[0])

# Display word count
print("\nTOTAL WORDS AFTER STEMMING:")
print(len(df["description"].iloc[0].split()))
