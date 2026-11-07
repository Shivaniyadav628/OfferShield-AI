
import pandas as pd
import numpy as np
import json

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# STEP 1: Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

# STEP 2: Define feature groups
numerical_features = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
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

# STEP 3: Separate final test data first
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# STEP 4: Split training data into subtraining and validation
X_subtrain, X_val, y_subtrain, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

print("\nSUBTRAINING SHAPE:", X_subtrain.shape)
print("VALIDATION SHAPE:", X_val.shape)
print("FINAL TEST SHAPE:", X_test.shape)

# STEP 5: Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("title_tfidf",
         TfidfVectorizer(max_features=500), "title"),

        ("company_tfidf",
         TfidfVectorizer(max_features=1000), "company_profile"),

        ("description_tfidf",
         TfidfVectorizer(max_features=3000), "description"),

        ("requirements_tfidf",
         TfidfVectorizer(max_features=2000), "requirements"),

        ("benefits_tfidf",
         TfidfVectorizer(max_features=1000), "benefits"),

        ("categorical",
         OneHotEncoder(handle_unknown="ignore"),
         categorical_features),

        ("numerical",
         "passthrough",
         numerical_features)
    ]
)

# STEP 6: Fit preprocessing ONLY on subtraining data
print("\nFITTING PREPROCESSOR...")

X_subtrain_processed = preprocessor.fit_transform(X_subtrain)

# Transform validation data using learned preprocessing
X_val_processed = preprocessor.transform(X_val)

print("SUBTRAINING PROCESSED:", X_subtrain_processed.shape)
print("VALIDATION PROCESSED:", X_val_processed.shape)

# STEP 7: Train Linear SVM
model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

print("\nTRAINING LINEAR SVM...")

model.fit(X_subtrain_processed, y_subtrain)

print("MODEL TRAINING COMPLETED!")

# STEP 8: Get validation decision scores
decision_scores = model.decision_function(X_val_processed)

# STEP 9: Test different thresholds
thresholds = np.arange(-1.0, 1.01, 0.1)

results = []

for threshold in thresholds:

    predictions = (
        decision_scores >= threshold
    ).astype(int)

    precision = precision_score(
        y_val, predictions, zero_division=0
    )

    recall = recall_score(
        y_val, predictions, zero_division=0
    )

    f1 = f1_score(
        y_val, predictions, zero_division=0
    )

    results.append({
        "Threshold": round(threshold, 2),
        "Precision": round(precision * 100, 2),
        "Recall": round(recall * 100, 2),
        "F1 Score": round(f1 * 100, 2)
    })

# STEP 10: Find best validation threshold
results_df = pd.DataFrame(results)

print("\nCLEAN VALIDATION THRESHOLD RESULTS:")
print(results_df.to_string(index=False))

best_result = results_df.loc[
    results_df["F1 Score"].idxmax()
]

best_threshold = float(best_result["Threshold"])

print("\nBEST VALIDATION RESULT:")
print(best_result)

# STEP 11: Display confusion matrix
best_predictions = (
    decision_scores >= best_threshold
).astype(int)

print("\nVALIDATION CONFUSION MATRIX:")
print(confusion_matrix(y_val, best_predictions))

# STEP 12: Save selected threshold
with open(
    "data/processed/best_threshold.json",
    "w"
) as file:

    json.dump(
        {"best_threshold": best_threshold},
        file,
        indent=4
    )

print("\nBEST THRESHOLD SAVED SUCCESSFULLY!")


from sklearn.metrics import accuracy_score, classification_report

# STEP 13: Transform untouched test data
X_test_processed = preprocessor.transform(X_test)

print("\nTEST DATA PROCESSED:", X_test_processed.shape)

# STEP 14: Get test decision scores
test_scores = model.decision_function(X_test_processed)

# STEP 15: Apply the threshold selected on validation data
test_predictions = (
    test_scores >= best_threshold
).astype(int)

# STEP 16: Evaluate final test performance
accuracy = accuracy_score(y_test, test_predictions)

precision = precision_score(
    y_test, test_predictions, zero_division=0
)

recall = recall_score(
    y_test, test_predictions, zero_division=0
)

f1 = f1_score(
    y_test, test_predictions, zero_division=0
)

print("\n========== FINAL TEST RESULTS ==========")

print("Selected Threshold:", best_threshold)
print("Accuracy:", round(accuracy * 100, 2), "%")
print("Fraud Precision:", round(precision * 100, 2), "%")
print("Fraud Recall:", round(recall * 100, 2), "%")
print("Fraud F1 Score:", round(f1 * 100, 2), "%")

# STEP 17: Confusion matrix
print("\nFINAL TEST CONFUSION MATRIX:")
print(confusion_matrix(y_test, test_predictions))

# STEP 18: Detailed classification report
print("\nFINAL TEST CLASSIFICATION REPORT:")

print(
    classification_report(
        y_test,
        test_predictions,
        target_names=["Genuine", "Fraudulent"],
        zero_division=0
    )
)

import joblib

# Save trained Linear SVM model
joblib.dump(
    model,
    "data/processed/final_svm_model.pkl"
)

# Save fitted preprocessing pipeline
joblib.dump(
    preprocessor,
    "data/processed/final_preprocessor.pkl"
)

print("\nFINAL MODEL SAVED SUCCESSFULLY!")
print("PREPROCESSOR SAVED SUCCESSFULLY!")