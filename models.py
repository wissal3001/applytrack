"""
models.py — MODEL layer (MVC architecture).

This file is the ONLY place that talks to the SQLite database.
The rest of the application calls these functions instead of writing SQL.
Requirements covered: FR1, FR2, FR3, FR4, FR5, FR9, NFR3 (data persists on disk).
"""

import sqlite3

# The four possible statuses of an application (used for validation and filters).
STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


def get_connection(db_path):
    """Open a connection to the SQLite file.
    row_factory lets us read columns by name: row["company"] instead of row[1]."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    """Create the 'applications' table if it does not exist yet (FR9)."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                company          TEXT NOT NULL,
                job_title        TEXT NOT NULL,
                location         TEXT,
                application_date TEXT NOT NULL,
                status           TEXT NOT NULL DEFAULT 'Applied',
                job_link         TEXT,
                notes            TEXT
            )
            """
        )


def create_application(db_path, data):
    """FR1 — Insert a new application. Returns the id of the new row.
    The '?' placeholders protect against SQL injection."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications
                (company, job_title, location, application_date, status, job_link, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["company"],
                data["job_title"],
                data.get("location", ""),
                data["application_date"],
                data.get("status", "Applied"),
                data.get("job_link", ""),
                data.get("notes", ""),
            ),
        )
        return cursor.lastrowid


def get_all_applications(db_path):
    """FR2 — Return every application, most recent first."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY application_date DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_application(db_path, app_id):
    """Return one application as a dictionary, or None if it does not exist."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        return dict(row) if row else None


def update_application(db_path, app_id, data):
    """FR3 — Replace all the fields of an existing application."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            UPDATE applications
            SET company = ?, job_title = ?, location = ?, application_date = ?,
                status = ?, job_link = ?, notes = ?
            WHERE id = ?
            """,
            (
                data["company"],
                data["job_title"],
                data.get("location", ""),
                data["application_date"],
                data["status"],
                data.get("job_link", ""),
                data.get("notes", ""),
                app_id,
            ),
        )


def update_status(db_path, app_id, status):
    """FR5 — Change only the status (quick update from the list page)."""
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?", (status, app_id)
        )


def delete_application(db_path, app_id):
    """FR4 — Delete an application."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
