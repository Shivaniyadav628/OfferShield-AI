
import pandas as pd

# STEP 1: Load dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# STEP 2: Prepare company profile text
profile = (
    df["company_profile"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# Treat the missing-value placeholder as empty text
profile = profile.replace("Not Specified", "")

# STEP 3: Calculate profile length
df["profile_length"] = profile.str.len()

# STEP 4: Calculate word count
df["profile_word_count"] = profile.apply(
    lambda text: len(text.split())
)

# STEP 5: Identify short profiles
df["short_company_profile"] = (
    (df["profile_length"] > 0) &
    (df["profile_length"] < 100)
).astype(int)

# STEP 6: Identify missing profiles
df["missing_company_profile"] = (
    (df["profile_length"] == 0)
).astype(int)

# STEP 7: Compare profile statistics
print("\nCOMPANY PROFILE QUALITY ANALYSIS")
print("=" * 60)

print("\nPROFILE LENGTH STATISTICS")

print(
    df.groupby("fraudulent")["profile_length"]
    .agg(["mean", "median", "min", "max"])
)

print("\nPROFILE WORD COUNT STATISTICS")

print(
    df.groupby("fraudulent")["profile_word_count"]
    .agg(["mean", "median", "min", "max"])
)

# STEP 8: Count short profiles
print("\nSHORT COMPANY PROFILES")
print("=" * 60)

print(
    df.groupby("fraudulent")["short_company_profile"]
    .sum()
)

# STEP 9: Analyse profile length groups
df["profile_length_group"] = pd.cut(
    df["profile_length"],
    bins=[-1, 0, 100, 300, 600, 1000, float("inf")],
    labels=[
        "Missing",
        "1-100",
        "101-300",
        "301-600",
        "601-1000",
        "Above 1000"
    ]
)

print("\nFRAUD DISTRIBUTION BY PROFILE LENGTH")
print("=" * 60)

profile_analysis = pd.crosstab(
    df["profile_length_group"],
    df["fraudulent"],
    margins=True
)

print(profile_analysis)

print("\nFRAUD RATE BY PROFILE LENGTH GROUP")
print("=" * 60)

fraud_rates = (
    df.groupby("profile_length_group", observed=False)["fraudulent"]
    .agg(["count", "sum", "mean"])
)

fraud_rates["fraud_rate_percent"] = (
    fraud_rates["mean"] * 100
)

print(fraud_rates)

print("\nCOMPANY PROFILE QUALITY ANALYSIS COMPLETED!")
