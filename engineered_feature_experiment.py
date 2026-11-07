# ============================================================
# OFFERSHIELD AI
# BASELINE VS ENHANCED FEATURE EXPERIMENT
# ============================================================


# STEP 1: Import libraries

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
    confusion_matrix,
    accuracy_score
)


# ============================================================
# STEP 2: Load the cleaned dataset
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")

print("ORIGINAL DATASET SHAPE:", df.shape)


# ============================================================
# STEP 3: Create text length features
# ============================================================

text_columns = [
    "description",
    "requirements",
    "benefits"
]

for column in text_columns:

    text = df[column].fillna("").astype(str)

    text = text.replace("Not Specified", "")

    df[column + "_length"] = text.str.len()


# ============================================================
# STEP 4: Create missing information indicators
# ============================================================

df["missing_company_profile"] = (
    df["company_profile"] == "Not Specified"
).astype(int)

df["missing_requirements"] = (
    df["requirements"] == "Not Specified"
).astype(int)

df["missing_benefits"] = (
    df["benefits"] == "Not Specified"
).astype(int)


# ============================================================
# STEP 5: Create short description feature
# ============================================================

df["short_description"] = (
    df["description_length"] < 200
).astype(int)


# ============================================================
# STEP 6: Create placeholder description feature
# ============================================================

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


# ============================================================
# STEP 7: Count missing information
# ============================================================

missing_columns = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits"
]

df["missing_information_count"] = (
    df[missing_columns].sum(axis=1)
)


# ============================================================
# STEP 8: Verify engineered features
# ============================================================

engineered_features = [
    "description_length",
    "requirements_length",
    "benefits_length",
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description",
    "missing_information_count"
]

print("\nENGINEERED FEATURES")
print("=" * 50)

print(df[engineered_features].head())

print("\nENGINEERED FEATURE COUNT:")
print(len(engineered_features))

print("\nDATASET SHAPE AFTER FEATURE ENGINEERING:")
print(df.shape)

print("\nTARGET DISTRIBUTION:")
print(df["fraudulent"].value_counts())


# ============================================================
# STEP 9: Prepare baseline and enhanced feature sets
# ============================================================

# Target variable
y = df["fraudulent"]

# Original 16 features
X_baseline = df.drop(
    columns=["job_id", "fraudulent"] + engineered_features
)

# Enhanced 25 features
X_enhanced = df.drop(
    columns=["job_id", "fraudulent"]
)

print("\nBASELINE FEATURE SET")
print("=" * 50)

print("Shape:", X_baseline.shape)
print("Number of features:", X_baseline.shape[1])

print("\nENHANCED FEATURE SET")
print("=" * 50)

print("Shape:", X_enhanced.shape)
print("Number of features:", X_enhanced.shape[1])

print("\nTARGET SHAPE:", y.shape)


# ============================================================
# STEP 10: Split the dataset
# ============================================================

# First split: training data and untouched test data

X_train_outer, X_test, y_train_outer, y_test = train_test_split(
    X_enhanced,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Second split: subtraining and validation data

X_subtrain, X_validation, y_subtrain, y_validation = train_test_split(
    X_train_outer,
    y_train_outer,
    test_size=0.2,
    random_state=42,
    stratify=y_train_outer
)


# Display dataset sizes

print("\nDATASET SPLIT RESULTS")
print("=" * 50)

print("Subtraining:", X_subtrain.shape)
print("Validation:", X_validation.shape)
print("Untouched Test:", X_test.shape)

print("\nTARGET DISTRIBUTION")

print("\nSubtraining:")
print(y_subtrain.value_counts())

print("\nValidation:")
print(y_validation.value_counts())

print("\nTest:")
print(y_test.value_counts())


# ============================================================
# STEP 11: Identify feature groups
# ============================================================

# Original numerical features

baseline_numerical = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]


# All engineered numerical features

engineered_numerical = [
    "description_length",
    "requirements_length",
    "benefits_length",
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description",
    "missing_information_count"
]


# Total enhanced numerical features

enhanced_numerical = (
    baseline_numerical + engineered_numerical
)


# Text features

text_features = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits"
]


# Categorical features

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


# Display feature groups

print("\nFEATURE GROUPS")
print("=" * 50)

print(
    "\nBaseline numerical features:",
    len(baseline_numerical)
)

print(
    "Enhanced numerical features:",
    len(enhanced_numerical)
)

print("Text features:", len(text_features))

print(
    "Categorical features:",
    len(categorical_features)
)

print(
    "\nTOTAL BASELINE FEATURES:",
    len(baseline_numerical)
    + len(text_features)
    + len(categorical_features)
)

print(
    "\nTOTAL ENHANCED FEATURES:",
    len(enhanced_numerical)
    + len(text_features)
    + len(categorical_features)
)


# ============================================================
# STEP 12: Create baseline preprocessing pipeline
# ============================================================

baseline_preprocessor = ColumnTransformer(
    transformers=[

        # Convert title into TF-IDF features

        (
            "title",
            TfidfVectorizer(max_features=500),
            "title"
        ),

        # Convert company profile into TF-IDF features

        (
            "company_profile",
            TfidfVectorizer(max_features=1000),
            "company_profile"
        ),

        # Convert description into TF-IDF features

        (
            "description",
            TfidfVectorizer(max_features=3000),
            "description"
        ),

        # Convert requirements into TF-IDF features

        (
            "requirements",
            TfidfVectorizer(max_features=2000),
            "requirements"
        ),

        # Convert benefits into TF-IDF features

        (
            "benefits",
            TfidfVectorizer(max_features=1000),
            "benefits"
        ),

        # Convert categorical features into numerical features

        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),

        # Keep original binary numerical features unchanged

        (
            "numerical",
            "passthrough",
            baseline_numerical
        )

    ]
)

print("\nBASELINE PREPROCESSOR CREATED SUCCESSFULLY!")


# ============================================================
# STEP 13: Create FAIR enhanced preprocessing pipeline
# ============================================================

# Continuous features that need standardisation

scaled_features = [
    "description_length",
    "requirements_length",
    "benefits_length",
    "missing_information_count"
]


# Binary features that should remain unchanged

enhanced_binary_features = baseline_numerical + [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description"
]


# Create enhanced preprocessor

enhanced_preprocessor = ColumnTransformer(
    transformers=[

        # Text features

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

        # Categorical features

        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),

        # Standardise only continuous numerical features

        (
            "scaled",
            StandardScaler(),
            scaled_features
        ),

        # Keep all binary features unchanged

        (
            "binary",
            "passthrough",
            enhanced_binary_features
        )

    ]
)

print("\nENHANCED PREPROCESSOR CREATED SUCCESSFULLY!")


# ============================================================
# STEP 14: Fit baseline preprocessor
# ============================================================

print("\nFITTING BASELINE PREPROCESSOR...")


# Select the original 16 baseline features

baseline_columns = (
    baseline_numerical
    + text_features
    + categorical_features
)

X_subtrain_baseline = X_subtrain[
    baseline_columns
]

X_validation_baseline = X_validation[
    baseline_columns
]


# Fit and transform subtraining data

X_subtrain_baseline_processed = (
    baseline_preprocessor.fit_transform(
        X_subtrain_baseline
    )
)


# Transform validation data

X_validation_baseline_processed = (
    baseline_preprocessor.transform(
        X_validation_baseline
    )
)


print("\nBASELINE TRANSFORMATION COMPLETED!")

print(
    "Subtraining processed shape:",
    X_subtrain_baseline_processed.shape
)

print(
    "Validation processed shape:",
    X_validation_baseline_processed.shape
)


# ============================================================
# STEP 15: Fit enhanced preprocessor
# ============================================================

print("\nFITTING ENHANCED PREPROCESSOR...")


# Select all 25 enhanced features

enhanced_columns = (
    enhanced_numerical
    + text_features
    + categorical_features
)

X_subtrain_enhanced = X_subtrain[
    enhanced_columns
]

X_validation_enhanced = X_validation[
    enhanced_columns
]


# Fit and transform subtraining data

X_subtrain_enhanced_processed = (
    enhanced_preprocessor.fit_transform(
        X_subtrain_enhanced
    )
)


# Transform validation data

X_validation_enhanced_processed = (
    enhanced_preprocessor.transform(
        X_validation_enhanced
    )
)


print("\nENHANCED TRANSFORMATION COMPLETED!")
print("\nVERIFYING ENHANCED PREPROCESSOR")
print("=" * 50)

print(enhanced_preprocessor)

print("\nSCALED FEATURE NAMES:")
print(
    enhanced_preprocessor
    .named_transformers_["scaled"]
    .feature_names_in_
)

print("\nSCALER MEANS:")
print(
    enhanced_preprocessor
    .named_transformers_["scaled"]
    .mean_
)

print("\nSCALER SCALES:")
print(
    enhanced_preprocessor
    .named_transformers_["scaled"]
    .scale_
)

print(
    "Subtraining processed shape:",
    X_subtrain_enhanced_processed.shape
)

print(
    "Validation processed shape:",
    X_validation_enhanced_processed.shape
)


# ============================================================
# STEP 16: Train baseline Linear SVM
# ============================================================

print("\nTRAINING BASELINE LINEAR SVM...")

baseline_model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

baseline_model.fit(
    X_subtrain_baseline_processed,
    y_subtrain
)

print("\nBASELINE MODEL TRAINING COMPLETED!")


# ============================================================
# STEP 17: Train enhanced Linear SVM
# ============================================================

print("\nTRAINING ENHANCED LINEAR SVM...")

enhanced_model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=20000
)

enhanced_model.fit(
    X_subtrain_enhanced_processed,
    y_subtrain
)

print("\nENHANCED MODEL TRAINING COMPLETED!")


# ============================================================
# STEP 18: Generate validation decision scores
# ============================================================

print("\nGENERATING VALIDATION PREDICTIONS...")


# Baseline decision scores

baseline_validation_scores = (
    baseline_model.decision_function(
        X_validation_baseline_processed
    )
)


# Enhanced decision scores

enhanced_validation_scores = (
    enhanced_model.decision_function(
        X_validation_enhanced_processed
    )
)


print(
    "\nBASELINE SCORES GENERATED:",
    baseline_validation_scores.shape
)

print(
    "ENHANCED SCORES GENERATED:",
    enhanced_validation_scores.shape
)


print("\nFIRST 10 BASELINE SCORES:")
print(baseline_validation_scores[:10])


print("\nFIRST 10 ENHANCED SCORES:")
print(enhanced_validation_scores[:10])


# ============================================================
# STEP 19: Tune validation thresholds
# ============================================================

# These are decision-score thresholds, NOT probabilities.

thresholds = np.arange(-1.0, 1.1, 0.1)


# Store evaluation results

baseline_results = []

enhanced_results = []


# ------------------------------------------------------------
# Evaluate baseline model
# ------------------------------------------------------------

for threshold in thresholds:

    predictions = (
        baseline_validation_scores >= threshold
    ).astype(int)

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )

    baseline_results.append({

        "Threshold": round(threshold, 2),

        "Precision": precision,

        "Recall": recall,

        "F1": f1

    })


# ------------------------------------------------------------
# Evaluate enhanced model
# ------------------------------------------------------------

for threshold in thresholds:

    predictions = (
        enhanced_validation_scores >= threshold
    ).astype(int)

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )

    enhanced_results.append({

        "Threshold": round(threshold, 2),

        "Precision": precision,

        "Recall": recall,

        "F1": f1

    })


# ============================================================
# STEP 20: Find the best thresholds
# ============================================================

baseline_results_df = pd.DataFrame(
    baseline_results
)

enhanced_results_df = pd.DataFrame(
    enhanced_results
)


# Find the threshold with the highest F1 score

best_baseline = baseline_results_df.loc[
    baseline_results_df["F1"].idxmax()
]

best_enhanced = enhanced_results_df.loc[
    enhanced_results_df["F1"].idxmax()
]


# ============================================================
# STEP 21: Display threshold comparison
# ============================================================

print("\nBASELINE THRESHOLD RESULTS")
print("=" * 60)

print(
    baseline_results_df.round(4).to_string(
        index=False
    )
)


print("\nENHANCED THRESHOLD RESULTS")
print("=" * 60)

print(
    enhanced_results_df.round(4).to_string(
        index=False
    )
)


# ============================================================
# STEP 22: Display best model results
# ============================================================

print("\nBEST BASELINE RESULT")
print("=" * 60)

print(best_baseline)


print("\nBEST ENHANCED RESULT")
print("=" * 60)

print(best_enhanced)


# ============================================================
# STEP 23: Compare both models
# ============================================================

print("\nFINAL VALIDATION COMPARISON")
print("=" * 60)

comparison = pd.DataFrame({

    "Model": [
        "Baseline",
        "Enhanced"
    ],

    "Best Threshold": [
        best_baseline["Threshold"],
        best_enhanced["Threshold"]
    ],

    "Precision": [
        best_baseline["Precision"],
        best_enhanced["Precision"]
    ],

    "Recall": [
        best_baseline["Recall"],
        best_enhanced["Recall"]
    ],

    "F1 Score": [
        best_baseline["F1"],
        best_enhanced["F1"]
    ]

})

print(comparison.round(4).to_string(index=False))


# Calculate absolute F1 improvement

f1_improvement = (
    best_enhanced["F1"] - best_baseline["F1"]
)

print("\nABSOLUTE F1 IMPROVEMENT:")
print(round(f1_improvement, 4))

print(
    "F1 IMPROVEMENT IN PERCENTAGE POINTS:",
    round(f1_improvement * 100, 2)
)


# ============================================================
# STEP 24: Confusion matrices at the best thresholds
# ============================================================

baseline_best_predictions = (
    baseline_validation_scores
    >= best_baseline["Threshold"]
).astype(int)


enhanced_best_predictions = (
    enhanced_validation_scores
    >= best_enhanced["Threshold"]
).astype(int)


baseline_cm = confusion_matrix(
    y_validation,
    baseline_best_predictions
)


enhanced_cm = confusion_matrix(
    y_validation,
    enhanced_best_predictions
)


print("\nBASELINE CONFUSION MATRIX")
print("=" * 50)

print(baseline_cm)


print("\nENHANCED CONFUSION MATRIX")
print("=" * 50)

print(enhanced_cm)


# ============================================================
# EXPERIMENT COMPLETED
# ============================================================

print("\nFEATURE ENGINEERING EXPERIMENT COMPLETED!")
# STEP: GROUP ENGINEERED FEATURES FOR ABLATION STUDY

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

print("\nENGINEERED FEATURE GROUPS")
print("=" * 50)

print("Text length features:", text_length_features)
print("Missing information features:", missing_information_features)
print("Description quality features:", description_quality_features)

print("\nTOTAL ENGINEERED FEATURES:",
      len(text_length_features)
      + len(missing_information_features)
      + len(description_quality_features))

# ============================================================
# STEP 25: ABLATION STUDY
# ============================================================

def run_ablation_experiment(experiment_name, removed_features):

    print("\nRUNNING:", experiment_name)
    print("=" * 60)

    # 1. Keep only engineered features not being removed

    remaining_engineered = [
        feature
        for feature in engineered_features
        if feature not in removed_features
    ]

    # 2. Select continuous features still available

    current_scaled_features = [
        feature
        for feature in scaled_features
        if feature in remaining_engineered
    ]

    # 3. Select binary features still available

    current_binary_features = [
        feature
        for feature in enhanced_binary_features
        if feature not in removed_features
    ]

    # 4. Build preprocessing pipeline

    transformers = [
        ("title", TfidfVectorizer(max_features=500), "title"),
        ("company_profile", TfidfVectorizer(max_features=1000), "company_profile"),
        ("description", TfidfVectorizer(max_features=3000), "description"),
        ("requirements", TfidfVectorizer(max_features=2000), "requirements"),
        ("benefits", TfidfVectorizer(max_features=1000), "benefits"),
        ("categorical", OneHotEncoder(handle_unknown="ignore"),
         categorical_features)
    ]

    if current_scaled_features:
        transformers.append(
            ("scaled", StandardScaler(), current_scaled_features)
        )

    if current_binary_features:
        transformers.append(
            ("binary", "passthrough", current_binary_features)
        )

    current_preprocessor = ColumnTransformer(
        transformers=transformers
    )

    # 5. Select columns for this experiment

    current_columns = (
        baseline_numerical
        + remaining_engineered
        + text_features
        + categorical_features
    )

    X_train_current = X_subtrain[current_columns]
    X_validation_current = X_validation[current_columns]

    # 6. Fit preprocessing only on subtraining data

    X_train_processed = current_preprocessor.fit_transform(
        X_train_current
    )

    X_validation_processed = current_preprocessor.transform(
        X_validation_current
    )

    print("Training processed shape:", X_train_processed.shape)
    print("Validation processed shape:", X_validation_processed.shape)

    # 7. Train Linear SVM

    model = LinearSVC(
        class_weight="balanced",
        random_state=42,
        max_iter=20000
    )

    model.fit(X_train_processed, y_subtrain)

    # 8. Generate validation decision scores

    validation_scores = model.decision_function(
        X_validation_processed
    )

    # 9. Find the best validation threshold

    experiment_results = []

    for threshold in np.arange(-1.0, 1.1, 0.1):

        predictions = (
            validation_scores >= threshold
        ).astype(int)

        precision = precision_score(
            y_validation,
            predictions,
            zero_division=0
        )

        recall = recall_score(
            y_validation,
            predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_validation,
            predictions,
            zero_division=0
        )

        experiment_results.append({
            "Threshold": round(threshold, 2),
            "Precision": precision,
            "Recall": recall,
            "F1": f1
        })

    results_df = pd.DataFrame(experiment_results)

    best_result = results_df.loc[
        results_df["F1"].idxmax()
    ]

    # 10. Confusion matrix at the selected threshold

    best_predictions = (
        validation_scores >= best_result["Threshold"]
    ).astype(int)

    cm = confusion_matrix(
        y_validation,
        best_predictions
    )

    print("\nBEST RESULT:")
    print(best_result)

    print("\nCONFUSION MATRIX:")
    print(cm)

    return {
        "Experiment": experiment_name,
        "Features Removed": len(removed_features),
        "Best Threshold": best_result["Threshold"],
        "Precision": best_result["Precision"],
        "Recall": best_result["Recall"],
        "F1": best_result["F1"]
    }


# ============================================================
# STEP 26: Run four experiments
# ============================================================

ablation_results = []

experiments = [
    ("All 9 engineered features", []),

    ("Without text length features",
     text_length_features),

    ("Without missing information features",
     missing_information_features),

    ("Without description quality features",
     description_quality_features)
]

for experiment_name, removed_features in experiments:

    result = run_ablation_experiment(
        experiment_name,
        removed_features
    )

    ablation_results.append(result)


# ============================================================
# STEP 27: Compare ablation results
# ============================================================

ablation_df = pd.DataFrame(ablation_results)

print("\nFINAL ABLATION STUDY RESULTS")
print("=" * 70)

print(
    ablation_df.round(4).to_string(index=False)
)

print("\nABLATION STUDY COMPLETED!")
