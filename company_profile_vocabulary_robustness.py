
import pandas as pd
import numpy as np

from pathlib import Path


# ============================================================
# STEP 1: LOAD PREVIOUS ANALYSIS RESULTS
# ============================================================

base_path = Path("data/processed")

posting_results_path = (
    base_path / "company_profile_word_analysis.csv"
)

unique_results_path = (
    base_path / "unique_profile_word_analysis.csv"
)

posting_df = pd.read_csv(posting_results_path)

unique_df = pd.read_csv(unique_results_path)

print("\nCOMPANY PROFILE VOCABULARY ROBUSTNESS ANALYSIS")
print("=" * 75)

print("Posting-level vocabulary words:", len(posting_df))
print("Unique-profile vocabulary words:", len(unique_df))


# ============================================================
# STEP 2: VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [
    "word",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "adjusted_p_value"
]

for name, data in [
    ("Posting-level", posting_df),
    ("Unique-profile", unique_df)
]:

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"{name} results are missing columns: {missing}"
        )


# ============================================================
# STEP 3: SELECT SIGNIFICANT WORDS
# ============================================================

posting_significant = posting_df[
    posting_df["adjusted_p_value"] < 0.05
].copy()

unique_significant = unique_df[
    unique_df["adjusted_p_value"] < 0.05
].copy()

print("\nSIGNIFICANT WORD COUNTS")
print("=" * 75)

print("Posting-level significant words:", len(posting_significant))

print("Unique-profile significant words:", len(unique_significant))


# ============================================================
# STEP 4: MERGE BOTH ANALYSES
# ============================================================

comparison = posting_df[
    [
        "word",
        "genuine_profiles",
        "fraud_profiles",
        "genuine_rate",
        "fraud_rate",
        "adjusted_p_value"
    ]
].merge(
    unique_df[
        [
            "word",
            "genuine_profiles",
            "fraud_profiles",
            "genuine_rate",
            "fraud_rate",
            "adjusted_p_value"
        ]
    ],
    on="word",
    how="inner",
    suffixes=("_posting", "_unique")
)

print("\nCOMMON VOCABULARY WORDS")
print("=" * 75)

print("Words present in both analyses:", len(comparison))


# ============================================================
# STEP 5: CALCULATE EFFECT SIZE
# ============================================================

# Rate ratio compares the fraud-labelled profile rate
# with the genuine profile rate.

def calculate_rate_ratio(fraud_rate, genuine_rate):

    if genuine_rate == 0:

        if fraud_rate > 0:
            return np.inf

        return np.nan

    return fraud_rate / genuine_rate


comparison["rate_ratio_posting"] = comparison.apply(
    lambda row: calculate_rate_ratio(
        row["fraud_rate_posting"],
        row["genuine_rate_posting"]
    ),
    axis=1
)

comparison["rate_ratio_unique"] = comparison.apply(
    lambda row: calculate_rate_ratio(
        row["fraud_rate_unique"],
        row["genuine_rate_unique"]
    ),
    axis=1
)


# ============================================================
# STEP 6: CHECK STATISTICAL CONSISTENCY
# ============================================================

comparison["posting_significant"] = (
    comparison["adjusted_p_value_posting"] < 0.05
)

comparison["unique_significant"] = (
    comparison["adjusted_p_value_unique"] < 0.05
)

comparison["posting_fraud_associated"] = (
    comparison["fraud_rate_posting"] >
    comparison["genuine_rate_posting"]
)

comparison["unique_fraud_associated"] = (
    comparison["fraud_rate_unique"] >
    comparison["genuine_rate_unique"]
)

comparison["same_direction"] = (
    comparison["posting_fraud_associated"] ==
    comparison["unique_fraud_associated"]
)

comparison["significant_in_both"] = (
    comparison["posting_significant"] &
    comparison["unique_significant"]
)

comparison["robust_fraud_association"] = (
    comparison["significant_in_both"] &
    comparison["posting_fraud_associated"] &
    comparison["unique_fraud_associated"]
)


# ============================================================
# STEP 7: APPLY SAMPLE-SIZE FILTERS
# ============================================================

# Require at least 20 fraudulent-labelled postings
# and at least 5 fraudulent-labelled unique profiles.

comparison["sample_size_eligible"] = (
    (comparison["fraud_profiles_posting"] >= 20) &
    (comparison["fraud_profiles_unique"] >= 5)
)

comparison["robust_with_sample_support"] = (
    comparison["robust_fraud_association"] &
    comparison["sample_size_eligible"]
)


# ============================================================
# STEP 8: PRINT ROBUSTNESS SUMMARY
# ============================================================

print("\nROBUSTNESS SUMMARY")
print("=" * 75)

print(
    "Words significant in both analyses:",
    comparison["significant_in_both"].sum()
)

print(
    "Words associated with fraud in both analyses:",
    comparison["robust_fraud_association"].sum()
)

print(
    "Words with sufficient sample support:",
    comparison["sample_size_eligible"].sum()
)

print(
    "Robust fraud-associated words with sample support:",
    comparison["robust_with_sample_support"].sum()
)

print(
    "Words with different association directions:",
    (~comparison["same_direction"]).sum()
)


# ============================================================
# STEP 9: DISPLAY ROBUST FRAUD-ASSOCIATED WORDS
# ============================================================

robust_words = comparison[
    comparison["robust_with_sample_support"]
].copy()

robust_words = robust_words.sort_values(
    by="rate_ratio_unique",
    ascending=False
)

print("\nROBUST FRAUD-ASSOCIATED WORDS")
print("=" * 75)

if not robust_words.empty:

    print(
        robust_words[
            [
                "word",
                "fraud_profiles_posting",
                "fraud_profiles_unique",
                "genuine_rate_unique",
                "fraud_rate_unique",
                "rate_ratio_unique",
                "adjusted_p_value_unique"
            ]
        ].to_string(index=False)
    )

else:

    print("No words passed all robustness conditions.")


# ============================================================
# STEP 10: IDENTIFY RARE WORDS
# ============================================================

rare_words = comparison[
    comparison["fraud_profiles_unique"] < 5
].copy()

print("\nRARE WORDS IN UNIQUE-PROFILE ANALYSIS")
print("=" * 75)

print("Number of rare words:", len(rare_words))

if not rare_words.empty:

    print(
        rare_words[
            [
                "word",
                "fraud_profiles_unique",
                "fraud_rate_unique",
                "adjusted_p_value_unique"
            ]
        ].sort_values(
            by="fraud_profiles_unique"
        ).to_string(index=False)
    )


# ============================================================
# STEP 11: SAVE RESULTS
# ============================================================

comparison.to_csv(
    base_path / "company_profile_vocabulary_robustness.csv",
    index=False
)

robust_words.to_csv(
    base_path / "robust_fraud_associated_vocabulary.csv",
    index=False
)

rare_words.to_csv(
    base_path / "rare_vocabulary_words.csv",
    index=False
)


# ============================================================
# STEP 12: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 75)

print("Common words compared:", len(comparison))

print("Significant in both:", comparison["significant_in_both"].sum())

print("Robust fraud-associated words:", len(robust_words))

print("Rare words:", len(rare_words))

print("\nFILES SAVED:")
print("1. company_profile_vocabulary_robustness.csv")
print("2. robust_fraud_associated_vocabulary.csv")
print("3. rare_vocabulary_words.csv")

print("\nVOCABULARY ROBUSTNESS ANALYSIS COMPLETED!")
