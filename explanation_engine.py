
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR / "data" / "processed" / "final_svm_model.pkl"
)

PREPROCESSOR_PATH = (
    BASE_DIR / "data" / "processed" / "final_preprocessor.pkl"
)

THRESHOLD_PATH = (
    BASE_DIR / "data" / "processed" / "best_threshold.json"
)


# ============================================================
# 2. REQUIRED INPUT COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "title",
    "location",
    "department",
    "salary_range",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "telecommuting",
    "has_company_logo",
    "has_questions",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function"
]


# ============================================================
# 3. TEXT AND NUMERICAL COLUMNS
# ============================================================

TEXT_COLUMNS = [
    "title",
    "location",
    "department",
    "salary_range",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function"
]

NUMERICAL_COLUMNS = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]


# ============================================================
# 4. LOAD TRAINED MODEL AND PREPROCESSOR
# ============================================================

model = joblib.load(MODEL_PATH)

preprocessor = joblib.load(PREPROCESSOR_PATH)


# ============================================================
# 5. LOAD SELECTED DECISION THRESHOLD
# ============================================================

with open(THRESHOLD_PATH, "r", encoding="utf-8") as file:

    threshold_data = json.load(file)

BEST_THRESHOLD = float(
    threshold_data["best_threshold"]
)


# ============================================================
# 6. LOAD TRANSFORMED FEATURE NAMES
# ============================================================

FEATURE_NAMES = preprocessor.get_feature_names_out()


# ============================================================
# 7. VERIFY MODEL AND FEATURE INFORMATION
# ============================================================

if len(FEATURE_NAMES) != model.coef_.shape[1]:

    raise ValueError(
        "Feature count mismatch between preprocessor and model."
    )


# ============================================================
# 8. CONVERT TECHNICAL FEATURE NAMES INTO READABLE LABELS
# ============================================================

def format_feature_name(feature_name):

    if "__" in feature_name:

        transformer, feature = feature_name.split(
            "__", 1
        )

    else:

        return str(feature_name)

    text_transformers = {
        "title_tfidf": "Job Title",
        "company_tfidf": "Company Profile",
        "description_tfidf": "Job Description",
        "requirements_tfidf": "Job Requirements",
        "benefits_tfidf": "Job Benefits"
    }

    if transformer in text_transformers:

        return (
            f'{text_transformers[transformer]} '
            f'- Word: "{feature}"'
        )

    if transformer == "categorical":

        return f"Category - {feature}"

    if transformer == "numerical":

        numerical_labels = {
            "telecommuting": "Remote Work",
            "has_company_logo": "Company Logo",
            "has_questions": "Screening Questions"
        }

        return numerical_labels.get(
            feature,
            feature
        )

    return str(feature)


# ============================================================
# 9. VALIDATE AND PREPARE JOB INPUT
# ============================================================

def prepare_job_input(job_data):

    # Check input type
    if not isinstance(job_data, pd.DataFrame):

        raise TypeError(
            "Job data must be provided as a pandas DataFrame."
        )

    # Check exactly one job posting
    if len(job_data) != 1:

        raise ValueError(
            "Please provide exactly one job posting."
        )

    # Check missing required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in job_data.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep required columns in the correct order.
    # Extra columns are safely ignored.
    job_df = job_data[REQUIRED_COLUMNS].copy()

    # Handle missing and empty text values
    for column in TEXT_COLUMNS:

        job_df[column] = (
            job_df[column]
            .fillna("Not Specified")
            .astype(str)
            .str.strip()
            .replace("", "Not Specified")
        )

    # Handle numerical values
    for column in NUMERICAL_COLUMNS:

        job_df[column] = (
            pd.to_numeric(
                job_df[column],
                errors="raise"
            )
            .fillna(0)
        )

    # Validate binary numerical values
    for column in NUMERICAL_COLUMNS:

        if not job_df[column].isin([0, 1]).all():

            raise ValueError(
                f"{column} must contain only 0 or 1."
            )

    return job_df


# ============================================================
# 10. FEATURE CONTRIBUTION FUNCTION
# ============================================================

def calculate_feature_contributions(processed_job):

    contributions = processed_job.multiply(
        model.coef_[0]
    ).toarray()[0]

    explanation_df = pd.DataFrame({

        "feature": [
            format_feature_name(name)
            for name in FEATURE_NAMES
        ],

        "contribution": contributions
    })

    # Remove zero contributions
    explanation_df = explanation_df[
        explanation_df["contribution"] != 0
    ].copy()

    # Sort from highest to lowest contribution
    explanation_df = explanation_df.sort_values(
        by="contribution",
        ascending=False
    )

    return explanation_df


# ============================================================
# 11. VERIFY EXPLANATION MATHEMATICS
# ============================================================

def verify_explanation(processed_job, explanation_df):

    # Actual model decision score
    actual_score = float(
        model.decision_function(processed_job)[0]
    )

    # Sum of feature contributions
    contribution_sum = float(
        explanation_df["contribution"].sum()
    )

    # Model intercept
    intercept = float(
        model.intercept_[0]
    )

    # Reconstruct the decision score
    reconstructed_score = (
        contribution_sum + intercept
    )

    # Calculate difference
    difference = abs(
        actual_score - reconstructed_score
    )

    # Verify mathematical consistency
    is_valid = np.isclose(
        actual_score,
        reconstructed_score,
        rtol=1e-9,
        atol=1e-9
    )

    return {
        "actual_score": actual_score,
        "contribution_sum": contribution_sum,
        "intercept": intercept,
        "reconstructed_score": reconstructed_score,
        "difference": float(difference),
        "verified": bool(is_valid)
    }


# ============================================================
# 12. UNIFIED JOB EXPLANATION FUNCTION
# ============================================================

def explain_job(job_data):

    # Validate and prepare input
    job_df = prepare_job_input(job_data)

    # Transform job data
    processed_job = preprocessor.transform(job_df)

    # Generate model decision score
    decision_score = float(
        model.decision_function(processed_job)[0]
    )

    # Apply selected decision threshold
    prediction = int(
        decision_score >= BEST_THRESHOLD
    )

    # Generate readable classification
    if prediction == 1:

        risk_classification = "Potentially Fraudulent"

    else:

        risk_classification = "Likely Genuine"

    # Calculate feature contributions
    explanation_df = calculate_feature_contributions(
        processed_job
    )

    # Identify fraud-increasing signals
    fraud_signals = (
        explanation_df[
            explanation_df["contribution"] > 0
        ]
        .head(10)
        .to_dict(orient="records")
    )

    # Identify genuine-increasing signals
    genuine_signals = (
        explanation_df[
            explanation_df["contribution"] < 0
        ]
        .tail(10)
        .sort_values("contribution")
        .to_dict(orient="records")
    )

    # Convert contribution values to native Python floats
    for signal in fraud_signals + genuine_signals:

        signal["contribution"] = float(
            signal["contribution"]
        )

    # Verify explanation mathematics
    verification = verify_explanation(
        processed_job,
        explanation_df
    )

    # Return complete explanation
    return {
        "job_title": str(job_df["title"].iloc[0]),
        "prediction": prediction,
        "risk_classification": risk_classification,
        "decision_score": decision_score,
        "threshold": BEST_THRESHOLD,
        "fraud_increasing_signals": fraud_signals,
        "genuine_increasing_signals": genuine_signals,
        "mathematical_verification": verification
    }


# ============================================================
# 13. RUN DEMONSTRATION ONLY WHEN EXECUTED DIRECTLY
# ============================================================

if __name__ == "__main__":

    print("\nExplanation engine components loaded successfully!")

    print("Model:", type(model).__name__)

    print("Preprocessor:", type(preprocessor).__name__)

    print("Total transformed features:", len(FEATURE_NAMES))

    print("Selected threshold:", BEST_THRESHOLD)

    # Load cleaned dataset
    df = pd.read_csv(
        BASE_DIR / "data" / "processed" / "jobs_cleaned.csv"
    )

    # Separate input features
    X = df.drop(
        columns=["job_id", "fraudulent"]
    )

    # Select one sample job
    sample_job = X.iloc[[0]]

    # Generate unified explanation
    result = explain_job(sample_job)

    # Display mathematical verification
    verification = result["mathematical_verification"]

    print("\n" + "=" * 60)

    print("EXPLANATION MATHEMATICAL VERIFICATION")

    print("=" * 60)

    print("Actual Decision Score:", verification["actual_score"])

    print("Sum of Contributions:", verification["contribution_sum"])

    print("Model Intercept:", verification["intercept"])

    print("Reconstructed Score:", verification["reconstructed_score"])

    print("Difference:", verification["difference"])

    print(
        "Verification Status:",
        "SUCCESS" if verification["verified"] else "FAILED"
    )

    print("=" * 60)

    # Display prediction
    print("\n" + "=" * 60)

    print("OFFERSHIELD AI - UNIFIED EXPLANATION")

    print("=" * 60)

    print("Job Title:", result["job_title"])

    print("Prediction:", result["prediction"])

    print("Risk Classification:", result["risk_classification"])

    print("Decision Score:", result["decision_score"])

    print("Selected Threshold:", result["threshold"])

    # Display fraud-increasing signals
    print("\nTOP FRAUD-INCREASING SIGNALS:")

    for signal in result["fraud_increasing_signals"]:

        print(signal)

    # Display genuine-increasing signals
    print("\nTOP GENUINE-INCREASING SIGNALS:")

    for signal in result["genuine_increasing_signals"]:

        print(signal)

    # Final verification
    if not verification["verified"]:

        raise RuntimeError(
            "Explanation mathematical verification failed!"
        )

    print("\nExplanation engine test completed successfully!")

