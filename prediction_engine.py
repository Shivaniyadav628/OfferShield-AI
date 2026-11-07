
import json
from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "data" / "processed" / "final_svm_model.pkl"

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
# 3. TEXT AND CATEGORICAL INPUT COLUMNS
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


# ============================================================
# 4. NUMERICAL INPUT COLUMNS
# ============================================================

NUMERICAL_COLUMNS = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]


# ============================================================
# 5. LOAD TRAINED MODEL AND PREPROCESSOR
# ============================================================

model = joblib.load(MODEL_PATH)

preprocessor = joblib.load(PREPROCESSOR_PATH)


# ============================================================
# 6. LOAD SELECTED DECISION THRESHOLD
# ============================================================

with open(THRESHOLD_PATH, "r", encoding="utf-8") as file:
    threshold_data = json.load(file)

BEST_THRESHOLD = float(threshold_data["best_threshold"])


# ============================================================
# 7. PREDICTION FUNCTION
# ============================================================

def predict_job_fraud(job_data):

    # --------------------------------------------------------
    # Check that input is a dictionary
    # --------------------------------------------------------

    if not isinstance(job_data, dict):
        raise TypeError(
            "Job data must be provided as a dictionary."
        )

    # --------------------------------------------------------
    # Check for missing required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in job_data
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # Create DataFrame using required columns only
    # --------------------------------------------------------

    job_df = pd.DataFrame([job_data])[REQUIRED_COLUMNS].copy()

    # --------------------------------------------------------
    # Handle missing and empty text values
    # --------------------------------------------------------

    for column in TEXT_COLUMNS:

        job_df[column] = (
            job_df[column]
            .fillna("Not Specified")
            .astype(str)
            .str.strip()
            .replace("", "Not Specified")
        )

    # --------------------------------------------------------
    # Handle missing numerical values
    # --------------------------------------------------------

    for column in NUMERICAL_COLUMNS:

        job_df[column] = (
            pd.to_numeric(
                job_df[column],
                errors="raise"
            )
            .fillna(0)
        )

    # --------------------------------------------------------
    # Validate numerical binary values
    # --------------------------------------------------------

    for column in NUMERICAL_COLUMNS:

        if not job_df[column].isin([0, 1]).all():

            raise ValueError(
                f"{column} must contain only 0 or 1."
            )

    # --------------------------------------------------------
    # Transform input using saved preprocessor
    # --------------------------------------------------------

    processed_job = preprocessor.transform(job_df)

    # --------------------------------------------------------
    # Generate model decision score
    # --------------------------------------------------------

    decision_score = model.decision_function(processed_job)[0]

    # --------------------------------------------------------
    # Apply validation-selected threshold
    # --------------------------------------------------------

    prediction = int(decision_score >= BEST_THRESHOLD)

    # --------------------------------------------------------
    # Generate readable risk classification
    # --------------------------------------------------------

    if prediction == 1:
        result = "Potentially Fraudulent"
    else:
        result = "Likely Genuine"

    # --------------------------------------------------------
    # Return prediction results
    # --------------------------------------------------------

    return {
        "prediction": prediction,
        "result": result,
        "decision_score": float(decision_score),
        "threshold": BEST_THRESHOLD
    }
