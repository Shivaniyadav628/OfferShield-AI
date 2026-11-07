
import pandas as pd
import numpy as np


# ============================================================
# STEP 1: LOAD DOCUMENT-LEVEL VOCABULARY ANALYSIS
# ============================================================

input_path = "data/processed/company_profile_word_analysis.csv"

df = pd.read_csv(input_path)

print("\nCOMPANY PROFILE VOCABULARY RELIABILITY ANALYSIS")
print("=" * 65)

print("Total vocabulary words:", len(df))


# ============================================================
# STEP 2: VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [
    "word",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "difference",
    "adjusted_p_value"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nCOLUMN VALIDATION PASSED!")


# ============================================================
# STEP 3: CALCULATE RATE DIFFERENCE
# ============================================================

# Positive difference means the word is more common
# in fraudulent profiles.

df["rate_difference"] = df["difference"]


# ============================================================
# STEP 4: CALCULATE RATE RATIO
# ============================================================

# Rate ratio compares the fraud rate with the genuine rate.
# If genuine rate is zero, the ratio is undefined.

df["rate_ratio"] = np.where(
    df["genuine_rate"] > 0,
    df["fraud_rate"] / df["genuine_rate"],
    np.nan
)


# ============================================================
# STEP 5: CALCULATE TOTAL PROFILE COUNTS
# ============================================================

df["total_profiles"] = (
    df["genuine_profiles"] +
    df["fraud_profiles"]
)


# ============================================================
# STEP 6: FILTER WORDS WITH SUFFICIENT OBSERVATIONS
# ============================================================

# Retain words appearing in at least 30 profiles overall,
# including at least 10 fraudulent profiles.

reliable_words = df[
    (df["total_profiles"] >= 30) &
    (df["fraud_profiles"] >= 10)
].copy()

print("\nSAMPLE SIZE FILTERING")
print("=" * 65)

print("Words before filtering:", len(df))
print("Words after filtering:", len(reliable_words))


# ============================================================
# STEP 7: FILTER STATISTICALLY SIGNIFICANT WORDS
# ============================================================

# Use the adjusted p-value to account for multiple testing.
# Threshold: 0.05.

significant_words = reliable_words[
    reliable_words["adjusted_p_value"] < 0.05
].copy()

print(
    "Significant words after filtering:",
    len(significant_words)
)


# ============================================================
# STEP 8: IDENTIFY FRAUD-ASSOCIATED WORDS
# ============================================================

fraud_candidates = significant_words[
    significant_words["rate_difference"] > 0
].copy()

fraud_candidates = fraud_candidates.sort_values(
    by="rate_difference",
    ascending=False
)


# ============================================================
# STEP 9: IDENTIFY GENUINE-ASSOCIATED WORDS
# ============================================================

genuine_candidates = significant_words[
    significant_words["rate_difference"] < 0
].copy()

genuine_candidates = genuine_candidates.sort_values(
    by="rate_difference",
    ascending=True
)


# ============================================================
# STEP 10: DISPLAY FRAUD-ASSOCIATED WORDS
# ============================================================

display_columns = [
    "word",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "rate_difference",
    "rate_ratio",
    "adjusted_p_value"
]

print("\nTOP 20 FRAUD-ASSOCIATED WORDS")
print("=" * 65)

if not fraud_candidates.empty:
    print(
        fraud_candidates[display_columns]
        .head(20)
        .to_string(index=False)
    )
else:
    print("No words passed the fraud-associated filters.")


# ============================================================
# STEP 11: DISPLAY GENUINE-ASSOCIATED WORDS
# ============================================================

print("\nTOP 20 GENUINE-ASSOCIATED WORDS")
print("=" * 65)

if not genuine_candidates.empty:
    print(
        genuine_candidates[display_columns]
        .head(20)
        .to_string(index=False)
    )
else:
    print("No words passed the genuine-associated filters.")


# ============================================================
# STEP 12: SAVE RESULTS
# ============================================================

fraud_candidates.to_csv(
    "data/processed/fraud_associated_vocabulary.csv",
    index=False
)

genuine_candidates.to_csv(
    "data/processed/genuine_associated_vocabulary.csv",
    index=False
)


# ============================================================
# STEP 13: FINAL SUMMARY
# ============================================================

print("\nFINAL ANALYSIS SUMMARY")
print("=" * 65)

print("Total words analysed:", len(df))
print("Words passing sample-size filter:", len(reliable_words))
print("Statistically significant words:", len(significant_words))
print("Fraud-associated words:", len(fraud_candidates))
print("Genuine-associated words:", len(genuine_candidates))

print("\nRESULT FILES SAVED:")
print("1. data/processed/fraud_associated_vocabulary.csv")
print("2. data/processed/genuine_associated_vocabulary.csv")

print("\nCOMPANY PROFILE VOCABULARY RELIABILITY ANALYSIS COMPLETED!")
