from pathlib import Path

from fastapi.testclient import TestClient

from salary_api.settings import settings


def test_create_change_request_generates_open_questions_and_syncs_markdown(
    client: TestClient,
    tmp_path: Path,
) -> None:
    settings.docs_root = str(tmp_path / "docs")

    response = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Empty update validation",
            "request_summary": (
                "Update employee should require employee_id and at least one body field. "
                "Empty payload behavior should be clarified."
            ),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "awaiting_answers"
    assert body["topic"] == "Empty update validation"
    assert body["request_date"] == "2026-03-20"
    assert len(body["open_questions"]) >= 2
    assert body["open_questions"][0]["status"] == "pending"

    change_request_file = (
        Path(settings.docs_root)
        / "CHANGE_REQUESTS"
        / "change-request-1-empty-update-validation.md"
    )
    assert change_request_file.exists()
    contents = change_request_file.read_text()
    assert "## Business Input" in contents
    assert "## Implementation Analysis" in contents
    assert "- Date: 2026-03-20" in contents
    assert "- Topic: Empty update validation" in contents
    assert "User answer: pending" in contents


def test_answering_questions_updates_records_and_markdown(
    client: TestClient,
    tmp_path: Path,
) -> None:
    settings.docs_root = str(tmp_path / "docs")

    created = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Country normalization",
            "request_summary": (
                "Country aliases like US, USA, and United States of America should be handled "
                "consistently across salary calculation and metrics."
            ),
        },
    ).json()

    questions_response = client.get(f"/change-requests/{created['id']}/questions")
    assert questions_response.status_code == 200
    questions = questions_response.json()
    assert len(questions) >= 2

    for question in questions:
        answer_response = client.post(
            f"/open-questions/{question['id']}/answer",
            json={
                "answered_by": "Stakeholder",
                "answer_text": f"Answer for question {question['id']}",
            },
        )
        assert answer_response.status_code == 200
        assert answer_response.json()["status"] == "answered"

    updated = client.get(f"/change-requests/{created['id']}")
    assert updated.status_code == 200
    updated_body = updated.json()
    assert updated_body["status"] == "answered"
    assert all(question["status"] == "answered" for question in updated_body["open_questions"])

    change_request_file = (
        Path(settings.docs_root)
        / "CHANGE_REQUESTS"
        / "change-request-1-country-normalization.md"
    )
    contents = change_request_file.read_text()
    assert "User answer: Answer for question" in contents


def test_get_change_requests_returns_existing_records(client: TestClient, tmp_path: Path) -> None:
    settings.docs_root = str(tmp_path / "docs")

    client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Metrics validation",
            "request_summary": "Salary metrics should clarify how empty country input is handled.",
        },
    )

    response = client.get("/change-requests")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["topic"] == "Metrics validation"
    assert body[0]["status"] == "awaiting_answers"


def test_preview_requires_all_questions_answered(client: TestClient, tmp_path: Path) -> None:
    settings.docs_root = str(tmp_path / "docs")

    created = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Preview gating",
            "request_summary": "This request should not preview until every question is answered.",
        },
    ).json()

    response = client.post(f"/change-requests/{created['id']}/preview")

    assert response.status_code == 409


def test_preview_and_reject_flow(client: TestClient, tmp_path: Path) -> None:
    settings.docs_root = str(tmp_path / "docs")

    created = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Country normalization",
            "request_summary": (
                "Country aliases like US, USA, and United States should be normalized "
                "consistently in the application."
            ),
        },
    ).json()

    questions = client.get(f"/change-requests/{created['id']}/questions").json()
    for question in questions:
        answer_response = client.post(
            f"/open-questions/{question['id']}/answer",
            json={
                "answered_by": "Stakeholder",
                "answer_text": f"Approved answer {question['id']}",
            },
        )
        assert answer_response.status_code == 200

    preview_response = client.post(f"/change-requests/{created['id']}/preview")
    assert preview_response.status_code == 200
    preview_body = preview_response.json()
    assert preview_body["status"] == "preview_ready"
    assert len(preview_body["files_to_change"]) >= 1
    assert len(preview_body["tests_to_update"]) >= 1
    assert len(preview_body["docs_to_update"]) >= 1

    rejected_response = client.post(f"/change-requests/{created['id']}/reject")
    assert rejected_response.status_code == 200
    assert rejected_response.json()["status"] == "rejected"


def test_open_question_cannot_be_answered_twice(client: TestClient, tmp_path: Path) -> None:
    settings.docs_root = str(tmp_path / "docs")

    created = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Single answer rule",
            "request_summary": "Stakeholders should not be able to edit answers after saving.",
        },
    ).json()

    question = client.get(f"/change-requests/{created['id']}/questions").json()[0]

    first_response = client.post(
        f"/open-questions/{question['id']}/answer",
        json={
            "answered_by": "Stakeholder",
            "answer_text": "First and final answer",
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/open-questions/{question['id']}/answer",
        json={
            "answered_by": "Stakeholder",
            "answer_text": "Edited answer",
        },
    )
    assert second_response.status_code == 409


def test_change_request_generates_contextual_questions_for_name_validation(
    client: TestClient,
    tmp_path: Path,
) -> None:
    settings.docs_root = str(tmp_path / "docs")

    response = client.post(
        "/change-requests",
        json={
            "request_date": "2026-03-20",
            "topic": "Full name validation",
            "request_summary": "Employee full name should reject numbers and special characters.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["open_questions"]) >= 2

    question_texts = [question["question_text"] for question in body["open_questions"]]
    why_texts = [question["why_this_matters"] for question in body["open_questions"]]
    blocked_areas = [question["blocked_areas"] for question in body["open_questions"]]

    assert any("allowed" in text.lower() and "full name" in text.lower() for text in question_texts)
    assert any("existing" in text.lower() and "records" in text.lower() for text in question_texts)
    assert any("validation" in text.lower() for text in why_texts)
    assert any("schema validation" in text.lower() or "employee create" in text.lower() for text in blocked_areas)
