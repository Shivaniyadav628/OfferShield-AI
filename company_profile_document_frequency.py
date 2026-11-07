
import pandas as pd
import re

from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests


# STEP 1: Load dataset

df = pd.read_csv("data/processed/jobs_cleaned.csv")

df = df[["company_profile", "fraudulent"]].copy()

df["company_profile"] = (
    df["company_profile"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df = df[
    df["company_profile"].str.lower() != "not specified"
].copy()


# STEP 2: Tokenize company profiles

stop_words = set(ENGLISH_STOP_WORDS)

def clean_and_tokenize(text):

    text = str(text).lower()

    words = re.findall(r"\b[a-z]{3,}\b", text)

    return [
        word for word in words
        if word not in stop_words
    ]


df["tokens"] = df["company_profile"].apply(
    clean_and_tokenize
)


# STEP 3: Separate genuine and fraudulent profiles

genuine = df[df["fraudulent"] == 0]
fraud = df[df["fraudulent"] == 1]

total_genuine = len(genuine)
total_fraud = len(fraud)

print("\nDOCUMENT-LEVEL VOCABULARY ANALYSIS")
print("=" * 65)

print("Genuine profiles:", total_genuine)
print("Fraudulent profiles:", total_fraud)

if total_genuine == 0 or total_fraud == 0:
    raise ValueError("One target category has no profiles.")


# STEP 4: Count word presence per profile

genuine_document_counts = Counter()

for tokens in genuine["tokens"]:
    genuine_document_counts.update(set(tokens))

fraud_document_counts = Counter()

for tokens in fraud["tokens"]:
    fraud_document_counts.update(set(tokens))


# STEP 5: Build comparison table

all_words = (
    set(genuine_document_counts) |
    set(fraud_document_counts)
)

results = []

for word in all_words:

    genuine_present = genuine_document_counts[word]
    fraud_present = fraud_document_counts[word]

    genuine_absent = total_genuine - genuine_present
    fraud_absent = total_fraud - fraud_present

    genuine_rate = genuine_present / total_genuine
    fraud_rate = fraud_present / total_fraud

    results.append({
        "word": word,
        "genuine_profiles": genuine_present,
        "fraud_profiles": fraud_present,
        "genuine_rate": genuine_rate,
        "fraud_rate": fraud_rate,
        "difference": fraud_rate - genuine_rate,
        "total_profiles": genuine_present + fraud_present,
        "genuine_absent": genuine_absent,
        "fraud_absent": fraud_absent
    })


comparison_df = pd.DataFrame(results)


# STEP 6: Filter rare words

MIN_DOCUMENT_FREQUENCY = 10

comparison_df = comparison_df[
    comparison_df["total_profiles"] >= MIN_DOCUMENT_FREQUENCY
].copy()

print("\nWORDS RETAINED FOR STATISTICAL TESTING")
print("=" * 65)

print("Vocabulary words:", len(all_words))
print("Words after frequency filtering:", len(comparison_df))


# STEP 7: Perform Chi-square tests

p_values = []

for _, row in comparison_df.iterrows():

    table = [
        [
            row["genuine_profiles"],
            row["genuine_absent"]
        ],
        [
            row["fraud_profiles"],
            row["fraud_absent"]
        ]
    ]

    _, p_value, _, _ = chi2_contingency(
        table,
        correction=True
    )

    p_values.append(p_value)


comparison_df["p_value"] = p_values


# STEP 8: Correct for multiple testing

if not comparison_df.empty:

    comparison_df["adjusted_p_value"] = multipletests(
        comparison_df["p_value"],
        method="fdr_bh"
    )[1]

else:

    comparison_df["adjusted_p_value"] = pd.Series(
        dtype=float
    )


# STEP 9: Display words more common in fraudulent profiles

print("\nWORDS MORE COMMON IN FRAUDULENT PROFILES")
print("=" * 65)

fraud_words = comparison_df.sort_values(
    "difference",
    ascending=False
)

display_columns = [
    "word",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "adjusted_p_value"
]

print(
    fraud_words[display_columns]
    .head(20)
    .to_string(index=False)
)


# STEP 10: Display words more common in genuine profiles

print("\nWORDS MORE COMMON IN GENUINE PROFILES")
print("=" * 65)

genuine_words = comparison_df.sort_values(
    "difference",
    ascending=True
)

print(
    genuine_words[display_columns]
    .head(20)
    .to_string(index=False)
)


# STEP 11: Statistical summary

significant = comparison_df[
    comparison_df["adjusted_p_value"] < 0.05
]

print("\nSTATISTICAL SUMMARY")
print("=" * 65)

print("Words tested:", len(comparison_df))
print("Significant words after correction:", len(significant))


# STEP 12: Save results

comparison_df.to_csv(
    "data/processed/company_profile_word_analysis.csv",
    index=False
)

print("\nRESULTS SAVED!")
print(
    "data/processed/company_profile_word_analysis.csv"
)

print("\nDOCUMENT-LEVEL ANALYSIS COMPLETED!")
