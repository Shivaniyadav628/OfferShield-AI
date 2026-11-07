
import re
import pandas as pd
import numpy as np

from pathlib import Path
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests


# ============================================================
# STEP 1: LOAD DATA
# ============================================================

base_path = Path("data/processed")

data_path = base_path / "jobs_cleaned.csv"

family_path = (
    base_path / "company_profile_word_family_analysis.csv"
)

df = pd.read_csv(data_path)

family_df = pd.read_csv(family_path)

print("\nCORRECTED WORD-LEVEL VS WORD-FAMILY COMPARISON")
print("=" * 80)

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
    ["genuine", "fraudulent"],
    default="mixed"
)

unique_profiles = unique_profiles[
    unique_profiles["profile_label"] != "mixed"
].copy()

genuine_total = (
    unique_profiles["profile_label"] == "genuine"
).sum()

fraud_total = (
    unique_profiles["profile_label"] == "fraudulent"
).sum()

print("\nUNIQUE PROFILE SUMMARY")
print("=" * 80)

print("Unique profiles:", len(unique_profiles))
print("Genuine-labelled profiles:", genuine_total)
print("Fraudulent-labelled profiles:", fraud_total)


# ============================================================
# STEP 3: TOKENIZE PROFILES
# ============================================================

def tokenize_profile(text):

    return set(
        re.findall(r"[a-z]{3,}", text)
    )


unique_profiles["tokens"] = (
    unique_profiles["normalized_profile"]
    .apply(tokenize_profile)
)


# ============================================================
# STEP 4: DEFINE THE SAME 23 WORD FAMILIES
# ============================================================

word_families = {

    "recruitment": [
        "recruit", "recruits", "recruited",
        "recruiting", "recruitment",
        "recruiter", "recruiters"
    ],

    "hiring": [
        "hire", "hires", "hired", "hiring"
    ],

    "career": [
        "career", "careers"
    ],

    "staffing": [
        "staffing"
    ],

    "leverage": [
        "leverage", "leverages",
        "leveraged", "leveraging"
    ],

    "provide": [
        "provide", "provides",
        "provided", "providing"
    ],

    "develop": [
        "develop", "develops", "developed",
        "developing", "development", "developments"
    ],

    "achieve": [
        "achieve", "achieves", "achieved",
        "achieving", "achievement", "achievements"
    ],

    "efficient": [
        "efficient", "efficiently", "efficiency"
    ],

    "partner": [
        "partner", "partners", "partnered",
        "partnering", "partnership", "partnerships"
    ],

    "goal": [
        "goal", "goals"
    ],

    "resource": [
        "resource", "resources"
    ],

    "system": [
        "system", "systems"
    ],

    "communication": [
        "communication", "communications"
    ],

    "focus": [
        "focus", "focuses", "focused", "focusing"
    ],

    "venture": [
        "venture", "ventures"
    ],

    "model": [
        "model", "models", "modeled", "modeling"
    ],

    "professional": [
        "professional", "professionals", "professionally"
    ],

    "direct": [
        "direct", "directly"
    ],

    "effort": [
        "effort", "efforts"
    ],

    "geographical": [
        "geographic", "geographical", "geographically"
    ],

    "department": [
        "department", "departments"
    ],

    "exciting": [
        "excite", "excites", "excited",
        "exciting", "excitement"
    ]
}


# ============================================================
# STEP 5: VERIFY WORD FAMILY DEFINITIONS
# ============================================================

word_mapping = []

for family, words in word_families.items():

    for word in words:

        word_mapping.append({
            "family": family,
            "word": word
        })

mapping_df = pd.DataFrame(word_mapping)

overlapping_words = mapping_df[
    mapping_df["word"].duplicated(keep=False)
]["word"].unique()

if len(overlapping_words) > 0:

    raise ValueError(
        f"Overlapping word forms: {overlapping_words}"
    )

all_words = mapping_df["word"].tolist()

print("\nWORD FAMILY MAPPING")
print("=" * 80)

print("Number of families:", len(word_families))
print("Total individual word forms:", len(all_words))


# ============================================================
# STEP 6: COUNT EVERY INDIVIDUAL WORD
# ============================================================

individual_results = []

for word in all_words:

    genuine_count = 0
    fraud_count = 0

    for _, row in unique_profiles.iterrows():

        if word in row["tokens"]:

            if row["profile_label"] == "genuine":

                genuine_count += 1

            elif row["profile_label"] == "fraudulent":

                fraud_count += 1

    genuine_absent = genuine_total - genuine_count

    fraud_absent = fraud_total - fraud_count

    genuine_rate = genuine_count / genuine_total

    fraud_rate = fraud_count / fraud_total

    contingency_table = [

        [fraud_count, fraud_absent],

        [genuine_count, genuine_absent]

    ]

    _, p_value = fisher_exact(contingency_table)

    if genuine_rate > 0:

        rate_ratio = fraud_rate / genuine_rate

    elif fraud_rate > 0:

        rate_ratio = np.inf

    else:

        rate_ratio = np.nan

    individual_results.append({

        "word": word,

        "genuine_profiles": genuine_count,

        "fraud_profiles": fraud_count,

        "genuine_rate": genuine_rate,

        "fraud_rate": fraud_rate,

        "difference": fraud_rate - genuine_rate,

        "rate_ratio": rate_ratio,

        "p_value": p_value

    })


individual_df = pd.DataFrame(individual_results)


# ============================================================
# STEP 7: APPLY MULTIPLE TESTING CORRECTION
# ============================================================

individual_df["adjusted_p_value"] = multipletests(
    individual_df["p_value"],
    method="fdr_bh"
)[1]

individual_df["significant"] = (
    individual_df["adjusted_p_value"] < 0.05
)

individual_df["fraud_associated"] = (
    individual_df["fraud_rate"] >
    individual_df["genuine_rate"]
)

print("\nINDIVIDUAL WORD ANALYSIS")
print("=" * 80)

print("Individual word forms tested:", len(individual_df))

print(
    "Significant individual words:",
    individual_df["significant"].sum()
)

print(
    "Fraud-associated individual words:",
    individual_df["fraud_associated"].sum()
)


# ============================================================
# STEP 8: MATCH INDIVIDUAL WORDS WITH FAMILIES
# ============================================================

matched_words = mapping_df.merge(
    individual_df,
    on="word",
    how="left"
)

print("\nWORD-FAMILY MATCHING")
print("=" * 80)

print("Family-word mappings:", len(mapping_df))

print("Matched individual word records:", len(matched_words))

print(
    "Missing individual word results:",
    matched_words["adjusted_p_value"].isna().sum()
)


# ============================================================
# STEP 9: SUMMARISE INDIVIDUAL WORDS BY FAMILY
# ============================================================

family_summaries = []

for family, group in matched_words.groupby("family"):

    significant_words = group[
        group["significant"]
    ]

    fraud_associated_words = group[
        group["fraud_associated"]
    ]

    valid = group.dropna(
        subset=["adjusted_p_value"]
    )

    if valid.empty:
        continue

    strongest_word = valid.sort_values(
        by="adjusted_p_value"
    ).iloc[0]

    family_summaries.append({

        "family": family,

        "individual_word_forms": len(valid),

        "significant_individual_words": len(
            significant_words
        ),

        "fraud_associated_individual_words": len(
            fraud_associated_words
        ),

        "strongest_individual_word": (
            strongest_word["word"]
        ),

        "strongest_individual_adjusted_p": (
            strongest_word["adjusted_p_value"]
        )

    })


individual_family_summary = pd.DataFrame(
    family_summaries
)


# ============================================================
# STEP 10: PREPARE EXISTING FAMILY RESULTS
# ============================================================

required_family_columns = [
    "family",
    "genuine_profiles",
    "fraud_profiles",
    "genuine_rate",
    "fraud_rate",
    "rate_ratio",
    "adjusted_p_value"
]

missing_columns = [
    column for column in required_family_columns
    if column not in family_df.columns
]

if missing_columns:

    raise ValueError(
        f"Family results missing columns: {missing_columns}"
    )

family_results = family_df[
    required_family_columns
].copy()

family_results["family_significant"] = (
    family_results["adjusted_p_value"] < 0.05
)

family_results["family_fraud_associated"] = (
    family_results["fraud_rate"] >
    family_results["genuine_rate"]
)


# ============================================================
# STEP 11: COMPARE BOTH ANALYSIS LEVELS
# ============================================================

comparison = family_results.merge(
    individual_family_summary,
    on="family",
    how="left"
)

comparison["family_has_significant_individual_word"] = (
    comparison["significant_individual_words"] > 0
)

comparison["family_significant_but_no_individual_word"] = (
    comparison["family_significant"] &
    ~comparison["family_has_significant_individual_word"]
)

comparison["comparison_result"] = np.select(

    [
        (
            comparison["family_significant"] &
            comparison["family_has_significant_individual_word"]
        ),

        (
            comparison["family_significant"] &
            ~comparison["family_has_significant_individual_word"]
        ),

        (
            ~comparison["family_significant"] &
            comparison["family_has_significant_individual_word"]
        )

    ],

    [
        "Significant at both levels",
        "Significant only as a family",
        "Significant only as individual words"
    ],

    default="Not significant at either level"

)


# ============================================================
# STEP 12: DISPLAY INDIVIDUAL WORD RESULTS
# ============================================================

print("\nALL INDIVIDUAL WORD RESULTS")
print("=" * 100)

print(

    individual_df.sort_values(
        by="adjusted_p_value"
    )[
        [
            "word",
            "genuine_profiles",
            "fraud_profiles",
            "genuine_rate",
            "fraud_rate",
            "rate_ratio",
            "adjusted_p_value"
        ]

    ].to_string(index=False)

)


# ============================================================
# STEP 13: DISPLAY FAMILY COMPARISON
# ============================================================

display_columns = [

    "family",

    "individual_word_forms",

    "significant_individual_words",

    "fraud_profiles",

    "fraud_rate",

    "rate_ratio",

    "adjusted_p_value",

    "comparison_result"

]

comparison = comparison.sort_values(
    by="adjusted_p_value"
)

print("\nCORRECTED WORD-LEVEL VS WORD-FAMILY RESULTS")
print("=" * 110)

print(
    comparison[display_columns].to_string(
        index=False
    )
)


# ============================================================
# STEP 14: COMPARISON SUMMARY
# ============================================================

print("\nCOMPARISON SUMMARY")
print("=" * 80)

print(
    "Families significant at both levels:",
    (
        comparison["comparison_result"]
        == "Significant at both levels"
    ).sum()
)

print(
    "Families significant only as families:",
    (
        comparison["comparison_result"]
        == "Significant only as a family"
    ).sum()
)

print(
    "Families significant only as individual words:",
    (
        comparison["comparison_result"]
        == "Significant only as individual words"
    ).sum()
)

print(
    "Families not significant at either level:",
    (
        comparison["comparison_result"]
        == "Not significant at either level"
    ).sum()
)


# ============================================================
# STEP 15: IDENTIFY FAMILY-ONLY SIGNIFICANT RESULTS
# ============================================================

family_only = comparison[
    comparison["comparison_result"]
    == "Significant only as a family"
].copy()

print("\nSIGNIFICANT ONLY AFTER WORD GROUPING")
print("=" * 80)

if not family_only.empty:

    print(
        family_only[
            [
                "family",
                "fraud_profiles",
                "fraud_rate",
                "rate_ratio",
                "adjusted_p_value"
            ]
        ].to_string(index=False)
    )

else:

    print("No family-only significant results found.")


# ============================================================
# STEP 16: SAVE UPDATED RESULTS
# ============================================================

individual_df.to_csv(
    base_path / "all_word_forms_unique_profile_analysis.csv",
    index=False
)

matched_words.to_csv(
    base_path / "individual_words_with_family_mapping.csv",
    index=False
)

comparison.to_csv(
    base_path / "company_profile_word_family_comparison.csv",
    index=False
)

family_only.to_csv(
    base_path / "family_only_significant_words.csv",
    index=False
)


# ============================================================
# STEP 17: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 80)

print("Unique profiles analysed:", len(unique_profiles))

print("Individual word forms tested:", len(individual_df))

print("Word families compared:", len(comparison))

print(
    "Significant individual words:",
    individual_df["significant"].sum()
)

print(
    "Significant word families:",
    comparison["family_significant"].sum()
)

print("\nFILES SAVED:")

print("1. all_word_forms_unique_profile_analysis.csv")

print("2. individual_words_with_family_mapping.csv")

print("3. company_profile_word_family_comparison.csv")

print("4. family_only_significant_words.csv")

print("\nCORRECTED WORD FAMILY COMPARISON COMPLETED!")
