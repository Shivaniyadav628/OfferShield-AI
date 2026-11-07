
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder

# Load cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Separate input features and target
X = df.drop(columns=["job_id", "fraudulent"])
y = df["fraudulent"]

# Define feature groups
numerical_features = [
    "telecommuting",
    "has_company_logo",
    "has_questions"
]

text_features = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits"
]

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

# Split dataset before preprocessing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Create preprocessing transformer
preprocessor = ColumnTransformer(
    transformers=[
        ("title_tfidf", TfidfVectorizer(max_features=500), "title"),
        ("company_tfidf", TfidfVectorizer(max_features=1000), "company_profile"),
        ("description_tfidf", TfidfVectorizer(max_features=3000), "description"),
        ("requirements_tfidf", TfidfVectorizer(max_features=2000), "requirements"),
        ("benefits_tfidf", TfidfVectorizer(max_features=1000), "benefits"),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numerical", "passthrough", numerical_features)
    ]
)

# Fit only on training data and transform training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform test data without fitting again
X_test_processed = preprocessor.transform(X_test)

# Display results
print("\nORIGINAL TRAINING DATA SHAPE:")
print(X_train.shape)

print("\nPROCESSED TRAINING DATA SHAPE:")
print(X_train_processed.shape)

print("\nPROCESSED TESTING DATA SHAPE:")
print(X_test_processed.shape)

print("\nTRAINING TARGET SHAPE:")
print(y_train.shape)

print("\nTESTING TARGET SHAPE:")
print(y_test.shape)

print("\nPREPROCESSING COMPLETED SUCCESSFULLY!")
