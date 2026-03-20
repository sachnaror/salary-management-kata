from datetime import UTC, date, datetime
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from salary_api.database import Base, engine, get_db
from salary_api.models import ChangeRequest, Employee, OpenQuestion
from salary_api.schemas import (
    ChangeRequestCreate,
    ChangeRequestPreviewResponse,
    ChangeRequestResponse,
    CountrySalaryMetricsResponse,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    JobTitleSalaryMetricsResponse,
    OpenQuestionAnswerCreate,
    OpenQuestionResponse,
    SalaryCalculationResponse,
)
from salary_api.services import (
    create_change_request_markdown,
    deduction_rate_for_country,
    generate_open_questions,
    generate_preview_plan,
    get_change_request_or_404,
    get_change_request_preview_or_404,
    get_employee_or_404,
    get_open_question_or_404,
    ensure_question_can_be_answered,
    refresh_change_request_status,
    record_answer_history,
    save_preview,
    serialize_preview,
)
from salary_api.settings import settings

Base.metadata.create_all(bind=engine)

logging.basicConfig(
    filename=settings.log_file,
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title=settings.app_name)
UI_DIR = Path(__file__).parent / "ui"


@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)) -> Employee:
    employee = Employee(
        full_name=payload.full_name,
        job_title=payload.job_title,
        country=payload.country,
        salary=payload.salary,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@app.get("/employees", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)) -> list[Employee]:
    return db.query(Employee).all()


@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> Employee:
    return get_employee_or_404(db, employee_id)


@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> Employee:
    employee = get_employee_or_404(db, employee_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> Response:
    employee = get_employee_or_404(db, employee_id)

    db.delete(employee)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/employees/{employee_id}/salary/calculate",
    response_model=SalaryCalculationResponse,
)
def calculate_salary(employee_id: int, db: Session = Depends(get_db)) -> SalaryCalculationResponse:
    employee = get_employee_or_404(db, employee_id)
    deduction_rate = deduction_rate_for_country(employee.country)

    gross_salary = float(employee.salary)
    deduction = round(gross_salary * deduction_rate, 2)
    net_salary = round(gross_salary - deduction, 2)

    return SalaryCalculationResponse(
        employee_id=employee.id,
        gross_salary=gross_salary,
        deduction=deduction,
        net_salary=net_salary,
    )


@app.get(
    "/salary-metrics/country/{country}",
    response_model=CountrySalaryMetricsResponse,
)
def salary_metrics_by_country(
    country: str,
    db: Session = Depends(get_db),
) -> CountrySalaryMetricsResponse:
    min_salary, max_salary, avg_salary = (
        db.query(
            func.min(Employee.salary),
            func.max(Employee.salary),
            func.avg(Employee.salary),
        )
        .filter(func.lower(Employee.country) == country.strip().lower())
        .one()
    )
    if min_salary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employees found")

    return CountrySalaryMetricsResponse(
        country=country,
        min_salary=float(min_salary),
        max_salary=float(max_salary),
        avg_salary=round(float(avg_salary), 2),
    )


@app.get(
    "/salary-metrics/job-title/{job_title}",
    response_model=JobTitleSalaryMetricsResponse,
)
def salary_metrics_by_job_title(
    job_title: str,
    db: Session = Depends(get_db),
) -> JobTitleSalaryMetricsResponse:
    avg_salary = (
        db.query(func.avg(Employee.salary))
        .filter(func.lower(Employee.job_title) == job_title.strip().lower())
        .scalar()
    )
    if avg_salary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employees found")

    return JobTitleSalaryMetricsResponse(
        job_title=job_title,
        avg_salary=round(float(avg_salary), 2),
    )


@app.get("/", include_in_schema=False)
def ui_home() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/ui/app.js", include_in_schema=False)
def ui_js() -> FileResponse:
    return FileResponse(UI_DIR / "app.js", media_type="application/javascript")


@app.get("/ui/styles.css", include_in_schema=False)
def ui_css() -> FileResponse:
    return FileResponse(UI_DIR / "styles.css", media_type="text/css")


@app.post(
    "/change-requests",
    response_model=ChangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_change_request(
    payload: ChangeRequestCreate,
    db: Session = Depends(get_db),
) -> ChangeRequest:
    change_request = ChangeRequest(
        request_date=payload.request_date or date.today().isoformat(),
        topic=payload.topic,
        requested_by="Business Analyst",
        request_summary=payload.request_summary,
        status="awaiting_answers",
    )
    db.add(change_request)
    db.flush()

    for question_data in generate_open_questions(payload.topic, payload.request_summary):
        db.add(
            OpenQuestion(
                change_request_id=change_request.id,
                question_text=question_data["question_text"],
                why_this_matters=question_data["why_this_matters"],
                blocked_areas=question_data["blocked_areas"],
                status="pending",
            )
        )

    db.commit()
    db.refresh(change_request)
    create_change_request_markdown(change_request)
    db.refresh(change_request)
    return change_request


@app.get("/change-requests", response_model=list[ChangeRequestResponse])
def list_change_requests(db: Session = Depends(get_db)) -> list[ChangeRequest]:
    return db.query(ChangeRequest).order_by(ChangeRequest.id.desc()).all()


@app.get("/change-requests/{change_request_id}", response_model=ChangeRequestResponse)
def get_change_request(change_request_id: int, db: Session = Depends(get_db)) -> ChangeRequest:
    return get_change_request_or_404(db, change_request_id)


@app.get(
    "/change-requests/{change_request_id}/questions",
    response_model=list[OpenQuestionResponse],
)
def list_open_questions(change_request_id: int, db: Session = Depends(get_db)) -> list[OpenQuestion]:
    change_request = get_change_request_or_404(db, change_request_id)
    return change_request.open_questions


@app.post("/open-questions/{question_id}/answer", response_model=OpenQuestionResponse)
def answer_open_question(
    question_id: int,
    payload: OpenQuestionAnswerCreate,
    db: Session = Depends(get_db),
) -> OpenQuestion:
    question = get_open_question_or_404(db, question_id)
    ensure_question_can_be_answered(question)
    question.answer_text = payload.answer_text
    question.answered_by = payload.answered_by
    question.answered_at = datetime.now(UTC)
    question.status = "answered"
    record_answer_history(db, question, payload.answered_by, payload.answer_text)
    refresh_change_request_status(question.change_request)
    db.commit()
    db.refresh(question)
    db.refresh(question.change_request)
    create_change_request_markdown(question.change_request)
    db.refresh(question)
    return question


@app.post(
    "/change-requests/{change_request_id}/preview",
    response_model=ChangeRequestPreviewResponse,
)
def preview_change_request(
    change_request_id: int,
    db: Session = Depends(get_db),
) -> ChangeRequestPreviewResponse:
    change_request = get_change_request_or_404(db, change_request_id)
    if change_request.status != "answered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="All open questions must be answered before preview is available.",
        )

    preview = save_preview(db, change_request, generate_preview_plan(change_request))
    return ChangeRequestPreviewResponse(**serialize_preview(preview))


@app.get(
    "/change-requests/{change_request_id}/preview",
    response_model=ChangeRequestPreviewResponse,
)
def get_change_request_preview(
    change_request_id: int,
    db: Session = Depends(get_db),
) -> ChangeRequestPreviewResponse:
    preview = get_change_request_preview_or_404(db, change_request_id)
    return ChangeRequestPreviewResponse(**serialize_preview(preview))


@app.post("/change-requests/{change_request_id}/reject", response_model=ChangeRequestResponse)
def reject_change_request(
    change_request_id: int,
    db: Session = Depends(get_db),
) -> ChangeRequest:
    change_request = get_change_request_or_404(db, change_request_id)
    change_request.status = "rejected"
    db.commit()
    db.refresh(change_request)
    return change_request


@app.post("/change-requests/{change_request_id}/approve", response_model=ChangeRequestResponse)
def approve_change_request(
    change_request_id: int,
    db: Session = Depends(get_db),
) -> ChangeRequest:
    change_request = get_change_request_or_404(db, change_request_id)
    if change_request.status != "preview_ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Preview must be generated before final approval.",
        )

    if not settings.llm_analysis_enabled or settings.llm_provider != "openai" or not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Automatic repo modification is not configured yet. "
                "Enable OpenAI configuration first before final approval can apply code changes."
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Automatic code application is not implemented yet.",
    )
