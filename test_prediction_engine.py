
from prediction_engine import predict_job_fraud


# Sample job posting
sample_job = {
    "title": "Software Engineer Intern",
    "location": "India",
    "department": "Engineering",
    "salary_range": "Not Specified",
    "company_profile": "We are a technology company developing software solutions.",
    "description": "We are looking for software engineering interns to work with our development team.",
    "requirements": "Knowledge of Python, Java, data structures and algorithms.",
    "benefits": "Mentorship, learning opportunities and internship certificate.",
    "telecommuting": 0,
    "has_company_logo": 1,
    "has_questions": 1,
    "employment_type": "Internship",
    "required_experience": "Internship",
    "required_education": "Bachelor's Degree",
    "industry": "Information Technology",
    "function": "Engineering"
}


# Run prediction
result = predict_job_fraud(sample_job)


# Display result
print("\n" + "=" * 50)
print("          OFFERSHIELD AI - PREDICTION")
print("=" * 50)

print("Prediction:", result["prediction"])
print("Risk classification:", result["result"])
print("Decision score:", result["decision_score"])
print("Selected threshold:", result["threshold"])

print("=" * 50)
# ============================================================
# TEST 2: MISSING INPUT VALIDATION
# ============================================================

print("\nTesting missing input validation...")

invalid_job = sample_job.copy()

# Remove the title field
del invalid_job["title"]

try:
    predict_job_fraud(invalid_job)

except ValueError as error:
    print("Validation successful!")
    print("Error:", error)

    # ============================================================
# TEST 3: EXTRA INPUT FIELDS
# ============================================================

print("\nTesting extra input fields...")

extra_job = sample_job.copy()

extra_job["company_website"] = "https://example.com"
extra_job["recruiter_email"] = "hr@example.com"

extra_result = predict_job_fraud(extra_job)

print("Extra fields handled successfully!")
print("Prediction:", extra_result["prediction"])
print("Classification:", extra_result["result"])


# ============================================================
# TEST 4: MISSING AND EMPTY VALUES
# ============================================================

print("\nTesting missing and empty values...")

incomplete_job = sample_job.copy()

# Simulate missing text information
incomplete_job["company_profile"] = None
incomplete_job["salary_range"] = ""
incomplete_job["benefits"] = None

# Simulate missing numerical information
incomplete_job["has_company_logo"] = None

# Run prediction
incomplete_result = predict_job_fraud(incomplete_job)

print("Missing values handled successfully!")
print("Prediction:", incomplete_result["prediction"])
print("Classification:", incomplete_result["result"])
print("Decision score:", incomplete_result["decision_score"])

# ============================================================
# TEST 5: INVALID NUMERICAL INPUT VALIDATION
# ============================================================

print("\nTesting invalid numerical input...")

invalid_numerical_job = sample_job.copy()

# Set an invalid value
invalid_numerical_job["has_company_logo"] = 2

try:
    predict_job_fraud(invalid_numerical_job)

except ValueError as error:
    print("Numerical validation successful!")
    print("Error:", error)

    # ============================================================
# TEST 6: INVALID INPUT TYPE
# ============================================================

print("\nTesting invalid input type...")

try:
    predict_job_fraud("This is not a dictionary")

except TypeError as error:
    print("Input type validation successful!")
    print("Error:", error)