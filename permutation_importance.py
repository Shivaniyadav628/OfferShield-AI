
import pandas as pd
import numpy as np
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# STEP 1: Load cleaned dataset
df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)

X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

# STEP 2: Recreate the EXACT original data split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_subtrain, X_val, y_subtrain, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

print("VALIDATION DATA SHAPE:", X_val.shape)

# STEP 3: Load the already-trained model
model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

# STEP 4: Load the already-fitted preprocessor
preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

# STEP 5: Load selected threshold
with open(
    "data/processed/best_threshold.json",
    "r"
) as file:
    threshold = json.load(file)["best_threshold"]

print("SELECTED THRESHOLD:", threshold)

# STEP 6: Calculate original validation F1-score

X_val_processed = preprocessor.transform(X_val)

original_scores = model.decision_function(
    X_val_processed
)

original_predictions = (
    original_scores >= threshold
).astype(int)

baseline_f1 = f1_score(
    y_val,
    original_predictions,
    zero_division=0
)

print("\nBASELINE VALIDATION F1:", round(baseline_f1, 4))

# STEP 7: Perform permutation importance

rng = np.random.default_rng(42)

results = []

number_of_repeats = 5

for column in X_val.columns:

    f1_scores_after_shuffle = []

    for repeat in range(number_of_repeats):

        # Make a fresh copy of validation data
        shuffled_X = X_val.copy()

        # Randomly shuffle one original input column
        permutation = rng.permutation(len(shuffled_X))

        shuffled_X[column] = (
            shuffled_X[column].to_numpy()[permutation]
        )

        # Transform using the SAME fitted preprocessor
        shuffled_processed = preprocessor.transform(
            shuffled_X
        )

        # Predict using the SAME trained model
        shuffled_scores = model.decision_function(
            shuffled_processed
        )

        shuffled_predictions = (
            shuffled_scores >= threshold
        ).astype(int)

        # Calculate F1 after shuffling
        shuffled_f1 = f1_score(
            y_val,
            shuffled_predictions,
            zero_division=0
        )

        f1_scores_after_shuffle.append(shuffled_f1)

    # Calculate average performance decrease
    mean_shuffled_f1 = np.mean(
        f1_scores_after_shuffle
    )

    importance = baseline_f1 - mean_shuffled_f1

    results.append({
        "Feature": column,
        "Baseline_F1": baseline_f1,
        "Mean_Shuffled_F1": mean_shuffled_f1,
        "Importance": importance,
        "Std_Deviation": np.std(
            f1_scores_after_shuffle
        )
    })

# STEP 8: Display results

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="Importance",
    ascending=False
)

print("\n" + "=" * 75)
print("PERMUTATION IMPORTANCE RESULTS")
print("=" * 75)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# STEP 9: Save results

results_df.to_csv(
    "data/processed/permutation_importance.csv",
    index=False
)

print("\nPERMUTATION IMPORTANCE SAVED SUCCESSFULLY!")
