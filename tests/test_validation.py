"""Unit tests for validation.py — NFR6 (Data Validation)."""

from validation import validate_application


def test_valid_input_has_no_errors(sample):
    data, errors = validate_application(sample)
    assert errors == []


def test_spaces_are_removed(sample):
    data, errors = validate_application({**sample, "company": "  Orange  "})
    assert data["company"] == "Orange"


def test_company_is_required(sample):
    _, errors = validate_application({**sample, "company": ""})
    assert "Company name is required." in errors


def test_job_title_is_required(sample):
    _, errors = validate_application({**sample, "job_title": "   "})
    assert "Job title is required." in errors


def test_invalid_date_is_rejected(sample):
    _, errors = validate_application({**sample, "application_date": "31/12/2026"})
    assert any("YYYY-MM-DD" in e for e in errors)


def test_unknown_status_is_rejected(sample):
    _, errors = validate_application({**sample, "status": "Hired"})
    assert any("Status must be" in e for e in errors)


def test_bad_link_is_rejected(sample):
    _, errors = validate_application({**sample, "job_link": "orange.com"})
    assert any("http" in e for e in errors)


def test_empty_link_is_allowed(sample):
    _, errors = validate_application({**sample, "job_link": ""})
    assert errors == []


def test_job_reference_is_optional(sample):  # FR10
    data, errors = validate_application(sample)  # sample has no reference
    assert errors == [] and data["job_reference"] == ""


def test_job_reference_is_trimmed(sample):  # FR10
    data, errors = validate_application({**sample, "job_reference": "  REF-2026-1234  "})
    assert errors == [] and data["job_reference"] == "REF-2026-1234"


def test_job_reference_too_long_is_rejected(sample):  # FR10
    _, errors = validate_application({**sample, "job_reference": "R" * 51})
    assert "Job reference must be at most 50 characters." in errors
