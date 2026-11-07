
import pandas as pd

from fastapi import FastAPI

from backend.schemas import (
    JobInput,
    PredictionResponse,
    ExplanationResponse
)
from prediction_engine import predict_job_fraud
from explanation_engine import explain_job


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

    - **Fraud Prediction:** Predict potential job fraud.
    - **Explainable AI:** Identify features influencing predictions.
    - **Input Validation:** Validate job posting information.
    - **Mathematical Verification:** Verify feature contributions
      against the model's decision score.

    **Important:** Model predictions are risk assessments,
    not independent verification of job legitimacy.
    """,
    version="1.0.0",
    contact={
        "name": "OfferShield AI",
        "url": "https://github.com/Shivaniyadav628/OfferShield-AI"
    }
)


# ============================================================
# 2. ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["General"],
    summary="Welcome to OfferShield AI",
    description="Returns basic information about the API.",
    response_description="API welcome information."
)
def home():

    return {
        "message": "Welcome to OfferShield AI API!",
        "project": "OfferShield AI",
        "status": "Running successfully"
    }


# ============================================================
# 3. HEALTH CHECK ENDPOINT
# ============================================================

@app.get(
    "/health",
    tags=["General"],
    summary="Check API health",
    description="Checks whether the OfferShield AI API is running.",
    response_description="Current application health status."
)
def health_check():

    return {
        "status": "healthy",
        "application": "OfferShield AI",
        "version": "1.0.0"
    }


# ============================================================
# 4. JOB FRAUD PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    tags=["Prediction"],
    summary="Predict job posting fraud risk",
    description="""
    Accepts a job posting containing 16 required features.

    The trained LinearSVC model evaluates the posting and
    returns a fraud classification, decision score, and
    selected decision threshold.

    The decision score is not a probability.
    """,
    response_description="Job fraud prediction result.",
    response_model=PredictionResponse
)
def predict_job(job: JobInput):

    job_data = job.model_dump()

    prediction_result = predict_job_fraud(job_data)

    return prediction_result


# ============================================================
# 5. JOB EXPLANATION ENDPOINT
# ============================================================

@app.post(
    "/explain",
    tags=["Explainable AI"],
    summary="Explain a job fraud prediction",
    description="""
    Accepts a job posting and generates an explanation
    using the trained Explainable AI engine.

    Returns:

    - Fraud prediction and risk classification.
    - Model decision score and selected threshold.
    - Top fraud-increasing feature contributions.
    - Top genuine-increasing feature contributions.
    - Mathematical verification of the explanation.

    Feature contributions describe model decision-score
    effects. They do not establish causality or prove fraud.
    """,
    response_description="Prediction explanation and mathematical verification.",
    response_model=ExplanationResponse
)
def explain_job_posting(job: JobInput):

    job_data = job.model_dump()

    job_df = pd.DataFrame([job_data])

    explanation_result = explain_job(job_df)

    return explanation_result