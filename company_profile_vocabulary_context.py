
import pandas as pd
import re


# ============================================================
# STEP 1: LOAD CLEANED DATASET
# ============================================================

input_path = "data/processed/jobs_cleaned.csv"

df = pd.read_csv(input_path)

print("\nCOMPANY PROFILE VOCABULARY CONTEXT ANALYSIS")
print("=" * 65)

print("Dataset shape:", df.shape)


# ============================================================
# STEP 2: VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [
    "company_profile",
    "fraudulent"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("Required columns verified!")


# ============================================================
# STEP 3: REMOVE MISSING COMPANY PROFILES
# ============================================================

df["company_profile"] = (
    df["company_profile"]
    .fillna("")
    .astype(str)
)

df = df[
    (df["company_profile"] != "") &
    (df["company_profile"] != "Not Specified")
].copy()

print("\nAVAILABLE COMPANY PROFILES")
print("=" * 65)

print(
    "Genuine profiles:",
    (df["fraudulent"] == 0).sum()
)

print(
    "Fraudulent profiles:",
    (df["fraudulent"] == 1).sum()
)


# ============================================================
# STEP 4: SELECT WORDS FOR CONTEXT ANALYSIS
# ============================================================

selected_words = [
    # Fraud-associated words
    "leveraging",
    "industry",
    "staffing",
    "recruiting",
    "solutions",
    "hired",
    "aptitude",
    "package",
    "career",
    "referral",

    # Genuine-associated words
    "work",
    "world",
    "companies",
    "team",
    "company",
    "people",
    "working",
    "customers",
    "quality"
]

print("\nWORDS SELECTED:", len(selected_words))


# ============================================================
# STEP 5: EXTRACT CONTEXT AROUND EACH WORD
# ============================================================

MAX_EXAMPLES_PER_CLASS = 10
CONTEXT_LENGTH = 100

results = []

for word in selected_words:

    pattern = re.compile(
        r"\b" + re.escape(word) + r"\b",
        re.IGNORECASE
    )

    for label in [0, 1]:

        class_name = (
            "Genuine" if label == 0
            else "Fraudulent"
        )

        matching_profiles = df[
            df["fraudulent"] == label
        ]

        example_count = 0

        for _, row in matching_profiles.iterrows():

            profile = row["company_profile"]

            match = pattern.search(profile)

            if match is None:
                continue

            start = max(
                0,
                match.start() - CONTEXT_LENGTH
            )

            end = min(
                len(profile),
                match.end() + CONTEXT_LENGTH
            )

            context = profile[start:end]

            if start > 0:
                context = "..." + context

            if end < len(profile):
                context = context + "..."

            results.append({
                "word": word,
                "profile_type": class_name,
                "fraudulent": label,
                "context": context
            })

            example_count += 1

            if example_count >= MAX_EXAMPLES_PER_CLASS:
                break


# ============================================================
# STEP 6: CREATE RESULTS DATAFRAME
# ============================================================

context_df = pd.DataFrame(results)

print("\nCONTEXT EXTRACTION SUMMARY")
print("=" * 65)

print("Total extracted examples:", len(context_df))

if not context_df.empty:

    print("\nExamples by profile type:")

    print(
        context_df["profile_type"]
        .value_counts()
    )


# ============================================================
# STEP 7: DISPLAY CONTEXT EXAMPLES
# ============================================================

print("\nCOMPANY PROFILE WORD CONTEXTS")
print("=" * 65)

if not context_df.empty:

    for word in selected_words:

        word_examples = context_df[
            context_df["word"] == word
        ]

        if word_examples.empty:
            continue

        print(f"\nWORD: {word.upper()}")
        print("-" * 65)

        for _, row in word_examples.iterrows():

            print(
                f"\nProfile type: {row['profile_type']}"
            )

            print(
                f"Context: {row['context']}"
            )

else:
    print("No matching contexts were found.")


# ============================================================
# STEP 8: SAVE RESULTS
# ============================================================

output_path = (
    "data/processed/"
    "company_profile_vocabulary_context.csv"
)

context_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# STEP 9: FINAL SUMMARY
# ============================================================

print("\nFINAL SUMMARY")
print("=" * 65)

print("Words investigated:", len(selected_words))

print("Extracted examples:", len(context_df))

print("Output saved to:", output_path)

print("\nCOMPANY PROFILE VOCABULARY CONTEXT ANALYSIS COMPLETED!")
