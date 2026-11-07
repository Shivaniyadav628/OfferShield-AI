
import pandas as pd
import numpy as np
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# STEP 1: Load cleaned dataset
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

# STEP 4: Load selected threshold
with open(
    "data/processed/best_threshold.json",
    "r"
) as file:
    threshold = json.load(file)["best_threshold"]

# STEP 5: Generate validation predictions
X_val_processed = preprocessor.transform(X_val)

scores = model.decision_function(X_val_processed)

predictions = (
    scores >= threshold
).astype(int)

# STEP 6: Create analysis DataFrame
analysis_df = X_val.copy()

analysis_df["Actual"] = y_val.to_numpy()
analysis_df["Predicted"] = predictions

analysis_df["Profile_Missing"] = (
    analysis_df["company_profile"] == "Not Specified"
)

# STEP 7: Evaluate each group
groups = {
    "Profile Available": False,
    "Profile Missing": True
}

print("\n" + "=" * 70)
print("MODEL PERFORMANCE BY COMPANY PROFILE")
print("=" * 70)

results = []

for group_name, missing_value in groups.items():

    group = analysis_df[
        analysis_df["Profile_Missing"] == missing_value
    ]

    actual = group["Actual"]
    predicted = group["Predicted"]

    precision = precision_score(
        actual, predicted, zero_division=0
    )

    recall = recall_score(
        actual, predicted, zero_division=0
    )

    f1 = f1_score(
        actual, predicted, zero_division=0
    )

    matrix = confusion_matrix(
        actual,
        predicted,
        labels=[0, 1]
    )

    tn, fp, fn, tp = matrix.ravel()

    results.append({
        "Group": group_name,
        "Total": len(group),
        "Actual_Fraud": int(actual.sum()),
        "Predicted_Fraud": int(predicted.sum()),
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp
    })

    print(f"\n{group_name}")
    print("-" * 50)

    print("Total postings:", len(group))
    print("Actual fraudulent:", int(actual.sum()))
    print("Predicted fraudulent:", int(predicted.sum()))

    print("Precision:", round(precision * 100, 2), "%")
    print("Recall:", round(recall * 100, 2), "%")
    print("F1 Score:", round(f1 * 100, 2), "%")

    print("\nConfusion Matrix:")
    print(matrix)

# STEP 8: Save results
results_df = pd.DataFrame(results)

results_df.to_csv(
    "data/processed/profile_group_performance.csv",
    index=False
)

print("\nGROUP PERFORMANCE ANALYSIS SAVED SUCCESSFULLY!")
