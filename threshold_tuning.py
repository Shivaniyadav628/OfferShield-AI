
import pandas as pd
import numpy as np

from scipy.sparse import load_npz

from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# Step 1: Load training data
X_train = load_npz("data/processed/X_train_processed.npz")
y_train = pd.read_csv(
    "data/processed/y_train.csv"
).squeeze()

# Step 2: Split training data into training and validation sets
X_subtrain, X_val, y_subtrain, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

print("SUBTRAINING SHAPE:", X_subtrain.shape)
print("VALIDATION SHAPE:", X_val.shape)

# Step 3: Train Linear SVM
model = LinearSVC(
    class_weight="balanced",
    random_state=42,
    max_iter=5000
)

model.fit(X_subtrain, y_subtrain)

# Step 4: Get decision scores
decision_scores = model.decision_function(X_val)

# Step 5: Test different thresholds
thresholds = np.arange(-1.0, 1.1, 0.1)

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

# Step 6: Display results
results_df = pd.DataFrame(results)

print("\nTHRESHOLD COMPARISON:")
print(results_df.to_string(index=False))

# Step 7: Find best threshold based on F1
best_result = results_df.loc[
    results_df["F1 Score"].idxmax()
]

print("\nBEST THRESHOLD:")
print(best_result)

# Step 8: Confusion matrix at best threshold
best_threshold = best_result["Threshold"]

best_predictions = (
    decision_scores >= best_threshold
).astype(int)

print("\nCONFUSION MATRIX AT BEST THRESHOLD:")
print(confusion_matrix(y_val, best_predictions))
