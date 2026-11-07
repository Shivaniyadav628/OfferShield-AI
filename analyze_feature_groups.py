import pandas as pd
import joblib

# STEP 1: Load the trained model
model = joblib.load(
    "data/processed/final_svm_model.pkl"
)

# STEP 2: Load feature names
preprocessor = joblib.load(
    "data/processed/final_preprocessor.pkl"
)

feature_names = preprocessor.get_feature_names_out()

# STEP 3: Get model coefficients
coefficients = model.coef_[0]

# STEP 4: Create DataFrame
df = pd.DataFrame({
    "Feature": feature_names,
    "Coefficient": coefficients
})

# STEP 5: Identify feature groups
df["Feature_Group"] = df["Feature"].str.split("__").str[0]

# STEP 6: Calculate statistics for each group
group_analysis = df.groupby("Feature_Group").agg(
    Total_Features=("Coefficient", "count"),
    Average_Coefficient=("Coefficient", "mean"),
    Average_Absolute_Weight=(
        "Coefficient",
        lambda x: x.abs().mean()
    ),
    Maximum_Weight=(
        "Coefficient",
        lambda x: x.abs().max()
    )
).reset_index()

# STEP 7: Display results
print("\n" + "=" * 65)
print("FEATURE GROUP ANALYSIS")
print("=" * 65)

print(
    group_analysis.to_string(index=False)
)

# STEP 8: Save results
group_analysis.to_csv(
    "data/processed/feature_group_analysis.csv",
    index=False
)

print("\nFEATURE GROUP ANALYSIS SAVED SUCCESSFULLY!")