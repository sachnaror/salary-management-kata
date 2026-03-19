from fastapi.testclient import TestClient


def test_create_employee_returns_201_and_payload(client: TestClient) -> None:
    payload = {
        "full_name": "Aarav Patel",
        "job_title": "Backend Engineer",
        "country": "India",
        "salary": 120000.0,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["full_name"] == payload["full_name"]
    assert body["job_title"] == payload["job_title"]
    assert body["country"] == payload["country"]
    assert body["salary"] == payload["salary"]


def test_create_employee_rejects_invalid_salary(client: TestClient) -> None:
    payload = {
        "full_name": "Sam Reed",
        "job_title": "Designer",
        "country": "United States",
        "salary": -10,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 422


def test_get_employee_by_id(client: TestClient) -> None:
    created = client.post(
        "/employees",
        json={
            "full_name": "Meera Shah",
            "job_title": "QA Engineer",
            "country": "India",
            "salary": 80000,
        },
    ).json()

    response = client.get(f"/employees/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["full_name"] == "Meera Shah"


def test_list_employees_returns_all_records(client: TestClient) -> None:
    client.post(
        "/employees",
        json={
            "full_name": "John Doe",
            "job_title": "Manager",
            "country": "United States",
            "salary": 150000,
        },
    )
    client.post(
        "/employees",
        json={
            "full_name": "Priya Nair",
            "job_title": "Manager",
            "country": "India",
            "salary": 140000,
        },
    )

    response = client.get("/employees")

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 2


def test_update_employee(client: TestClient) -> None:
    created = client.post(
        "/employees",
        json={
            "full_name": "Lisa Brown",
            "job_title": "Analyst",
            "country": "United States",
            "salary": 90000,
        },
    ).json()

    update_payload = {
        "full_name": "Lisa Brown",
        "job_title": "Senior Analyst",
        "country": "United States",
        "salary": 99000,
    }
    response = client.put(f"/employees/{created['id']}", json=update_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["job_title"] == "Senior Analyst"
    assert body["salary"] == 99000


def test_update_employee_partial_payload(client: TestClient) -> None:
    created = client.post(
        "/employees",
        json={
            "full_name": "Partial Update",
            "job_title": "Analyst",
            "country": "United States",
            "salary": 90000,
        },
    ).json()

    response = client.put(
        f"/employees/{created['id']}",
        json={"job_title": "Lead Analyst"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["full_name"] == "Partial Update"
    assert body["job_title"] == "Lead Analyst"
    assert body["country"] == "United States"
    assert body["salary"] == 90000


def test_update_employee_with_empty_payload_keeps_existing_values(client: TestClient) -> None:
    created = client.post(
        "/employees",
        json={
            "full_name": "No Change",
            "job_title": "QA Engineer",
            "country": "India",
            "salary": 70000,
        },
    ).json()

    response = client.put(
        f"/employees/{created['id']}",
        json={},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == created


def test_delete_employee(client: TestClient) -> None:
    created = client.post(
        "/employees",
        json={
            "full_name": "Delete Me",
            "job_title": "Temp",
            "country": "India",
            "salary": 50000,
        },
    ).json()

    delete_response = client.delete(f"/employees/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/employees/{created['id']}")
    assert get_response.status_code == 404


def test_get_employee_not_found(client: TestClient) -> None:
    response = client.get("/employees/999999")
    assert response.status_code == 404
