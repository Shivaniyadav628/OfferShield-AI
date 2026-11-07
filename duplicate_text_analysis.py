import pandas as pd


# STEP 1: Load cleaned dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# STEP 2: Define a function to detect repeated lines

def calculate_duplicate_ratio(text):

    if pd.isna(text):
        return 0

    lines = [
        line.strip().lower()
        for line in str(text).splitlines()
        if len(line.strip()) > 20
    ]

    if len(lines) == 0:
        return 0

    unique_lines = set(lines)

    duplicate_count = len(lines) - len(unique_lines)

    return duplicate_count / len(lines)


# STEP 3: Calculate duplicate ratios

df["description_duplicate_ratio"] = (
    df["description"].apply(calculate_duplicate_ratio)
)

df["requirements_duplicate_ratio"] = (
    df["requirements"].apply(calculate_duplicate_ratio)
)


# STEP 4: Compare genuine and fraudulent postings

print("\nDESCRIPTION DUPLICATION ANALYSIS")
print("=" * 60)

print(
    df.groupby("fraudulent")[
        "description_duplicate_ratio"
    ].agg(["mean", "median", "max"])
)


print("\nREQUIREMENTS DUPLICATION ANALYSIS")
print("=" * 60)

print(
    df.groupby("fraudulent")[
        "requirements_duplicate_ratio"
    ].agg(["mean", "median", "max"])
)


# STEP 5: Check how many postings contain duplicates

print("\nDUPLICATE CONTENT COUNTS")
print("=" * 60)

print(
    "Descriptions with duplicates:",
    (df["description_duplicate_ratio"] > 0).sum()
)

print(
    "Requirements with duplicates:",
    (df["requirements_duplicate_ratio"] > 0).sum()
)


print("\nDUPLICATE TEXT ANALYSIS COMPLETED!")