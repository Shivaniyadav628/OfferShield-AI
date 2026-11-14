
import re
import pandas as pd


# ============================================================
# OFFERSHIELD AI - FEATURE ENGINEERING VERSION 2
# ============================================================

def add_risk_features(df):

    df = df.copy()

    # Combine relevant job text
    combined_text = (
        df["title"].fillna("").astype(str) + " " +
        df["description"].fillna("").astype(str) + " " +
        df["requirements"].fillna("").astype(str) + " " +
        df["benefits"].fillna("").astype(str)
    ).str.lower()

    # --------------------------------------------------------
    # 1. COMPENSATION RISK FEATURES
    # --------------------------------------------------------

    compensation_patterns = [
        r"\$\s*\d[\d,]*(?:\.\d+)?\s*(?:per|a|/)\s*(?:day|week|hour)",
        r"\d+\s*(?:to|-)\s*\$?\d+\s*(?:per|a|/)\s*day",
        r"earn\s+(?:up to\s+)?\$?\d[\d,]*",
        r"unlimited\s+(?:earning|income|commission)",
        r"commissions?\s+paid\s+daily",
        r"daily\s+pay",
        r"guaranteed\s+(?:income|earnings|pay)"
    ]

    df["compensation_risk_count"] = combined_text.apply(
        lambda text: sum(
            bool(re.search(pattern, text))
            for pattern in compensation_patterns
        )
    )

    # --------------------------------------------------------
    # 2. RECRUITMENT LANGUAGE FEATURES
    # --------------------------------------------------------

    recruitment_patterns = [
        r"no experience required",
        r"start immediately",
        r"limited positions",
        r"apply today",
        r"guaranteed job",
        r"career of your dreams",
        r"unlimited earning potential",
        r"work from home.*earn",
        r"get paid daily",
        r"no interview required"
    ]

    df["recruitment_risk_count"] = combined_text.apply(
        lambda text: sum(
            bool(re.search(pattern, text))
            for pattern in recruitment_patterns
        )
    )

    # --------------------------------------------------------
    # 3. RELOCATION AND VISA FEATURES
    # --------------------------------------------------------

    relocation_patterns = [
        r"visa (?:and )?sponsorship",
        r"visa expenses",
        r"flight ticket",
        r"airfare",
        r"free accommodation",
        r"relocation allowance",
        r"travel expenses",
        r"work permit",
        r"immigration assistance"
    ]

    df["relocation_claim_count"] = combined_text.apply(
        lambda text: sum(
            bool(re.search(pattern, text))
            for pattern in relocation_patterns
        )
    )

    # --------------------------------------------------------
    # 4. COMPANY TRANSPARENCY FEATURES
    # --------------------------------------------------------

    company_profile = (
        df["company_profile"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    missing_values = [
        "",
        "not specified",
        "nan",
        "none"
    ]

    df["company_profile_missing_v2"] = company_profile.isin(
        missing_values
    ).astype(int)

    df["company_profile_length_v2"] = company_profile.str.len()

    df["company_profile_very_short"] = (
        (df["company_profile_length_v2"] > 0) &
        (df["company_profile_length_v2"] < 50)
    ).astype(int)

    # Contact and website references in job text.
    # These indicate whether contact information is mentioned,
    # not whether it is genuine or independently verified.

    df["email_reference_present"] = combined_text.str.contains(
        r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b",
        regex=True
    ).astype(int)

    df["website_reference_present"] = combined_text.str.contains(
        r"\b(?:https?://|www\.)\S+",
        regex=True
    ).astype(int)

    # --------------------------------------------------------
    # DISPLAY FEATURE SUMMARY
    # --------------------------------------------------------

    new_features = [
        "compensation_risk_count",
        "recruitment_risk_count",
        "relocation_claim_count",
        "company_profile_missing_v2",
        "company_profile_length_v2",
        "company_profile_very_short",
        "email_reference_present",
        "website_reference_present"
    ]

    print("\nNEW FEATURES CREATED")
    print("=" * 55)

    for feature in new_features:
        print(feature)

    print("\nTOTAL NEW FEATURES:", len(new_features))

    return df


# ============================================================
# TEST FEATURE ENGINEERING
# ============================================================

if __name__ == "__main__":

    print("LOADING CLEANED DATASET...")

    df = pd.read_csv("data/processed/jobs_cleaned.csv")

    print("Original dataset shape:", df.shape)

    enhanced_df = add_risk_features(df)

    print("\nENHANCED DATASET SHAPE:", enhanced_df.shape)

    output_path = (
        "data/processed/jobs_with_risk_features_v2.csv"
    )

    enhanced_df.to_csv(output_path, index=False)

    print("\nFEATURE ENGINEERING COMPLETED!")
    print("Saved:", output_path)
