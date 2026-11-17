"""Unit tests for models.py — the database layer."""

import sqlite3
from datetime import date, timedelta

import models


def test_create_and_get(db_path, sample):  # FR1, FR9
    app_id = models.create_application(db_path, sample)
    saved = models.get_application(db_path, app_id)
    assert saved["company"] == "Orange"
    assert saved["status"] == "Applied"


def test_list_all(db_path, sample):  # FR2
    models.create_application(db_path, sample)
    models.create_application(db_path, {**sample, "company": "Airbus"})
    assert len(models.get_all_applications(db_path)) == 2


def test_update(db_path, sample):  # FR3
    app_id = models.create_application(db_path, sample)
    models.update_application(db_path, app_id, {**sample, "job_title": "AI Intern"})
    assert models.get_application(db_path, app_id)["job_title"] == "AI Intern"


def test_delete(db_path, sample):  # FR4
    app_id = models.create_application(db_path, sample)
    models.delete_application(db_path, app_id)
    assert models.get_application(db_path, app_id) is None


def test_update_status(db_path, sample):  # FR5
    app_id = models.create_application(db_path, sample)
    models.update_status(db_path, app_id, "Interview")
    assert models.get_application(db_path, app_id)["status"] == "Interview"


def test_search_by_company_is_partial_and_case_insensitive(db_path, sample):  # FR6
    models.create_application(db_path, sample)
    models.create_application(db_path, {**sample, "company": "Airbus"})
    results = models.search_applications(db_path, query="oran")
    assert [a["company"] for a in results] == ["Orange"]


def test_filter_by_status(db_path, sample):  # FR7
    models.create_application(db_path, sample)
    models.create_application(db_path, {**sample, "status": "Offer"})
    results = models.search_applications(db_path, status="Offer")
    assert len(results) == 1 and results[0]["status"] == "Offer"


def test_statistics(db_path, sample):  # FR8
    for status in ["Applied", "Interview", "Offer", "Rejected"]:
        models.create_application(db_path, {**sample, "status": status})
    stats = models.get_statistics(db_path)
    assert stats["total"] == 4
    assert stats["by_status"]["Offer"] == 1
    assert stats["interview_rate"] == 50  # 2 of 4 reached Interview or Offer


def test_statistics_empty_database(db_path):  # FR8 edge case: no division by zero
    stats = models.get_statistics(db_path)
    assert stats["total"] == 0 and stats["interview_rate"] == 0


def test_data_persists_after_reconnect(db_path, sample):  # NFR3
    app_id = models.create_application(db_path, sample)
    models.init_db(db_path)  # simulates restarting the application
    assert models.get_application(db_path, app_id) is not None


def test_create_with_job_reference(db_path, sample):  # FR10
    app_id = models.create_application(db_path, {**sample, "job_reference": "REF-2026-1234"})
    assert models.get_application(db_path, app_id)["job_reference"] == "REF-2026-1234"


def test_search_by_job_reference(db_path, sample):  # FR10
    models.create_application(db_path, {**sample, "job_reference": "REF-2026-1234"})
    models.create_application(db_path, {**sample, "company": "Airbus", "job_reference": "AB-99"})
    results = models.search_applications(db_path, query="2026-12")
    assert [a["company"] for a in results] == ["Orange"]


def test_find_by_reference_exact_and_case_insensitive(db_path, sample):  # FR10
    models.create_application(db_path, {**sample, "job_reference": "REF-2026-1234"})
    assert len(models.find_by_reference(db_path, " ref-2026-1234 ")) == 1
    assert models.find_by_reference(db_path, "REF-2026") == []  # partial is not exact
    assert models.find_by_reference(db_path, "") == []


def test_migration_adds_job_reference_to_old_database(tmp_path):  # FR10, NFR3
    path = str(tmp_path / "old.db")
    # Build a database with the Sprint 1-3 schema (no job_reference column)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """CREATE TABLE applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL,
                job_title TEXT NOT NULL, location TEXT, application_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied', job_link TEXT, notes TEXT)"""
        )
        conn.execute(
            "INSERT INTO applications (company, job_title, application_date) "
            "VALUES ('Orange', 'Data Intern', '2026-11-01')"
        )
    models.init_db(path)  # must add the column without losing data
    models.init_db(path)  # running it twice must not fail
    rows = models.get_all_applications(path)
    assert len(rows) == 1 and rows[0]["company"] == "Orange"
    assert rows[0]["job_reference"] is None


TODAY = date(2026, 11, 17)  # fixed "today" so the tests never depend on the real date


def test_per_day_missing_days_are_zero(db_path, sample):  # FR11
    models.create_application(db_path, {**sample, "application_date": "2026-11-15"})
    result = models.get_applications_per_day(db_path, days=14, today=TODAY)
    assert len(result) == 14
    assert result[0] == ("2026-11-04", 0) and result[-1] == ("2026-11-17", 0)
    assert dict(result)["2026-11-15"] == 1
    assert sum(n for _, n in result) == 1


def test_per_day_several_applications_same_day(db_path, sample):  # FR11
    for company in ["Orange", "Airbus", "Thales"]:
        models.create_application(db_path, {**sample, "company": company,
                                            "application_date": "2026-11-17"})
    models.create_application(db_path, {**sample, "application_date": "2026-10-01"})  # too old
    result = models.get_applications_per_day(db_path, days=14, today=TODAY)
    assert result[-1] == ("2026-11-17", 3)
    assert sum(n for _, n in result) == 3


def test_per_day_empty_database(db_path):  # FR11 edge case
    result = models.get_applications_per_day(db_path, days=14, today=TODAY)
    assert len(result) == 14 and all(n == 0 for _, n in result)
    assert models.get_daily_summary(db_path, today=TODAY) == {
        "today": 0, "last_7_days": 0, "avg_30_days": 0.0}


def test_daily_summary(db_path, sample):  # FR11
    for days_ago in [0, 0, 3, 10, 40]:
        day = (TODAY - timedelta(days=days_ago)).isoformat()
        models.create_application(db_path, {**sample, "application_date": day})
    summary = models.get_daily_summary(db_path, today=TODAY)
    assert summary["today"] == 2
    assert summary["last_7_days"] == 3
    assert summary["avg_30_days"] == round(4 / 30, 1)  # 40 days ago is not counted
