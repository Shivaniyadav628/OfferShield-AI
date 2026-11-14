
import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split


# ============================================================
# 1. PROJECT PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT_DIR / "data" / "processed" / "jobs_cleaned.csv"

MODEL_PATH = ROOT_DIR / "data" / "processed" / "final_svm_model.pkl"

PREPROCESSOR_PATH = (
    ROOT_DIR / "data" / "processed" / "final_preprocessor.pkl"
)

RESULTS_PATH = (
    ROOT_DIR / "data" / "processed" / "risk_level_validation_results.csv"
)

SUMMARY_PATH = (
    ROOT_DIR / "data" / "processed" / "risk_level_validation_summary.json"
)


# ============================================================
# 2. RISK THRESHOLDS
# ============================================================

LOWER_REVIEW_THRESHOLD = -0.1
FRAUD_THRESHOLD = 0.1


# ============================================================
# 3. LOAD DATA AND SAVED MODEL
# ============================================================

print("\nLOADING DATA AND SAVED MODEL...")

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)

preprocessor = joblib.load(PREPROCESSOR_PATH)

print("Dataset shape:", df.shape)


# ============================================================
# 4. RECREATE ORIGINAL DATA SPLIT
# ============================================================

print("\nRECREATING TRAINING AND VALIDATION SPLITS...")

X = df.drop(columns=["job_id", "fraudulent"])

y = df["fraudulent"]

# Original 80% training / 20% untouched test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Split the training portion into subtraining and validation
X_subtrain, X_validation, y_subtrain, y_validation = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

print("Subtraining rows:", len(X_subtrain))
print("Validation rows:", len(X_validation))
print("Untouched test rows:", len(X_test))


# ============================================================
# 5. TRANSFORM VALIDATION DATA
# ============================================================

print("\nTRANSFORMING VALIDATION DATA...")

X_validation_processed = preprocessor.transform(X_validation)

print("Processed validation shape:", X_validation_processed.shape)

print("Model expected features:", model.n_features_in_)

assert X_validation_processed.shape[1] == model.n_features_in_, (
    "Feature mismatch between preprocessor and saved model."
)


# ============================================================
# 6. GENERATE DECISION SCORES
# ============================================================

print("\nGENERATING DECISION SCORES...")

decision_scores = model.decision_function(
    X_validation_processed
)

results = pd.DataFrame({
    "actual": y_validation.to_numpy(),
    "decision_score": decision_scores
})


# ============================================================
# 7. ASSIGN THREE RISK LEVELS
# ============================================================

def classify_risk(score):

    if score >= FRAUD_THRESHOLD:
        return "Potentially Fraudulent"

    elif score >= LOWER_REVIEW_THRESHOLD:
        return "Needs Manual Review"

    return "Likely Genuine"


results["risk_level"] = results["decision_score"].apply(
    classify_risk
)


# ============================================================
# 8. CALCULATE RISK LEVEL STATISTICS
# ============================================================

print("\n" + "=" * 65)
print("THREE-LEVEL RISK CLASSIFICATION EVALUATION")
print("=" * 65)

risk_order = [
    "Likely Genuine",
    "Needs Manual Review",
    "Potentially Fraudulent"
]

summary = {}

total_fraud = int((results["actual"] == 1).sum())

total_genuine = int((results["actual"] == 0).sum())

for risk in risk_order:

    group = results[results["risk_level"] == risk]

    count = len(group)

    fraud_count = int((group["actual"] == 1).sum())

    genuine_count = int((group["actual"] == 0).sum())

    fraud_rate = (
        fraud_count / count * 100
        if count > 0 else 0
    )

    summary[risk] = {
        "total_jobs": count,
        "dataset_label_fraud": fraud_count,
        "dataset_label_genuine": genuine_count,
        "dataset_label_fraud_rate_percent": round(fraud_rate, 2)
    }

    print(f"\n{risk}")

    print("Total jobs:", count)

    print("Dataset-labelled fraud:", fraud_count)

    print("Dataset-labelled genuine:", genuine_count)

    print("Dataset-labelled fraud rate:", f"{fraud_rate:.2f}%")


# ============================================================
# 9. MEASURE FRAUD DETECTION COVERAGE
# ============================================================

print("\n" + "=" * 65)
print("FRAUD DETECTION COVERAGE")
print("=" * 65)

high_group = results[
    results["risk_level"] == "Potentially Fraudulent"
]

review_group = results[
    results["risk_level"] == "Needs Manual Review"
]

low_group = results[
    results["risk_level"] == "Likely Genuine"
]

high_fraud = int((high_group["actual"] == 1).sum())

review_fraud = int((review_group["actual"] == 1).sum())

low_fraud = int((low_group["actual"] == 1).sum())

high_only_recall = (
    high_fraud / total_fraud * 100
    if total_fraud > 0 else 0
)

combined_recall = (
    (high_fraud + review_fraud) / total_fraud * 100
    if total_fraud > 0 else 0
)

missed_fraud = low_fraud

print("Total dataset-labelled fraud:", total_fraud)

print(
    "Fraud in high-risk category:",
    high_fraud
)

print(
    "Fraud in manual-review category:",
    review_fraud
)

print(
    "Fraud in lower-risk category:",
    missed_fraud
)

print(
    f"\nHigh-risk-only fraud recall: {high_only_recall:.2f}%"
)

print(
    f"High-risk + manual-review fraud coverage: "
    f"{combined_recall:.2f}%"
)


# ============================================================
# 10. MANUAL REVIEW WORKLOAD
# ============================================================

manual_review_jobs = len(review_group) + len(high_group)

manual_review_percentage = (
    manual_review_jobs / len(results) * 100
    if len(results) > 0 else 0
)

print("\nMANUAL INVESTIGATION WORKLOAD")

print(
    "Jobs requiring review or investigation:",
    manual_review_jobs
)

print(
    f"Percentage of validation jobs: "
    f"{manual_review_percentage:.2f}%"
)


# ============================================================
# 11. SAVE VALIDATION RESULTS
# ============================================================

results.to_csv(RESULTS_PATH, index=False)

summary_data = {
    "validation_rows": len(results),
    "total_dataset_label_fraud": total_fraud,
    "total_dataset_label_genuine": total_genuine,
    "lower_review_threshold": LOWER_REVIEW_THRESHOLD,
    "fraud_threshold": FRAUD_THRESHOLD,
    "risk_level_statistics": summary,
    "high_risk_only_fraud_recall_percent": round(
        high_only_recall, 2
    ),
    "high_and_review_fraud_coverage_percent": round(
        combined_recall, 2
    ),
    "jobs_requiring_investigation": manual_review_jobs,
    "investigation_workload_percent": round(
        manual_review_percentage, 2
    ),
    "fraud_in_lower_risk_category": missed_fraud
}

with open(SUMMARY_PATH, "w", encoding="utf-8") as file:

    json.dump(
        summary_data,
        file,
        indent=4
    )


# ============================================================
# 12. FINAL REPORT
# ============================================================

print("\n" + "=" * 65)

print("VALIDATION EVALUATION COMPLETED")

print("=" * 65)

print("Detailed results:", RESULTS_PATH)

print("Summary:", SUMMARY_PATH)

print("\nNo model files or thresholds were modified.")
