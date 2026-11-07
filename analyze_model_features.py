
import pandas as pd
import joblib

# STEP 1: Load saved model
model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

# STEP 2: Load saved preprocessor
preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

# STEP 3: Get feature names
feature_names = preprocessor.get_feature_names_out()

# STEP 4: Get model coefficients
coefficients = model.coef_[0]

# STEP 5: Create a DataFrame
feature_importance = pd.DataFrame({
    "Feature": feature_names,
    "Coefficient": coefficients
})

# STEP 6: Sort features by coefficient
# Positive = pushes towards fraud
# Negative = pushes towards genuine

top_fraud_features = feature_importance.nlargest(
    25, "Coefficient"
)

top_genuine_features = feature_importance.nsmallest(
    25, "Coefficient"
)

# STEP 7: Display results
print("\n" + "=" * 60)
print("TOP 25 FRAUD-ASSOCIATED MODEL FEATURES")
print("=" * 60)

print(
    top_fraud_features.to_string(
        index=False
    )
)

print("\n" + "=" * 60)
print("TOP 25 GENUINE-ASSOCIATED MODEL FEATURES")
print("=" * 60)

print(
    top_genuine_features.to_string(
        index=False
    )
)

# STEP 8: Save results
feature_importance.to_csv(
    "data/processed/model_feature_weights.csv",
    index=False
)

print("\nFEATURE ANALYSIS SAVED SUCCESSFULLY!")
