#  OfferShield AI
### Intelligent Job & Internship Fraud Detection and Opportunity Risk Analysis Platform

**An Explainable AI-Powered System for Safer Job and Internship Searching**

OfferShield AI is an AI-powered job and internship fraud detection platform designed to help job seekers evaluate suspicious recruitment opportunities through machine learning, natural language processing, statistical analysis, and explainable AI.

The project aims to go beyond basic fake-job classification by analysing job descriptions, company profiles, recruitment information, and other opportunity-related signals to estimate potential fraud risk and explain the factors influencing a prediction.

The long-term vision is to build an intelligent opportunity verification and risk analysis platform that helps students, fresh graduates, and professionals make more informed decisions before applying for jobs or sharing personal information.

> **Important:** OfferShield AI provides risk assessments, not guarantees of legitimacy or fraud. Users should independently verify employers and recruitment offers.

---

## 📌 Table of Contents

1. Project Overview
2. Problem Statement
3. Proposed Solution
4. Key Features
5. System Architecture
6. Machine Learning Approach
7. Dataset
8. Exploratory Data Analysis and Research
9. Model Evaluation
10. Explainable AI
11. Technology Stack
12. Project Structure
13. Installation and Setup
14. How the System Works
15. Development Roadmap
16. Limitations and Responsible AI
17. Future Improvements
18. Author

---

## 1. Project Overview

Online recruitment has made job and internship opportunities more accessible. However, fraudulent job advertisements and misleading recruitment practices can expose job seekers to financial loss, identity theft, and misuse of personal information.

OfferShield AI aims to address this challenge through an intelligent analysis system that examines recruitment information and identifies patterns associated with fraudulent job postings.

The system is designed around five major capabilities:

- **Fraud Detection:** Machine learning-based classification of job postings.
- **Risk Analysis:** Identification of suspicious patterns and missing information.
- **Explainability:** Human-readable explanations of model predictions.
- **Company Consistency Analysis:** Examination of company identity and recruitment information for inconsistencies.
- **Opportunity Assistance:** Tools to help users evaluate and compare job and internship opportunities.

---

## 2. Problem Statement

Job seekers often encounter recruitment advertisements through job portals, social media, email, and unofficial websites.

Some fraudulent advertisements may contain:
- Unrealistic salary or compensation claims.
- Missing or incomplete company information.
- Vague job descriptions and unclear responsibilities.
- Suspicious recruitment or payment requests.
- Inconsistent employer contact information.
- Misleading claims about guaranteed selection.

Traditional job search platforms may not provide sufficient information to help every applicant evaluate these risks.

**The objective of OfferShield AI is to develop an intelligent system that analyses available recruitment information and provides an interpretable fraud-risk assessment.**

---

## 3. Proposed Solution

OfferShield AI combines machine learning, text analysis, structured feature engineering, and explainable AI.

The proposed workflow is:

1. Accept a job posting, internship description, or recruitment offer.
2. Extract and preprocess relevant text and structured information.
3. Analyse textual patterns, company information, and missing details.
4. Generate machine learning predictions.
5. Identify features contributing to the prediction.
6. Present a risk assessment with understandable explanations.
7. Provide additional verification guidance where supporting information is available.

The platform is intended to support users in evaluating opportunities rather than making final decisions on their behalf.

---

## 4. Key Features

The following describes the complete product vision. Implementation status is indicated honestly.

### 4.1 AI-Based Job Fraud Detection
**Status: In development**

- Analyse job descriptions and recruitment information.
- Classify job postings as potentially genuine or potentially fraudulent.
- Use machine learning models trained on labelled recruitment data.
- Account for class imbalance during model training.
- Evaluate performance using precision, recall, F1-score, and confusion matrices.

### 4.2 Fraud Risk Assessment
**Status: Planned**

- Generate an interpretable risk assessment.
- Highlight suspicious information and missing details.
- Present the model's classification separately from independent verification evidence.
- Help users understand why an opportunity may deserve additional investigation.

### 4.3 Explainable AI
**Status: Research and model-analysis work completed; user-facing interface planned**

- Explain the contribution of important model features.
- Identify influential textual and structured features.
- Analyse model coefficients and feature importance.
- Explore SHAP-based explanations for suitable models.
- Provide understandable reasons behind predictions.

### 4.4 Company Profile Analysis
**Status: Statistical research completed; product integration planned**

- Analyse company profile descriptions.
- Examine vocabulary patterns associated with genuine-labelled and fraudulent-labelled postings.
- Investigate missing company profiles.
- Study repeated company descriptions.
- Compare posting-level and unique-profile vocabulary patterns.
- Examine individual words and word families.
- Investigate whether observed patterns remain consistent under sensitivity analysis.

### 4.5 Company Identity and Consistency Checks
**Status: Planned**

- Compare company names across submitted information.
- Examine company website and email-domain consistency.
- Identify mismatches between employer identity and recruitment details.
- Highlight missing or inconsistent contact information.

These checks are intended to identify inconsistencies, not certify that a company is legitimate.

### 4.6 Offer Letter Analysis
**Status: Planned**

- Extract text from uploaded offer letters.
- Analyse compensation, joining dates, job titles, and employer details.
- Identify potentially inconsistent or suspicious information.
- Highlight requests for payments or sensitive personal information.
- Provide a structured report of findings.

### 4.7 Job Eligibility Matching
**Status: Planned**

- Compare job requirements with a user's skills and qualifications.
- Identify missing skills.
- Highlight relevant eligibility requirements.
- Help students understand whether an opportunity matches their profile.

### 4.8 Opportunity Comparison
**Status: Planned**

- Compare multiple job and internship opportunities.
- Examine eligibility, skills, responsibilities, and compensation information.
- Present risk assessments alongside opportunity details.
- Help users make informed comparisons.

---

## 5. System Architecture

The planned architecture separates the user interface, backend services, machine learning pipeline, and data storage.

```text
                  USER
                    |
                    v
             REACT FRONTEND
                    |
                    v
              FASTAPI BACKEND
                    |
          +---------+---------+
          |         |         |
          v         v         v
       TEXT      COMPANY    DOCUMENT
    PROCESSING   ANALYSIS   EXTRACTION
          |         |         |
          +---------+---------+
                    |
                    v
           FEATURE ENGINEERING
                    |
                    v
          MACHINE LEARNING MODEL
                    |
                    v
            EXPLAINABLE AI
                    |
                    v
          RISK ANALYSIS REPORT
                    |
                    v
              USER RESULTS
```

The architecture is a development target; individual services will be integrated as implementation progresses.

---

## 6. Machine Learning Approach

The current research focuses on detecting patterns in labelled job postings using supervised machine learning.

### Data preprocessing
- Missing-value analysis and treatment.
- Text cleaning and normalization.
- Duplicate-record investigation.
- Categorical and numerical feature preparation.
- Stratified training, validation, and test splitting.

### Feature engineering

The project investigates multiple feature categories.

**Textual features**
- Job title.
- Company profile.
- Job description.
- Requirements.
- Benefits.

**Categorical features**
- Location.
- Department.
- Employment type.
- Required experience.
- Required education.
- Industry.
- Job function.

**Structured features**
- Telecommuting.
- Company logo availability.
- Screening-question availability.

**Engineered features**
- Description length.
- Requirements length.
- Benefits length.
- Missing company profile.
- Missing requirements.
- Missing benefits.
- Short description.
- Placeholder description.
- Missing-information count.

### Model development

Current model experimentation includes:

- Logistic Regression.
- Linear Support Vector Machine (LinearSVC).
- TF-IDF text vectorization.
- One-hot encoding for categorical features.
- Class-weight balancing.
- Validation-based decision threshold selection.

The current experimental pipeline uses a ColumnTransformer to process text, categorical, and numerical features.

---

## 7. Dataset

**Dataset:** Employment Scam Aegean Dataset (EMSCAD)

The current project uses a publicly available labelled job-posting dataset containing:

| Dataset characteristic | Value |
|---|---:|
| Total job postings | 17,880 |
| Genuine-labelled postings | 17,014 |
| Fraudulent-labelled postings | 866 |
| Total features in cleaned dataset | 18 |
| Genuine-labelled proportion | 95.16% |
| Fraudulent-labelled proportion | 4.84% |

**Target variable:** `fraudulent`

- `0` – Genuine-labelled job posting.
- `1` – Fraudulent-labelled job posting.

The dataset is imbalanced, so accuracy alone is not sufficient to evaluate model performance.

The project therefore focuses on fraud-class precision, recall, F1-score, and confusion-matrix analysis.

---

## 8. Exploratory Data Analysis and Research

A significant part of OfferShield AI involves investigating recruitment data before introducing additional features into the machine learning pipeline.

Research completed includes:

### Dataset and data-quality analysis
- Missing-value investigation.
- Duplicate-record checks.
- Target distribution analysis.
- Text-field quality analysis.

### Feature and error analysis
- Feature importance investigation.
- Permutation importance.
- Feature-group analysis.
- False-positive and false-negative analysis.
- Company-profile availability analysis.
- Comparison of detected and missed fraudulent-labelled postings.

### Company-profile vocabulary research
- Document-level vocabulary analysis.
- Word-frequency and profile-presence analysis.
- Fisher's exact test and Chi-square-based statistical investigation.
- Benjamini–Hochberg multiple-testing correction.
- Unique company-profile analysis.
- Repeated-profile concentration analysis.
- Vocabulary sensitivity analysis.
- Word-family analysis.
- Individual-word versus word-family comparison.
- Statistical consistency audit.

The purpose of this research is to investigate whether vocabulary patterns are consistent across different analytical approaches, rather than assuming that individual words establish fraudulent behaviour.

---

## 9. Model Evaluation

The project uses separate training, validation, and untouched test datasets.

### Experimental split

| Dataset | Records |
|---|---:|
| Subtraining | 11,443 |
| Validation | 2,861 |
| Untouched test | 3,576 |

### Current experimental results

The enhanced LinearSVC experiment produced the following holdout test results:

| Metric | Result |
|---|---:|
| Accuracy | 98.83% |
| Fraud precision | 95.80% |
| Fraud recall | 79.19% |
| Fraud F1-score | 86.71% |

Confusion matrix:

```text
                 Predicted
                 Genuine  Fraud
Actual Genuine     3397      6
Actual Fraud         36    137
```

### Baseline comparison

| Metric | Baseline | Enhanced |
|---|---:|---:|
| Accuracy | 98.88% | 98.83% |
| Fraud precision | 95.86% | 95.80% |
| Fraud recall | 80.35% | 79.19% |
| Fraud F1-score | 87.42% | 86.71% |

The enhanced experiment did not outperform the baseline on the untouched test set. This comparison is retained to document the actual experimental outcome rather than presenting only favourable results.

**Evaluation note:** The LinearSVC decision score is not a calibrated probability. A threshold-based decision score must not be presented as a percentage probability of fraud.

---

## 10. Explainable AI

A major objective is to make model predictions understandable.

Instead of presenting only a classification, the intended system will explain which available features influenced the result.

Current research includes:
- LinearSVC coefficient analysis.
- Feature contribution analysis.
- Permutation importance.
- Feature-group analysis.
- False-positive and false-negative investigation.

Planned user-facing explanations include:
- Missing company information.
- Unusually short job descriptions.
- Relevant textual patterns.
- Inconsistent recruitment information.
- Important model features influencing the prediction.

Explanations will distinguish statistical associations from verified evidence.

---

## 11. Technology Stack

| Area | Technologies |
|---|---|
| Programming language | Python |
| Data analysis | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine learning | Scikit-learn |
| Statistical analysis | SciPy, Statsmodels |
| NLP | NLTK, TF-IDF |
| Model interpretation | SHAP (planned integration) |
| Backend | FastAPI (planned) |
| Frontend | React, Tailwind CSS (planned) |
| Database | PostgreSQL (planned) |
| Document processing | PyMuPDF (planned) |
| Version control | Git, GitHub |

The technologies marked as planned are part of the intended implementation and should not be interpreted as already integrated.

---

## 12. Project Structure

```text
OfferShield-AI/
│
├── data/
│   ├── raw/
│   │   └── fake_job_postings.csv
│   │
│   └── processed/
│       ├── jobs_cleaned.csv
│       ├── model evaluation outputs
│       ├── feature analysis outputs
│       ├── vocabulary research outputs
│       └── statistical audit outputs
│
├── venv/
│
├── text_quality_features.py
├── final_model_evaluation.py
│
├── company_profile_vocabulary_analysis.py
├── company_profile_document_frequency.py
├── company_profile_vocabulary_reliability.py
├── company_profile_vocabulary_context.py
├── company_profile_vocabulary_concentration.py
├── company_profile_vocabulary_sensitivity.py
├── company_profile_unique_document_analysis.py
├── company_profile_vocabulary_robustness.py
├── company_profile_word_family_analysis.py
├── company_profile_word_family_comparison.py
├── company_profile_word_family_statistical_audit.py
│
├── company_profile_vocabulary_research_report.py
│
└── README.md
```

Additional project files and application components will be added as development continues.

---

## 13. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- Visual Studio Code (recommended).

### Clone the repository

```bash
git clone https://github.com/Shivaniyadav628/OfferShield-AI.git
```

### Navigate to the project directory

```bash
cd OfferShield-AI
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install pandas numpy matplotlib seaborn nltk scikit-learn scipy statsmodels joblib
```

### Run the model evaluation script

```bash
python final_model_evaluation.py
```

Run scripts from the project root directory so that relative data paths work correctly.

---

## 14. How the System Works

The planned end-to-end workflow is:

**Step 1 — Opportunity submission**

The user submits a job description, internship advertisement, or supported recruitment document.

**Step 2 — Information extraction**

The backend extracts relevant textual and structured information.

**Step 3 — Data preprocessing**

Text is cleaned, missing values are identified, and model features are generated.

**Step 4 — Machine learning analysis**

The trained model analyses the posting and produces a classification decision score.

**Step 5 — Risk explanation**

The system identifies influential features and relevant inconsistencies.

**Step 6 — Results presentation**

The user receives a structured analysis containing:
- Model classification.
- Risk assessment.
- Suspicious or missing information.
- Explanation of important findings.
- Recommended verification steps.

---

## 15. Development Roadmap

| Phase | Development task | Status |
|---|---|---|
| 1 | Dataset collection and understanding | Completed |
| 2 | Data cleaning and preprocessing | Completed |
| 3 | Exploratory data analysis | Completed |
| 4 | Baseline ML model development | Completed |
| 5 | Validation and threshold experiments | Completed |
| 6 | Engineered feature experiments | Completed |
| 7 | Model evaluation and error analysis | Completed |
| 8 | Company-profile vocabulary research | Completed |
| 9 | Statistical robustness and sensitivity analysis | Completed |
| 10 | Model serialization and prediction pipeline | In progress |
| 11 | Explainable AI integration | Planned |
| 12 | FastAPI backend development | Planned |
| 13 | React frontend development | Planned |
| 14 | Company consistency verification | Planned |
| 15 | Offer letter analysis | Planned |
| 16 | Eligibility matching | Planned |
| 17 | Opportunity comparison | Planned |
| 18 | Deployment and testing | Planned |

---

## 16. Limitations and Responsible AI

OfferShield AI is a research and development project. Its output must be interpreted carefully.

- A model prediction does not prove that an employer is fraudulent.
- Missing company information is not sufficient evidence of fraud.
- Dataset labels may not represent independently verified company-level truth.
- The current dataset may not represent every country, industry, or recruitment platform.
- Class imbalance can affect model performance.
- Statistical associations do not establish causation.
- A legitimate employer may have incomplete information, and a fraudulent posting may appear professionally written.
- Company verification requires reliable external evidence beyond textual classification.

The platform is intended to support human decision-making, not replace independent verification.

---

## 17. Future Improvements

Potential future development includes:

- Larger and more diverse recruitment datasets.
- More robust fraud detection models.
- Calibrated risk probabilities where appropriate.
- SHAP-based local explanations.
- Company website and email-domain verification.
- PDF and offer-letter analysis.
- Multilingual job-posting analysis.
- Real-time recruitment opportunity analysis.
- User feedback and model monitoring.
- Secure deployment and privacy-aware document handling.

---

## 18. Author

**Shivani Yadav**

B.Tech Computer Science and Engineering

GitHub: [@Shivaniyadav628](https://github.com/Shivaniyadav628)

---

### Project Vision

OfferShield AI aims to make online job and internship searching safer through responsible machine learning, transparent risk analysis, and understandable explanations.

**Building technology that helps people make safer and more informed career decisions.**