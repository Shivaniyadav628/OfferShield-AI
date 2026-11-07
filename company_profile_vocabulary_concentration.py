
import pandas as pd
import re
from pathlib import Path


# ============================================================
# STEP 1: LOAD DATASET
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")

print("\nUNIQUE COMPANY PROFILE CONCENTRATION ANALYSIS")
print("=" * 70)

print("Original dataset shape:", df.shape)


# ============================================================
# STEP 2: CLEAN PROFILE TEXT
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

# Normalise case and whitespace to identify repeated descriptions.
df["normalized_profile"] = (
    df["company_profile"]
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

print("\nPOSTINGS WITH AVAILABLE PROFILES:", len(df))


# ============================================================
# STEP 3: DEFINE SELECTED WORDS
# ============================================================

selected_words = [
    "leveraging",
    "industry",
    "staffing",
    "recruiting",
    "solutions",
    "hired",
    "aptitude",
    "package",
    "direct",
    "career",
    "addition",
    "expert",
    "referred",
    "negotiations",
    "encouraged",
    "participate",
    "represented",
    "town",
    "maximizing",
    "referral"
]

word_patterns = {
    word: re.compile(
        r"\b" + re.escape(word) + r"\b",
        re.IGNORECASE
    )
    for word in selected_words
}


# ============================================================
# STEP 4: GROUP IDENTICAL PROFILE TEXTS
# ============================================================

profile_groups = (
    df.groupby("normalized_profile")
    .agg(
        posting_count=("fraudulent", "size"),
        genuine_postings_count=(
            "fraudulent",
            lambda x: (x == 0).sum()
        ),
        fraudulent_postings_count=(
            "fraudulent",
            lambda x: (x == 1).sum()
        )
    )
    .reset_index()
)

# Create a unique numeric ID for every distinct profile.
profile_groups.insert(
    0,
    "profile_id",
    range(1, len(profile_groups) + 1)
)

# Determine how each profile's associated postings are labelled.
def get_profile_composition(row):

    if row["genuine_postings_count"] > 0 and row["fraudulent_postings_count"] > 0:
        return "Mixed"

    if row["fraudulent_postings_count"] > 0:
        return "Fraudulent-labelled postings only"

    return "Genuine-labelled postings only"


profile_groups["label_composition"] = (
    profile_groups.apply(get_profile_composition, axis=1)
)

print("\nUNIQUE PROFILE SUMMARY")
print("=" * 70)

print("Unique company-profile texts:", len(profile_groups))

print(
    "\nProfile composition:\n",
    profile_groups["label_composition"].value_counts().to_string()
)


# ============================================================
# STEP 5: COUNT WORDS ONCE PER UNIQUE PROFILE
# ============================================================

profile_word_results = []

for _, row in profile_groups.iterrows():

    profile_text = row["normalized_profile"]

    matched_words = [
        word
        for word, pattern in word_patterns.items()
        if pattern.search(profile_text)
    ]

    result = {
        "profile_id": row["profile_id"],
        "posting_count": row["posting_count"],
        "genuine_postings_count": row["genuine_postings_count"],
        "fraudulent_postings_count": row["fraudulent_postings_count"],
        "label_composition": row["label_composition"],
        "selected_word_count": len(matched_words),
        "selected_words": ", ".join(matched_words)
    }

    profile_word_results.append(result)


profile_analysis = pd.DataFrame(profile_word_results)


# ============================================================
# STEP 6: ANALYSE WORD CONCENTRATION
# ============================================================

print("\nUNIQUE PROFILES WITH MULTIPLE SELECTED WORDS")
print("=" * 70)

for minimum_words in [3, 5, 8, 15]:

    count = (
        profile_analysis["selected_word_count"] >= minimum_words
    ).sum()

    print(
        f"Unique profiles containing at least "
        f"{minimum_words} selected words: {count}"
    )


# ============================================================
# STEP 7: IDENTIFY MOST CONCENTRATED UNIQUE PROFILES
# ============================================================

top_profiles = profile_analysis.sort_values(
    by="selected_word_count",
    ascending=False
)

print("\nTOP UNIQUE PROFILES BY WORD CONCENTRATION")
print("=" * 70)

print(
    top_profiles[
        [
            "profile_id",
            "posting_count",
            "genuine_postings_count",
            "fraudulent_postings_count",
            "label_composition",
            "selected_word_count",
            "selected_words"
        ]
    ].head(20).to_string(index=False)
)


# ============================================================
# STEP 8: CREATE WORD-LEVEL CONCENTRATION SUMMARY
# ============================================================

word_summary = []

for word, pattern in word_patterns.items():

    # Find unique profiles containing this word.
    matching = profile_groups[
        profile_groups["normalized_profile"].apply(
            lambda text: bool(pattern.search(text))
        )
    ]

    word_summary.append({
        "word": word,
        "unique_profiles": len(matching),

        "genuine_only_profiles": (
            matching["label_composition"] ==
            "Genuine-labelled postings only"
        ).sum(),

        "fraud_only_profiles": (
            matching["label_composition"] ==
            "Fraudulent-labelled postings only"
        ).sum(),

        "mixed_profiles": (
            matching["label_composition"] == "Mixed"
        ).sum(),

        "genuine_postings_attached": (
            matching["genuine_postings_count"].sum()
        ),

        "fraudulent_postings_attached": (
            matching["fraudulent_postings_count"].sum()
        )
    })


word_summary_df = pd.DataFrame(word_summary)

word_summary_df = word_summary_df.sort_values(
    by="unique_profiles",
    ascending=False
)


# ============================================================
# STEP 9: DISPLAY WORD SUMMARY
# ============================================================

print("\nWORD-LEVEL UNIQUE PROFILE CONCENTRATION")
print("=" * 70)

print(word_summary_df.to_string(index=False))


# ============================================================
# STEP 10: SAVE RESULTS
# ============================================================

output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

profile_analysis.to_csv(
    output_folder / "company_profile_vocabulary_concentration.csv",
    index=False
)

word_summary_df.to_csv(
    output_folder / "vocabulary_word_concentration_summary.csv",
    index=False
)


# ============================================================
# STEP 11: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 70)

print("Total postings with available profiles:", len(df))

print("Unique company-profile texts:", len(profile_analysis))

print(
    "Profiles with only genuine-labelled postings:",
    (profile_analysis["label_composition"] ==
     "Genuine-labelled postings only").sum()
)

print(
    "Profiles with only fraudulent-labelled postings:",
    (profile_analysis["label_composition"] ==
     "Fraudulent-labelled postings only").sum()
)

print(
    "Profiles with mixed posting labels:",
    (profile_analysis["label_composition"] == "Mixed").sum()
)

print("\nFILES SAVED:")
print("1. data/processed/company_profile_vocabulary_concentration.csv")
print("2. data/processed/vocabulary_word_concentration_summary.csv")

print("\nUNIQUE PROFILE CONCENTRATION ANALYSIS COMPLETED!")
