
import re


def verify_company_profile(job_data: dict) -> dict:
    """
    Review company information supplied in a job posting.

    This is a rule-based completeness and consistency review.
    It does not independently verify a company's legal existence.
    """

    company_profile = str(
        job_data.get("company_profile") or ""
    ).strip()

    description = str(
        job_data.get("description") or ""
    ).strip()

    title = str(
        job_data.get("title") or ""
    ).strip()

    benefits = str(
        job_data.get("benefits") or ""
    ).strip()

    checks = []

    def add_check(name, status, severity, message):
        checks.append({
            "name": name,
            "status": status,
            "severity": severity,
            "message": message
        })

    # 1. Company profile availability
    if not company_profile:
        add_check(
            "Company profile",
            "missing",
            "warning",
            "The job posting does not provide a company profile."
        )
    elif len(company_profile) < 40:
        add_check(
            "Company profile",
            "incomplete",
            "warning",
            "The company profile contains very limited information."
        )
    else:
        add_check(
            "Company profile",
            "provided",
            "info",
            "A company profile has been provided."
        )

    # 2. Job description completeness
    if not description:
        add_check(
            "Job description",
            "missing",
            "warning",
            "No job description was provided."
        )
    elif len(description) < 100:
        add_check(
            "Job description",
            "incomplete",
            "warning",
            "The job description is quite short. More details would help applicants evaluate the opportunity."
        )
    else:
        add_check(
            "Job description",
            "provided",
            "info",
            "The job description contains sufficient text for an initial review."
        )

    # 3. Company website or contact information
    combined_text = f"{company_profile} {description}"

    has_email = bool(
        re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            combined_text,
            re.IGNORECASE
        )
    )

    has_website = bool(
        re.search(
            r"(https?://|www\.)[^\s]+",
            combined_text,
            re.IGNORECASE
        )
    )

    has_phone = bool(
        re.search(
            r"\b(?:\+?\d[\d\s().-]{7,}\d)\b",
            combined_text
        )
    )

    if has_email or has_website or has_phone:
        add_check(
            "Contact information",
            "provided",
            "info",
            "The posting includes at least one contact detail or website reference. Its authenticity has not been independently checked."
        )
    else:
        add_check(
            "Contact information",
            "not_found",
            "warning",
            "No email address, website, or phone number was found in the supplied text."
        )

    # 4. Application instructions
    application_terms = [
        "apply",
        "application",
        "submit your",
        "send your resume",
        "send your cv",
        "careers page",
        "application form"
    ]

    has_application_instructions = any(
        term in description.lower()
        for term in application_terms
    )

    if has_application_instructions:
        add_check(
            "Application instructions",
            "provided",
            "info",
            "The description contains an application-related instruction."
        )
    else:
        add_check(
            "Application instructions",
            "not_found",
            "warning",
            "The job description does not clearly explain how candidates should apply."
        )

    # 5. Job title availability
    if title:
        add_check(
            "Job title",
            "provided",
            "info",
            "A job title has been provided."
        )
    else:
        add_check(
            "Job title",
            "missing",
            "warning",
            "The job posting does not contain a job title."
        )

    # 6. Benefits information
    if benefits:
        add_check(
            "Benefits information",
            "provided",
            "info",
            "Benefits information has been included."
        )
    else:
        add_check(
            "Benefits information",
            "not_provided",
            "info",
            "No benefits information was supplied. This alone does not indicate fraud."
        )

    warning_count = sum(
        1 for check in checks
        if check["severity"] == "warning"
    )

    passed_count = sum(
        1 for check in checks
        if check["severity"] == "info"
    )

    return {
        "review_type": "Company Information Review",
        "status": (
            "Needs Attention"
            if warning_count > 0
            else "Information Provided"
        ),
        "total_checks": len(checks),
        "passed_checks": passed_count,
        "warning_checks": warning_count,
        "checks": checks,
        "disclaimer": (
            "This review checks the completeness of information "
            "supplied in the job posting. It does not independently "
            "confirm company registration, ownership, website "
            "authenticity, or employer legitimacy."
        )
    }
