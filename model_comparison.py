
import pandas as pd

from scipy.sparse import load_npz

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Load processed data
X_train = load_npz("data/processed/X_train_processed.npz")
X_test = load_npz("data/processed/X_test_processed.npz")

y_train = pd.read_csv("data/processed/y_train.csv").squeeze()
y_test = pd.read_csv("data/processed/y_test.csv").squeeze()

# Create models
models = {
    "Logistic Regression": LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    ),

    "Linear SVM": LinearSVC(
        class_weight="balanced",
        random_state=42,
        max_iter=5000
    )
}

results = []

# Train and evaluate each model
for name, model in models.items():

    print("\nTraining:", name)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    results.append({
        "Model": name,
        "Accuracy": round(
            accuracy_score(y_test, predictions) * 100, 2
        ),
        "Precision": round(
            precision_score(y_test, predictions) * 100, 2
        ),
        "Recall": round(
            recall_score(y_test, predictions) * 100, 2
        ),
        "F1 Score": round(
            f1_score(y_test, predictions) * 100, 2
        )
    })

# Display comparison
comparison = pd.DataFrame(results)

print("\nMODEL COMPARISON:")
print(comparison.to_string(index=False))

# Select model with highest F1 score
best_model = comparison.loc[
    comparison["F1 Score"].idxmax()
]

print("\nBEST MODEL BASED ON F1 SCORE:")
print(best_model)
