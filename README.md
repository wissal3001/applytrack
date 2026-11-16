# ApplyTrack — Job Application Tracking Web Application

Advanced Software Engineering project — Huazhong University of Science and Technology
Author: Wissal RAMDANI (I202680252)

ApplyTrack helps students organize their internship and job applications in one place:
add, edit, delete, track status, search, filter, view statistics and check
whether an offer was already applied to using its job reference code.

## Tech stack
| Layer | Technology |
|---|---|
| Frontend (View) | HTML, CSS, Jinja2 templates |
| Backend (Controller) | Python 3, Flask |
| Database (Model) | SQLite |
| Tests | pytest |
| Version control | Git |

## How to run
```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5001

## How to run the tests
```bash
python -m pytest -v
```

## Architecture (MVC)
```
applytrack/
├── app.py            Controller: routes (URL -> function)
├── models.py         Model: all SQLite access
├── validation.py     Input validation (NFR6)
├── templates/        View: HTML pages (Jinja2)
│   ├── base.html         common layout
│   ├── index.html        list + search + filter
│   ├── form.html         create / edit form
│   └── dashboard.html    statistics
├── static/style.css  Styles
└── tests/            Automated tests (pytest)
```

## Database schema
Table `applications`

| Column | Type | Constraint |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| company | TEXT | NOT NULL |
| job_title | TEXT | NOT NULL |
| location | TEXT | |
| application_date | TEXT (YYYY-MM-DD) | NOT NULL |
| status | TEXT | NOT NULL, one of Applied / Interview / Offer / Rejected |
| job_link | TEXT | |
| notes | TEXT | |
| job_reference | TEXT | optional, max 50 characters (added in Sprint 4; `init_db` adds it automatically to older databases with `ALTER TABLE`, without data loss) |

## Routes
| Method | URL | Purpose | Requirement |
|---|---|---|---|
| GET | `/` | List, search by company or reference (`?q=`), filter (`?status=`), reference lookup | FR2, FR6, FR7, FR10 |
| GET/POST | `/applications/new` | Create an application | FR1 |
| GET/POST | `/applications/<id>/edit` | Edit an application | FR3 |
| POST | `/applications/<id>/status` | Change status | FR5 |
| POST | `/applications/<id>/delete` | Delete | FR4 |
| GET | `/dashboard` | Statistics | FR8 |

## Traceability matrix (requirement -> code -> test)
| Req. | Implemented in | Verified by |
|---|---|---|
| FR1 Create | `models.create_application`, route `new_application` | `test_create_and_get`, `test_create_through_form` |
| FR2 List | `models.get_all_applications`, route `index` | `test_list_all`, `test_home_page_loads` |
| FR3 Edit | `models.update_application`, route `edit_application` | `test_update`, `test_edit_through_form` |
| FR4 Delete | `models.delete_application`, route `delete_application` | `test_delete`, `test_delete_through_button` |
| FR5 Status | `models.update_status`, route `change_status` | `test_update_status`, `test_change_status` |
| FR6 Search | `models.search_applications` | `test_search_by_company_...`, `test_search_route` |
| FR7 Filter | `models.search_applications` | `test_filter_by_status` |
| FR8 Statistics | `models.get_statistics`, route `dashboard` | `test_statistics`, `test_statistics_empty_database`, `test_dashboard_route` |
| FR9 SQLite | `models.init_db` | all model tests |
| FR10 Job reference | `models.init_db` (migration), `models.find_by_reference`, `models.search_applications`, `validation.validate_application`, route `index`, `form.html`, `index.html` | `test_create_with_job_reference`, `test_search_by_job_reference`, `test_find_by_reference_exact_and_case_insensitive`, `test_migration_adds_job_reference_to_old_database`, `test_job_reference_is_optional`, `test_job_reference_is_trimmed`, `test_job_reference_too_long_is_rejected`, `test_create_with_reference_through_form`, `test_reference_lookup_says_already_applied`, `test_reference_lookup_not_found` |
| NFR1 Usability | flash messages, single form for create/edit, coloured statuses | manual test |
| NFR2 Performance | indexed primary key, simple queries | `test_common_operations_are_fast` |
| NFR3 Reliability | data stored in `applytrack.db` file | `test_data_persists_after_reconnect` |
| NFR4 Maintainability | MVC separation, one module per responsibility | code review |
| NFR5 Compatibility | standard HTML/CSS, no plugins | manual test on Chrome / Safari |
| NFR6 Validation | `validation.validate_application` | `tests/test_validation.py` (11 tests) |
| NFR7 Testability | app factory `create_app(db_path)`, pytest fixtures | 38 automated tests |

## Development process (Agile, 4 sprints)
| Sprint | Content | Commit |
|---|---|---|
| 1 | CRUD + status + validation | `Sprint 1: CRUD ...` |
| 2 | Search, filter, dashboard | `Sprint 2: search ...` |
| 3 | Automated tests + documentation | `Sprint 3: tests ...` |
| 4 | Job reference field and lookup (FR10) | `Sprint 4: job reference ...` |

## Out of scope (v1)
Machine learning, automatic applications, external job platform integration, multi-user authentication.
