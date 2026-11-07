"""Unit tests for models.py — the database layer."""

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
