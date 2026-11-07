
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

print("\nUNIQUE COMPANY PROFILE DOCUMENT ANALYSIS")
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

# Normalise text to identify identical descriptions.
df["normalized_profile"] = (
    df["company_profile"]
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

print("\nPOSTINGS WITH AVAILABLE PROFILES:", len(df))


# ============================================================
# STEP 3: CREATE UNIQUE PROFILE DATASET
# ============================================================

# Group identical profile descriptions.
unique_profiles = (
    df.groupby("normalized_profile")
    .agg(
        posting_count=("fraudulent", "size"),
        genuine_postings=("fraudulent", lambda x: (x == 0).sum()),
        fraudulent_postings=("fraudulent", lambda x: (x == 1).sum())
    )
    .reset_index()
)

# Determine label composition for each unique profile.
unique_profiles["label_composition"] = "Genuine-labelled only"

unique_profiles.loc[
    unique_profiles["fraudulent_postings"] > 0,
    "label_composition"
] = "Fraudulent-labelled only"

unique_profiles.loc[
    (unique_profiles["genuine_postings"] > 0) &
    (unique_profiles["fraudulent_postings"] > 0),
    "label_composition"
] = "Mixed"

print("\nUNIQUE PROFILE SUMMARY")
print("=" * 70)

print("Unique profiles:", len(unique_profiles))

print(
    unique_profiles["label_composition"]
    .value_counts()
    .to_string()
)


# ============================================================
# STEP 4: CREATE PROFILE-LEVEL CLASS DATASETS
# ============================================================

genuine_profiles = unique_profiles[
    unique_profiles["label_composition"] ==
    "Genuine-labelled only"
].copy()

fraudulent_profiles = unique_profiles[
    unique_profiles["label_composition"] ==
    "Fraudulent-labelled only"
].copy()

print("\nPROFILE-LEVEL CLASS DISTRIBUTION")
print("=" * 70)

print("Genuine unique profiles:", len(genuine_profiles))
print("Fraudulent unique profiles:", len(fraudulent_profiles))

print(
    "Mixed-label profiles:",
    (unique_profiles["label_composition"] == "Mixed").sum()
)


# ============================================================
# STEP 5: TOKENISATION FUNCTION
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
# STEP 6: DOCUMENT-LEVEL WORD FREQUENCY
# ============================================================

genuine_document_frequency = Counter()
fraudulent_document_frequency = Counter()

for text in genuine_profiles["normalized_profile"]:

    # A word is counted only once per unique profile.
    unique_words = set(tokenize_profile(text))

    genuine_document_frequency.update(unique_words)


for text in fraudulent_profiles["normalized_profile"]:

    # A word is counted only once per unique profile.
    unique_words = set(tokenize_profile(text))

    fraudulent_document_frequency.update(unique_words)


vocabulary = (
    set(genuine_document_frequency.keys()) |
    set(fraudulent_document_frequency.keys())
)

print("\nVOCABULARY SUMMARY")
print("=" * 70)

print("Total unique vocabulary words:", len(vocabulary))


# ============================================================
# STEP 7: APPLY FREQUENCY FILTERS
# ============================================================

genuine_total = len(genuine_profiles)
fraudulent_total = len(fraudulent_profiles)

results = []

for word in vocabulary:

    genuine_count = genuine_document_frequency[word]
    fraudulent_count = fraudulent_document_frequency[word]

    total_count = genuine_count + fraudulent_count

    # Require enough unique profiles containing the word.
    if total_count < 10:
        continue

    # Require at least 5 fraudulent-labelled-only profiles.
    if fraudulent_count < 5:
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
    fraud_rate = fraudulent_count / fraudulent_total

    results.append({
        "word": word,
        "genuine_profiles": genuine_count,
        "fraud_profiles": fraudulent_count,
        "genuine_rate": genuine_rate,
        "fraud_rate": fraud_rate,
        "difference": fraud_rate - genuine_rate,
        "total_profiles": total_count,
        "genuine_absent": genuine_absent,
        "fraud_absent": fraudulent_absent,
        "p_value": p_value
    })


results_df = pd.DataFrame(results)


# ============================================================
# STEP 8: MULTIPLE TESTING CORRECTION
# ============================================================

if not results_df.empty:

    results_df["adjusted_p_value"] = multipletests(
        results_df["p_value"],
        method="fdr_bh"
    )[1]

    results_df = results_df.sort_values(
        by="adjusted_p_value"
    )

    significant_words = results_df[
        results_df["adjusted_p_value"] < 0.05
    ]

    fraud_associated = significant_words[
        significant_words["difference"] > 0
    ]

    genuine_associated = significant_words[
        significant_words["difference"] < 0
    ]

else:

    significant_words = results_df
    fraud_associated = results_df
    genuine_associated = results_df


# ============================================================
# STEP 9: DISPLAY STATISTICAL RESULTS
# ============================================================

print("\nSTATISTICAL ANALYSIS RESULTS")
print("=" * 70)

print("Words passing frequency filters:", len(results_df))

print("Statistically significant words:", len(significant_words))

print("Fraud-associated words:", len(fraud_associated))

print("Genuine-associated words:", len(genuine_associated))


# ============================================================
# STEP 10: DISPLAY TOP FRAUD-ASSOCIATED WORDS
# ============================================================

print("\nTOP FRAUD-ASSOCIATED WORDS")
print("=" * 70)

if not fraud_associated.empty:

    print(
        fraud_associated.sort_values(
            by="difference",
            ascending=False
        )[
            [
                "word",
                "genuine_profiles",
                "fraud_profiles",
                "genuine_rate",
                "fraud_rate",
                "difference",
                "adjusted_p_value"
            ]
        ].head(20).to_string(index=False)
    )

else:

    print("No significant fraud-associated words found.")


# ============================================================
# STEP 11: DISPLAY TOP GENUINE-ASSOCIATED WORDS
# ============================================================

print("\nTOP GENUINE-ASSOCIATED WORDS")
print("=" * 70)

if not genuine_associated.empty:

    print(
        genuine_associated.sort_values(
            by="difference",
            ascending=True
        )[
            [
                "word",
                "genuine_profiles",
                "fraud_profiles",
                "genuine_rate",
                "fraud_rate",
                "difference",
                "adjusted_p_value"
            ]
        ].head(20).to_string(index=False)
    )

else:

    print("No significant genuine-associated words found.")


# ============================================================
# STEP 12: SAVE RESULTS
# ============================================================

output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

results_df.to_csv(
    output_folder / "unique_profile_word_analysis.csv",
    index=False
)

fraud_associated.to_csv(
    output_folder / "unique_profile_fraud_vocabulary.csv",
    index=False
)

genuine_associated.to_csv(
    output_folder / "unique_profile_genuine_vocabulary.csv",
    index=False
)

unique_profiles.drop(
    columns=["normalized_profile"]
).to_csv(
    output_folder / "unique_company_profile_summary.csv",
    index=False
)


# ============================================================
# STEP 13: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 70)

print("Available profile postings:", len(df))

print("Unique profile descriptions:", len(unique_profiles))

print("Genuine unique profiles:", genuine_total)

print("Fraudulent unique profiles:", fraudulent_total)

print("Vocabulary tested:", len(results_df))

print("Significant vocabulary:", len(significant_words))

print("\nFILES SAVED:")
print("1. unique_profile_word_analysis.csv")
print("2. unique_profile_fraud_vocabulary.csv")
print("3. unique_profile_genuine_vocabulary.csv")
print("4. unique_company_profile_summary.csv")

print("\nUNIQUE PROFILE DOCUMENT ANALYSIS COMPLETED!")
