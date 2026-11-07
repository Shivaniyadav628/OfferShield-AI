import pandas as pd
import re


# STEP 1: Load dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# STEP 2: Define sentence duplication function

def calculate_sentence_duplicate_ratio(text):

    if pd.isna(text):
        return 0

    text = str(text).lower()

    sentences = re.split(r'[.!?]+', text)

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]

    if len(sentences) == 0:
        return 0

    unique_sentences = set(sentences)

    duplicate_count = (
        len(sentences) - len(unique_sentences)
    )

    return duplicate_count / len(sentences)


# STEP 3: Calculate duplication ratios

df["description_sentence_duplicates"] = (
    df["description"].apply(
        calculate_sentence_duplicate_ratio
    )
)

df["requirements_sentence_duplicates"] = (
    df["requirements"].apply(
        calculate_sentence_duplicate_ratio
    )
)


# STEP 4: Compare genuine and fraudulent jobs

print("\nDESCRIPTION SENTENCE DUPLICATION")
print("=" * 60)

print(
    df.groupby("fraudulent")[
        "description_sentence_duplicates"
    ].agg(["mean", "median", "max"])
)


print("\nREQUIREMENTS SENTENCE DUPLICATION")
print("=" * 60)

print(
    df.groupby("fraudulent")[
        "requirements_sentence_duplicates"
    ].agg(["mean", "median", "max"])
)


# STEP 5: Count postings with duplicates

print("\nDUPLICATE SENTENCE COUNTS")
print("=" * 60)

print(
    "Description duplicates:",
    (df["description_sentence_duplicates"] > 0).sum()
)

print(
    "Requirements duplicates:",
    (df["requirements_sentence_duplicates"] > 0).sum()
)


print("\nSENTENCE DUPLICATION ANALYSIS COMPLETED!")