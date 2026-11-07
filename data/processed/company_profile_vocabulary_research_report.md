# OfferShield AI

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
| Unique company profiles | 1707 |
| Genuine-labelled profiles | 1658 |
| Fraudulent-labelled profiles | 49 |
| Mixed-label profiles | 0 |

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
5. Tokenize text using the regular expression `[a-z]{3,}`.
6. Remove selected stop words.
7. Count each word at most once per unique profile.
8. Construct a 2x2 presence/absence contingency table.
9. Apply Fisher's exact test.
10. Correct multiple comparisons using the Benjamini-Hochberg
    false discovery rate procedure.

Individual word analysis tests 78 word forms.

Word-family analysis tests 23 manually defined families.

The two analyses use the same unique-profile groups and the same
statistical testing approach. Multiple-testing correction is applied
separately to each analysis.

## 4. Individual Word Results

| Metric | Result |
|---|---:|
| Individual word forms tested | 78 |
| Significant individual words | 25 |
| Fraud-associated significant words | 25 |
| Genuine-associated significant words | 0 |

### Top Significant Individual Words

| word | genuine_profiles | fraud_profiles | genuine_rate | fraud_rate | rate_ratio | adjusted_p_value |
| --- | --- | --- | --- | --- | --- | --- |
| leveraging | 12 | 11 | 0.72% | 22.45% | 31.02 | 1.584e-10 |
| geographical | 4 | 9 | 0.24% | 18.37% | 76.13 | 1.584e-10 |
| partnered | 8 | 9 | 0.48% | 18.37% | 38.07 | 3.294e-09 |
| effort | 9 | 9 | 0.54% | 18.37% | 33.84 | 4.836e-09 |
| efficient | 42 | 11 | 2.53% | 22.45% | 8.86 | 1.654e-06 |
| recruiting | 42 | 10 | 2.53% | 20.41% | 8.06 | 1.227e-05 |
| exciting | 56 | 11 | 3.38% | 22.45% | 6.65 | 1.482e-05 |
| hiring | 48 | 10 | 2.90% | 20.41% | 7.05 | 2.372e-05 |
| department | 17 | 7 | 1.03% | 14.29% | 13.93 | 2.372e-05 |
| model | 40 | 9 | 2.41% | 18.37% | 7.61 | 4.186e-05 |
| achieve | 67 | 11 | 4.04% | 22.45% | 5.56 | 4.518e-05 |
| career | 85 | 12 | 5.13% | 24.49% | 4.78 | 5.977e-05 |
| goals | 61 | 10 | 3.68% | 20.41% | 5.55 | 1.099e-04 |
| communications | 37 | 8 | 2.23% | 16.33% | 7.32 | 1.376e-04 |
| provide | 239 | 18 | 14.41% | 36.73% | 2.55 | 6.492e-04 |

## 5. Word-Family Results

| Metric | Result |
|---|---:|
| Word families tested | 23 |
| Significant word families | 20 |

### Top Significant Word Families

| family | genuine_profiles | fraud_profiles | genuine_rate | fraud_rate | rate_ratio | adjusted_p_value |
| --- | --- | --- | --- | --- | --- | --- |
| effort | 23 | 11 | 1.39% | 22.45% | 16.18 | 1.365e-08 |
| leverage | 44 | 13 | 2.65% | 26.53% | 10.00 | 1.903e-08 |
| geographical | 14 | 9 | 0.84% | 18.37% | 21.75 | 2.870e-08 |
| hiring | 102 | 13 | 6.15% | 26.53% | 4.31 | 4.604e-05 |
| efficient | 85 | 12 | 5.13% | 24.49% | 4.78 | 4.604e-05 |
| department | 23 | 7 | 1.39% | 14.29% | 10.30 | 4.895e-05 |
| career | 104 | 12 | 6.27% | 24.49% | 3.90 | 1.950e-04 |
| exciting | 89 | 11 | 5.37% | 22.45% | 4.18 | 2.084e-04 |
| model | 61 | 9 | 3.68% | 18.37% | 4.99 | 2.750e-04 |
| achieve | 97 | 11 | 5.85% | 22.45% | 3.84 | 3.420e-04 |
| communication | 84 | 9 | 5.07% | 18.37% | 3.63 | 2.012e-03 |
| recruitment | 128 | 11 | 7.72% | 22.45% | 2.91 | 2.495e-03 |
| venture | 90 | 9 | 5.43% | 18.37% | 3.38 | 2.495e-03 |
| focus | 238 | 16 | 14.35% | 32.65% | 2.27 | 2.495e-03 |
| direct | 73 | 8 | 4.40% | 16.33% | 3.71 | 2.564e-03 |

## 6. Word-Level Versus Word-Family Comparison

| Comparison category | Number of families |
|---|---:|
| Significant at both levels | 20 |
| Significant only as a family | 0 |
| Significant only as individual words | 3 |
| Not significant at either level | 0 |

The comparison illustrates that combining related word forms can
change statistical significance. Individual word forms and their
combined family can produce different statistical results.

## 7. Vocabulary Robustness Analysis

The robustness analysis compares posting-level vocabulary results
with unique-profile vocabulary results.

### Robustness Summary


- Total comparison records: 74
- Posting-level significant words: 46
- Unique-profile significant words: 40
- Words with the same association direction: 59
- Robust fraud-associated words: 29
- Words meeting sample-size eligibility: 56
- Robust words with sample-size support: 28


### Top Words Meeting Robustness and Sample-Size Criteria

| word | genuine_profiles_unique | fraud_profiles_unique | genuine_rate_unique | fraud_rate_unique | rate_ratio_unique | adjusted_p_value_unique |
| --- | --- | --- | --- | --- | --- | --- |
| provide | 239 | 18 | 14.41% | 36.73% | 2.55 | 4.993e-05 |
| career | 85 | 12 | 5.13% | 24.49% | 4.78 | 3.208e-08 |
| exciting | 56 | 11 | 3.38% | 22.45% | 6.65 | 7.181e-11 |
| achieve | 67 | 11 | 4.04% | 22.45% | 5.56 | 5.676e-09 |
| professional | 132 | 11 | 7.96% | 22.45% | 2.82 | 6.954e-04 |
| leveraging | 12 | 11 | 0.72% | 22.45% | 31.02 | 4.969e-37 |
| efficient | 42 | 11 | 2.53% | 22.45% | 8.86 | 2.114e-14 |
| goals | 61 | 10 | 3.68% | 20.41% | 5.55 | 3.177e-08 |
| develop | 89 | 10 | 5.37% | 20.41% | 3.80 | 2.926e-05 |
| focus | 109 | 10 | 6.57% | 20.41% | 3.10 | 4.519e-04 |
| hiring | 48 | 10 | 2.90% | 20.41% | 7.05 | 1.393e-10 |
| effective | 66 | 10 | 3.98% | 20.41% | 5.13 | 1.510e-07 |
| recruiting | 42 | 10 | 2.53% | 20.41% | 8.06 | 4.489e-12 |
| venture | 70 | 9 | 4.22% | 18.37% | 4.35 | 1.198e-05 |
| geographical | 4 | 9 | 0.24% | 18.37% | 76.13 | 5.274e-45 |

A robust association here means that a word meets the specific
criteria defined by this project's robustness analysis.

It does not establish that the word is a reliable fraud predictor
or that it identifies a fraudulent company.

## 8. Vocabulary Sensitivity Analysis

The sensitivity analysis investigates how vocabulary associations
change after excluding two highly repeated fraudulent-labelled
company-profile texts.

### Sensitivity Summary


- Words compared: 359
- Significant words in original analysis: 290
- Significant words after profile exclusion: 228
- Significant in both analyses: 209
- No longer significant after exclusion: 81
- Newly significant after exclusion: 19
- Original significant-word retention: 72.07%


Excluding these profiles also reduces the fraudulent-labelled
posting sample. Therefore, changes in statistical significance may
reflect both reduced profile concentration and reduced statistical
power.

The results should not be interpreted as evidence that the excluded
profiles alone explain all vocabulary differences.

## 9. Company Profile Concentration


- Unique company profiles: 1707
- Profiles associated with multiple postings: 1173
- Maximum postings associated with one profile:
  726


Repeated company-profile texts can cause the same language pattern
to appear across multiple job postings.

Grouping identical normalized profiles helps reduce this repeated
text effect in the unique-profile analysis.

However, different profile texts may still belong to related
companies, recruitment agencies, or shared templates.

## 10. Statistical Limitations

1. The unique-profile fraudulent-labelled group contains only
   49 profiles, which limits statistical power and
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

The analysis found 25 significant individual word
forms and 20 significant word families after
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
