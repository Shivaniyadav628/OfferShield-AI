
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# STEP 1: LOAD DATASET
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")


# ============================================================
# STEP 2: CREATE ENGINEERED FEATURES
# ============================================================

for column in ["description", "requirements", "benefits"]:

    text = df[column].fillna("").astype(str)

    text = text.replace("Not Specified", "")

    df[column + "_length"] = text.str.len()


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
    .fillna("")
    .astype(str)
    .str.lower()
    .apply(
        lambda text: int(
            any(
                phrase in text
                for phrase in placeholder_phrases
            )
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


# ============================================================
# STEP 3: SEPARATE INPUT FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["job_id", "fraudulent"])

y = df["fraudulent"]


# ============================================================
# STEP 4: RECREATE SAME DATASET SPLIT
# ============================================================

X_train_outer, X_test, y_train_outer, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


X_subtrain, X_validation, y_subtrain, y_validation = train_test_split(
    X_train_outer,
    y_train_outer,
    test_size=0.2,
    random_state=42,
    stratify=y_train_outer
)


print("SUBTRAINING SHAPE:", X_subtrain.shape)
print("VALIDATION SHAPE:", X_validation.shape)
print("UNTOUCHED TEST SHAPE:", X_test.shape)


# ============================================================
# STEP 5: DEFINE FEATURE GROUPS
# ============================================================

baseline_numerical = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]


text_length_features = [
    "description_length",
    "requirements_length",
    "benefits_length"
]


missing_information_features = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "missing_information_count"
]


description_quality_features = [
    "short_description",
    "placeholder_description"
]


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


enhanced_numerical = (
    baseline_numerical
    + text_length_features
    + missing_information_features
    + description_quality_features
)


print("\nFEATURE GROUPS")
print("=" * 50)

print("Baseline numerical:", baseline_numerical)
print("Text length:", text_length_features)
print("Missing information:", missing_information_features)
print("Description quality:", description_quality_features)

print(
    "\nTOTAL ENHANCED NUMERICAL FEATURES:",
    len(enhanced_numerical)
)


# ============================================================
# STEP 6: DEFINE INDIVIDUAL ABLATION EXPERIMENTS
# ============================================================

ablation_experiments = {
    "All engineered features (control)": None,

    "Without description_length": "description_length",

    "Without requirements_length": "requirements_length",

    "Without benefits_length": "benefits_length"
}


print("\nINDIVIDUAL FEATURE ABLATION EXPERIMENTS")
print("=" * 50)

for experiment, removed_feature in ablation_experiments.items():

    print("\nExperiment:", experiment)

    print("Removed feature:", removed_feature)

    print(
        "Remaining numerical features:",
        len(enhanced_numerical)
        - (1 if removed_feature is not None else 0)
    )


# ============================================================
# STEP 7: DEFINE INDIVIDUAL ABLATION FUNCTION
# ============================================================

def run_individual_ablation(experiment_name, removed_feature):

    print("\n" + "=" * 60)
    print("RUNNING:", experiment_name)
    print("=" * 60)

    # Remove selected feature, if any

    remaining_numerical = [
        feature
        for feature in enhanced_numerical
        if feature != removed_feature
    ]

    # Continuous features that require scaling

    scaled_features = [
        "description_length",
        "requirements_length",
        "benefits_length",
        "missing_information_count"
    ]

    scaled_features = [
        feature
        for feature in scaled_features
        if feature in remaining_numerical
    ]

    # Binary features pass through without scaling

    binary_features = [
        feature
        for feature in remaining_numerical
        if feature not in scaled_features
    ]

    # Create preprocessing transformations

    transformers = [

        (
            "title",
            TfidfVectorizer(max_features=500),
            "title"
        ),

        (
            "company_profile",
            TfidfVectorizer(max_features=1000),
            "company_profile"
        ),

        (
            "description",
            TfidfVectorizer(max_features=3000),
            "description"
        ),

        (
            "requirements",
            TfidfVectorizer(max_features=2000),
            "requirements"
        ),

        (
            "benefits",
            TfidfVectorizer(max_features=1000),
            "benefits"
        ),

        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ]

    # Add scaling for continuous numerical features

    if scaled_features:

        transformers.append(
            (
                "scaled",
                StandardScaler(),
                scaled_features
            )
        )

    # Add binary numerical features

    if binary_features:

        transformers.append(
            (
                "binary",
                "passthrough",
                binary_features
            )
        )

    # Build ColumnTransformer

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    # Fit preprocessing ONLY on subtraining data

    X_subtrain_processed = preprocessor.fit_transform(
        X_subtrain
    )

    X_validation_processed = preprocessor.transform(
        X_validation
    )

    print(
        "SUBTRAINING PROCESSED:",
        X_subtrain_processed.shape
    )

    print(
        "VALIDATION PROCESSED:",
        X_validation_processed.shape
    )

    # Train Linear SVM

    model = LinearSVC(
        class_weight="balanced",
        random_state=42,
        max_iter=20000
    )

    model.fit(
        X_subtrain_processed,
        y_subtrain
    )

    print("MODEL TRAINING COMPLETED!")

    # Generate validation decision scores

    validation_scores = model.decision_function(
        X_validation_processed
    )

    # Find best threshold using validation F1

    best_threshold = None
    best_f1 = -1

    for threshold in np.arange(-1.0, 1.01, 0.1):

        predictions = (
            validation_scores >= threshold
        ).astype(int)

        current_f1 = f1_score(
            y_validation,
            predictions,
            zero_division=0
        )

        if current_f1 > best_f1:

            best_f1 = current_f1
            best_threshold = threshold

    # Generate final validation predictions

    final_predictions = (
        validation_scores >= best_threshold
    ).astype(int)

    # Calculate evaluation metrics

    precision = precision_score(
        y_validation,
        final_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        final_predictions,
        zero_division=0
    )

    final_f1 = f1_score(
        y_validation,
        final_predictions,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_validation,
        final_predictions
    )

    # Display results

    print("\nVALIDATION RESULTS")
    print("-" * 40)

    print("Removed feature:", removed_feature)

    print("Best threshold:", best_threshold)

    print(
        "Precision:",
        round(precision * 100, 2),
        "%"
    )

    print(
        "Recall:",
        round(recall * 100, 2),
        "%"
    )

    print(
        "F1 Score:",
        round(final_f1 * 100, 2),
        "%"
    )

    print("\nCONFUSION MATRIX:")
    print(matrix)

    # Return experiment results

    return {
        "experiment": experiment_name,
        "removed_feature": removed_feature,
        "threshold": best_threshold,
        "precision": precision,
        "recall": recall,
        "f1": final_f1
    }


# ============================================================
# STEP 8: RUN ALL ABLATION EXPERIMENTS
# ============================================================

results = []

for experiment_name, removed_feature in ablation_experiments.items():

    result = run_individual_ablation(
        experiment_name,
        removed_feature
    )

    results.append(result)


# ============================================================
# STEP 9: COMPARE EXPERIMENT RESULTS
# ============================================================

results_df = pd.DataFrame(results)

print("\n\nFINAL INDIVIDUAL ABLATION COMPARISON")
print("=" * 70)

print(
    results_df[
        [
            "experiment",
            "threshold",
            "precision",
            "recall",
            "f1"
        ]
    ].to_string(index=False)
)


# ============================================================
# STEP 10: CALCULATE F1 DIFFERENCE FROM CONTROL
# ============================================================

control_f1 = results_df.loc[
    results_df["removed_feature"].isna(),
    "f1"
].iloc[0]


results_df["f1_change_percentage_points"] = (
    results_df["f1"] - control_f1
) * 100


print("\nF1 CHANGE COMPARED WITH CONTROL")
print("=" * 50)

print(
    results_df[
        [
            "experiment",
            "f1_change_percentage_points"
        ]
    ].to_string(index=False)
)


print("\nINDIVIDUAL FEATURE ABLATION COMPLETED!")
