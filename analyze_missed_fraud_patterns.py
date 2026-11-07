import pandas as pd

# STEP 1: Load false-negative dataset
df = pd.read_csv(
    "data/processed/missing_profile_false_negatives.csv"
)

print("\nAVAILABLE COLUMNS:")
print(df.columns.tolist())

print("\nMISSED FRAUD PATTERN ANALYSIS")
print("=" * 60)

print("\nTOTAL MISSED POSTINGS:", len(df))


# STEP 2: Missing information analysis
columns = [
    "location",
    "department",
    "industry",
    "employment_type"
]

print("\nMISSING INFORMATION ANALYSIS")
print("=" * 60)

for column in columns:
    missing_count = (df[column] == "Not Specified").sum()

    percentage = (missing_count / len(df)) * 100

    print(
        f"{column}: {missing_count} "
        f"({percentage:.2f}%)"
    )


# STEP 3: Description length
df["description_length"] = (
    df["description"].fillna("").str.len()
)

print("\nDESCRIPTION LENGTH STATISTICS")
print("=" * 60)

print(df["description_length"].describe())


# STEP 4: Title length
df["title_length"] = (
    df["title"].fillna("").str.len()
)

print("\nTITLE LENGTH STATISTICS")
print("=" * 60)

print(df["title_length"].describe())


# STEP 5: Five shortest descriptions
print("\nFIVE SHORTEST JOB DESCRIPTIONS")
print("=" * 60)

shortest = df.nsmallest(5, "description_length")

for _, row in shortest.iterrows():

    print("\nTitle:", row["title"])

    print("Description:", row["description"])

    print("Length:", row["description_length"])


print("\nPATTERN ANALYSIS COMPLETED!")

# STEP 6: Requirements and benefits analysis

print("\nREQUIREMENTS AND BENEFITS ANALYSIS")
print("=" * 60)

for column in ["requirements", "benefits"]:

    missing_count = (
        df[column].isna() |
        (df[column] == "Not Specified") |
        (df[column].str.strip() == "")
    ).sum()

    percentage = (missing_count / len(df)) * 100

    print(
        f"{column}: {missing_count} "
        f"({percentage:.2f}%)"
    )