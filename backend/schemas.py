
from pydantic import BaseModel, Field, ConfigDict


class JobInput(BaseModel):

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Software Engineer Intern",
                    "location": "Bangalore, India",
                    "department": "Engineering",
                    "salary_range": "30000-50000",
                    "company_profile": "An established technology company developing software solutions.",
                    "description": "We are looking for a Software Engineer Intern to work with our engineering team on real-world projects.",
                    "requirements": "Knowledge of Python, Java, data structures and algorithms.",
                    "benefits": "Internship certificate, mentorship and hands-on project experience.",
                    "telecommuting": 0,
                    "has_company_logo": 1,
                    "has_questions": 1,
                    "employment_type": "Internship",
                    "required_experience": "Internship",
                    "required_education": "Bachelor's Degree",
                    "industry": "Information Technology",
                    "function": "Engineering"
                },
                {
                    "title": "Work From Home Data Entry - Urgent Hiring",
                    "location": "Anywhere",
                    "department": "Not Specified",
                    "salary_range": "50000-100000",
                    "company_profile": "Not Specified",
                    "description": "Earn huge money from home! No experience required. Guaranteed job. Apply immediately. Pay a small registration fee to secure your position.",
                    "requirements": "No qualifications or experience required. Anyone can apply.",
                    "benefits": "High salary, flexible hours, instant selection.",
                    "telecommuting": 1,
                    "has_company_logo": 0,
                    "has_questions": 0,
                    "employment_type": "Not Specified",
                    "required_experience": "Not Specified",
                    "required_education": "Not Specified",
                    "industry": "Not Specified",
                    "function": "Not Specified"
                }
            ]
        }
    )

    title: str = Field(..., description="Job title")
    location: str = Field(..., description="Job location")
    department: str = Field(..., description="Job department")
    salary_range: str = Field(..., description="Salary range")

    company_profile: str = Field(..., description="Company profile")
    description: str = Field(..., description="Job description")
    requirements: str = Field(..., description="Job requirements")
    benefits: str = Field(..., description="Job benefits")

    telecommuting: int = Field(..., ge=0, le=1)
    has_company_logo: int = Field(..., ge=0, le=1)
    has_questions: int = Field(..., ge=0, le=1)

    employment_type: str = Field(..., description="Employment type")
    required_experience: str = Field(..., description="Required experience")
    required_education: str = Field(..., description="Required education")
    industry: str = Field(..., description="Industry")
    function: str = Field(..., description="Job function")


from typing import Literal


class PredictionResponse(BaseModel):

    prediction: int = Field(..., ge=0, le=1)

    result: Literal[
        "Likely Genuine",
        "Potentially Fraudulent"
    ]

    decision_score: float

    threshold: float

class FeatureSignal(BaseModel):

    feature: str = Field(..., description="Name of the contributing feature")

    contribution: float = Field(
        ...,
        description="Contribution to the model decision score"
    )


class MathematicalVerification(BaseModel):

    actual_score: float

    contribution_sum: float

    intercept: float

    reconstructed_score: float

    difference: float

    verified: bool


class ExplanationResponse(BaseModel):

    job_title: str

    prediction: int = Field(..., ge=0, le=1)

    risk_classification: Literal[
        "Likely Genuine",
        "Potentially Fraudulent"
    ]

    decision_score: float

    threshold: float

    fraud_increasing_signals: list[FeatureSignal]

    genuine_increasing_signals: list[FeatureSignal]

    mathematical_verification: MathematicalVerification
