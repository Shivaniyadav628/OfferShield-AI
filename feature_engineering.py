
import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Separate input features and target variable
X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

# Numerical features
numerical_features = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]

# Text features
text_features = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits"
]

# Categorical features
categorical_features = [
    "location",
    "department",
    "salary_range",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function"
]

print("INPUT FEATURES SHAPE:", X.shape)
print("TARGET SHAPE:", y.shape)

print("\nNUMERICAL FEATURES:", numerical_features)
print("NUMBER:", len(numerical_features))

print("\nTEXT FEATURES:", text_features)
print("NUMBER:", len(text_features))

print("\nCATEGORICAL FEATURES:", categorical_features)
print("NUMBER:", len(categorical_features))
