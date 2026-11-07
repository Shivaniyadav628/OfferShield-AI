
import pandas as pd

# Load the cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Display dataset shape
print("\nDATASET SHAPE:")
print(df.shape)

# Separate input features (X) and target (y)
X = df.drop(columns=["fraudulent", "job_id"])
y = df["fraudulent"]

# Display input features
print("\nINPUT FEATURES:")
print(X.columns.tolist())

# Display target variable
print("\nTARGET VARIABLE:")
print(y.name)

# Display feature and target shapes
print("\nFEATURE SHAPE:")
print(X.shape)

print("\nTARGET SHAPE:")
print(y.shape)


from sklearn.model_selection import train_test_split

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Display training and testing shapes
print("\nTRAINING FEATURES SHAPE:")
print(X_train.shape)

print("\nTESTING FEATURES SHAPE:")
print(X_test.shape)

print("\nTRAINING TARGET SHAPE:")
print(y_train.shape)

print("\nTESTING TARGET SHAPE:")
print(y_test.shape)

# Check fraud distribution in training data
print("\nTRAINING FRAUD DISTRIBUTION:")
print(y_train.value_counts(normalize=True) * 100)

# Check fraud distribution in testing data
print("\nTESTING FRAUD DISTRIBUTION:")
print(y_test.value_counts(normalize=True) * 100)
