import pandas as pd

# STEP 1: Load cleaned dataset
df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)

# STEP 2: Identify missing company profiles
df["company_profile_missing"] = (
    df["company_profile"] == "Not Specified"
)

# STEP 3: Count genuine and fraudulent postings
print("\nCOMPANY PROFILE AVAILABILITY")
print("=" * 60)

print(
    pd.crosstab(
        df["company_profile_missing"],
        df["fraudulent"],
        margins=True
    )
)

# STEP 4: Calculate fraud percentages
print("\nFRAUD RATE BY COMPANY PROFILE AVAILABILITY")
print("=" * 60)

fraud_rates = df.groupby(
    "company_profile_missing"
)["fraudulent"].mean() * 100

print(fraud_rates)

# STEP 5: Display group sizes
print("\nNUMBER OF JOB POSTINGS")
print("=" * 60)

print(
    df["company_profile_missing"].value_counts()
)

print("\nCOMPANY PROFILE ANALYSIS COMPLETED!")