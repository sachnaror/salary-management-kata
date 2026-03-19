from fastapi.testclient import TestClient


def _create_employee(client: TestClient, country: str, salary: float) -> int:
    response = client.post(
        "/employees",
        json={
            "full_name": f"Employee {country}",
            "job_title": "Engineer",
            "country": country,
            "salary": salary,
        },
    )
    return response.json()["id"]


def test_calculate_salary_for_india(client: TestClient) -> None:
    employee_id = _create_employee(client, country="India", salary=100000)

    response = client.get(f"/employees/{employee_id}/salary/calculate")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "employee_id": employee_id,
        "gross_salary": 100000.0,
        "deduction": 10000.0,
        "net_salary": 90000.0,
    }


def test_calculate_salary_for_united_states(client: TestClient) -> None:
    employee_id = _create_employee(client, country="United States", salary=100000)

    response = client.get(f"/employees/{employee_id}/salary/calculate")

    assert response.status_code == 200
    body = response.json()
    assert body["deduction"] == 12000.0
    assert body["net_salary"] == 88000.0


def test_calculate_salary_for_other_country_has_no_deduction(client: TestClient) -> None:
    employee_id = _create_employee(client, country="Brazil", salary=100000)

    response = client.get(f"/employees/{employee_id}/salary/calculate")

    assert response.status_code == 200
    body = response.json()
    assert body["deduction"] == 0.0
    assert body["net_salary"] == 100000.0


def test_calculate_salary_employee_not_found(client: TestClient) -> None:
    response = client.get("/employees/999999/salary/calculate")

    assert response.status_code == 404
