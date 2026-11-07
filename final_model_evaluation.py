
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# STEP 1: LOAD CLEANED DATASET
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")

print("ORIGINAL DATASET SHAPE:", df.shape)

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]


# ============================================================
# STEP 2: CREATE ENGINEERED FEATURES
# ============================================================

# Text length features

for column in ["description", "requirements", "benefits"]:

    text = df[column].fillna("").astype(str)

    text = text.replace("Not Specified", "")

    df[column + "_length"] = text.str.len()


# Missing information features

df["missing_company_profile"] = (
    df["company_profile"] == "Not Specified"
).astype(int)

df["missing_requirements"] = (
    df["requirements"] == "Not Specified"
).astype(int)

df["missing_benefits"] = (
    df["benefits"] == "Not Specified"
).astype(int)


# Short description feature

df["short_description"] = (
    df["description_length"] < 200
).astype(int)


# Placeholder description feature

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


# Total missing information count

missing_columns = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits"
]

df["missing_information_count"] = (
    df[missing_columns].sum(axis=1)
)


# ============================================================
# STEP 3: SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["job_id", "fraudulent"])

y = df["fraudulent"]

print("\nENGINEERED DATASET SHAPE:", X.shape)


# ============================================================
# STEP 4: CREATE OUTER TRAIN-TEST SPLIT
# ============================================================

X_train_outer, X_test, y_train_outer, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ============================================================
# STEP 5: CREATE SUBTRAINING-VALIDATION SPLIT
# ============================================================

X_subtrain, X_validation, y_subtrain, y_validation = train_test_split(
    X_train_outer,
    y_train_outer,
    test_size=0.2,
    random_state=42,
    stratify=y_train_outer
)


print("\nFINAL THREE-WAY DATA SPLIT")
print("Subtraining:", X_subtrain.shape)
print("Validation:", X_validation.shape)
print("Untouched Test:", X_test.shape)


# ============================================================
# STEP 6: DEFINE FEATURE GROUPS
# ============================================================

baseline_numerical = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]

scaled_features = [
    "description_length",
    "requirements_length",
    "benefits_length",
    "missing_information_count"
]

binary_features = baseline_numerical + [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description"
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


# ============================================================
# STEP 7: CREATE FINAL PREPROCESSOR
# ============================================================

final_preprocessor = ColumnTransformer(
    transformers=[

        ("title",
         TfidfVectorizer(max_features=500),
         "title"),

        ("company_profile",
         TfidfVectorizer(max_features=1000),
         "company_profile"),

        ("description",
         TfidfVectorizer(max_features=3000),
         "description"),

        ("requirements",
         TfidfVectorizer(max_features=2000),
         "requirements"),

        ("benefits",
         TfidfVectorizer(max_features=1000),
         "benefits"),

        ("categorical",
         OneHotEncoder(handle_unknown="ignore"),
         categorical_features),

        ("scaled",
         StandardScaler(),
         scaled_features),

        ("binary",
         "passthrough",
         binary_features)
    ]
)


print("\nFINAL PREPROCESSOR CREATED!")


# ============================================================
# STEP 8: FIT PREPROCESSOR ON SUBTRAINING DATA ONLY
# ============================================================

print("\nFITTING PREPROCESSOR ON SUBTRAINING DATA...")

X_subtrain_processed = final_preprocessor.fit_transform(
    X_subtrain
)

X_validation_processed = final_preprocessor.transform(
    X_validation
)

X_test_processed = final_preprocessor.transform(
    X_test
)


# ============================================================
# STEP 9: DISPLAY PROCESSED DATA SHAPES
# ============================================================

print("\nPREPROCESSING COMPLETED!")

print("SUBTRAINING PROCESSED SHAPE:",
      X_subtrain_processed.shape)

print("VALIDATION PROCESSED SHAPE:",
      X_validation_processed.shape)

print("TEST PROCESSED SHAPE:",
      X_test_processed.shape)


# ============================================================
# STEP 10: CREATE LINEAR SVM MODEL
# ============================================================

final_model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=20000
)


# ============================================================
# STEP 11: TRAIN MODEL ON SUBTRAINING DATA
# ============================================================

print("\nTRAINING FINAL LINEAR SVM...")

final_model.fit(
    X_subtrain_processed,
    y_subtrain
)

print("FINAL MODEL TRAINING COMPLETED!")


# ============================================================
# STEP 12: GENERATE VALIDATION DECISION SCORES
# ============================================================

validation_scores = final_model.decision_function(
    X_validation_processed
)

print("\nVALIDATION DECISION SCORES GENERATED!")


# ============================================================
# STEP 13: SELECT BEST THRESHOLD USING VALIDATION DATA
# ============================================================

print("\nVALIDATION THRESHOLD TUNING")
print("=" * 60)

thresholds = np.arange(-1.0, 1.01, 0.1)

best_threshold = 0
best_f1 = -1

for threshold in thresholds:

    validation_predictions = (
        validation_scores >= threshold
    ).astype(int)

    precision = precision_score(
        y_validation,
        validation_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        validation_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_validation,
        validation_predictions,
        zero_division=0
    )

    if f1 > best_f1:

        best_f1 = f1
        best_threshold = threshold

        best_precision = precision
        best_recall = recall


print("\nBEST VALIDATION THRESHOLD:", best_threshold)

print("VALIDATION PRECISION:",
      round(best_precision * 100, 2), "%")

print("VALIDATION RECALL:",
      round(best_recall * 100, 2), "%")

print("VALIDATION F1 SCORE:",
      round(best_f1 * 100, 2), "%")

# ============================================================
# STEP 13A: VALIDATION ERROR ANALYSIS
# ============================================================

print("\nVALIDATION ERROR ANALYSIS")
print("=" * 60)

# Generate predictions using the selected threshold

validation_predictions = (
    validation_scores >= best_threshold
).astype(int)


# Create analysis dataframe

validation_analysis = X_validation.copy()

validation_analysis["actual"] = y_validation

validation_analysis["predicted"] = validation_predictions

validation_analysis["decision_score"] = validation_scores


# Identify false negatives

false_negatives = validation_analysis[
    (validation_analysis["actual"] == 1) &
    (validation_analysis["predicted"] == 0)
]


# Identify false positives

false_positives = validation_analysis[
    (validation_analysis["actual"] == 0) &
    (validation_analysis["predicted"] == 1)
]


print("\nTOTAL VALIDATION FALSE NEGATIVES:",
      len(false_negatives))

print("TOTAL VALIDATION FALSE POSITIVES:",
      len(false_positives))


# Display missed fraudulent job information

print("\nMISSED FRAUDULENT POSTINGS")
print("=" * 60)

columns_to_display = [
    "title",
    "location",
    "company_profile",
    "description",
    "requirements",
    "employment_type",
    "industry",
    "actual",
    "predicted",
    "decision_score"
]

print(
    false_negatives[columns_to_display]
    .head(10)
    .to_string(index=False)
)


# Save false negatives

false_negatives.to_csv(
    "data/processed/validation_false_negatives.csv",
    index=False
)


# Save false positives

false_positives.to_csv(
    "data/processed/validation_false_positives.csv",
    index=False
)


print("\nVALIDATION ERROR ANALYSIS COMPLETED!")

print("False negatives saved:")
print("data/processed/validation_false_negatives.csv")

print("\nFalse positives saved:")
print("data/processed/validation_false_positives.csv")

# ============================================================
# STEP 13B: MISSED VS DETECTED FRAUD COMPARISON
# ============================================================

print("\nMISSED VS DETECTED FRAUD COMPARISON")
print("=" * 60)


# Select all actual fraudulent postings

actual_fraud = validation_analysis[
    validation_analysis["actual"] == 1
].copy()


# Separate correctly detected and missed fraud

detected_fraud = actual_fraud[
    actual_fraud["predicted"] == 1
]

missed_fraud = actual_fraud[
    actual_fraud["predicted"] == 0
]


print("\nGROUP COUNTS")
print("=" * 60)

print("Correctly detected fraud:", len(detected_fraud))
print("Missed fraud:", len(missed_fraud))


# Features to compare

features_to_compare = [
    "missing_company_profile",
    "missing_requirements",
    "missing_benefits",
    "short_description",
    "placeholder_description",
    "description_length",
    "requirements_length",
    "benefits_length",
    "missing_information_count"
]


# Compare both groups

comparison = pd.DataFrame({
    "Detected Fraud": detected_fraud[features_to_compare].mean(),
    "Missed Fraud": missed_fraud[features_to_compare].mean()
})


print("\nFEATURE COMPARISON")
print("=" * 60)

print(comparison.round(3))


# Compare median text lengths

print("\nMEDIAN TEXT LENGTH COMPARISON")
print("=" * 60)

for column in [
    "description_length",
    "requirements_length",
    "benefits_length"
]:

    print(f"\n{column}")

    print(
        "Detected fraud median:",
        detected_fraud[column].median()
    )

    print(
        "Missed fraud median:",
        missed_fraud[column].median()
    )


# Analyse decision scores

print("\nDECISION SCORE COMPARISON")
print("=" * 60)

print(
    "Detected fraud average score:",
    round(detected_fraud["decision_score"].mean(), 4)
)

print(
    "Missed fraud average score:",
    round(missed_fraud["decision_score"].mean(), 4)
)


# Save comparison

comparison.to_csv(
    "data/processed/missed_vs_detected_fraud_comparison.csv"
)


print("\nCOMPARISON COMPLETED!")

print(
    "Saved: data/processed/"
    "missed_vs_detected_fraud_comparison.csv"
)

# ============================================================
# STEP 14: GENERATE TEST DECISION SCORES
# ============================================================

test_scores = final_model.decision_function(
    X_test_processed
)

print("\nTEST DECISION SCORES GENERATED!")


# ============================================================
# STEP 15: APPLY VALIDATION THRESHOLD TO TEST DATA
# ============================================================

test_predictions = (
    test_scores >= best_threshold
).astype(int)


# ============================================================
# STEP 16: FINAL TEST EVALUATION
# ============================================================

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)


print("\n" + "=" * 60)
print("FINAL MODEL PERFORMANCE ON UNTOUCHED TEST DATA")
print("=" * 60)

print("Selected threshold:", best_threshold)

print("Accuracy:",
      round(test_accuracy * 100, 2), "%")

print("Fraud Precision:",
      round(test_precision * 100, 2), "%")

print("Fraud Recall:",
      round(test_recall * 100, 2), "%")

print("Fraud F1 Score:",
      round(test_f1 * 100, 2), "%")


# ============================================================
# STEP 17: CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    test_predictions
)

print("\nCONFUSION MATRIX")
print(cm)


# ============================================================
# STEP 18: CLASSIFICATION REPORT
# ============================================================

print("\nCLASSIFICATION REPORT")

print(
    classification_report(
        y_test,
        test_predictions,
        target_names=["Genuine Jobs", "Fraudulent Jobs"],
        zero_division=0
    )
)


print("\nFINAL MODEL EVALUATION COMPLETED!")
