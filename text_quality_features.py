
import pandas as pd

# STEP 1: Load the cleaned dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# STEP 2: Calculate description length

df["description_length"] = (
    df["description"]
    .fillna("")
    .astype(str)
    .str.len()
)


# STEP 2: Calculate requirements length

df["requirements_length"] = (
    df["requirements"]
    .fillna("")
    .astype(str)
    .str.len()
)


# Display requirements length

print("\nREQUIREMENTS LENGTH FEATURE")
print("=" * 50)

print(
    df[["requirements", "requirements_length"]].head()
)


# Statistical summary

print("\nREQUIREMENTS LENGTH STATISTICS")
print("=" * 50)

print(
    df["requirements_length"].describe()
)

# STEP 3: Calculate benefits length

df["benefits_length"] = (
    df["benefits"]
    .fillna("")
    .astype(str)
    .str.len()
)


# Display benefits length

print("\nBENEFITS LENGTH FEATURE")
print("=" * 50)

print(
    df[["benefits", "benefits_length"]].head()
)


# Statistical summary

print("\nBENEFITS LENGTH STATISTICS")
print("=" * 50)

print(
    df["benefits_length"].describe()
)

# STEP 4: Create company profile missing indicator

df["missing_company_profile"] = (
    df["company_profile"] == "Not Specified"
).astype(int)


# Display the new feature

print("\nMISSING COMPANY PROFILE FEATURE")
print("=" * 50)

print(
    df[
        ["company_profile", "missing_company_profile"]
    ].head(10)
)


# Count missing and available profiles

print("\nCOMPANY PROFILE AVAILABILITY")
print("=" * 50)

print(
    df["missing_company_profile"].value_counts()
)

print(
    "\nMissing profile percentage:",
    round(
        df["missing_company_profile"].mean() * 100,
        2
    ),
    "%"
)

# STEP 3: Display the new feature

print("\nDESCRIPTION LENGTH FEATURE")
print("=" * 50)

print(
    df[["description", "description_length"]].head()
)


# STEP 4: Generate statistical summary

print("\nDESCRIPTION LENGTH STATISTICS")
print("=" * 50)

print(
    df["description_length"].describe()
)


# STEP 5: Create missing requirements indicator

df["missing_requirements"] = (
    df["requirements"] == "Not Specified"
).astype(int)


# STEP 6: Create missing benefits indicator

df["missing_benefits"] = (
    df["benefits"] == "Not Specified"
).astype(int)


# STEP 7: Display all missing-information features

print("\nMISSING INFORMATION FEATURES")
print("=" * 50)

print(
    df[
        [
            "missing_company_profile",
            "missing_requirements",
            "missing_benefits"
        ]
    ].head(10)
)


# STEP 8: Count missing values

print("\nMISSING INFORMATION COUNTS")
print("=" * 50)

for column in [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits"
]:

    print("\n", column)

    print("Missing postings:", df[column].sum())

    print(
        "Percentage:",
        round(df[column].mean() * 100, 2),
        "%"
    )


# STEP 5: Check very short descriptions

print("\nSHORT DESCRIPTION COUNT")
print("=" * 50)

short_descriptions = (
    df["description_length"] < 200
)

print(
    "Descriptions below 200 characters:",
    short_descriptions.sum()
)

print(
    "Percentage:",
    round(short_descriptions.mean() * 100, 2),
    "%"
)

# STEP 9: Detect placeholder text in job descriptions

placeholder_phrases = [
    "descripción de prueba",
    "description of test",
    "test description",
    "build a website",
    "lorem ipsum"
]

df["placeholder_description"] = (
    df["description"]
    .fillna("")
    .astype(str)
    .str.lower()
    .apply(
        lambda text: int(
            any(
                phrase in text
                for phrase in placeholder_phrases
            )
        )
    )
)


# STEP 10: Display placeholder detection results

print("\nPLACEHOLDER DESCRIPTION ANALYSIS")
print("=" * 50)

print(
    df[
        ["description", "placeholder_description"]
    ].head(10)
)


# STEP 11: Count detected placeholders

print("\nPLACEHOLDER DESCRIPTION COUNTS")
print("=" * 50)

print(
    df["placeholder_description"].value_counts()
)

print(
    "\nPlaceholder percentage:",
    round(
        df["placeholder_description"].mean() * 100,
        2
    ),
    "%"
)
# STEP 12: Compare placeholder descriptions with fraud labels

print("\nPLACEHOLDER VS FRAUD ANALYSIS")
print("=" * 50)

print(
    pd.crosstab(
        df["placeholder_description"],
        df["fraudulent"],
        margins=True
    )
)


# STEP 13: Display the matched descriptions

print("\nMATCHED PLACEHOLDER DESCRIPTIONS")
print("=" * 50)

print(
    df.loc[
        df["placeholder_description"] == 1,
        ["title", "description", "fraudulent"]
    ].to_string(index=False)
)
# STEP 14: Calculate accurate text lengths

text_columns = [
    "description",
    "requirements",
    "benefits"
]

for column in text_columns:

    df[f"{column}_length"] = (
        df[column]
        .replace("Not Specified", "")
        .fillna("")
        .astype(str)
        .str.len()
    )


# STEP 15: Display corrected statistics

print("\nCORRECTED TEXT LENGTH STATISTICS")
print("=" * 50)

for column in text_columns:

    print(f"\n{column.upper()}")

    print(
        df[f"{column}_length"].describe()
    )
    # STEP 14: Identify short job descriptions

df["short_description"] = (
    df["description_length"] < 200
).astype(int)


# STEP 15: Compare short descriptions with fraud labels

print("\nSHORT DESCRIPTION VS FRAUD ANALYSIS")
print("=" * 50)

print(
    pd.crosstab(
        df["short_description"],
        df["fraudulent"],
        margins=True
    )
)


# STEP 16: Calculate fraud rate for short descriptions

print("\nFRAUD RATE BY DESCRIPTION LENGTH GROUP")
print("=" * 50)

print(
    df.groupby("short_description")["fraudulent"].mean() * 100
)

# STEP 17: Count missing information fields

missing_columns = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits"
]

df["missing_information_count"] = (
    df[missing_columns].sum(axis=1)
)


# STEP 18: Analyse fraud rate by missing information count

print("\nMISSING INFORMATION COUNT VS FRAUD")
print("=" * 50)

print(
    df.groupby("missing_information_count")["fraudulent"]
    .agg(["count", "sum", "mean"])
)


# STEP 19: Convert fraud rate into percentage

print("\nFRAUD RATE BY MISSING INFORMATION COUNT")
print("=" * 50)

print(
    (
        df.groupby("missing_information_count")["fraudulent"]
        .mean() * 100
    ).round(2)
)
# STEP: Analyse missing information count

print("\nMISSING INFORMATION COUNT VS FRAUD")
print("=" * 50)

print(
    df.groupby("missing_information_count")["fraudulent"]
    .agg(["count", "sum", "mean"])
)

print("\nFRAUD RATE BY MISSING INFORMATION COUNT")
print("=" * 50)

print(
    (
        df.groupby("missing_information_count")["fraudulent"]
        .mean() * 100
    ).round(2)
)