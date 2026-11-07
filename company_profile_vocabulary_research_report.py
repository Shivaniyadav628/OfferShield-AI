
from pathlib import Path
import pandas as pd


# ============================================================
# 1. PATHS AND SETTINGS
# ============================================================

DATA_DIR = Path("data/processed")

REPORT_PATH = (
    DATA_DIR / "company_profile_vocabulary_research_report.md"
)

SIGNIFICANCE_LEVEL = 0.05


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def load_csv(filename):

    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    return pd.read_csv(path)


def verify_columns(df, required_columns, filename):

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {sorted(missing)}"
        )


def to_bool(value):

    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "true", "1", "1.0", "yes"
    }


def percentage(value):

    return f"{value * 100:.2f}%"


def format_p_value(value):

    if pd.isna(value):
        return "Not available"

    return f"{value:.3e}"


def format_ratio(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}"


def markdown_table(df, columns=None, max_rows=None):

    if columns is not None:
        df = df[columns].copy()

    if max_rows is not None:
        df = df.head(max_rows)

    if df.empty:
        return "No records available."

    headers = [str(column) for column in df.columns]

    rows = []

    for row in df.itertuples(index=False, name=None):

        formatted_row = []

        for value in row:

            if pd.isna(value):
                formatted_row.append("N/A")
            else:
                formatted_row.append(str(value))

        rows.append(formatted_row)

    header_line = "| " + " | ".join(headers) + " |"

    separator_line = (
        "| " +
        " | ".join(["---"] * len(headers)) +
        " |"
    )

    data_lines = [
        "| " + " | ".join(row) + " |"
        for row in rows
    ]

    return "\n".join(
        [header_line, separator_line] + data_lines
    )


# ============================================================
# 3. LOAD RESEARCH OUTPUTS
# ============================================================

print("\nLOADING RESEARCH RESULTS")
print("=" * 75)

individual = load_csv(
    "audit_individual_word_results.csv"
)

families = load_csv(
    "audit_word_family_results.csv"
)

comparison = load_csv(
    "audit_word_family_comparison.csv"
)

unique_summary = load_csv(
    "unique_company_profile_summary.csv"
)

robustness = load_csv(
    "company_profile_vocabulary_robustness.csv"
)

sensitivity = load_csv(
    "vocabulary_sensitivity_comparison.csv"
)

print("All research files loaded successfully.")


# ============================================================
# 4. VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = {

    "individual": [
        "word",
        "genuine_profiles",
        "fraud_profiles",
        "genuine_rate",
        "fraud_rate",
        "rate_ratio",
        "adjusted_p_value",
        "association"
    ],

    "families": [
        "family",
        "genuine_profiles",
        "fraud_profiles",
        "genuine_rate",
        "fraud_rate",
        "rate_ratio",
        "adjusted_p_value",
        "association"
    ],

    "comparison": [
        "family",
        "comparison_result"
    ],

    "unique_summary": [
        "genuine_postings",
        "fraudulent_postings"
    ],

    "robustness": [
        "word",
        "posting_significant",
        "unique_significant",
        "same_direction",
        "robust_fraud_association",
        "sample_size_eligible",
        "robust_with_sample_support"
    ],

    "sensitivity": [
        "word",
        "adjusted_p_value_original",
        "adjusted_p_value_after_exclusion",
        "significant_original",
        "significant_after_exclusion"
    ]
}

dataframes = {
    "individual": individual,
    "families": families,
    "comparison": comparison,
    "unique_summary": unique_summary,
    "robustness": robustness,
    "sensitivity": sensitivity
}

for name, columns in required_columns.items():

    verify_columns(
        dataframes[name],
        columns,
        name
    )

print("All required columns verified.")


# ============================================================
# 5. DATASET AND UNIQUE PROFILE SUMMARY
# ============================================================

total_unique_profiles = len(unique_summary)

genuine_profiles = (
    unique_summary["genuine_postings"].gt(0) &
    unique_summary["fraudulent_postings"].eq(0)
).sum()

fraud_profiles = (
    unique_summary["fraudulent_postings"].gt(0) &
    unique_summary["genuine_postings"].eq(0)
).sum()

mixed_profiles = (
    unique_summary["genuine_postings"].gt(0) &
    unique_summary["fraudulent_postings"].gt(0)
).sum()


# Optional concentration statistics.
# Calculate only if the required column exists.

repeated_profiles = None
maximum_postings_per_profile = None

if "posting_count" in unique_summary.columns:

    repeated_profiles = (
        unique_summary["posting_count"] > 1
    ).sum()

    maximum_postings_per_profile = (
        unique_summary["posting_count"].max()
    )


# ============================================================
# 6. INDIVIDUAL WORD STATISTICS
# ============================================================

total_word_tests = len(individual)

individual["adjusted_p_value"] = pd.to_numeric(
    individual["adjusted_p_value"],
    errors="coerce"
)

significant_individual = individual[
    individual["adjusted_p_value"] < SIGNIFICANCE_LEVEL
].copy()

significant_words = len(significant_individual)

fraud_associated_words = (
    significant_individual["association"] ==
    "fraud-associated"
).sum()

genuine_associated_words = (
    significant_individual["association"] ==
    "genuine-associated"
).sum()


# ============================================================
# 7. WORD-FAMILY STATISTICS
# ============================================================

total_families = len(families)

families["adjusted_p_value"] = pd.to_numeric(
    families["adjusted_p_value"],
    errors="coerce"
)

significant_family_df = families[
    families["adjusted_p_value"] < SIGNIFICANCE_LEVEL
].copy()

significant_families = len(significant_family_df)


# ============================================================
# 8. PREPARE TOP INDIVIDUAL WORDS
# ============================================================

top_words = significant_individual.sort_values(
    "adjusted_p_value"
).head(15).copy()

top_words["genuine_rate"] = (
    top_words["genuine_rate"].map(percentage)
)

top_words["fraud_rate"] = (
    top_words["fraud_rate"].map(percentage)
)

top_words["rate_ratio"] = (
    top_words["rate_ratio"].map(format_ratio)
)

top_words["adjusted_p_value"] = (
    top_words["adjusted_p_value"].map(format_p_value)
)


# ============================================================
# 9. PREPARE TOP WORD FAMILIES
# ============================================================

top_families = significant_family_df.sort_values(
    "adjusted_p_value"
).head(15).copy()

top_families["genuine_rate"] = (
    top_families["genuine_rate"].map(percentage)
)

top_families["fraud_rate"] = (
    top_families["fraud_rate"].map(percentage)
)

top_families["rate_ratio"] = (
    top_families["rate_ratio"].map(format_ratio)
)

top_families["adjusted_p_value"] = (
    top_families["adjusted_p_value"].map(format_p_value)
)


# ============================================================
# 10. WORD-LEVEL VS FAMILY-LEVEL COMPARISON
# ============================================================

comparison_results = (
    comparison["comparison_result"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

both_significant = comparison_results.str.contains(
    "both levels"
).sum()

family_only = comparison_results.str.contains(
    "only as a family"
).sum()

individual_only = comparison_results.str.contains(
    "only as individual words"
).sum()

neither = comparison_results.str.contains(
    "not significant at either level"
).sum()


# ============================================================
# 11. ROBUSTNESS ANALYSIS
# ============================================================

boolean_columns = [
    "posting_significant",
    "unique_significant",
    "same_direction",
    "robust_fraud_association",
    "sample_size_eligible",
    "robust_with_sample_support"
]

for column in boolean_columns:

    robustness[column] = (
        robustness[column].map(to_bool)
    )


total_robustness_records = len(robustness)

posting_significant_count = (
    robustness["posting_significant"].sum()
)

unique_significant_count = (
    robustness["unique_significant"].sum()
)

same_direction_count = (
    robustness["same_direction"].sum()
)

robust_fraud_count = (
    robustness["robust_fraud_association"].sum()
)

sample_eligible_count = (
    robustness["sample_size_eligible"].sum()
)

robust_with_support_count = (
    robustness["robust_with_sample_support"].sum()
)


robust_words = robustness[
    robustness["robust_with_sample_support"]
].sort_values(
    "fraud_rate_unique",
    ascending=False
).copy()


print("\nROBUSTNESS SUMMARY")
print("=" * 75)

print("Total comparison records:", total_robustness_records)

print("Posting-level significant words:",
      posting_significant_count)

print("Unique-profile significant words:",
      unique_significant_count)

print("Words with same association direction:",
      same_direction_count)

print("Robust fraud-associated words:",
      robust_fraud_count)

print("Words meeting sample-size eligibility:",
      sample_eligible_count)

print("Robust words with sample-size support:",
      robust_with_support_count)


# Prepare robustness table.

robust_table = robust_words.head(15).copy()

if not robust_table.empty:

    robust_table["genuine_rate_unique"] = (
        robust_table["genuine_rate_unique"].map(percentage)
    )

    robust_table["fraud_rate_unique"] = (
        robust_table["fraud_rate_unique"].map(percentage)
    )

    robust_table["rate_ratio_unique"] = (
        robust_table["rate_ratio_unique"].map(format_ratio)
    )

    robust_table["adjusted_p_value_unique"] = (
        robust_table["adjusted_p_value_unique"].map(
            format_p_value
        )
    )


robustness_summary = f"""
- Total comparison records: {total_robustness_records}
- Posting-level significant words: {posting_significant_count}
- Unique-profile significant words: {unique_significant_count}
- Words with the same association direction: {same_direction_count}
- Robust fraud-associated words: {robust_fraud_count}
- Words meeting sample-size eligibility: {sample_eligible_count}
- Robust words with sample-size support: {robust_with_support_count}
"""


# ============================================================
# 12. SENSITIVITY ANALYSIS
# ============================================================

sensitivity["significant_original"] = (
    sensitivity["significant_original"].map(to_bool)
)

sensitivity["significant_after_exclusion"] = (
    sensitivity["significant_after_exclusion"].map(to_bool)
)


total_sensitivity_words = len(sensitivity)

significant_original = (
    sensitivity["significant_original"].sum()
)

significant_after = (
    sensitivity["significant_after_exclusion"].sum()
)

significant_both = (
    sensitivity["significant_original"] &
    sensitivity["significant_after_exclusion"]
).sum()

lost_significance = (
    sensitivity["significant_original"] &
    ~sensitivity["significant_after_exclusion"]
).sum()

new_significance = (
    ~sensitivity["significant_original"] &
    sensitivity["significant_after_exclusion"]
).sum()


retention_percentage = (
    significant_both / significant_original * 100
    if significant_original > 0
    else 0
)


sensitivity_summary = f"""
- Words compared: {total_sensitivity_words}
- Significant words in original analysis: {significant_original}
- Significant words after profile exclusion: {significant_after}
- Significant in both analyses: {significant_both}
- No longer significant after exclusion: {lost_significance}
- Newly significant after exclusion: {new_significance}
- Original significant-word retention: {retention_percentage:.2f}%
"""


print("\nSENSITIVITY SUMMARY")
print("=" * 75)

print(sensitivity_summary)


# ============================================================
# 13. UNIQUE PROFILE CONCENTRATION ANALYSIS
# ============================================================

concentration_summary = (
    "Posting-count information was not available in the "
    "unique-profile summary file."
)

if repeated_profiles is not None:

    concentration_summary = f"""
- Unique company profiles: {total_unique_profiles}
- Profiles associated with multiple postings: {repeated_profiles}
- Maximum postings associated with one profile:
  {maximum_postings_per_profile}
"""

print("\nPROFILE CONCENTRATION SUMMARY")
print("=" * 75)

print(concentration_summary)


# ============================================================
# 14. ROBUSTNESS TABLE
# ============================================================

if not robust_table.empty:

    robustness_table_text = markdown_table(
        robust_table,
        [
            "word",
            "genuine_profiles_unique",
            "fraud_profiles_unique",
            "genuine_rate_unique",
            "fraud_rate_unique",
            "rate_ratio_unique",
            "adjusted_p_value_unique"
        ]
    )

else:

    robustness_table_text = (
        "No words met the specified robustness criteria."
    )


# ============================================================
# 15. BUILD FINAL RESEARCH REPORT
# ============================================================

report = f"""# OfferShield AI

# Company Profile Vocabulary Research Report

## 1. Research Objective

This investigation examines whether vocabulary used in company
profiles differs between genuine-labelled and fraudulent-labelled
job postings in the EMSCAD dataset.

The objective is exploratory: identify language associations,
investigate repeated company-profile templates, and examine whether
word-level findings remain consistent after grouping related word forms.

These results are not used as proof that a company is fraudulent.

## 2. Dataset and Sample Composition

The analysis uses normalized, unique company-profile texts.

| Metric | Count |
|---|---:|
| Unique company profiles | {total_unique_profiles} |
| Genuine-labelled profiles | {genuine_profiles} |
| Fraudulent-labelled profiles | {fraud_profiles} |
| Mixed-label profiles | {mixed_profiles} |

A profile is assigned a label based on the job postings associated
with that exact normalized profile.

A fraudulent-labelled profile does not establish that the company
itself is fraudulent.

## 3. Statistical Methodology

The analysis uses the following procedure:

1. Normalize company-profile text.
2. Group identical normalized profile texts.
3. Assign profile groups based on associated posting labels.
4. Exclude mixed-label profiles.
5. Tokenize text using the regular expression `[a-z]{{3,}}`.
6. Remove selected stop words.
7. Count each word at most once per unique profile.
8. Construct a 2x2 presence/absence contingency table.
9. Apply Fisher's exact test.
10. Correct multiple comparisons using the Benjamini-Hochberg
    false discovery rate procedure.

Individual word analysis tests {total_word_tests} word forms.

Word-family analysis tests {total_families} manually defined families.

The two analyses use the same unique-profile groups and the same
statistical testing approach. Multiple-testing correction is applied
separately to each analysis.

## 4. Individual Word Results

| Metric | Result |
|---|---:|
| Individual word forms tested | {total_word_tests} |
| Significant individual words | {significant_words} |
| Fraud-associated significant words | {fraud_associated_words} |
| Genuine-associated significant words | {genuine_associated_words} |

### Top Significant Individual Words

{markdown_table(
    top_words,
    [
        "word",
        "genuine_profiles",
        "fraud_profiles",
        "genuine_rate",
        "fraud_rate",
        "rate_ratio",
        "adjusted_p_value"
    ]
)}

## 5. Word-Family Results

| Metric | Result |
|---|---:|
| Word families tested | {total_families} |
| Significant word families | {significant_families} |

### Top Significant Word Families

{markdown_table(
    top_families,
    [
        "family",
        "genuine_profiles",
        "fraud_profiles",
        "genuine_rate",
        "fraud_rate",
        "rate_ratio",
        "adjusted_p_value"
    ]
)}

## 6. Word-Level Versus Word-Family Comparison

| Comparison category | Number of families |
|---|---:|
| Significant at both levels | {both_significant} |
| Significant only as a family | {family_only} |
| Significant only as individual words | {individual_only} |
| Not significant at either level | {neither} |

The comparison illustrates that combining related word forms can
change statistical significance. Individual word forms and their
combined family can produce different statistical results.

## 7. Vocabulary Robustness Analysis

The robustness analysis compares posting-level vocabulary results
with unique-profile vocabulary results.

### Robustness Summary

{robustness_summary}

### Top Words Meeting Robustness and Sample-Size Criteria

{robustness_table_text}

A robust association here means that a word meets the specific
criteria defined by this project's robustness analysis.

It does not establish that the word is a reliable fraud predictor
or that it identifies a fraudulent company.

## 8. Vocabulary Sensitivity Analysis

The sensitivity analysis investigates how vocabulary associations
change after excluding two highly repeated fraudulent-labelled
company-profile texts.

### Sensitivity Summary

{sensitivity_summary}

Excluding these profiles also reduces the fraudulent-labelled
posting sample. Therefore, changes in statistical significance may
reflect both reduced profile concentration and reduced statistical
power.

The results should not be interpreted as evidence that the excluded
profiles alone explain all vocabulary differences.

## 9. Company Profile Concentration

{concentration_summary}

Repeated company-profile texts can cause the same language pattern
to appear across multiple job postings.

Grouping identical normalized profiles helps reduce this repeated
text effect in the unique-profile analysis.

However, different profile texts may still belong to related
companies, recruitment agencies, or shared templates.

## 10. Statistical Limitations

1. The unique-profile fraudulent-labelled group contains only
   {fraud_profiles} profiles, which limits statistical power and
   makes estimates sensitive to individual observations.

2. Posting labels are not verified company-level fraud labels.

3. Exact text deduplication does not guarantee statistical
   independence between different profiles.

4. Some vocabulary terms may occur together or reflect common
   industry language, company templates, or recruitment terminology.

5. Large rate ratios can occur when a word is rare in the
   genuine-labelled group.

6. Statistical significance does not establish causation or
   predictive performance.

7. Benjamini-Hochberg correction controls the false discovery
   rate under its assumptions; it does not remove sampling bias,
   dependence, or limitations in the underlying dataset.

8. The word families were manually defined, so different family
   definitions could produce different results.

9. These results must not be interpreted as proof that a job,
   company, or recruiter is fraudulent.

## 11. Research Conclusion

The company-profile vocabulary analysis identified differences
between genuine-labelled and fraudulent-labelled profile groups.

The analysis found {significant_words} significant individual word
forms and {significant_families} significant word families after
multiple-testing correction.

The word-family comparison provides an additional way to study
related vocabulary forms and reveals that individual word and
family-level significance are not always identical.

The robustness and sensitivity analyses provide additional
information about how repeated profiles and alternative counting
approaches affect the observed associations.

These findings provide exploratory linguistic evidence for further
research into job-posting fraud detection. They do not independently
establish whether a posting or company is fraudulent.

## 12. Reproducibility

The research outputs are stored in `data/processed/`.

Important files include:

- `audit_individual_word_results.csv`
- `audit_word_family_results.csv`
- `audit_word_family_comparison.csv`
- `audit_individual_words_with_families.csv`
- `unique_profile_word_analysis.csv`
- `unique_profile_fraud_vocabulary.csv`
- `unique_profile_genuine_vocabulary.csv`
- `company_profile_vocabulary_robustness.csv`
- `vocabulary_sensitivity_comparison.csv`
- `unique_company_profile_summary.csv`

The scripts used to produce these outputs are maintained in the
OfferShield AI project repository.

---

**Project:** OfferShield AI

**Research component:** Company Profile Vocabulary Analysis

**Purpose:** Exploratory research for explainable job-posting
fraud detection.
"""


# ============================================================
# 16. SAVE FINAL REPORT
# ============================================================

REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_PATH.write_text(
    report,
    encoding="utf-8"
)


# ============================================================
# 17. FINAL VERIFICATION
# ============================================================

saved_report = REPORT_PATH.read_text(
    encoding="utf-8"
)

if len(saved_report.strip()) == 0:
    raise ValueError("The generated report is empty.")

required_report_sections = [
    "Research Objective",
    "Dataset and Sample Composition",
    "Statistical Methodology",
    "Individual Word Results",
    "Word-Family Results",
    "Word-Level Versus Word-Family Comparison",
    "Vocabulary Robustness Analysis",
    "Vocabulary Sensitivity Analysis",
    "Company Profile Concentration",
    "Statistical Limitations",
    "Research Conclusion",
    "Reproducibility"
]

missing_sections = [
    section
    for section in required_report_sections
    if section not in saved_report
]

if missing_sections:
    raise ValueError(
        f"Report is missing sections: {missing_sections}"
    )


print("\nFINAL RESEARCH REPORT GENERATED")
print("=" * 75)

print("Report location:", REPORT_PATH)

print("\nDATASET SUMMARY")
print("Unique profiles:", total_unique_profiles)
print("Genuine-labelled profiles:", genuine_profiles)
print("Fraudulent-labelled profiles:", fraud_profiles)
print("Mixed-label profiles:", mixed_profiles)

print("\nVOCABULARY RESULTS")
print("Individual words tested:", total_word_tests)
print("Significant individual words:", significant_words)
print("Word families tested:", total_families)
print("Significant word families:", significant_families)

print("\nROBUSTNESS RESULTS")
print("Robust words with sample-size support:",
      robust_with_support_count)

print("\nSENSITIVITY RESULTS")
print("Original significant words:", significant_original)
print("Significant after exclusion:", significant_after)
print("Significant in both:", significant_both)
print("Original significance retention:",
      f"{retention_percentage:.2f}%")

print("\nREPORT VERIFICATION")
print("Sections verified:", len(required_report_sections))
print("Report file size:", len(saved_report), "characters")

print("\nALL OPERATIONS COMPLETED SUCCESSFULLY!")
