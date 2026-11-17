"""
models.py — MODEL layer (MVC architecture).

This file is the ONLY place that talks to the SQLite database.
The rest of the application calls these functions instead of writing SQL.
Requirements covered: FR1, FR2, FR3, FR4, FR5, FR9, FR10, FR11, NFR3 (data persists on disk).
"""

import sqlite3
from datetime import date, timedelta

# The four possible statuses of an application (used for validation and filters).
STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


def get_connection(db_path):
    """Open a connection to the SQLite file.
    row_factory lets us read columns by name: row["company"] instead of row[1]."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    """Create the 'applications' table if it does not exist yet (FR9).
    Also upgrades an older database: if the job_reference column (FR10) is
    missing, it is added with ALTER TABLE. Existing rows are kept untouched."""
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
                notes            TEXT,
                job_reference    TEXT
            )
            """
        )
        # Migration for databases created before Sprint 4 (FR10)
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(applications)")]
        if "job_reference" not in columns:
            conn.execute("ALTER TABLE applications ADD COLUMN job_reference TEXT")


def create_application(db_path, data):
    """FR1 — Insert a new application. Returns the id of the new row.
    The '?' placeholders protect against SQL injection."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications
                (company, job_title, location, application_date, status, job_link, notes,
                 job_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["company"],
                data["job_title"],
                data.get("location", ""),
                data["application_date"],
                data.get("status", "Applied"),
                data.get("job_link", ""),
                data.get("notes", ""),
                data.get("job_reference", ""),
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


def search_applications(db_path, query="", status=""):
    """FR6 + FR7 + FR10 — Search by company name or job reference,
    and/or filter by status.
    Empty values mean 'no filter'. The SQL query is built step by step."""
    sql = "SELECT * FROM applications WHERE 1=1"
    params = []
    if query:
        sql += " AND (company LIKE ? OR job_reference LIKE ?)"  # LIKE + % = 'contains'
        params += ["%" + query + "%", "%" + query + "%"]
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY application_date DESC, id DESC"
    with get_connection(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def find_by_reference(db_path, reference):
    """FR10 — Return the applications whose job reference is EXACTLY the given code
    (ignoring upper/lower case and surrounding spaces). Empty list if none."""
    reference = (reference or "").strip()
    if not reference:
        return []
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE job_reference = ? COLLATE NOCASE "
            "ORDER BY application_date DESC, id DESC",
            (reference,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_statistics(db_path):
    """FR8 — Compute the numbers shown on the dashboard."""
    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM applications GROUP BY status"
        ).fetchall()

    # Start every status at 0 so the dashboard always shows all four
    by_status = {s: 0 for s in STATUSES}
    for row in rows:
        by_status[row["status"]] = row["n"]

    # Percentage of applications that reached at least an interview
    progressed = by_status["Interview"] + by_status["Offer"]
    interview_rate = round(progressed * 100 / total) if total else 0

    return {"total": total, "by_status": by_status, "interview_rate": interview_rate}


def get_applications_per_day(db_path, days=14, today=None):
    """FR11 — Number of applications sent on each of the last `days` days
    (today included), based on application_date.
    Returns a list of (date "YYYY-MM-DD", count), oldest first.
    Days without any application are included with 0.
    `today` can be given by the tests; by default it is the real date."""
    today = today or date.today()
    start = today - timedelta(days=days - 1)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT application_date, COUNT(*) AS n FROM applications "
            "WHERE application_date BETWEEN ? AND ? GROUP BY application_date",
            (start.isoformat(), today.isoformat()),
        ).fetchall()
    counts = {row["application_date"]: row["n"] for row in rows}
    result = []
    for i in range(days):
        day = (start + timedelta(days=i)).isoformat()
        result.append((day, counts.get(day, 0)))  # missing day -> 0
    return result


def get_daily_summary(db_path, today=None):
    """FR11 — The three numbers of the dashboard: applications sent today,
    during the last 7 days, and the average per day over the last 30 days."""
    last_30 = [n for _, n in get_applications_per_day(db_path, 30, today)]
    return {
        "today": last_30[-1],
        "last_7_days": sum(last_30[-7:]),
        "avg_30_days": round(sum(last_30) / 30, 1),
    }


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
                status = ?, job_link = ?, notes = ?, job_reference = ?
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
                data.get("job_reference", ""),
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
