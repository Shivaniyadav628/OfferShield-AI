
import re
from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests


# ============================================================
# 1. PATHS AND SETTINGS
# ============================================================

DATA_PATH = Path("data/processed/jobs_cleaned.csv")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05

# Same tokenization approach used in the earlier analyses.
TOKEN_PATTERN = re.compile(r"[a-z]{3,}")

STOP_WORDS = {
    "company", "companies", "business", "businesses"
}


# ============================================================
# 2. DEFINE THE 23 WORD FAMILIES
# ============================================================

WORD_FAMILIES = {
    "recruitment": [
        "recruit", "recruits", "recruited", "recruiting",
        "recruitment", "recruiter", "recruiters"
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
        "leverage", "leverages", "leveraged", "leveraging"
    ],

    "provide": [
        "provide", "provides", "provided", "providing"
    ],

    "develop": [
        "develop", "develops", "developed", "developing",
        "development", "developments"
    ],

    "achieve": [
        "achieve", "achieves", "achieved", "achieving",
        "achievement", "achievements"
    ],

    "efficient": [
        "efficient", "efficiently", "efficiency"
    ],

    "partner": [
        "partner", "partners", "partnered", "partnering",
        "partnership", "partnerships"
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
# 3. TOKENIZATION FUNCTION
# ============================================================

def tokenize_profile(text):

    text = str(text).lower()

    tokens = TOKEN_PATTERN.findall(text)

    tokens = [
        word for word in tokens
        if word not in STOP_WORDS
    ]

    return set(tokens)


# ============================================================
# 4. LOAD DATASET
# ============================================================

print("\nLOADING CLEANED DATASET")
print("=" * 75)

df = pd.read_csv(DATA_PATH)

print("Original dataset shape:", df.shape)

required_columns = {
    "company_profile",
    "fraudulent"
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# 5. NORMALIZE COMPANY PROFILES
# ============================================================

df["company_profile_normalized"] = (
    df["company_profile"]
    .fillna("")
    .astype(str)
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Remove missing and placeholder profiles.

available_profiles = df[
    (df["company_profile_normalized"] != "") &
    (df["company_profile_normalized"] != "not specified")
].copy()

print("\nPOSTINGS WITH AVAILABLE COMPANY PROFILES")
print("=" * 75)

print("Available postings:", len(available_profiles))


# ============================================================
# 6. CREATE UNIQUE PROFILE DATASET
# ============================================================

profile_summary = (
    available_profiles
    .groupby("company_profile_normalized")
    .agg(
        posting_count=("fraudulent", "size"),
        genuine_postings=("fraudulent", lambda x: (x == 0).sum()),
        fraudulent_postings=("fraudulent", lambda x: (x == 1).sum())
    )
    .reset_index()
)

# Identify profile label composition.

profile_summary["profile_label"] = np.select(
    [
        (
            (profile_summary["genuine_postings"] > 0) &
            (profile_summary["fraudulent_postings"] == 0)
        ),
        (
            (profile_summary["fraudulent_postings"] > 0) &
            (profile_summary["genuine_postings"] == 0)
        ),
        (
            (profile_summary["genuine_postings"] > 0) &
            (profile_summary["fraudulent_postings"] > 0)
        )
    ],
    [
        "genuine",
        "fraudulent",
        "mixed"
    ],
    default="unknown"
)

print("\nUNIQUE PROFILE SUMMARY")
print("=" * 75)

print("Unique profiles:", len(profile_summary))

print(
    profile_summary["profile_label"]
    .value_counts()
    .to_string()
)

# Exclude mixed profiles to maintain the same comparison groups.

profiles = profile_summary[
    profile_summary["profile_label"].isin(
        ["genuine", "fraudulent"]
    )
].copy()

genuine_profiles = profiles[
    profiles["profile_label"] == "genuine"
]

fraud_profiles = profiles[
    profiles["profile_label"] == "fraudulent"
]

N_GENUINE = len(genuine_profiles)
N_FRAUD = len(fraud_profiles)

print("\nFINAL ANALYSIS GROUPS")
print("=" * 75)

print("Genuine-labelled profiles:", N_GENUINE)
print("Fraudulent-labelled profiles:", N_FRAUD)
print("Mixed profiles excluded:", len(profile_summary) - len(profiles))


# ============================================================
# 7. TOKENIZE EACH UNIQUE PROFILE ONCE
# ============================================================

profiles["tokens"] = profiles[
    "company_profile_normalized"
].apply(tokenize_profile)

genuine_token_sets = genuine_profiles[
    "company_profile_normalized"
].map(
    lambda text: tokenize_profile(text)
).tolist()

fraud_token_sets = fraud_profiles[
    "company_profile_normalized"
].map(
    lambda text: tokenize_profile(text)
).tolist()

print("\nTOKENIZATION COMPLETED")
print("=" * 75)

print("Genuine token sets:", len(genuine_token_sets))
print("Fraud token sets:", len(fraud_token_sets))


# ============================================================
# 8. VERIFY WORD FAMILY MAPPING
# ============================================================

all_word_forms = [
    word
    for words in WORD_FAMILIES.values()
    for word in words
]

if len(all_word_forms) != len(set(all_word_forms)):
    raise ValueError(
        "Duplicate word forms found across word families."
    )

print("\nWORD FAMILY MAPPING")
print("=" * 75)

print("Number of families:", len(WORD_FAMILIES))
print("Total word forms:", len(all_word_forms))


# ============================================================
# 9. COMMON FISHER TEST FUNCTION
# ============================================================

def calculate_statistics(
    genuine_present,
    fraud_present,
    genuine_total,
    fraud_total
):

    genuine_absent = genuine_total - genuine_present
    fraud_absent = fraud_total - fraud_present

    contingency_table = [
        [genuine_present, genuine_absent],
        [fraud_present, fraud_absent]
    ]

    odds_ratio, p_value = fisher_exact(
        contingency_table,
        alternative="two-sided"
    )

    genuine_rate = genuine_present / genuine_total
    fraud_rate = fraud_present / fraud_total

    rate_difference = fraud_rate - genuine_rate

    if genuine_rate > 0:
        rate_ratio = fraud_rate / genuine_rate
    elif fraud_rate > 0:
        rate_ratio = np.inf
    else:
        rate_ratio = np.nan

    return {
        "genuine_profiles": genuine_present,
        "fraud_profiles": fraud_present,
        "genuine_absent": genuine_absent,
        "fraud_absent": fraud_absent,
        "genuine_rate": genuine_rate,
        "fraud_rate": fraud_rate,
        "rate_difference": rate_difference,
        "rate_ratio": rate_ratio,
        "odds_ratio": odds_ratio,
        "p_value": p_value
    }


# ============================================================
# 10. INDIVIDUAL WORD-LEVEL ANALYSIS
# ============================================================

print("\nRUNNING INDIVIDUAL WORD ANALYSIS")
print("=" * 75)

individual_results = []

for word in all_word_forms:

    genuine_count = sum(
        word in tokens
        for tokens in genuine_token_sets
    )

    fraud_count = sum(
        word in tokens
        for tokens in fraud_token_sets
    )

    result = calculate_statistics(
        genuine_count,
        fraud_count,
        N_GENUINE,
        N_FRAUD
    )

    result["word"] = word

    individual_results.append(result)


individual_df = pd.DataFrame(individual_results)

# Apply BH correction across all 78 individual word tests.

individual_df["adjusted_p_value"] = multipletests(
    individual_df["p_value"],
    method="fdr_bh"
)[1]

individual_df["significant"] = (
    individual_df["adjusted_p_value"] < ALPHA
)

individual_df["association"] = np.select(
    [
        (
            individual_df["significant"] &
            (individual_df["rate_difference"] > 0)
        ),
        (
            individual_df["significant"] &
            (individual_df["rate_difference"] < 0)
        )
    ],
    [
        "fraud-associated",
        "genuine-associated"
    ],
    default="not significant"
)

individual_df = individual_df.sort_values(
    "adjusted_p_value"
).reset_index(drop=True)

individual_df.to_csv(
    OUTPUT_DIR / "audit_individual_word_results.csv",
    index=False
)

print("Individual words tested:", len(individual_df))

print(
    "Significant individual words:",
    individual_df["significant"].sum()
)

print(
    "Fraud-associated individual words:",
    (
        individual_df["association"] == "fraud-associated"
    ).sum()
)

print(
    "Genuine-associated individual words:",
    (
        individual_df["association"] == "genuine-associated"
    ).sum()
)


# ============================================================
# 11. WORD-FAMILY ANALYSIS
# ============================================================

print("\nRUNNING WORD-FAMILY ANALYSIS")
print("=" * 75)

family_results = []

for family, word_forms in WORD_FAMILIES.items():

    genuine_count = sum(
        any(word in tokens for word in word_forms)
        for tokens in genuine_token_sets
    )

    fraud_count = sum(
        any(word in tokens for word in word_forms)
        for tokens in fraud_token_sets
    )

    result = calculate_statistics(
        genuine_count,
        fraud_count,
        N_GENUINE,
        N_FRAUD
    )

    result["family"] = family
    result["word_forms"] = len(word_forms)
    result["word_form_list"] = ", ".join(word_forms)

    family_results.append(result)


family_df = pd.DataFrame(family_results)

# Apply BH correction across all 23 family tests.

family_df["adjusted_p_value"] = multipletests(
    family_df["p_value"],
    method="fdr_bh"
)[1]

family_df["significant"] = (
    family_df["adjusted_p_value"] < ALPHA
)

family_df["association"] = np.select(
    [
        (
            family_df["significant"] &
            (family_df["rate_difference"] > 0)
        ),
        (
            family_df["significant"] &
            (family_df["rate_difference"] < 0)
        )
    ],
    [
        "fraud-associated",
        "genuine-associated"
    ],
    default="not significant"
)

family_df = family_df.sort_values(
    "adjusted_p_value"
).reset_index(drop=True)

family_df.to_csv(
    OUTPUT_DIR / "audit_word_family_results.csv",
    index=False
)

print("Word families tested:", len(family_df))

print(
    "Significant word families:",
    family_df["significant"].sum()
)


# ============================================================
# 12. MATCH INDIVIDUAL WORDS TO THEIR FAMILIES
# ============================================================

mapping_rows = []

for family, word_forms in WORD_FAMILIES.items():

    for word in word_forms:

        mapping_rows.append({
            "family": family,
            "word": word
        })

mapping_df = pd.DataFrame(mapping_rows)

individual_mapping = mapping_df.merge(
    individual_df,
    on="word",
    how="left",
    validate="one_to_one"
)

if individual_mapping["p_value"].isna().any():
    raise ValueError(
        "Some individual word results are missing."
    )

print("\nWORD-LEVEL MAPPING CHECK")
print("=" * 75)

print("Total mappings:", len(mapping_df))
print("Matched results:", individual_mapping["p_value"].notna().sum())
print("Missing results:", individual_mapping["p_value"].isna().sum())


# ============================================================
# 13. SUMMARIZE INDIVIDUAL WORDS WITHIN EACH FAMILY
# ============================================================

word_summary = (
    individual_mapping
    .groupby("family")
    .agg(
        individual_word_forms=("word", "count"),
        significant_individual_words=("significant", "sum"),
        fraud_associated_words=(
            "association",
            lambda x: (x == "fraud-associated").sum()
        ),
        genuine_associated_words=(
            "association",
            lambda x: (x == "genuine-associated").sum()
        ),
        strongest_individual_word=(
            "word",
            lambda x: x.iloc[
                individual_mapping.loc[x.index, "adjusted_p_value"].argmin()
            ]
        ),
        strongest_individual_adjusted_p=(
            "adjusted_p_value",
            "min"
        )
    )
    .reset_index()
)


# ============================================================
# 14. COMPARE WORD-LEVEL AND FAMILY-LEVEL RESULTS
# ============================================================

comparison_df = family_df.merge(
    word_summary,
    on="family",
    how="left",
    validate="one_to_one"
)

def classify_comparison(row):

    word_significant = row["significant_individual_words"] > 0
    family_significant = row["significant"]

    if word_significant and family_significant:
        return "Significant at both levels"

    if family_significant and not word_significant:
        return "Significant only as a family"

    if word_significant and not family_significant:
        return "Significant only as individual words"

    return "Not significant at either level"


comparison_df["comparison_result"] = comparison_df.apply(
    classify_comparison,
    axis=1
)

comparison_df = comparison_df.sort_values(
    "adjusted_p_value"
).reset_index(drop=True)

comparison_df.to_csv(
    OUTPUT_DIR / "audit_word_family_comparison.csv",
    index=False
)

individual_mapping.to_csv(
    OUTPUT_DIR / "audit_individual_words_with_families.csv",
    index=False
)


# ============================================================
# 15. PRINT INDIVIDUAL WORD RESULTS
# ============================================================

print("\nINDIVIDUAL WORD RESULTS")
print("=" * 100)

print(
    individual_df[
        [
            "word",
            "genuine_profiles",
            "fraud_profiles",
            "genuine_rate",
            "fraud_rate",
            "rate_ratio",
            "adjusted_p_value",
            "association"
        ]
    ].to_string(index=False)
)


# ============================================================
# 16. PRINT WORD-FAMILY RESULTS
# ============================================================

print("\nWORD-FAMILY RESULTS")
print("=" * 100)

print(
    family_df[
        [
            "family",
            "word_forms",
            "genuine_profiles",
            "fraud_profiles",
            "genuine_rate",
            "fraud_rate",
            "rate_ratio",
            "adjusted_p_value",
            "association"
        ]
    ].to_string(index=False)
)


# ============================================================
# 17. PRINT FINAL COMPARISON
# ============================================================

print("\nWORD-LEVEL VS WORD-FAMILY COMPARISON")
print("=" * 110)

print(
    comparison_df[
        [
            "family",
            "individual_word_forms",
            "significant_individual_words",
            "fraud_associated_words",
            "fraud_profiles",
            "fraud_rate",
            "rate_ratio",
            "adjusted_p_value",
            "comparison_result"
        ]
    ].to_string(index=False)
)


# ============================================================
# 18. COMPARISON SUMMARY
# ============================================================

print("\nCOMPARISON SUMMARY")
print("=" * 75)

print(
    "Families significant at both levels:",
    (
        comparison_df["comparison_result"]
        == "Significant at both levels"
    ).sum()
)

print(
    "Families significant only as families:",
    (
        comparison_df["comparison_result"]
        == "Significant only as a family"
    ).sum()
)

print(
    "Families significant only as individual words:",
    (
        comparison_df["comparison_result"]
        == "Significant only as individual words"
    ).sum()
)

print(
    "Families not significant at either level:",
    (
        comparison_df["comparison_result"]
        == "Not significant at either level"
    ).sum()
)


# ============================================================
# 19. FINAL AUDIT SUMMARY
# ============================================================

print("\nFINAL STATISTICAL AUDIT SUMMARY")
print("=" * 75)

print("Unique profiles analysed:", len(profiles))
print("Genuine-labelled profiles:", N_GENUINE)
print("Fraudulent-labelled profiles:", N_FRAUD)

print("Individual word tests:", len(individual_df))
print("Significant individual words:", individual_df["significant"].sum())

print("Word-family tests:", len(family_df))
print("Significant word families:", family_df["significant"].sum())

print("\nMULTIPLE-TESTING CORRECTION")
print("=" * 75)

print("Individual words: Benjamini-Hochberg across 78 tests")
print("Word families: Benjamini-Hochberg across 23 tests")

print("\nFILES SAVED")
print("=" * 75)

print("1. audit_individual_word_results.csv")
print("2. audit_word_family_results.csv")
print("3. audit_word_family_comparison.csv")
print("4. audit_individual_words_with_families.csv")

print("\nSTATISTICAL AUDIT COMPLETED!")
