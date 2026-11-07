
import pandas as pd
import re
from urllib.parse import urlparse

# STEP 1: Load dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# STEP 2: Select text columns
text_columns = [
    "company_profile",
    "description",
    "requirements",
    "benefits"
]

# STEP 3: Detect complete URLs
url_pattern = r"""
    https?://[^\s<>"']+
    |
    www\.[^\s<>"']+
"""

def extract_domains(text):

    urls = re.findall(
        url_pattern,
        str(text),
        flags=re.IGNORECASE | re.VERBOSE
    )

    domains = []

    for url in urls:

        # Remove trailing punctuation
        url = url.rstrip(".,;:!?)]}")

        # Add scheme when missing
        if url.lower().startswith("www."):
            url = "https://" + url

        parsed_url = urlparse(url)

        domain = parsed_url.hostname

        if domain:

            domain = domain.lower().rstrip(".")

            # Basic domain validation
            if (
                "." in domain
                and not domain.startswith(".")
                and not domain.endswith(".")
            ):
                domains.append(domain)

    return domains


# STEP 4: Combine text columns
combined_text = (
    df[text_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
)

# STEP 5: Extract domains
df["all_domains"] = combined_text.apply(extract_domains)

df["domain_count"] = df["all_domains"].apply(len)

# STEP 6: Compare domain counts
print("\nCORRECTED WEBSITE DOMAIN ANALYSIS")
print("=" * 60)

print(
    df.groupby("fraudulent")["domain_count"]
    .agg(["mean", "median", "max"])
)

# STEP 7: Count postings containing domains
print("\nPOSTINGS CONTAINING DOMAINS")
print("=" * 60)

print(
    df.groupby("fraudulent")["domain_count"]
    .apply(lambda values: (values > 0).sum())
)

# STEP 8: Display frequent domains
print("\nTOP 20 DOMAINS")
print("=" * 60)

all_domains = [
    domain
    for domains in df["all_domains"]
    for domain in domains
]

print(pd.Series(all_domains).value_counts().head(20))

print("\nCORRECTED DOMAIN ANALYSIS COMPLETED!")
