
import pandas as pd
import numpy as np
import joblib
import json

# STEP 1: Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# STEP 2: Load saved Linear SVM model
model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

# STEP 3: Load fitted preprocessor
preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

# STEP 4: Load selected decision threshold
with open(
    "data/processed/best_threshold.json", "r"
) as file:
    threshold = json.load(file)["best_threshold"]

# STEP 5: Separate input features
X = df.drop(columns=["job_id", "fraudulent"])

# STEP 6: Get feature names
feature_names = preprocessor.get_feature_names_out()


# STEP 7: Define explanation function
def explain_job(job, actual_label):

    # Transform the job using the saved preprocessor
    processed_job = preprocessor.transform(job)

    # Calculate model decision score
    score = model.decision_function(processed_job)[0]

    # Generate prediction using selected threshold
    prediction = int(score >= threshold)

    # Calculate contribution of every feature
    contributions = processed_job.multiply(
        model.coef_[0]
    ).toarray()[0]

    # Create explanation DataFrame
    explanation = pd.DataFrame({
        "Feature": feature_names,
        "Contribution": contributions
    })

    # Remove features with zero contribution
    explanation = explanation[
        explanation["Contribution"] != 0
    ]

    # Get top 10 fraud-increasing features
    suspicious_signals = explanation.nlargest(
        10, "Contribution"
    )

    # Get top 10 fraud-decreasing features
    genuine_signals = explanation.nsmallest(
        10, "Contribution"
    )

    # Display job information
    print("\n" + "=" * 55)
    print("JOB EXPLANATION")
    print("=" * 55)

    print("Actual Label:", actual_label)

    print("Job Title:", job["title"].iloc[0])

    print("Industry:", job["industry"].iloc[0])

    print("Department:", job["department"].iloc[0])

    print(
        "Employment Type:",
        job["employment_type"].iloc[0]
    )

    # Display model prediction
    print(
        "\nModel Prediction:",
        "FRAUDULENT" if prediction == 1 else "GENUINE"
    )

    # Display decision score
    print("Decision Score:", round(score, 4))

    # Display threshold comparison
    print(
        "Fraud Decision:",
        "Above threshold" if score >= threshold
        else "Below threshold"
    )

    print("Selected Threshold:", threshold)

    # Display fraud-increasing features
    print("\nTOP FRAUD-INCREASING FEATURES:")
    print(suspicious_signals.to_string(index=False))

    # Display fraud-decreasing features
    print("\nTOP FRAUD-DECREASING FEATURES:")
    print(genuine_signals.to_string(index=False))


# STEP 8: Find one genuine job
genuine_index = df.index[
    df["fraudulent"] == 0
][0]

# STEP 9: Find one fraudulent job
fraud_index = df.index[
    df["fraudulent"] == 1
][0]


# STEP 10: Explain genuine job
explain_job(
    X.loc[[genuine_index]],
    "GENUINE"
)

# STEP 11: Explain fraudulent job
explain_job(
    X.loc[[fraud_index]],
    "FRAUDULENT"
)
