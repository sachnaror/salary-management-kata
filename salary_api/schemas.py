from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    full_name: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    country: str = Field(min_length=1)
    salary: float = Field(gt=0)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    full_name: str | None = Field(default=None, min_length=1)
    job_title: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, min_length=1)
    salary: float | None = Field(default=None, gt=0)


class EmployeeResponse(EmployeeBase):
    id: int

    model_config = {"from_attributes": True}


class SalaryCalculationResponse(BaseModel):
    employee_id: int
    gross_salary: float
    deduction: float
    net_salary: float


class CountrySalaryMetricsResponse(BaseModel):
    country: str
    min_salary: float
    max_salary: float
    avg_salary: float


class JobTitleSalaryMetricsResponse(BaseModel):
    job_title: str
    avg_salary: float


class OpenQuestionAnswerCreate(BaseModel):
    answered_by: str = Field(min_length=1)
    answer_text: str = Field(min_length=1)


class OpenQuestionAnswerHistoryResponse(BaseModel):
    id: int
    open_question_id: int
    answered_by: str
    answer_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OpenQuestionResponse(BaseModel):
    id: int
    change_request_id: int
    question_text: str
    why_this_matters: str
    blocked_areas: str
    status: str
    answer_text: str | None = None
    answered_by: str | None = None
    answered_at: datetime | None = None
    answer_history: list[OpenQuestionAnswerHistoryResponse] = []

    model_config = {"from_attributes": True}


class ChangeRequestCreate(BaseModel):
    request_date: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    request_summary: str = Field(min_length=1)


class ChangeRequestResponse(BaseModel):
    id: int
    request_date: str
    topic: str
    request_summary: str
    status: str
    created_at: datetime
    updated_at: datetime
    open_questions: list[OpenQuestionResponse]

    model_config = {"from_attributes": True}


class ChangeRequestPreviewResponse(BaseModel):
    id: int
    change_request_id: int
    files_to_change: list[str]
    tests_to_update: list[str]
    docs_to_update: list[str]
    conflict_warnings: list[str]
    diff_text: str
    created_at: datetime
    updated_at: datetime
    status: str
