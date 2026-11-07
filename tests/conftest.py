"""
conftest.py — shared test setup (pytest "fixtures").
Each test gets a brand-new temporary database, so tests never touch real data
and never depend on each other.
"""

import os
import sys

import pytest

# Allow 'import app', 'import models' from the tests folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
import models  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    """Path to an empty temporary SQLite database."""
    path = str(tmp_path / "test.db")
    models.init_db(path)
    return path


@pytest.fixture
def client(tmp_path):
    """A fake browser to call the routes without starting a real server."""
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def sample():
    """A valid application used by many tests."""
    return {
        "company": "Orange",
        "job_title": "Data Intern",
        "location": "Paris",
        "application_date": "2026-11-01",
        "status": "Applied",
        "job_link": "https://orange.com/jobs/1",
        "notes": "Referral from a friend",
    }
