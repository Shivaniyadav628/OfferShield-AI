
from fastapi.testclient import TestClient
import pytest

from backend.main import app


client = TestClient(app)


# ============================================================
# SHARED TEST DATA
# ============================================================

VALID_JOB_DATA = {
    "title": "Software Engineer Intern",
    "location": "Bangalore, India",
    "department": "Engineering",
    "salary_range": "30000-50000",
    "company_profile": (
        "An established technology company developing "
        "innovative software solutions for businesses."
    ),
    "description": (
        "We are looking for a software engineering intern. "
        "Candidates should know Python, Java and DSA. "
        "Apply through our careers page."
    ),
    "requirements": "Knowledge of Python, Java and DSA.",
    "benefits": "Mentorship and internship certificate.",
    "telecommuting": 0,
    "has_company_logo": 1,
    "has_questions": 1,
    "employment_type": "Internship",
    "required_experience": "Internship",
    "required_education": "Bachelor's Degree",
    "industry": "Information Technology",
    "function": "Engineering"
}


# ============================================================
# TEST 1: ROOT ENDPOINT
# ============================================================

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "OfferShield AI"
    assert data["status"] == "Running successfully"


# ============================================================
# TEST 2: HEALTH CHECK
# ============================================================

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "OfferShield AI"
    assert data["version"] == "1.0.0"


# ============================================================
# TEST 3: JOB PREDICTION
# ============================================================

def test_prediction_endpoint():
    response = client.post(
        "/predict",
        json=VALID_JOB_DATA
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] in [0, 1]

    assert data["result"] in [
        "Likely Genuine",
        "Potentially Fraudulent"
    ]

    assert isinstance(data["decision_score"], (int, float))
    assert isinstance(data["threshold"], (int, float))


# ============================================================
# TEST 4: EXPLAINABLE AI
# ============================================================

def test_explanation_endpoint():
    response = client.post(
        "/explain",
        json=VALID_JOB_DATA
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_title"] == "Software Engineer Intern"
    assert data["prediction"] in [0, 1]

    assert "fraud_increasing_signals" in data
    assert "genuine_increasing_signals" in data
    assert "mathematical_verification" in data

    assert data["mathematical_verification"]["verified"] is True


# ============================================================
# TEST 5: PREDICTION WITH MISSING FIELD
# ============================================================

def test_prediction_missing_field():
    response = client.post(
        "/predict",
        json={"location": "Bangalore, India"}
    )

    assert response.status_code == 422


# ============================================================
# TEST 6: PREDICTION WITH INVALID NUMERICAL VALUE
# ============================================================

def test_prediction_invalid_numerical_value():
    job_data = VALID_JOB_DATA.copy()
    job_data["has_company_logo"] = 2

    response = client.post(
        "/predict",
        json=job_data
    )

    assert response.status_code == 422


# ============================================================
# TEST 7: EXPLANATION WITH MISSING FIELD
# ============================================================

def test_explanation_missing_field():
    response = client.post(
        "/explain",
        json={"title": "Software Engineer Intern"}
    )

    assert response.status_code == 422


# ============================================================
# TEST 8: EXPLANATION WITH INVALID NUMERICAL VALUE
# ============================================================

def test_explanation_invalid_numerical_value():
    job_data = VALID_JOB_DATA.copy()
    job_data["has_company_logo"] = 5

    response = client.post(
        "/explain",
        json=job_data
    )

    assert response.status_code == 422


# ============================================================
# TEST 9: COMPANY VERIFICATION
# ============================================================

def test_company_verification_endpoint():
    response = client.post(
        "/verify-company",
        json=VALID_JOB_DATA
    )

    assert response.status_code == 200

    data = response.json()

    assert data["review_type"] == "Company Information Review"

    assert data["total_checks"] == 6

    assert len(data["checks"]) == 6

    assert "passed_checks" in data
    assert "warning_checks" in data


# ============================================================
# TEST 10: COMPANY VERIFICATION CHECK NAMES
# ============================================================

def test_company_verification_check_names():
    response = client.post(
        "/verify-company",
        json=VALID_JOB_DATA
    )

    assert response.status_code == 200

    data = response.json()

    check_names = [
        check["name"]
        for check in data["checks"]
    ]

    expected_checks = [
        "Company profile",
        "Job description",
        "Contact information",
        "Application instructions",
        "Job title",
        "Benefits information"
    ]

    assert check_names == expected_checks


# ============================================================
# TEST 11: COMPANY VERIFICATION MISSING FIELD
# ============================================================

def test_company_verification_missing_field():
    response = client.post(
        "/verify-company",
        json={"title": "Software Engineer Intern"}
    )

    assert response.status_code == 422


# ============================================================
# TEST 12: COMPANY VERIFICATION DISCLAIMER
# ============================================================

def test_company_verification_disclaimer():
    response = client.post(
        "/verify-company",
        json=VALID_JOB_DATA
    )

    assert response.status_code == 200

    data = response.json()

    assert "does not independently" in data["disclaimer"]

    assert "employer legitimacy" in data["disclaimer"]


# ============================================================
# TEST 13: COMPANY VERIFICATION WITH MISSING INFORMATION
# ============================================================

def test_company_verification_missing_information():
    job_data = VALID_JOB_DATA.copy()

    job_data["company_profile"] = ""
    job_data["description"] = ""
    job_data["benefits"] = ""

    response = client.post(
        "/verify-company",
        json=job_data
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Needs Attention"

    assert data["warning_checks"] > 0

    assert data["passed_checks"] < data["total_checks"]


# ============================================================
# TEST 14: ALL BINARY FIELDS REJECT INVALID VALUES
# ============================================================

@pytest.mark.parametrize(
    "field",
    [
        "telecommuting",
        "has_company_logo",
        "has_questions"
    ]
)
@pytest.mark.parametrize("invalid_value", [-1, 2])
def test_prediction_invalid_binary_fields(field, invalid_value):

    job_data = VALID_JOB_DATA.copy()
    job_data[field] = invalid_value

    response = client.post("/predict", json=job_data)

    assert response.status_code == 422


# ============================================================
# TEST 15: EXPLANATION REJECTS INVALID BINARY FIELDS
# ============================================================

@pytest.mark.parametrize(
    "field",
    [
        "telecommuting",
        "has_company_logo",
        "has_questions"
    ]
)
@pytest.mark.parametrize("invalid_value", [-1, 2])
def test_explanation_invalid_binary_fields(field, invalid_value):

    job_data = VALID_JOB_DATA.copy()
    job_data[field] = invalid_value

    response = client.post("/explain", json=job_data)

    assert response.status_code == 422


# ============================================================
# TEST 16: PREDICTION AND EXPLANATION CONSISTENCY
# ============================================================

def test_prediction_explanation_consistency():

    prediction_response = client.post(
        "/predict",
        json=VALID_JOB_DATA
    )

    explanation_response = client.post(
        "/explain",
        json=VALID_JOB_DATA
    )

    assert prediction_response.status_code == 200
    assert explanation_response.status_code == 200

    prediction = prediction_response.json()
    explanation = explanation_response.json()

    assert prediction["prediction"] == explanation["prediction"]

    assert prediction["result"] == explanation["risk_classification"]

    assert prediction["decision_score"] == pytest.approx(
        explanation["decision_score"],
        abs=1e-6
    )
