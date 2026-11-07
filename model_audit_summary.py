import pandas as pd

# Load feature group analysis
df = pd.read_csv(
    "data/processed/feature_group_analysis.csv"
)

print("\nOFFER SHIELD AI - MODEL AUDIT")
print("=" * 55)

print("\n1. FEATURE GROUP COUNTS")

print(
    df[["Feature_Group", "Total_Features"]]
    .to_string(index=False)
)

print("\n2. AVERAGE ABSOLUTE WEIGHTS")

print(
    df[
        ["Feature_Group", "Average_Absolute_Weight"]
    ].sort_values(
        by="Average_Absolute_Weight",
        ascending=False
    ).to_string(index=False)
)

print("\n3. AUDIT OBSERVATIONS")

print("- Text features contain learned fraud-related patterns.")
print("- Some categorical features have large individual weights.")
print("- Numerical features contain only three binary inputs.")
print("- Coefficients indicate learned associations, not causation.")
print("- Further validation is needed before real-world deployment.")

print("\nMODEL AUDIT COMPLETED!")