
import pandas as pd
import nltk
import re

from nltk.stem import WordNetLemmatizer

# Download required language resources
nltk.download("wordnet")
nltk.download("omw-1.4")

# Load the dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Create a lemmatizer object
lemmatizer = WordNetLemmatizer()

# Function to perform lemmatization
def perform_lemmatization(text):

    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Split text into individual words
    words = text.split()

    # Apply lemmatization to each word
    lemmatized_words = [
        lemmatizer.lemmatize(word) for word in words
    ]

    # Join words into a sentence
    return " ".join(lemmatized_words)


# Apply lemmatization to job descriptions
df["description"] = df["description"].apply(perform_lemmatization)

# Display original description
print("\nORIGINAL DESCRIPTION:")
print(pd.read_csv("data/processed/jobs_cleaned.csv")["description"].iloc[0])

# Display lemmatized description
print("\nLEMMATIZED DESCRIPTION:")
print(df["description"].iloc[0])

# Display word count
print("\nTOTAL WORDS AFTER LEMMATIZATION:")
print(len(df["description"].iloc[0].split()))


# Test individual words
print("\nINDIVIDUAL WORD EXAMPLES:")
test_words = ["studies", "mice", "running", "better", "cars"]

for word in test_words:
    print(word, "->", lemmatizer.lemmatize(word))
