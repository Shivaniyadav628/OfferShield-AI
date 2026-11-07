
import joblib
import pandas as pd


# ============================================================
# 1. LOAD MODEL AND PREPROCESSOR
# ============================================================

model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

df = pd.read_csv(
    "data/processed/jobs_cleaned.csv"
)


# ============================================================
# 2. SELECT ONE JOB POSTING
# ============================================================

X = df.drop(
    columns=["job_id", "fraudulent"]
)

sample_job = X.iloc[[0]]


# ============================================================
# 3. TRANSFORM JOB POSTING
# ============================================================

processed_job = preprocessor.transform(sample_job)


# ============================================================
# 4. CALCULATE DECISION SCORE
# ============================================================

decision_score = model.decision_function(
    processed_job
)[0]


# ============================================================
# 5. CALCULATE FEATURE CONTRIBUTIONS
# ============================================================

contributions = processed_job.multiply(
    model.coef_[0]
).toarray()[0]


# ============================================================
# 6. CALCULATE INTERCEPT
# ============================================================

intercept = model.intercept_[0]

reconstructed_score = (
    contributions.sum() + intercept
)


# ============================================================
# 7. VERIFY MATHEMATICAL CONSISTENCY
# ============================================================

difference = abs(
    decision_score - reconstructed_score
)

print("\n" + "=" * 55)
print("OFFERSHIELD AI - EXPLANATION MATHEMATICAL AUDIT")
print("=" * 55)

print("Model Decision Score:", decision_score)

print("Sum of Contributions:", contributions.sum())

print("Model Intercept:", intercept)

print("Reconstructed Score:", reconstructed_score)

print("Difference:", difference)

print("=" * 55)

if difference < 1e-6:
    print("SUCCESS: Feature contributions correctly reconstruct the decision score.")
else:
    print("WARNING: Mathematical consistency check failed.")
