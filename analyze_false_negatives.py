
import pandas as pd
import numpy as np
import json
import joblib

from sklearn.model_selection import train_test_split

# STEP 1: Load dataset
df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

# STEP 2: Recreate exact validation split
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

# STEP 3: Load saved model and preprocessor
model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

# STEP 4: Load threshold
with open(
    "data/processed/best_threshold.json",
    "r"
) as file:
    threshold = json.load(file)["best_threshold"]

# STEP 5: Predict validation data
X_val_processed = preprocessor.transform(X_val)

scores = model.decision_function(X_val_processed)

predictions = (
    scores >= threshold
).astype(int)

# STEP 6: Identify false negatives
results = X_val.copy()

results["Actual"] = y_val.to_numpy()
results["Predicted"] = predictions
results["Decision_Score"] = scores

false_negatives = results[
    (results["Actual"] == 1) &
    (results["Predicted"] == 0)
]

# STEP 7: Focus on missing company profiles
missing_profile_fn = false_negatives[
    false_negatives["company_profile"] == "Not Specified"
]

print("\n" + "=" * 65)
print("FALSE NEGATIVE ANALYSIS")
print("=" * 65)

print("Total false negatives:", len(false_negatives))
print("Missing-profile false negatives:", len(missing_profile_fn))

# STEP 8: Display missed fraudulent postings
columns_to_display = [
    "title",
    "location",
    "department",
    "employment_type",
    "industry",
    "description",
    "requirements",
    "benefits",
    "Decision_Score"
]

print("\nMISSED FRAUDULENT JOB POSTINGS")
print("=" * 65)

for index, row in missing_profile_fn.iterrows():

    print("\nJob:", index)
    print("Title:", row["title"])
    print("Location:", row["location"])
    print("Industry:", row["industry"])
    print("Employment type:", row["employment_type"])
    print("Decision score:", round(row["Decision_Score"], 4))

    print("Description:", str(row["description"])[:500])

    print("Requirements:", str(row["requirements"])[:300])

    print("-" * 65)

# STEP 9: Save missed postings
missing_profile_fn[columns_to_display].to_csv(
    "data/processed/missing_profile_false_negatives.csv",
    index=False
)

print("\nFALSE NEGATIVE ANALYSIS SAVED SUCCESSFULLY!")
