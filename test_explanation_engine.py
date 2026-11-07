
import json
import pandas as pd

from explanation_engine import explain_job


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv("data/processed/jobs_cleaned.csv")

X = df.drop(columns=["job_id", "fraudulent"])


# ============================================================
# TEST 1: VALID JOB INPUT
# ============================================================

print("\nTEST 1: Valid job input")

job = X.iloc[[0]]

result = explain_job(job)

assert isinstance(result, dict)

assert result["prediction"] in [0, 1]

assert result["risk_classification"] in [
    "Likely Genuine",
    "Potentially Fraudulent"
]

assert result["mathematical_verification"]["verified"] is True

print("PASSED: Valid job explanation generated successfully!")


# ============================================================
# TEST 2: INVALID INPUT TYPE
# ============================================================

print("\nTEST 2: Invalid input type")

try:

    explain_job("This is not a DataFrame")

    raise AssertionError(
        "Expected TypeError was not raised!"
    )

except TypeError as error:

    print("PASSED:", error)


# ============================================================
# TEST 3: EMPTY DATAFRAME
# ============================================================

print("\nTEST 3: Empty DataFrame")

try:

    empty_job = pd.DataFrame()

    explain_job(empty_job)

    raise AssertionError(
        "Expected ValueError was not raised!"
    )

except ValueError as error:

    print("PASSED:", error)


# ============================================================
# TEST 4: MULTIPLE JOB POSTINGS
# ============================================================

print("\nTEST 4: Multiple job postings")

try:

    multiple_jobs = pd.concat(
        [job, job],
        ignore_index=True
    )

    explain_job(multiple_jobs)

    raise AssertionError(
        "Expected ValueError was not raised!"
    )

except ValueError as error:

    print("PASSED:", error)


# ============================================================
# TEST 5: MISSING TITLE COLUMN
# ============================================================

print("\nTEST 5: Missing title column")

try:

    invalid_job = job.drop(columns=["title"])

    explain_job(invalid_job)

    raise AssertionError(
        "Expected ValueError was not raised!"
    )

except ValueError as error:

    print("PASSED:", error)


# ============================================================
# TEST 6: MATHEMATICAL VERIFICATION
# ============================================================

print("\nTEST 6: Mathematical verification")

verification = result["mathematical_verification"]

assert verification["verified"] is True

assert abs(
    verification["actual_score"]
    - verification["reconstructed_score"]
) < 1e-9

print(
    "PASSED: Feature contributions correctly "
    "reconstruct the decision score!"
)


# ============================================================
# TEST 7: OUTPUT STRUCTURE
# ============================================================

print("\nTEST 7: Output structure")

required_keys = [
    "job_title",
    "prediction",
    "risk_classification",
    "decision_score",
    "threshold",
    "fraud_increasing_signals",
    "genuine_increasing_signals",
    "mathematical_verification"
]

for key in required_keys:

    assert key in result, f"Missing output key: {key}"

print(
    "PASSED: All required explanation output fields are present!"
)


# ============================================================
# TEST 8: EXPLANATION SIGNAL VALIDATION
# ============================================================

print("\nTEST 8: Explanation signal validation")

fraud_signals = result["fraud_increasing_signals"]

genuine_signals = result["genuine_increasing_signals"]

assert isinstance(fraud_signals, list)

assert isinstance(genuine_signals, list)

for signal in fraud_signals:

    assert signal["contribution"] > 0

for signal in genuine_signals:

    assert signal["contribution"] < 0

print(
    "PASSED: Fraud and genuine signals have "
    "the correct contribution directions!"
)


# ============================================================
# TEST 9: JSON SERIALIZATION
# ============================================================

print("\nTEST 9: JSON serialization")

try:

    json_output = json.dumps(result)

    assert isinstance(json_output, str)

    print(
        "PASSED: Explanation result can be serialized into JSON!"
    )

except (TypeError, ValueError) as error:

    print("FAILED:", error)

    raise


# ============================================================
# TEST 10: EXPLANATION SIGNAL LIMIT
# ============================================================

print("\nTEST 10: Explanation signal limit")

assert len(result["fraud_increasing_signals"]) <= 10

assert len(result["genuine_increasing_signals"]) <= 10

print(
    "PASSED: Explanation signals respect "
    "the maximum limit of 10!"
)


# ============================================================
# TEST 11: SECOND JOB POSTING
# ============================================================

print("\nTEST 11: Second job posting")

second_job = X.iloc[[100]]

second_result = explain_job(second_job)

assert isinstance(second_result, dict)

assert second_result["mathematical_verification"]["verified"] is True

assert second_result["prediction"] in [0, 1]

print("Job Title:", second_result["job_title"])

print("Prediction:", second_result["risk_classification"])

print(
    "PASSED: Second job explanation generated successfully!"
)


# ============================================================
# TEST 12: THIRD JOB POSTING
# ============================================================

print("\nTEST 12: Third job posting")

third_job = X.iloc[[500]]

third_result = explain_job(third_job)

assert isinstance(third_result, dict)

assert third_result["mathematical_verification"]["verified"] is True

assert third_result["prediction"] in [0, 1]

print("Job Title:", third_result["job_title"])

print("Prediction:", third_result["risk_classification"])

print(
    "PASSED: Third job explanation generated successfully!"
)


# ============================================================
# TEST 13: FOURTH JOB POSTING
# ============================================================

print("\nTEST 13: Fourth job posting")

fourth_job = X.iloc[[1000]]

fourth_result = explain_job(fourth_job)

assert isinstance(fourth_result, dict)

assert fourth_result["mathematical_verification"]["verified"] is True

assert fourth_result["prediction"] in [0, 1]

print("Job Title:", fourth_result["job_title"])

print("Prediction:", fourth_result["risk_classification"])

print(
    "PASSED: Fourth job explanation generated successfully!"
)


# ============================================================
# TEST 14: FIFTH JOB POSTING
# ============================================================

print("\nTEST 14: Fifth job posting")

fifth_job = X.iloc[[2000]]

fifth_result = explain_job(fifth_job)

assert isinstance(fifth_result, dict)

assert fifth_result["mathematical_verification"]["verified"] is True

assert fifth_result["prediction"] in [0, 1]

print("Job Title:", fifth_result["job_title"])

print("Prediction:", fifth_result["risk_classification"])

print(
    "PASSED: Fifth job explanation generated successfully!"
)


# ============================================================
# TEST 15: FIND A POTENTIALLY FRAUDULENT PREDICTION
# ============================================================

print("\nTEST 15: Fraud prediction validation")

fraud_prediction_found = False

for index in range(len(X)):

    sample = X.iloc[[index]]

    sample_result = explain_job(sample)

    if sample_result["prediction"] == 1:

        assert (
            sample_result["mathematical_verification"]["verified"]
            is True
        )

        print("Job Title:", sample_result["job_title"])

        print(
            "Prediction:",
            sample_result["risk_classification"]
        )

        print(
            "Decision Score:",
            sample_result["decision_score"]
        )

        fraud_prediction_found = True

        break


assert fraud_prediction_found, (
    "No potentially fraudulent prediction was found."
)

print(
    "PASSED: A potentially fraudulent prediction "
    "was explained successfully!"
)


# ============================================================
# TEST 16: DECISION THRESHOLD CONSISTENCY
# ============================================================

print("\nTEST 16: Decision threshold consistency")

assert sample_result["prediction"] == int(
    sample_result["decision_score"]
    >= sample_result["threshold"]
)

assert sample_result["prediction"] == 1

print(
    "Decision Score:",
    sample_result["decision_score"]
)

print(
    "Threshold:",
    sample_result["threshold"]
)

print(
    "PASSED: Prediction correctly matches "
    "the selected threshold!"
)


# ============================================================
# FINAL TEST SUMMARY
# ============================================================

print("\n" + "=" * 60)

print("OFFERSHIELD AI - EXPLANATION ENGINE TEST SUMMARY")

print("=" * 60)

print("Total Tests: 16")

print("Status: ALL TESTS PASSED")

print("=" * 60)

# ============================================================
# TEST 17: MISSING REQUIRED COLUMN
# ============================================================

print("\nTEST 17: Missing required column")

invalid_job = job.drop(columns=["description"])

try:

    explain_job(invalid_job)

    raise AssertionError(
        "Expected ValueError was not raised!"
    )

except ValueError as error:

    assert "description" in str(error)

    print("PASSED:", error)


# ============================================================
# TEST 18: EMPTY TEXT VALUES
# ============================================================

print("\nTEST 18: Empty text values")

empty_text_job = job.copy()

empty_text_job["company_profile"] = ""

empty_text_job["description"] = None

empty_text_result = explain_job(empty_text_job)

assert isinstance(empty_text_result, dict)

assert (
    empty_text_result["mathematical_verification"]["verified"]
    is True
)

print(
    "PASSED: Empty and missing text values "
    "were handled successfully!"
)


# ============================================================
# TEST 19: MISSING NUMERICAL VALUES
# ============================================================

print("\nTEST 19: Missing numerical values")

missing_numeric_job = job.copy()

missing_numeric_job["has_company_logo"] = None

missing_numeric_job["telecommuting"] = float("nan")

missing_numeric_result = explain_job(missing_numeric_job)

assert isinstance(missing_numeric_result, dict)

assert (
    missing_numeric_result["mathematical_verification"]["verified"]
    is True
)

print(
    "PASSED: Missing numerical values "
    "were safely replaced with zero!"
)


# ============================================================
# TEST 20: INVALID NUMERICAL VALUES
# ============================================================

print("\nTEST 20: Invalid numerical values")

invalid_numeric_job = job.copy()

invalid_numeric_job["has_company_logo"] = 2

try:

    explain_job(invalid_numeric_job)

    raise AssertionError(
        "Expected ValueError was not raised!"
    )

except ValueError as error:

    assert "has_company_logo" in str(error)

    print("PASSED:", error)


# ============================================================
# TEST 21: EXTRA INPUT COLUMNS
# ============================================================

print("\nTEST 21: Extra input columns")

extra_column_job = job.copy()

extra_column_job["unnecessary_field"] = "Extra information"

extra_column_result = explain_job(extra_column_job)

assert isinstance(extra_column_result, dict)

assert (
    extra_column_result["mathematical_verification"]["verified"]
    is True
)

print(
    "PASSED: Extra input columns were safely ignored!"
)


# ============================================================
# UPDATED FINAL TEST SUMMARY
# ============================================================

print("\n" + "=" * 60)

print("OFFERSHIELD AI - COMPLETE EXPLANATION ENGINE TESTS")

print("=" * 60)

print("Total Tests: 21")

print("Previous Tests: 16 PASSED")

print("Additional Validation Tests: 5")

print("Status: ALL TESTS PASSED")

print("=" * 60)
