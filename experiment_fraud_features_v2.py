
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

DATA_PATH = DATA_DIR / "jobs_cleaned.csv"
V2_DATA_PATH = DATA_DIR / "jobs_with_risk_features_v2.csv"

OUTPUT_PATH = DATA_DIR / "feature_experiment_v2_results.json"


# ============================================================
# 2. LOAD DATASETS
# ============================================================

print("\nLOADING DATASETS...")

original_df = pd.read_csv(DATA_PATH)
enhanced_df = pd.read_csv(V2_DATA_PATH)

print("Original dataset:", original_df.shape)
print("Enhanced dataset:", enhanced_df.shape)

# Confirm that both datasets have the same original rows.
if len(original_df) != len(enhanced_df):
    raise ValueError("Original and enhanced datasets have different row counts.")

if not original_df["job_id"].equals(enhanced_df["job_id"]):
    raise ValueError("Dataset row alignment does not match.")

if not original_df["fraudulent"].equals(enhanced_df["fraudulent"]):
    raise ValueError("Target labels do not match.")

y = original_df["fraudulent"]

X_v1 = original_df.drop(columns=["job_id", "fraudulent"])

X_v2 = enhanced_df.drop(columns=["job_id", "fraudulent"])


# ============================================================
# 3. DEFINE FEATURE GROUPS
# ============================================================

text_features = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits"
]

categorical_features = [
    "location",
    "department",
    "salary_range",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function"
]

original_binary_features = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]

new_scaled_features = [
    "compensation_risk_count",
    "recruitment_risk_count",
    "relocation_claim_count",
    "company_profile_length_v2"
]

new_binary_features = [
    "company_profile_missing_v2",
    "company_profile_very_short",
    "email_reference_present",
    "website_reference_present"
]


# ============================================================
# 4. CREATE IDENTICAL TRAIN / VALIDATION / TEST SPLITS
# ============================================================

print("\nCREATING DATA SPLITS...")

indices = np.arange(len(original_df))

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.2,
    random_state=42,
    stratify=y
)

subtrain_indices, validation_indices = train_test_split(
    train_indices,
    test_size=0.2,
    random_state=42,
    stratify=y.iloc[train_indices]
)

print("Subtraining rows:", len(subtrain_indices))
print("Validation rows:", len(validation_indices))
print("Untouched test rows:", len(test_indices))

# We intentionally do not evaluate or inspect the test set.


# ============================================================
# 5. BUILD PREPROCESSORS
# ============================================================

def build_preprocessor(use_v2_features=False):

    transformers = [
        (
            "title_tfidf",
            TfidfVectorizer(max_features=500),
            "title"
        ),
        (
            "company_tfidf",
            TfidfVectorizer(max_features=1000),
            "company_profile"
        ),
        (
            "description_tfidf",
            TfidfVectorizer(max_features=3000),
            "description"
        ),
        (
            "requirements_tfidf",
            TfidfVectorizer(max_features=2000),
            "requirements"
        ),
        (
            "benefits_tfidf",
            TfidfVectorizer(max_features=1000),
            "benefits"
        ),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "original_numerical",
            "passthrough",
            original_binary_features
        )
    ]

    if use_v2_features:

        transformers.extend([
            (
                "new_scaled_features",
                StandardScaler(with_mean=False),
                new_scaled_features
            ),
            (
                "new_binary_features",
                "passthrough",
                new_binary_features
            )
        ])

    return ColumnTransformer(transformers=transformers)


# ============================================================
# 6. EVALUATION FUNCTION
# ============================================================

def evaluate_validation_model(
    model_name,
    model,
    X_validation_processed,
    y_validation
):

    scores = model.decision_function(X_validation_processed)

    thresholds = np.arange(-1.0, 1.01, 0.1)

    results = []

    for threshold in thresholds:

        predictions = (scores >= threshold).astype(int)

        results.append({
            "threshold": round(float(threshold), 2),
            "accuracy": round(
                accuracy_score(y_validation, predictions) * 100, 2
            ),
            "precision": round(
                precision_score(
                    y_validation, predictions, zero_division=0
                ) * 100, 2
            ),
            "recall": round(
                recall_score(
                    y_validation, predictions, zero_division=0
                ) * 100, 2
            ),
            "f1": round(
                f1_score(
                    y_validation, predictions, zero_division=0
                ) * 100, 2
            )
        })

    results_df = pd.DataFrame(results)

    best_row = results_df.loc[results_df["f1"].idxmax()]

    best_threshold = float(best_row["threshold"])

    best_predictions = (scores >= best_threshold).astype(int)

    matrix = confusion_matrix(
        y_validation,
        best_predictions,
        labels=[0, 1]
    )

    tn, fp, fn, tp = matrix.ravel()

    print(f"\n========== {model_name} VALIDATION RESULTS ==========")

    print("Best threshold:", best_threshold)
    print("Accuracy:", best_row["accuracy"], "%")
    print("Precision:", best_row["precision"], "%")
    print("Recall:", best_row["recall"], "%")
    print("F1 Score:", best_row["f1"], "%")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nTN:", tn)
    print("FP:", fp)
    print("FN:", fn)
    print("TP:", tp)

    print("\nTop threshold results:")
    print(
        results_df.sort_values(
            "f1", ascending=False
        ).head(5).to_string(index=False)
    )

    return {
        "model": model_name,
        "best_threshold": best_threshold,
        "accuracy": float(best_row["accuracy"]),
        "precision": float(best_row["precision"]),
        "recall": float(best_row["recall"]),
        "f1": float(best_row["f1"]),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "threshold_results": results
    }


# ============================================================
# 7. TRAIN V1 BASELINE MODEL
# ============================================================

print("\n\nTRAINING V1 BASELINE MODEL...")

X_v1_subtrain = X_v1.iloc[subtrain_indices]
X_v1_validation = X_v1.iloc[validation_indices]

y_subtrain = y.iloc[subtrain_indices]
y_validation = y.iloc[validation_indices]

v1_preprocessor = build_preprocessor(use_v2_features=False)

X_v1_train_processed = v1_preprocessor.fit_transform(
    X_v1_subtrain
)

X_v1_validation_processed = v1_preprocessor.transform(
    X_v1_validation
)

v1_model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

v1_model.fit(X_v1_train_processed, y_subtrain)

print("V1 training completed.")

v1_results = evaluate_validation_model(
    "V1 BASELINE",
    v1_model,
    X_v1_validation_processed,
    y_validation
)


# ============================================================
# 8. TRAIN V2 FEATURE-ENHANCED MODEL
# ============================================================

print("\n\nTRAINING V2 FEATURE-ENHANCED MODEL...")

X_v2_subtrain = X_v2.iloc[subtrain_indices]
X_v2_validation = X_v2.iloc[validation_indices]

v2_preprocessor = build_preprocessor(use_v2_features=True)

X_v2_train_processed = v2_preprocessor.fit_transform(
    X_v2_subtrain
)

X_v2_validation_processed = v2_preprocessor.transform(
    X_v2_validation
)

print("V2 training shape:", X_v2_train_processed.shape)
print("V2 validation shape:", X_v2_validation_processed.shape)

v2_model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

v2_model.fit(X_v2_train_processed, y_subtrain)

print("V2 training completed.")

v2_results = evaluate_validation_model(
    "V2 FEATURE-ENHANCED",
    v2_model,
    X_v2_validation_processed,
    y_validation
)


# ============================================================
# 9. COMPARE V1 AND V2
# ============================================================

print("\n\n========== V1 vs V2 COMPARISON ==========")

comparison = pd.DataFrame([
    {
        "Model": "V1 Baseline",
        "Precision": v1_results["precision"],
        "Recall": v1_results["recall"],
        "F1 Score": v1_results["f1"],
        "False Negatives": v1_results["false_negatives"]
    },
    {
        "Model": "V2 Enhanced",
        "Precision": v2_results["precision"],
        "Recall": v2_results["recall"],
        "F1 Score": v2_results["f1"],
        "False Negatives": v2_results["false_negatives"]
    }
])

print(comparison.to_string(index=False))


# ============================================================
# 10. SAVE EXPERIMENT RESULTS
# ============================================================

experiment_results = {
    "experiment": "OfferShield AI V2 Risk Feature Experiment",
    "test_set_used": False,
    "training_rows": len(subtrain_indices),
    "validation_rows": len(validation_indices),
    "untouched_test_rows": len(test_indices),
    "v1": v1_results,
    "v2": v2_results,
    "improvement": {
        "precision_difference": round(
            v2_results["precision"] - v1_results["precision"], 2
        ),
        "recall_difference": round(
            v2_results["recall"] - v1_results["recall"], 2
        ),
        "f1_difference": round(
            v2_results["f1"] - v1_results["f1"], 2
        ),
        "false_negative_difference": (
            v1_results["false_negatives"] -
            v2_results["false_negatives"]
        )
    }
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(experiment_results, file, indent=4)

print("\nEXPERIMENT RESULTS SAVED:")
print(OUTPUT_PATH)

print("\nEXPERIMENT COMPLETED SUCCESSFULLY!")
print("Existing model files were not modified.")
