"""Integration tests: they call the web pages like a real browser would."""

import time


def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_create_through_form(client, sample):  # FR1
    response = client.post("/applications/new", data=sample, follow_redirects=True)
    assert response.status_code == 200
    assert b"Orange" in response.data
    assert b"Application added." in response.data


def test_invalid_form_shows_error(client, sample):  # NFR6
    response = client.post("/applications/new", data={**sample, "company": ""})
    assert response.status_code == 400
    assert b"Company name is required." in response.data


def test_edit_through_form(client, sample):  # FR3
    client.post("/applications/new", data=sample)
    client.post("/applications/1/edit", data={**sample, "job_title": "AI Intern"})
    assert b"AI Intern" in client.get("/").data


def test_change_status(client, sample):  # FR5
    client.post("/applications/new", data=sample)
    client.post("/applications/1/status", data={"status": "Offer"})
    assert b"Offer" in client.get("/?status=Offer").data
    assert b"Orange" in client.get("/?status=Offer").data


def test_delete_through_button(client, sample):  # FR4
    client.post("/applications/new", data=sample)
    client.post("/applications/1/delete")
    assert b"No applications yet" in client.get("/").data


def test_search_route(client, sample):  # FR6
    client.post("/applications/new", data=sample)
    client.post("/applications/new", data={**sample, "company": "Airbus"})
    page = client.get("/?q=airbus").data
    assert b"Airbus" in page and b"Orange" not in page


def test_dashboard_route(client, sample):  # FR8
    client.post("/applications/new", data=sample)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Total applications" in response.data


def test_unknown_application_returns_404(client):
    assert client.get("/applications/999/edit").status_code == 404


def test_common_operations_are_fast(client, sample):  # NFR2: under 2 seconds
    for i in range(50):
        client.post("/applications/new", data={**sample, "company": f"Company {i}"})
    start = time.perf_counter()
    client.get("/")
    client.get("/dashboard")
    client.get("/?q=Company 4")
    assert time.perf_counter() - start < 2
