
import pandas as pd
import json
import joblib

from sklearn.model_selection import train_test_split


# STEP 1: Load the cleaned dataset

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]


# STEP 2: Recreate the exact validation split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_subtrain, X_val, y_subtrain, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)


# STEP 3: Load the saved model and preprocessor

model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)


# STEP 4: Load the selected decision threshold

with open(
    "data/processed/best_threshold.json",
    "r"
) as file:

    threshold = json.load(file)["best_threshold"]


# STEP 5: Generate validation decision scores

X_val_processed = preprocessor.transform(X_val)

scores = model.decision_function(X_val_processed)

predictions = (scores >= threshold).astype(int)


# STEP 6: Create the analysis DataFrame

analysis_df = X_val.copy()

# Store scores and predictions in their corresponding rows
analysis_df["Decision_Score"] = scores
analysis_df["Actual"] = y_val.to_numpy()
analysis_df["Predicted"] = predictions

print("\nVALIDATION SCORE CHECK")
print("=" * 65)

print("Number of validation rows:", len(analysis_df))
print("Number of decision scores:", len(scores))
print("Selected threshold:", threshold)


# STEP 7: Find fraudulent postings with missing company profiles

missing_profile = (
    analysis_df["company_profile"] == "Not Specified"
)

fraud_df = analysis_df[
    (analysis_df["Actual"] == 1) &
    missing_profile
].copy()


# STEP 8: Separate detected and missed fraud

detected = fraud_df[
    fraud_df["Predicted"] == 1
].copy()

missed = fraud_df[
    fraud_df["Predicted"] == 0
].copy()


print("\nDETECTED VS MISSED FRAUD ANALYSIS")
print("=" * 65)

print("DETECTED FRAUD:", len(detected))
print("MISSED FRAUD:", len(missed))


# STEP 9: Compare missing information

columns = [
    "location",
    "department",
    "industry",
    "employment_type",
    "required_experience",
    "required_education",
    "salary_range",
    "requirements",
    "benefits"
]

print("\nMISSING INFORMATION COMPARISON")
print("=" * 65)

for column in columns:

    detected_missing = (
        detected[column].isna() |
        (detected[column] == "Not Specified") |
        (detected[column].astype(str).str.strip() == "")
    )

    missed_missing = (
        missed[column].isna() |
        (missed[column] == "Not Specified") |
        (missed[column].astype(str).str.strip() == "")
    )

    detected_pct = (
        detected_missing.mean() * 100
        if len(detected) else 0
    )

    missed_pct = (
        missed_missing.mean() * 100
        if len(missed) else 0
    )

    print(f"\n{column}")

    print(
        "Detected fraud missing:",
        round(detected_pct, 2), "%"
    )

    print(
        "Missed fraud missing:",
        round(missed_pct, 2), "%"
    )


# STEP 10: Compare description lengths

print("\nDESCRIPTION LENGTH COMPARISON")
print("=" * 65)

for name, group in [
    ("Detected fraud", detected),
    ("Missed fraud", missed)
]:

    lengths = group["description"].fillna("").str.len()

    print(f"\n{name}")
    print("Count:", len(lengths))

    if len(lengths):

        print("Mean length:", round(lengths.mean(), 2))
        print("Median length:", round(lengths.median(), 2))


# STEP 11: Analyze short descriptions

print("\nSHORT DESCRIPTION ANALYSIS")
print("=" * 65)

for name, group in [
    ("Detected fraud", detected),
    ("Missed fraud", missed)
]:

    lengths = group["description"].fillna("").str.len()

    short_count = (lengths < 200).sum()

    percentage = (
        short_count / len(group) * 100
        if len(group) else 0
    )

    print(f"\n{name}")

    print("Descriptions below 200 characters:", short_count)
    print("Percentage:", round(percentage, 2), "%")


# STEP 12: Inspect short missed fraudulent postings

print("\nSHORT MISSED FRAUD POSTINGS WITH DECISION SCORES")
print("=" * 65)

missed_lengths = missed["description"].fillna("").str.len()

short_missed = missed[
    missed_lengths < 200
].copy()

for _, row in short_missed.iterrows():

    print("\nJob Title:", row["title"])
    print("Location:", row["location"])
    print("Industry:", row["industry"])
    print("Description:", row["description"])
    print("Requirements:", row["requirements"])
    print("Benefits:", row["benefits"])

    score = row["Decision_Score"]

    print("Decision Score:", round(score, 4))
    print("Threshold:", threshold)

    print(
        "Distance Below Threshold:",
        round(threshold - score, 4)
    )


# STEP 13: Save detected and missed fraud records

detected.assign(
    Analysis_Group="Detected Fraud"
).to_csv(
    "data/processed/detected_missing_profile_fraud.csv",
    index=False
)

missed.assign(
    Analysis_Group="Missed Fraud"
).to_csv(
    "data/processed/missed_missing_profile_fraud.csv",
    index=False
)


# STEP 14: Completion message

print("\nCOMPARISON FILES SAVED SUCCESSFULLY!")
print("DECISION SCORE ANALYSIS COMPLETED!")
