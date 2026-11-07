import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Total job postings
print("TOTAL JOB POSTINGS:", len(df))

# Genuine and fraudulent jobs
print("\nFRAUD DISTRIBUTION:")
print(df["fraudulent"].value_counts())

# Fraud percentage for company logo
print("\nFRAUD RATE BY COMPANY LOGO:")
print(
    df.groupby("has_company_logo")["fraudulent"].mean() * 100
)

# Fraud percentage for screening questions
print("\nFRAUD RATE BY SCREENING QUESTIONS:")
print(
    df.groupby("has_questions")["fraudulent"].mean() * 100
)

# Fraud percentage for telecommuting
print("\nFRAUD RATE BY TELECOMMUTING:")
print(
    df.groupby("telecommuting")["fraudulent"].mean() * 100
)