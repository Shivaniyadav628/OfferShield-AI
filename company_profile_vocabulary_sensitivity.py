
import pandas as pd
import re

from pathlib import Path
from collections import Counter
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests


# ============================================================
# STEP 1: LOAD DATASET
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")

print("\nCOMPANY PROFILE VOCABULARY SENSITIVITY ANALYSIS")
print("=" * 70)

print("Original dataset shape:", df.shape)


# ============================================================
# STEP 2: CLEAN COMPANY PROFILE TEXT
# ============================================================

df["company_profile"] = (
    df["company_profile"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df = df[
    (df["company_profile"] != "") &
    (df["company_profile"] != "Not Specified")
].copy()

# Normalise text so repeated descriptions can be identified.
df["normalized_profile"] = (
    df["company_profile"]
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

print("\nAVAILABLE PROFILE POSTINGS:", len(df))


# ============================================================
# STEP 3: IDENTIFY THE TWO DOMINANT PROFILES
# ============================================================

profile_counts = (
    df.groupby("normalized_profile")
    .agg(
        posting_count=("fraudulent", "size"),
        fraudulent_postings=("fraudulent", "sum")
    )
    .reset_index()
)

# Sort by number of fraudulent-labelled postings.
top_fraud_profiles = profile_counts.sort_values(
    by="fraudulent_postings",
    ascending=False
).head(2)

excluded_profiles = set(
    top_fraud_profiles["normalized_profile"]
)

print("\nPROFILES SELECTED FOR EXCLUSION")
print("=" * 70)

print(
    top_fraud_profiles[
        ["posting_count", "fraudulent_postings"]
    ].to_string(index=False)
)


# ============================================================
# STEP 4: CREATE TWO DATASETS
# ============================================================

# Original dataset: all available company profiles.
original_df = df.copy()

# Sensitivity dataset: exclude the two dominant descriptions.
sensitivity_df = df[
    ~df["normalized_profile"].isin(excluded_profiles)
].copy()

print("\nDATASET COMPARISON")
print("=" * 70)

print("Original postings:", len(original_df))
print("After exclusion:", len(sensitivity_df))

print(
    "Excluded postings:",
    len(original_df) - len(sensitivity_df)
)

print(
    "Original fraudulent-labelled postings:",
    (original_df["fraudulent"] == 1).sum()
)

print(
    "Remaining fraudulent-labelled postings:",
    (sensitivity_df["fraudulent"] == 1).sum()
)


# ============================================================
# STEP 5: DEFINE TOKENISATION FUNCTION
# ============================================================

stop_words = set(
    """
    a an the and or but if while with without
    to of in on for from by as at is are was were
    be been being it its this that these those
    we our us you your they their them he she
    his her i me my who which what when where
    how why can could will would should may might
    have has had do does did not no so than then
    also very more most some any all each other
    such into about over under up down out
    company companies business businesses
    """.split()
)


def tokenize_profile(text):

    words = re.findall(r"[a-z]{3,}", text.lower())

    return [
        word for word in words
        if word not in stop_words
    ]


# ============================================================
# STEP 6: DOCUMENT-LEVEL WORD FREQUENCY ANALYSIS
# ============================================================

def analyse_vocabulary(data, dataset_name):

    print(f"\nANALYSING: {dataset_name}")
    print("-" * 70)

    genuine_profiles = data[
        data["fraudulent"] == 0
    ]["normalized_profile"].tolist()

    fraudulent_profiles = data[
        data["fraudulent"] == 1
    ]["normalized_profile"].tolist()

    print("Genuine-labelled postings:", len(genuine_profiles))
    print("Fraudulent-labelled postings:", len(fraudulent_profiles))

    # Count each word at most once per posting.
    genuine_document_frequency = Counter()
    fraudulent_document_frequency = Counter()

    for text in genuine_profiles:

        unique_words = set(tokenize_profile(text))

        genuine_document_frequency.update(unique_words)

    for text in fraudulent_profiles:

        unique_words = set(tokenize_profile(text))

        fraudulent_document_frequency.update(unique_words)

    vocabulary = (
        set(genuine_document_frequency.keys()) |
        set(fraudulent_document_frequency.keys())
    )

    genuine_total = len(genuine_profiles)
    fraudulent_total = len(fraudulent_profiles)

    results = []

    for word in vocabulary:

        genuine_count = genuine_document_frequency[word]
        fraudulent_count = fraudulent_document_frequency[word]

        total_count = genuine_count + fraudulent_count

        # Minimum sample-size filter.
        if total_count < 30:
            continue

        if fraudulent_count < 10:
            continue

        genuine_absent = genuine_total - genuine_count
        fraudulent_absent = fraudulent_total - fraudulent_count

        contingency_table = [
            [genuine_count, genuine_absent],
            [fraudulent_count, fraudulent_absent]
        ]

        chi2, p_value, _, _ = chi2_contingency(
            contingency_table,
            correction=False
        )

        genuine_rate = genuine_count / genuine_total
        fraudulent_rate = fraudulent_count / fraudulent_total

        results.append({
            "word": word,
            "genuine_profiles": genuine_count,
            "fraud_profiles": fraudulent_count,
            "genuine_rate": genuine_rate,
            "fraud_rate": fraudulent_rate,
            "difference": fraudulent_rate - genuine_rate,
            "total_profiles": total_count,
            "p_value": p_value
        })

    results_df = pd.DataFrame(results)

    if results_df.empty:

        print("No words passed the frequency filters.")

        return results_df

    # Apply Benjamini-Hochberg correction.
    results_df["adjusted_p_value"] = multipletests(
        results_df["p_value"],
        method="fdr_bh"
    )[1]

    results_df = results_df.sort_values(
        by="adjusted_p_value"
    )

    significant = results_df[
        results_df["adjusted_p_value"] < 0.05
    ]

    fraud_associated = significant[
        significant["difference"] > 0
    ]

    genuine_associated = significant[
        significant["difference"] < 0
    ]

    print("\nVOCABULARY RESULTS")
    print("-" * 70)

    print("Words passing frequency filters:", len(results_df))
    print("Statistically significant words:", len(significant))
    print("Fraud-associated words:", len(fraud_associated))
    print("Genuine-associated words:", len(genuine_associated))

    return results_df


# ============================================================
# STEP 7: ANALYSE ORIGINAL DATASET
# ============================================================

original_results = analyse_vocabulary(
    original_df,
    "ORIGINAL DATASET"
)


# ============================================================
# STEP 8: ANALYSE DATASET AFTER EXCLUSION
# ============================================================

sensitivity_results = analyse_vocabulary(
    sensitivity_df,
    "AFTER EXCLUDING TWO DOMINANT PROFILES"
)


# ============================================================
# STEP 9: COMPARE RESULTS
# ============================================================

def get_significant_words(results):

    if results.empty:
        return set()

    return set(
        results.loc[
            results["adjusted_p_value"] < 0.05,
            "word"
        ]
    )


original_significant = get_significant_words(
    original_results
)

sensitivity_significant = get_significant_words(
    sensitivity_results
)

remaining_words = (
    original_significant & sensitivity_significant
)

lost_words = (
    original_significant - sensitivity_significant
)

new_words = (
    sensitivity_significant - original_significant
)

print("\nSENSITIVITY COMPARISON")
print("=" * 70)

print("Original significant words:", len(original_significant))

print("Significant after exclusion:", len(sensitivity_significant))

print("Words significant in both analyses:", len(remaining_words))

print("Words no longer significant:", len(lost_words))

print("New significant words:", len(new_words))


# ============================================================
# STEP 10: DISPLAY WORD COMPARISON
# ============================================================

if not original_results.empty and not sensitivity_results.empty:

    comparison = original_results[
        [
            "word",
            "fraud_rate",
            "genuine_rate",
            "adjusted_p_value"
        ]
    ].merge(
        sensitivity_results[
            [
                "word",
                "fraud_rate",
                "genuine_rate",
                "adjusted_p_value"
            ]
        ],
        on="word",
        how="outer",
        suffixes=("_original", "_after_exclusion")
    )

    comparison["significant_original"] = (
        comparison["adjusted_p_value_original"] < 0.05
    )

    comparison["significant_after_exclusion"] = (
        comparison["adjusted_p_value_after_exclusion"] < 0.05
    )

    print("\nWORD-LEVEL COMPARISON")
    print("=" * 70)

    print(
        comparison.sort_values(
            by="adjusted_p_value_after_exclusion",
            na_position="last"
        ).head(30).to_string(index=False)
    )


# ============================================================
# STEP 11: SAVE RESULTS
# ============================================================

output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

original_results.to_csv(
    output_folder / "vocabulary_sensitivity_original.csv",
    index=False
)

sensitivity_results.to_csv(
    output_folder / "vocabulary_sensitivity_excluded.csv",
    index=False
)

if not original_results.empty and not sensitivity_results.empty:

    comparison.to_csv(
        output_folder / "vocabulary_sensitivity_comparison.csv",
        index=False
    )


# ============================================================
# STEP 12: FINAL MESSAGE
# ============================================================

print("\nFILES SAVED")
print("=" * 70)

print("1. vocabulary_sensitivity_original.csv")
print("2. vocabulary_sensitivity_excluded.csv")
print("3. vocabulary_sensitivity_comparison.csv")

print("\nVOCABULARY SENSITIVITY ANALYSIS COMPLETED!")
