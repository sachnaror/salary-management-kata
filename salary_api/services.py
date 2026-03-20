import json
from datetime import UTC, datetime
from pathlib import Path
from re import sub

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from salary_api.models import (
    ChangeRequest,
    ChangeRequestPreview,
    Employee,
    OpenQuestion,
    OpenQuestionAnswerHistory,
)
from salary_api.settings import settings


def get_employee_or_404(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


def deduction_rate_for_country(country: str) -> float:
    normalized_country = country.strip().lower()
    if normalized_country == "india":
        return 0.10
    if normalized_country in {"united states", "usa", "us"}:
        return 0.12
    return 0.0


def get_change_request_or_404(db: Session, change_request_id: int) -> ChangeRequest:
    change_request = db.query(ChangeRequest).filter(ChangeRequest.id == change_request_id).first()
    if not change_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change request not found")
    return change_request


def get_open_question_or_404(db: Session, question_id: int) -> OpenQuestion:
    question = db.query(OpenQuestion).filter(OpenQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Open question not found")
    return question


def get_change_request_preview_or_404(db: Session, change_request_id: int) -> ChangeRequestPreview:
    preview = (
        db.query(ChangeRequestPreview)
        .filter(ChangeRequestPreview.change_request_id == change_request_id)
        .first()
    )
    if not preview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preview not found")
    return preview


def generate_open_questions(topic: str, request_summary: str) -> list[dict[str, str]]:
    normalized = f"{topic} {request_summary}".lower()
    if "full name" in normalized and (
        "special character" in normalized or "numbers" in normalized or "reject" in normalized
    ):
        return [
            {
                "question_text": (
                    "Which characters should still be allowed in the full name field, "
                    "for example spaces, hyphens, apostrophes, or periods?"
                ),
                "why_this_matters": (
                    "The exact allowed-character set defines the validation rule and prevents "
                    "accidentally blocking legitimate real-world names."
                ),
                "blocked_areas": (
                    "schema validation, employee create/update endpoints, UI validation hints, "
                    "edge-case tests"
                ),
            },
            {
                "question_text": (
                    "How should the system handle existing employee records that already contain "
                    "numbers or special characters in the full name?"
                ),
                "why_this_matters": (
                    "Changing validation for new requests is straightforward, but existing data may "
                    "need to be grandfathered, flagged, or cleaned up."
                ),
                "blocked_areas": (
                    "existing database records, update behavior, migration strategy, regression tests"
                ),
            },
        ]

    if "country" in normalized or "usa" in normalized or "united states" in normalized:
        return [
            {
                "question_text": (
                    "Should normalization happen only during calculations and metrics, "
                    "or should values be normalized before saving to the database?"
                ),
                "why_this_matters": (
                    "Persisted normalization changes stored data, while read-time normalization "
                    "keeps original user input intact."
                ),
                "blocked_areas": (
                    "employee create/update validation, salary calculation logic, "
                    "metrics aggregation logic, test expectations for stored values"
                ),
            },
            {
                "question_text": (
                    "What aliases should be accepted for the same country, starting with the United States?"
                ),
                "why_this_matters": (
                    "Without a defined alias list, contributors may implement different mappings "
                    "and create inconsistent behavior."
                ),
                "blocked_areas": (
                    "domain rules, validation utilities, seeded demo data, regression tests"
                ),
            },
        ]

    if "delete" in normalized and "confirm" in normalized:
        return [
            {
                "question_text": (
                    "Should the delete confirmation exist only in the UI, or should the API also require "
                    "an explicit confirmation flag?"
                ),
                "why_this_matters": (
                    "UI-only confirmation protects browser users, but API-level confirmation changes the "
                    "contract for scripts and future integrations."
                ),
                "blocked_areas": (
                    "delete endpoint contract, dashboard behavior, API examples, tests"
                ),
            },
            {
                "question_text": (
                    "What confirmation wording should be shown so users understand the deletion is permanent?"
                ),
                "why_this_matters": (
                    "Confirmation UX needs explicit wording to reduce accidental destructive actions."
                ),
                "blocked_areas": (
                    "UI copy, dashboard interactions, product wording, manual review expectations"
                ),
            },
        ]

    if "decimal" in normalized and "salary" in normalized:
        return [
            {
                "question_text": (
                    "Should salary allow exactly two decimal places, or up to two decimal places?"
                ),
                "why_this_matters": (
                    "That choice changes validation rules and determines whether whole numbers remain valid "
                    "without trailing decimal digits."
                ),
                "blocked_areas": (
                    "salary schema validation, UI input behavior, tests, API examples"
                ),
            },
            {
                "question_text": (
                    "If a salary value has more than two decimal places, should the system reject it or round it?"
                ),
                "why_this_matters": (
                    "Rounding and rejection are both valid strategies, but they lead to different financial behavior."
                ),
                "blocked_areas": (
                    "create/update validation, salary calculations, metrics accuracy, regression tests"
                ),
            },
        ]

    return [
        {
            "question_text": (
                "Should this new rule be enforced at the API level, the UI level, or both?"
            ),
            "why_this_matters": (
                "The enforcement layer defines whether integrations and direct API clients are affected, "
                "or only interactive dashboard users."
            ),
            "blocked_areas": (
                "endpoint validation, dashboard behavior, regression tests, documentation examples"
            ),
        },
        {
            "question_text": (
                "How should existing records or current behavior be handled if this request conflicts with them?"
            ),
            "why_this_matters": (
                "A new rule may require backward-compatibility handling, migration, or explicit rejection of old behavior."
            ),
            "blocked_areas": (
                "domain rules, existing data, tests, decision log, implementation plan"
            ),
        },
    ]


def generate_preview_plan(change_request: ChangeRequest) -> dict[str, list[str] | str]:
    normalized = f"{change_request.topic} {change_request.request_summary}".lower()

    files_to_change = ["salary_api/main.py", "salary_api/services.py"]
    tests_to_update = ["tests/test_change_requests.py"]
    docs_to_update = [
        "rulechain/DOMAIN_RULES.md",
        "rulechain/DECISION_LOG.md",
        "rulechain/TEST_MATRIX.md",
        "README.md",
    ]
    conflict_warnings = []

    if "employee" in normalized:
        files_to_change.extend(["salary_api/schemas.py", "salary_api/ui/index.html", "salary_api/ui/app.js"])
        tests_to_update.append("tests/test_employee_crud.py")
    if "country" in normalized or "metrics" in normalized:
        tests_to_update.extend(["tests/test_salary_calculation.py", "tests/test_salary_metrics.py"])
    if "empty update" in normalized or "update" in normalized:
        conflict_warnings.append(
            "Current update behavior allows empty payloads. The requested change may break existing tests."
        )

    diff_text = "\n".join(
        [
            "--- implementation-preview",
            "+++ implementation-preview",
            "@@",
            f"+ Topic: {change_request.topic}",
            f"+ Request summary: {change_request.request_summary}",
            "+ Proposed workflow: add/update failing tests, make them pass, refactor, update docs.",
        ]
    )

    return {
        "files_to_change": sorted(set(files_to_change)),
        "tests_to_update": sorted(set(tests_to_update)),
        "docs_to_update": sorted(set(docs_to_update)),
        "conflict_warnings": conflict_warnings or ["No immediate conflicts detected by the local analyzer."],
        "diff_text": diff_text,
    }


def create_change_request_markdown(change_request: ChangeRequest) -> None:
    docs_root = Path(settings.docs_root)
    change_requests_dir = docs_root / "CHANGE_REQUESTS"
    change_requests_dir.mkdir(parents=True, exist_ok=True)

    slug = sub(r"[^a-z0-9]+", "-", change_request.topic.lower()).strip("-")
    file_path = change_requests_dir / f"change-request-{change_request.id}-{slug}.md"

    questions_section = "\n".join(
        [
            "\n".join(
                [
                    f"- Question {index}: {question.question_text}",
                    f"  - Why this matters: {question.why_this_matters}",
                    "  - Blocked implementation areas:",
                    *[f"    - {area.strip()}" for area in question.blocked_areas.split(",")],
                    f"  - User answer: {question.answer_text or 'pending'}",
                ]
            )
            for index, question in enumerate(change_request.open_questions, start=1)
        ]
    )

    body = "\n".join(
        [
            "# Change Request",
            "",
            "## Business Input",
            f"- Date: {change_request.request_date}",
            f"- Topic: {change_request.topic}",
            f"- Request summary: {change_request.request_summary}",
            "",
            "## Implementation Analysis",
            "### Why This Matters",
            "- Generated from current rules and request summary.",
            "",
            "### Conflict Check",
            "- Existing rules reviewed:",
            "  - rulechain/DOMAIN_RULES.md",
            "  - rulechain/DECISION_LOG.md",
            "  - rulechain/TEST_MATRIX.md",
            "- Existing tests reviewed:",
            "  - tests relevant to the affected area",
            "- Conflicts found:",
            f"  - Current workflow status: {change_request.status}",
            "",
            "### Open Questions",
            questions_section,
            "",
            "### TDD Status",
            "- Red: not started",
            "- Green: not started",
            "- Refactor: not started",
            "",
            "### Documentation Files To Update After Answers",
            "- rulechain/DOMAIN_RULES.md",
            "- rulechain/DECISION_LOG.md",
            "- rulechain/TEST_MATRIX.md",
            "- active change request file",
            "",
        ]
    )
    file_path.write_text(body)

    sync_open_questions_summary(change_request)


def sync_open_questions_summary(change_request: ChangeRequest) -> None:
    docs_root = Path(settings.docs_root)
    docs_root.mkdir(parents=True, exist_ok=True)
    file_path = docs_root / "OPEN_QUESTIONS.md"

    lines = [
        "# Open Questions",
        "",
        "This file is synchronized from change-request records.",
        "",
        f"## Change Request {change_request.id}: {change_request.topic}",
    ]

    if not change_request.open_questions:
        lines.extend(["- No open questions."])
    else:
        for index, question in enumerate(change_request.open_questions, start=1):
            lines.extend(
                [
                    f"- Question {index}: {question.question_text}",
                    f"  - Status: {question.status}",
                    f"  - Why this matters: {question.why_this_matters}",
                    f"  - Blocked implementation areas: {question.blocked_areas}",
                    f"  - User answer: {question.answer_text or 'pending'}",
                ]
            )

    lines.append("")
    file_path.write_text("\n".join(lines))


def refresh_change_request_status(change_request: ChangeRequest) -> None:
    if change_request.open_questions and all(
        question.status == "answered" for question in change_request.open_questions
    ):
        change_request.status = "answered"
    else:
        change_request.status = "awaiting_answers"
    change_request.updated_at = datetime.now(UTC)


def serialize_preview(preview: ChangeRequestPreview) -> dict[str, list[str] | str | int | datetime]:
    return {
        "id": preview.id,
        "change_request_id": preview.change_request_id,
        "files_to_change": json.loads(preview.files_to_change),
        "tests_to_update": json.loads(preview.tests_to_update),
        "docs_to_update": json.loads(preview.docs_to_update),
        "conflict_warnings": json.loads(preview.conflict_warnings),
        "diff_text": preview.diff_text,
        "created_at": preview.created_at,
        "updated_at": preview.updated_at,
        "status": "preview_ready",
    }


def save_preview(
    db: Session,
    change_request: ChangeRequest,
    preview_data: dict[str, list[str] | str],
) -> ChangeRequestPreview:
    preview = change_request.preview
    if preview is None:
        preview = ChangeRequestPreview(change_request_id=change_request.id)
        db.add(preview)

    preview.files_to_change = json.dumps(preview_data["files_to_change"])
    preview.tests_to_update = json.dumps(preview_data["tests_to_update"])
    preview.docs_to_update = json.dumps(preview_data["docs_to_update"])
    preview.conflict_warnings = json.dumps(preview_data["conflict_warnings"])
    preview.diff_text = str(preview_data["diff_text"])
    change_request.status = "preview_ready"
    change_request.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(change_request)
    db.refresh(preview)
    return preview


def ensure_question_can_be_answered(question: OpenQuestion) -> None:
    if question.status == "answered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This question has already been answered and cannot be edited.",
        )


def record_answer_history(
    db: Session,
    question: OpenQuestion,
    answered_by: str,
    answer_text: str,
) -> None:
    db.add(
        OpenQuestionAnswerHistory(
            open_question_id=question.id,
            answered_by=answered_by,
            answer_text=answer_text,
        )
    )
