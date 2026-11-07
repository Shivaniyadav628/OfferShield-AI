
import pandas as pd
import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from scipy.stats import chi2_contingency

# STEP 1: Load dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# STEP 2: Select company profiles
df = df[["company_profile", "fraudulent"]].copy()

# Remove missing profiles
df = df[
    df["company_profile"].notna() &
    (df["company_profile"] != "Not Specified")
].copy()

# STEP 3: Clean text
stop_words = set(ENGLISH_STOP_WORDS)

def clean_and_tokenize(text):

    text = str(text).lower()

    # Extract alphabetic words
    words = re.findall(r"\b[a-z]{3,}\b", text)

    # Remove common English stopwords
    words = [
        word for word in words
        if word not in stop_words
    ]

    return words


df["tokens"] = df["company_profile"].apply(
    clean_and_tokenize
)

# STEP 4: Separate genuine and fraudulent profiles
genuine_tokens = [
    word
    for tokens in df[df["fraudulent"] == 0]["tokens"]
    for word in tokens
]

fraud_tokens = [
    word
    for tokens in df[df["fraudulent"] == 1]["tokens"]
    for word in tokens
]

genuine_counts = Counter(genuine_tokens)
fraud_counts = Counter(fraud_tokens)

# STEP 5: Display dataset statistics
print("\nCOMPANY PROFILE VOCABULARY ANALYSIS")
print("=" * 65)

print("Genuine profiles:", len(genuine_counts))
print("Fraudulent profiles:", len(fraud_counts))

print("Genuine total words:", len(genuine_tokens))
print("Fraudulent total words:", len(fraud_tokens))

# STEP 6: Most frequent words
print("\nTOP 30 WORDS IN GENUINE COMPANY PROFILES")
print("=" * 65)

print(genuine_counts.most_common(30))

print("\nTOP 30 WORDS IN FRAUDULENT COMPANY PROFILES")
print("=" * 65)

print(fraud_counts.most_common(30))

# STEP 7: Compare word frequencies
all_words = set(genuine_counts) | set(fraud_counts)

word_comparison = []

for word in all_words:

    genuine_frequency = genuine_counts[word]
    fraud_frequency = fraud_counts[word]

    word_comparison.append({
        "word": word,
        "genuine_count": genuine_frequency,
        "fraud_count": fraud_frequency
    })

comparison_df = pd.DataFrame(word_comparison)

comparison_df["genuine_rate"] = (
    comparison_df["genuine_count"] /
    max(len(genuine_tokens), 1)
)

comparison_df["fraud_rate"] = (
    comparison_df["fraud_count"] /
    max(len(fraud_tokens), 1)
)

comparison_df["frequency_difference"] = (
    comparison_df["fraud_rate"] -
    comparison_df["genuine_rate"]
)

# STEP 8: Display words relatively more frequent in fraud
print("\nWORDS MORE FREQUENT IN FRAUDULENT PROFILES")
print("=" * 65)

print(
    comparison_df.sort_values(
        "frequency_difference",
        ascending=False
    ).head(20).to_string(index=False)
)

# STEP 9: Display words relatively more frequent in genuine
print("\nWORDS MORE FREQUENT IN GENUINE PROFILES")
print("=" * 65)

print(
    comparison_df.sort_values(
        "frequency_difference",
        ascending=True
    ).head(20).to_string(index=False)
)

# STEP 10: Chi-square test on selected frequent words
print("\nCHI-SQUARE WORD ASSOCIATION ANALYSIS")
print("=" * 65)

results = []

for word in all_words:

    # Ignore extremely rare words
    if genuine_counts[word] + fraud_counts[word] < 10:
        continue

    table = [
        [
            genuine_counts[word],
            len(genuine_tokens) - genuine_counts[word]
        ],
        [
            fraud_counts[word],
            len(fraud_tokens) - fraud_counts[word]
        ]
    ]

    chi2, p_value, _, _ = chi2_contingency(table)

    results.append({
        "word": word,
        "chi2": chi2,
        "p_value": p_value
    })

stats_df = pd.DataFrame(results)

if not stats_df.empty:

    stats_df = stats_df.sort_values("p_value")

    print(
        stats_df.head(20).to_string(index=False)
    )

else:
    print("No words met the minimum frequency requirement.")

print("\nCOMPANY PROFILE VOCABULARY ANALYSIS COMPLETED!")
