import pandas as pd


# STEP 1: Load dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# STEP 2: Define suspicious phrase categories

suspicious_phrases = {

    "payment_request": [
        "registration fee",
        "processing fee",
        "pay a fee",
        "payment required",
        "upfront payment"
    ],

    "guaranteed_job": [
        "guaranteed job",
        "guaranteed employment",
        "100% placement",
        "job guaranteed"
    ],

    "bank_information": [
        "bank account details",
        "bank details",
        "credit card details"
    ],

    "urgency_language": [
        "apply immediately",
        "urgent hiring",
        "limited vacancies",
        "immediate joining"
    ],

    "unrealistic_salary": [
        "earn money instantly",
        "earn thousands daily",
        "unlimited income guaranteed"
    ]
}


# STEP 3: Combine relevant text columns

text_columns = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits"
]

combined_text = (
    df[text_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.lower()
)


# STEP 4: Detect phrase categories

for category, phrases in suspicious_phrases.items():

    df[category] = combined_text.apply(
        lambda text: int(
            any(phrase in text for phrase in phrases)
        )
    )


# STEP 5: Compare genuine and fraudulent jobs

feature_columns = list(suspicious_phrases.keys())

print("\nSUSPICIOUS LANGUAGE ANALYSIS")
print("=" * 65)

print(
    df.groupby("fraudulent")[feature_columns]
    .mean()
    .round(4)
)


# STEP 6: Count phrase occurrences by category

print("\nDETECTED POSTINGS")
print("=" * 65)

for category in feature_columns:

    print("\n", category)

    print(
        df.groupby("fraudulent")[category]
        .sum()
    )


print("\nSUSPICIOUS LANGUAGE ANALYSIS COMPLETED!")