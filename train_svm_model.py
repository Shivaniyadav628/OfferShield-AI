
import pandas as pd
import joblib

from scipy.sparse import load_npz

from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# Step 1: Load processed datasets
X_train = load_npz("data/processed/X_train_processed.npz")
X_test = load_npz("data/processed/X_test_processed.npz")

y_train = pd.read_csv("data/processed/y_train.csv").squeeze()
y_test = pd.read_csv("data/processed/y_test.csv").squeeze()

# Step 2: Create Linear SVM model
model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

# Step 3: Train model
print("\nTRAINING LINEAR SVM MODEL...")

model.fit(X_train, y_train)

print("MODEL TRAINING COMPLETED!")

# Step 4: Make predictions
y_pred = model.predict(X_test)

# Step 5: Evaluate model
print("\nLINEAR SVM PERFORMANCE:")

print("Accuracy:",
      round(accuracy_score(y_test, y_pred) * 100, 2), "%")

print("Precision:",
      round(precision_score(y_test, y_pred, zero_division=0) * 100, 2), "%")

print("Recall:",
      round(recall_score(y_test, y_pred, zero_division=0) * 100, 2), "%")

print("F1 Score:",
      round(f1_score(y_test, y_pred, zero_division=0) * 100, 2), "%")

# Step 6: Confusion matrix
print("\nCONFUSION MATRIX:")
print(confusion_matrix(y_test, y_pred))

# Step 7: Classification report
print("\nCLASSIFICATION REPORT:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Genuine", "Fraudulent"],
    zero_division=0
))

# Step 8: Save model
joblib.dump(model, "data/processed/linear_svm_model.pkl")

print("\nLINEAR SVM MODEL SAVED SUCCESSFULLY!")
