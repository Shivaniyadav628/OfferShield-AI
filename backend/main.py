
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    JobInput,
    PredictionResponse,
    ExplanationResponse
)

from prediction_engine import predict_job_fraud
from explanation_engine import explain_job
from backend.company_verification import verify_company_profile


# ============================================================
# 1. CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OfferShield AI API",
    description="""
    ## Intelligent Job and Internship Fraud Detection

    OfferShield AI uses machine learning, natural language
    processing, and explainable AI to assess potentially
    fraudulent job and internship postings.

    ### Available capabilities

    - Fraud Prediction
    - Explainable AI
    - Company Information Review
    - Input Validation
    - Mathematical Verification

    Model predictions are risk assessments, not proof of fraud
    or independent verification of job legitimacy.
    """,
    version="1.0.0",
    contact={
        "name": "OfferShield AI",
        "url": "https://github.com/Shivaniyadav628/OfferShield-AI"
    }
)


# ============================================================
# 2. CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["General"])
def home():

    return {
        "message": "Welcome to OfferShield AI API!",
        "project": "OfferShield AI",
        "status": "Running successfully"
    }


# ============================================================
# 4. HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health", tags=["General"])
def health_check():

    return {
        "status": "healthy",
        "application": "OfferShield AI",
        "version": "1.0.0"
    }


# ============================================================
# 5. JOB FRAUD PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    tags=["Prediction"],
    response_model=PredictionResponse
)
def predict_job(job: JobInput):

    job_data = job.model_dump()

    return predict_job_fraud(job_data)


# ============================================================
# 6. JOB EXPLANATION ENDPOINT
# ============================================================

@app.post(
    "/explain",
    tags=["Explainable AI"],
    response_model=ExplanationResponse
)
def explain_job_posting(job: JobInput):

    job_data = job.model_dump()

    job_df = pd.DataFrame([job_data])

    return explain_job(job_df)


# ============================================================
# 7. COMPANY PROFILE VERIFICATION ENDPOINT
# ============================================================

@app.post(
    "/verify-company",
    tags=["Company Verification"],
    summary="Review company information in a job posting",
    description="""
    Submit a complete job posting using the JobInput schema.

    The endpoint reviews:
    - Company profile completeness.
    - Job description completeness.
    - Contact information availability.
    - Application instructions.
    - Job title availability.
    - Benefits information.

    This is a rule-based review. It does not independently
    verify company registration or employer legitimacy.
    """,
    response_model=dict
)
def verify_company(job: JobInput):

    job_data = job.model_dump()

    verification_result = verify_company_profile(job_data)

    return verification_result
