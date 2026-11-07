import pandas as pd
import re


# STEP 1: Load dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# STEP 2: Select text columns

text_columns = [
    "company_profile",
    "description",
    "requirements",
    "benefits"
]


# STEP 3: Combine text

combined_text = (
    df[text_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
)


# STEP 4: Detect email addresses

email_pattern = (
    r'\b[A-Za-z0-9._%+-]+@'
    r'[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

df["email_count"] = combined_text.apply(
    lambda text: len(
        re.findall(email_pattern, text)
    )
)


# STEP 5: Detect URLs

url_pattern = r'https?://[^\s]+|www\.[^\s]+'

df["url_count"] = combined_text.apply(
    lambda text: len(
        re.findall(url_pattern, text, flags=re.IGNORECASE)
    )
)


# STEP 6: Detect phone-like sequences

phone_pattern = r'\b(?:\+?\d[\d\s().-]{7,}\d)\b'

df["phone_count"] = combined_text.apply(
    lambda text: len(
        re.findall(phone_pattern, text)
    )
)


# STEP 7: Compare genuine and fraudulent jobs

features = [
    "email_count",
    "url_count",
    "phone_count"
]

print("\nCONTACT INFORMATION ANALYSIS")
print("=" * 60)

print(
    df.groupby("fraudulent")[features]
    .agg(["mean", "median", "max"])
)


# STEP 8: Count postings containing contact information

print("\nPOSTINGS WITH CONTACT INFORMATION")
print("=" * 60)

for feature in features:

    print("\n", feature)

    print(
        df.groupby("fraudulent")[feature]
        .apply(lambda values: (values > 0).sum())
    )


print("\nCONTACT INFORMATION ANALYSIS COMPLETED!")