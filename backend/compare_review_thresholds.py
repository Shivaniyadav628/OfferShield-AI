
import json
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

RESULTS_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "risk_level_validation_results.csv"
)

OUTPUT_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "review_threshold_comparison.csv"
)


# ============================================================
# 2. LOAD VALIDATION RESULTS
# ============================================================

results = pd.read_csv(RESULTS_PATH)

total_jobs = len(results)

total_fraud = int((results["actual"] == 1).sum())


# ============================================================
# 3. THRESHOLDS TO COMPARE
# ============================================================

LOWER_THRESHOLDS = [
    -0.1,
    -0.2,
    -0.3,
    -0.4,
    -0.5
]

FRAUD_THRESHOLD = 0.1


# ============================================================
# 4. EVALUATE EACH LOWER THRESHOLD
# ============================================================

comparison = []

for lower_threshold in LOWER_THRESHOLDS:

    high_risk = results[
        results["decision_score"] >= FRAUD_THRESHOLD
    ]

    manual_review = results[
        (results["decision_score"] >= lower_threshold)
        & (results["decision_score"] < FRAUD_THRESHOLD)
    ]

    low_risk = results[
        results["decision_score"] < lower_threshold
    ]

    high_fraud = int((high_risk["actual"] == 1).sum())

    review_fraud = int((manual_review["actual"] == 1).sum())

    low_fraud = int((low_risk["actual"] == 1).sum())

    high_genuine = int((high_risk["actual"] == 0).sum())

    review_genuine = int((manual_review["actual"] == 0).sum())

    low_genuine = int((low_risk["actual"] == 0).sum())

    combined_fraud_coverage = (
        (high_fraud + review_fraud) / total_fraud * 100
    )

    high_only_recall = (
        high_fraud / total_fraud * 100
    )

    review_count = len(manual_review)

    high_count = len(high_risk)

    total_investigation = review_count + high_count

    workload_percentage = (
        total_investigation / total_jobs * 100
    )

    review_fraud_rate = (
        review_fraud / review_count * 100
        if review_count else 0
    )

    comparison.append({

        "lower_threshold": lower_threshold,

        "high_risk_jobs": len(high_risk),

        "manual_review_jobs": review_count,

        "low_risk_jobs": len(low_risk),

        "high_risk_fraud": high_fraud,

        "manual_review_fraud": review_fraud,

        "low_risk_fraud": low_fraud,

        "high_risk_genuine": high_genuine,

        "manual_review_genuine": review_genuine,

        "low_risk_genuine": low_genuine,

        "high_only_recall_percent": round(
            high_only_recall, 2
        ),

        "combined_fraud_coverage_percent": round(
            combined_fraud_coverage, 2
        ),

        "manual_review_fraud_rate_percent": round(
            review_fraud_rate, 2
        ),

        "investigation_workload_percent": round(
            workload_percentage, 2
        )
    })


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

comparison_df = pd.DataFrame(comparison)

print("\n" + "=" * 100)

print("LOWER REVIEW THRESHOLD COMPARISON")

print("=" * 100)

print(comparison_df.to_string(index=False))


# ============================================================
# 6. SAVE RESULTS
# ============================================================

comparison_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nComparison saved to:")

print(OUTPUT_PATH)
