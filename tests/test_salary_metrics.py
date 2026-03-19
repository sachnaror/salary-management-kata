from fastapi.testclient import TestClient


def _create_employee(
    client: TestClient,
    full_name: str,
    job_title: str,
    country: str,
    salary: float,
) -> None:
    client.post(
        "/employees",
        json={
            "full_name": full_name,
            "job_title": job_title,
            "country": country,
            "salary": salary,
        },
    )


def test_country_salary_metrics(client: TestClient) -> None:
    _create_employee(client, "A", "Engineer", "India", 100000)
    _create_employee(client, "B", "Engineer", "India", 200000)
    _create_employee(client, "C", "Manager", "India", 300000)

    response = client.get("/salary-metrics/country/India")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "country": "India",
        "min_salary": 100000.0,
        "max_salary": 300000.0,
        "avg_salary": 200000.0,
    }


def test_country_salary_metrics_not_found(client: TestClient) -> None:
    response = client.get("/salary-metrics/country/Japan")

    assert response.status_code == 404


def test_job_title_average_salary_metrics(client: TestClient) -> None:
    _create_employee(client, "A", "Manager", "India", 100000)
    _create_employee(client, "B", "Manager", "United States", 300000)
    _create_employee(client, "C", "Engineer", "India", 500000)

    response = client.get("/salary-metrics/job-title/Manager")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "job_title": "Manager",
        "avg_salary": 200000.0,
    }


def test_job_title_average_salary_metrics_not_found(client: TestClient) -> None:
    response = client.get("/salary-metrics/job-title/Designer")

    assert response.status_code == 404
