
from fastapi.testclient import TestClient

from backend.main import app


# Create a test client for our FastAPI application
client = TestClient(app)


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
# TEST 2: HEALTH CHECK ENDPOINT
# ============================================================

def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["application"] == "OfferShield AI"


# ============================================================
# TEST 3: PREDICTION ENDPOINT
# ============================================================

def test_prediction_endpoint():

    job_data = {
        "title": "Software Engineer Intern",
        "location": "Bangalore, India",
        "department": "Engineering",
        "salary_range": "30000-50000",
        "company_profile": "An established technology company.",
        "description": "We are looking for a software engineering intern.",
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

    response = client.post("/predict", json=job_data)

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] in [0, 1]

    assert data["result"] in [
        "Likely Genuine",
        "Potentially Fraudulent"
    ]

    assert isinstance(data["decision_score"], float)

    assert isinstance(data["threshold"], float)


# ============================================================
# TEST 4: EXPLANATION ENDPOINT
# ============================================================

def test_explanation_endpoint():

    job_data = {
        "title": "Software Engineer Intern",
        "location": "Bangalore, India",
        "department": "Engineering",
        "salary_range": "30000-50000",
        "company_profile": "An established technology company.",
        "description": "We are looking for a software engineering intern.",
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

    response = client.post("/explain", json=job_data)

    assert response.status_code == 200

    data = response.json()

    assert data["job_title"] == "Software Engineer Intern"

    assert data["prediction"] in [0, 1]

    assert "fraud_increasing_signals" in data

    assert "genuine_increasing_signals" in data

    assert data["mathematical_verification"]["verified"] is True


# ============================================================
# TEST 5: MISSING REQUIRED FIELD
# ============================================================

def test_prediction_missing_field():

    job_data = {
        "location": "Bangalore, India"
    }

    response = client.post("/predict", json=job_data)

    assert response.status_code == 422


# ============================================================
# TEST 6: INVALID NUMERICAL VALUE
# ============================================================

def test_prediction_invalid_numerical_value():

    job_data = {
        "title": "Software Engineer Intern",
        "location": "Bangalore, India",
        "department": "Engineering",
        "salary_range": "30000-50000",
        "company_profile": "Technology company.",
        "description": "Software engineering internship.",
        "requirements": "Java and Python.",
        "benefits": "Mentorship.",
        "telecommuting": 0,
        "has_company_logo": 2,
        "has_questions": 1,
        "employment_type": "Internship",
        "required_experience": "Internship",
        "required_education": "Bachelor's Degree",
        "industry": "Information Technology",
        "function": "Engineering"
    }

    response = client.post("/predict", json=job_data)

    assert response.status_code == 422

# ============================================================
# TEST 7: EXPLANATION WITH MISSING REQUIRED FIELD
# ============================================================

def test_explanation_missing_field():

    job_data = {
        "title": "Software Engineer Intern"
    }

    response = client.post("/explain", json=job_data)

    assert response.status_code == 422


# ============================================================
# TEST 8: EXPLANATION WITH INVALID NUMERICAL VALUE
# ============================================================

def test_explanation_invalid_numerical_value():

    job_data = {
        "title": "Software Engineer Intern",
        "location": "Bangalore, India",
        "department": "Engineering",
        "salary_range": "30000-50000",
        "company_profile": "Technology company.",
        "description": "Software engineering internship.",
        "requirements": "Java and Python.",
        "benefits": "Mentorship.",
        "telecommuting": 0,
        "has_company_logo": 5,
        "has_questions": 1,
        "employment_type": "Internship",
        "required_experience": "Internship",
        "required_education": "Bachelor's Degree",
        "industry": "Information Technology",
        "function": "Engineering"
    }

    response = client.post("/explain", json=job_data)

    assert response.status_code == 422
