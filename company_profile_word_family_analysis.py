
import re
import pandas as pd
import numpy as np

from pathlib import Path
from collections import Counter
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests


# ============================================================
# STEP 1: LOAD THE CLEANED DATASET
# ============================================================

base_path = Path("data/processed")

data_path = base_path / "jobs_cleaned.csv"

df = pd.read_csv(data_path)

print("\nCOMPANY PROFILE WORD FAMILY ANALYSIS")
print("=" * 75)

print("Original dataset shape:", df.shape)


# ============================================================
# STEP 2: PREPARE UNIQUE COMPANY PROFILES
# ============================================================

profiles = df[
    df["company_profile"].notna()
].copy()

profiles["normalized_profile"] = (
    profiles["company_profile"]
    .astype(str)
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

profiles = profiles[
    profiles["normalized_profile"] != "not specified"
].copy()

unique_profiles = (
    profiles.groupby("normalized_profile")
    .agg(
        posting_count=("fraudulent", "size"),
        genuine_postings=("fraudulent", lambda x: (x == 0).sum()),
        fraudulent_postings=("fraudulent", lambda x: (x == 1).sum())
    )
    .reset_index()
)

unique_profiles["profile_label"] = np.select(
    [
        (
            (unique_profiles["genuine_postings"] > 0) &
            (unique_profiles["fraudulent_postings"] == 0)
        ),
        (
            (unique_profiles["fraudulent_postings"] > 0) &
            (unique_profiles["genuine_postings"] == 0)
        )
    ],
    [
        "genuine",
        "fraudulent"
    ],
    default="mixed"
)

unique_profiles = unique_profiles[
    unique_profiles["profile_label"] != "mixed"
].copy()

print("\nUNIQUE PROFILE SUMMARY")
print("=" * 75)

print("Unique profiles:", len(unique_profiles))

print(
    unique_profiles["profile_label"]
    .value_counts()
    .to_string()
)


# ============================================================
# STEP 3: TOKENIZE EACH UNIQUE PROFILE
# ============================================================

def tokenize_profile(text):

    words = re.findall(r"[a-z]{3,}", text)

    return set(words)


unique_profiles["tokens"] = (
    unique_profiles["normalized_profile"]
    .apply(tokenize_profile)
)


# ============================================================
# STEP 4: DEFINE MORPHOLOGICAL WORD FAMILIES
# ============================================================

# Related word forms are grouped manually.
# We only group forms that represent a reasonably
# consistent underlying word or concept.

word_families = {

    "recruitment": [
        "recruit",
        "recruits",
        "recruited",
        "recruiting",
        "recruitment",
        "recruiter",
        "recruiters"
    ],

    "hiring": [
        "hire",
        "hires",
        "hired",
        "hiring"
    ],

    "career": [
        "career",
        "careers"
    ],

    "staffing": [
        "staffing"
    ],

    "leverage": [
        "leverage",
        "leverages",
        "leveraged",
        "leveraging"
    ],

    "provide": [
        "provide",
        "provides",
        "provided",
        "providing"
    ],

    "develop": [
        "develop",
        "develops",
        "developed",
        "developing",
        "development",
        "developments"
    ],

    "achieve": [
        "achieve",
        "achieves",
        "achieved",
        "achieving",
        "achievement",
        "achievements"
    ],

    "efficient": [
        "efficient",
        "efficiently",
        "efficiency"
    ],

    "partner": [
        "partner",
        "partners",
        "partnered",
        "partnering",
        "partnership",
        "partnerships"
    ],

    "goal": [
        "goal",
        "goals"
    ],

    "resource": [
        "resource",
        "resources"
    ],

    "system": [
        "system",
        "systems"
    ],

    "communication": [
        "communication",
        "communications"
    ],

    "focus": [
        "focus",
        "focuses",
        "focused",
        "focusing"
    ],

    "venture": [
        "venture",
        "ventures"
    ],

    "model": [
        "model",
        "models",
        "modeled",
        "modeling"
    ],

    "professional": [
        "professional",
        "professionals",
        "professionally"
    ],

    "direct": [
        "direct",
        "directly"
    ],

    "effort": [
        "effort",
        "efforts"
    ],

    "geographical": [
        "geographic",
        "geographical",
        "geographically"
    ],

    "department": [
        "department",
        "departments"
    ],

    "exciting": [
        "excite",
        "excites",
        "excited",
        "exciting",
        "excitement"
    ]
}


# ============================================================
# STEP 5: CHECK FOR OVERLAPPING WORD FAMILIES
# ============================================================

all_family_words = []

for family, words in word_families.items():

    all_family_words.extend(words)

word_counts = Counter(all_family_words)

overlapping_words = [
    word
    for word, count in word_counts.items()
    if count > 1
]

if overlapping_words:

    raise ValueError(
        f"Words assigned to multiple families: {overlapping_words}"
    )

print("\nWORD FAMILY DEFINITION")
print("=" * 75)

print("Number of word families:", len(word_families))

print("Total family word forms:", len(all_family_words))


# ============================================================
# STEP 6: COUNT FAMILY PRESENCE PER UNIQUE PROFILE
# ============================================================

family_results = []

for family, family_words in word_families.items():

    family_word_set = set(family_words)

    genuine_count = 0
    fraud_count = 0

    genuine_member_counts = Counter()
    fraud_member_counts = Counter()

    for _, row in unique_profiles.iterrows():

        profile_tokens = row["tokens"]

        present_words = profile_tokens.intersection(
            family_word_set
        )

        if not present_words:
            continue

        if row["profile_label"] == "genuine":

            genuine_count += 1

            genuine_member_counts.update(present_words)

        elif row["profile_label"] == "fraudulent":

            fraud_count += 1

            fraud_member_counts.update(present_words)

    genuine_total = (
        unique_profiles["profile_label"] == "genuine"
    ).sum()

    fraud_total = (
        unique_profiles["profile_label"] == "fraudulent"
    ).sum()

    genuine_rate = genuine_count / genuine_total

    fraud_rate = fraud_count / fraud_total

    family_results.append({

        "family": family,

        "genuine_profiles": genuine_count,

        "fraud_profiles": fraud_count,

        "genuine_rate": genuine_rate,

        "fraud_rate": fraud_rate,

        "difference": fraud_rate - genuine_rate,

        "genuine_member_counts": dict(genuine_member_counts),

        "fraud_member_counts": dict(fraud_member_counts)

    })


# ============================================================
# STEP 7: STATISTICAL TESTING
# ============================================================

results_df = pd.DataFrame(family_results)

p_values = []

for _, row in results_df.iterrows():

    contingency_table = [

        [
            row["fraud_profiles"],
            (
                (unique_profiles["profile_label"] == "fraudulent").sum()
                - row["fraud_profiles"]
            )
        ],

        [
            row["genuine_profiles"],
            (
                (unique_profiles["profile_label"] == "genuine").sum()
                - row["genuine_profiles"]
            )
        ]

    ]

    _, p_value = fisher_exact(contingency_table)

    p_values.append(p_value)


results_df["p_value"] = p_values

results_df["adjusted_p_value"] = multipletests(
    results_df["p_value"],
    method="fdr_bh"
)[1]


# ============================================================
# STEP 8: CALCULATE RATE RATIOS
# ============================================================

def calculate_rate_ratio(fraud_rate, genuine_rate):

    if genuine_rate == 0:

        if fraud_rate > 0:
            return np.inf

        return np.nan

    return fraud_rate / genuine_rate


results_df["rate_ratio"] = results_df.apply(

    lambda row: calculate_rate_ratio(
        row["fraud_rate"],
        row["genuine_rate"]
    ),

    axis=1
)


# ============================================================
# STEP 9: IDENTIFY FRAUD-ASSOCIATED WORD FAMILIES
# ============================================================

results_df["fraud_associated"] = (
    results_df["fraud_rate"] >
    results_df["genuine_rate"]
)

results_df["statistically_significant"] = (
    results_df["adjusted_p_value"] < 0.05
)

results_df["fraud_associated_significant"] = (
    results_df["fraud_associated"] &
    results_df["statistically_significant"]
)


# ============================================================
# STEP 10: DISPLAY FAMILY ANALYSIS RESULTS
# ============================================================

display_columns = [

    "family",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "difference",
    "rate_ratio",
    "adjusted_p_value"

]

results_df = results_df.sort_values(
    by="fraud_rate",
    ascending=False
)

print("\nWORD FAMILY STATISTICAL RESULTS")
print("=" * 100)

print(
    results_df[display_columns].to_string(
        index=False
    )
)


# ============================================================
# STEP 11: DISPLAY SIGNIFICANT FRAUD-ASSOCIATED FAMILIES
# ============================================================

significant_families = results_df[
    results_df["fraud_associated_significant"]
].copy()

print("\nSIGNIFICANT FRAUD-ASSOCIATED WORD FAMILIES")
print("=" * 100)

print(
    "Number of significant families:",
    len(significant_families)
)

if not significant_families.empty:

    print(
        significant_families[
            display_columns
        ].to_string(index=False)
    )

else:

    print("No significant fraud-associated families found.")


# ============================================================
# STEP 12: SAVE FAMILY MEMBER COUNTS
# ============================================================

member_results = []

for _, row in results_df.iterrows():

    family = row["family"]

    for word, count in row["genuine_member_counts"].items():

        member_results.append({

            "family": family,
            "word": word,
            "label": "genuine",
            "profile_count": count

        })

    for word, count in row["fraud_member_counts"].items():

        member_results.append({

            "family": family,
            "word": word,
            "label": "fraudulent",
            "profile_count": count

        })


member_df = pd.DataFrame(member_results)


# ============================================================
# STEP 13: SAVE OUTPUT FILES
# ============================================================

results_df.drop(
    columns=[
        "genuine_member_counts",
        "fraud_member_counts"
    ]
).to_csv(
    base_path / "company_profile_word_family_analysis.csv",
    index=False
)

significant_families.drop(
    columns=[
        "genuine_member_counts",
        "fraud_member_counts"
    ]
).to_csv(
    base_path / "significant_fraud_word_families.csv",
    index=False
)

member_df.to_csv(
    base_path / "company_profile_word_family_members.csv",
    index=False
)


# ============================================================
# STEP 14: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 75)

print("Unique profiles analysed:", len(unique_profiles))

print("Word families analysed:", len(results_df))

print(
    "Significant fraud-associated families:",
    len(significant_families)
)

print("\nFILES SAVED:")

print("1. company_profile_word_family_analysis.csv")

print("2. significant_fraud_word_families.csv")

print("3. company_profile_word_family_members.csv")

print("\nWORD FAMILY ANALYSIS COMPLETED!")
