import pandas as pd

# STEP 1: Load dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")


# STEP 2: Create engineered features

df["description_length"] = (
    df["description"].replace("Not Specified", "").str.len()
)

df["requirements_length"] = (
    df["requirements"].replace("Not Specified", "").str.len()
)

df["benefits_length"] = (
    df["benefits"].replace("Not Specified", "").str.len()
)

df["missing_company_profile"] = (
    df["company_profile"] == "Not Specified"
).astype(int)

df["missing_requirements"] = (
    df["requirements"] == "Not Specified"
).astype(int)

df["missing_benefits"] = (
    df["benefits"] == "Not Specified"
).astype(int)

df["short_description"] = (
    df["description_length"] < 200
).astype(int)

placeholder_phrases = [
    "descripción de prueba",
    "description of test",
    "test description",
    "build a website",
    "lorem ipsum"
]

df["placeholder_description"] = (
    df["description"]
    .str.lower()
    .apply(
        lambda text: int(
            any(phrase in text for phrase in placeholder_phrases)
        )
    )
)

missing_columns = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits"
]

df["missing_information_count"] = (
    df[missing_columns].sum(axis=1)
)


# STEP 3: Analyse binary features

binary_features = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description"
]

for feature in binary_features:

    print("\nFEATURE:", feature)
    print("=" * 50)

    result = df.groupby(feature)["fraudulent"].agg(
        total_postings="count",
        fraudulent_postings="sum",
        fraud_rate="mean"
    )

    result["fraud_rate"] = (
        result["fraud_rate"] * 100
    ).round(2)

    print(result)

    # STEP 4: Compare text lengths by fraud label

length_features = [
    "description_length",
    "requirements_length",
    "benefits_length"
]

for feature in length_features:

    print("\nFEATURE:", feature)
    print("=" * 50)

    result = df.groupby("fraudulent")[feature].agg(
        count="count",
        mean="mean",
        median="median",
        minimum="min",
        maximum="max"
    )

    print(result.round(2))

    # STEP 5: Visualise text length distributions

import matplotlib.pyplot as plt

length_features = [
    "description_length",
    "requirements_length",
    "benefits_length"
]

for feature in length_features:

    plt.figure(figsize=(9, 5))

    genuine = df[df["fraudulent"] == 0][feature]
    fraudulent = df[df["fraudulent"] == 1][feature]

    plt.hist(
        genuine,
        bins=50,
        alpha=0.6,
        label="Genuine",
        density=True
    )

    plt.hist(
        fraudulent,
        bins=50,
        alpha=0.6,
        label="Fraudulent",
        density=True
    )

    plt.title(f"{feature} Distribution")
    plt.xlabel("Number of Characters")
    plt.ylabel("Density")
    plt.legend()

    plt.tight_layout()
    plt.show()