
import pandas as pd

from scipy.sparse import load_npz

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import joblib

# Step 1: Load processed training and testing data
X_train = load_npz("data/processed/X_train_processed.npz")
X_test = load_npz("data/processed/X_test_processed.npz")

y_train = pd.read_csv("data/processed/y_train.csv").squeeze()
y_test = pd.read_csv("data/processed/y_test.csv").squeeze()

print("TRAINING DATA SHAPE:", X_train.shape)
print("TESTING DATA SHAPE:", X_test.shape)

# Step 2: Create Logistic Regression model
model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=42
)

# Step 3: Train the model
print("\nTRAINING MODEL...")

model.fit(X_train, y_train)

print("MODEL TRAINING COMPLETED!")

# Step 4: Make predictions
y_pred = model.predict(X_test)

# Step 5: Evaluate model performance
accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(y_test, y_pred, zero_division=0)

recall = recall_score(y_test, y_pred, zero_division=0)

f1 = f1_score(y_test, y_pred, zero_division=0)

print("\nMODEL PERFORMANCE:")
print("Accuracy:", round(accuracy * 100, 2), "%")
print("Precision:", round(precision * 100, 2), "%")
print("Recall:", round(recall * 100, 2), "%")
print("F1 Score:", round(f1 * 100, 2), "%")

# Step 6: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)

print("\nCONFUSION MATRIX:")
print(cm)

# Step 7: Detailed classification report
print("\nCLASSIFICATION REPORT:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Genuine", "Fraudulent"],
    zero_division=0
))

# Step 8: Save trained model
joblib.dump(model, "data/processed/logistic_model.pkl")

print("\nMODEL SAVED SUCCESSFULLY!")
