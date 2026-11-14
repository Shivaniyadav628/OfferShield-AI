
import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# STEP 1: PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

DATASET_PATH = DATA_DIR / "jobs_cleaned.csv"
MODEL_PATH = DATA_DIR / "final_svm_model.pkl"
PREPROCESSOR_PATH = DATA_DIR / "final_preprocessor.pkl"
THRESHOLD_PATH = DATA_DIR / "best_threshold.json"

OUTPUT_PATH = DATA_DIR / "model_evaluation_results.json"


# ============================================================
# STEP 2: LOAD THE SAVED APPLICATION ARTIFACTS
# ============================================================

print("\nLOADING SAVED MODEL AND PREPROCESSOR...")

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

with open(THRESHOLD_PATH, "r") as file:
    threshold_data = json.load(file)

BEST_THRESHOLD = float(threshold_data["best_threshold"])

print("Model loaded successfully.")
print("Preprocessor loaded successfully.")
print("Decision threshold:", BEST_THRESHOLD)


# ============================================================
# STEP 3: LOAD THE ORIGINAL CLEANED DATASET
# ============================================================

print("\nLOADING CLEANED DATASET...")

df = pd.read_csv(DATASET_PATH)

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

print("Dataset shape:", df.shape)
print("Feature count:", X.shape[1])


# ============================================================
# STEP 4: RECREATE THE ORIGINAL OUTER TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
# Recreate the original subtraining-validation split

X_subtrain, X_validation, y_subtrain, y_validation = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

# Transform validation data using the saved preprocessor

X_validation_processed = preprocessor.transform(X_validation)

# Generate validation predictions

validation_scores = model.decision_function(
    X_validation_processed
)

validation_predictions = (
    validation_scores >= BEST_THRESHOLD
).astype(int)

# Identify missed fraudulent validation jobs

validation_analysis = X_validation.copy()

validation_analysis["actual"] = y_validation
validation_analysis["predicted"] = validation_predictions
validation_analysis["decision_score"] = validation_scores

validation_false_negatives = validation_analysis[
    (validation_analysis["actual"] == 1) &
    (validation_analysis["predicted"] == 0)
]

validation_false_negatives.to_csv(
    DATA_DIR / "validation_false_negatives.csv",
    index=False
)

print("\nVALIDATION ERROR ANALYSIS")
print("Missed fraudulent validation jobs:",
      len(validation_false_negatives))

print("Saved:",
      DATA_DIR / "validation_false_negatives.csv")
print("\nRECREATED TEST SPLIT")
print("Training rows:", len(X_train))
print("Test rows:", len(X_test))


# ============================================================
# STEP 5: TRANSFORM TEST DATA USING SAVED PREPROCESSOR
# ============================================================

print("\nTRANSFORMING TEST DATA...")

X_test_processed = preprocessor.transform(X_test)

print("Processed test shape:", X_test_processed.shape)

expected_features = model.n_features_in_
actual_features = X_test_processed.shape[1]

print("Model expected features:", expected_features)
print("Test actual features:", actual_features)

if expected_features != actual_features:
    raise ValueError(
        "Feature mismatch! The saved model and preprocessor "
        "are not compatible with this test dataset."
    )


# ============================================================
# STEP 6: GENERATE DECISION SCORES
# ============================================================

print("\nGENERATING PREDICTIONS...")

decision_scores = model.decision_function(X_test_processed)

predictions = (
    decision_scores >= BEST_THRESHOLD
).astype(int)

# ============================================================
# SAVE FALSE NEGATIVES AND FALSE POSITIVES
# ============================================================

test_analysis = X_test.copy()

test_analysis["actual"] = y_test
test_analysis["predicted"] = predictions
test_analysis["decision_score"] = decision_scores

false_negatives = test_analysis[
    (test_analysis["actual"] == 1) &
    (test_analysis["predicted"] == 0)
]

false_positives = test_analysis[
    (test_analysis["actual"] == 0) &
    (test_analysis["predicted"] == 1)
]

false_negatives.to_csv(
    DATA_DIR / "test_false_negatives.csv",
    index=False
)

false_positives.to_csv(
    DATA_DIR / "test_false_positives.csv",
    index=False
)

print("\nERROR ANALYSIS FILES SAVED")
print("Missed fraudulent jobs:", len(false_negatives))
print("Incorrectly flagged genuine jobs:", len(false_positives))

# ============================================================
# STEP 7: CALCULATE EVALUATION METRICS
# ============================================================

accuracy = accuracy_score(y_test, predictions)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)


# ============================================================
# STEP 8: DISPLAY FINAL TEST RESULTS
# ============================================================

print("\n" + "=" * 60)
print("OFFERSHIELD AI - FINAL MODEL EVALUATION")
print("=" * 60)

print("Model: LinearSVC")
print("Decision threshold:", BEST_THRESHOLD)

print("Accuracy:", round(accuracy * 100, 2), "%")
print("Fraud Precision:", round(precision * 100, 2), "%")
print("Fraud Recall:", round(recall * 100, 2), "%")
print("Fraud F1 Score:", round(f1 * 100, 2), "%")


# ============================================================
# STEP 9: CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1]
)

print("\nCONFUSION MATRIX")
print("Rows = Actual | Columns = Predicted")
print(cm)

tn, fp, fn, tp = cm.ravel()

print("\nTRUE NEGATIVES:", int(tn))
print("FALSE POSITIVES:", int(fp))
print("FALSE NEGATIVES:", int(fn))
print("TRUE POSITIVES:", int(tp))


# ============================================================
# STEP 10: CLASSIFICATION REPORT
# ============================================================

print("\nCLASSIFICATION REPORT")

report = classification_report(
    y_test,
    predictions,
    labels=[0, 1],
    target_names=["Genuine Jobs", "Fraudulent Jobs"],
    zero_division=0
)

print(report)


# ============================================================
# STEP 11: SAVE EVALUATION RESULTS
# ============================================================

results = {
    "model": "LinearSVC",
    "decision_threshold": BEST_THRESHOLD,
    "dataset_rows": int(len(df)),
    "test_rows": int(len(y_test)),
    "processed_test_features": int(actual_features),
    "accuracy": round(float(accuracy), 6),
    "fraud_precision": round(float(precision), 6),
    "fraud_recall": round(float(recall), 6),
    "fraud_f1_score": round(float(f1), 6),
    "confusion_matrix": {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp)
    },
    "classification_report": classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Genuine Jobs", "Fraudulent Jobs"],
        output_dict=True,
        zero_division=0
    )
}

with open(OUTPUT_PATH, "w") as file:
    json.dump(results, file, indent=4)

print("\nEVALUATION RESULTS SAVED!")
print(OUTPUT_PATH)

print("\nMODEL EVALUATION COMPLETED SUCCESSFULLY!")
