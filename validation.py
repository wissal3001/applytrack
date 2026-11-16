"""
validation.py — checks what the user typed BEFORE it reaches the database.
Requirement covered: NFR6 (Data Validation).

Keeping validation in its own module makes it easy to test on its own (NFR7).
"""

from datetime import datetime

from models import STATUSES


def validate_application(form):
    """Take the raw form fields and return (clean_data, errors).
    If 'errors' is empty, the data is safe to save."""
    data = {
        "company": form.get("company", "").strip(),
        "job_title": form.get("job_title", "").strip(),
        "location": form.get("location", "").strip(),
        "application_date": form.get("application_date", "").strip(),
        "status": form.get("status", "Applied").strip(),
        "job_link": form.get("job_link", "").strip(),
        "notes": form.get("notes", "").strip(),
        "job_reference": form.get("job_reference", "").strip(),  # FR10, optional
    }
    errors = []

    # Required fields
    if not data["company"]:
        errors.append("Company name is required.")
    if not data["job_title"]:
        errors.append("Job title is required.")

    # Date must exist and follow the YYYY-MM-DD format
    if not data["application_date"]:
        errors.append("Application date is required.")
    else:
        try:
            datetime.strptime(data["application_date"], "%Y-%m-%d")
        except ValueError:
            errors.append("Application date must use the format YYYY-MM-DD.")

    # Status must be one of the allowed values
    if data["status"] not in STATUSES:
        errors.append("Status must be one of: " + ", ".join(STATUSES) + ".")

    # Link is optional, but if given it must look like a web address
    if data["job_link"] and not data["job_link"].startswith(("http://", "https://")):
        errors.append("Job link must start with http:// or https://")

    # Length limits avoid absurd inputs
    if len(data["company"]) > 100 or len(data["job_title"]) > 100:
        errors.append("Company and job title must be at most 100 characters.")
    if len(data["job_reference"]) > 50:
        errors.append("Job reference must be at most 50 characters.")

    return data, errors
