from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from salary_api.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    job_title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String, nullable=False, index=True)
    salary: Mapped[float] = mapped_column(Float, nullable=False)


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_date: Mapped[str] = mapped_column(String, nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    requested_by: Mapped[str] = mapped_column(String, nullable=False, default="Business Analyst")
    request_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="awaiting_answers")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    open_questions: Mapped[list["OpenQuestion"]] = relationship(
        back_populates="change_request",
        cascade="all, delete-orphan",
    )
    preview: Mapped["ChangeRequestPreview | None"] = relationship(
        back_populates="change_request",
        cascade="all, delete-orphan",
        uselist=False,
    )


class OpenQuestion(Base):
    __tablename__ = "open_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    change_request_id: Mapped[int] = mapped_column(
        ForeignKey("change_requests.id"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    why_this_matters: Mapped[str] = mapped_column(Text, nullable=False)
    blocked_areas: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by: Mapped[str | None] = mapped_column(String, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    change_request: Mapped[ChangeRequest] = relationship(back_populates="open_questions")
    answer_history: Mapped[list["OpenQuestionAnswerHistory"]] = relationship(
        back_populates="open_question",
        cascade="all, delete-orphan",
    )


class OpenQuestionAnswerHistory(Base):
    __tablename__ = "open_question_answer_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    open_question_id: Mapped[int] = mapped_column(
        ForeignKey("open_questions.id"),
        nullable=False,
        index=True,
    )
    answered_by: Mapped[str] = mapped_column(String, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    open_question: Mapped[OpenQuestion] = relationship(back_populates="answer_history")


class ChangeRequestPreview(Base):
    __tablename__ = "change_request_previews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    change_request_id: Mapped[int] = mapped_column(
        ForeignKey("change_requests.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    files_to_change: Mapped[str] = mapped_column(Text, nullable=False)
    tests_to_update: Mapped[str] = mapped_column(Text, nullable=False)
    docs_to_update: Mapped[str] = mapped_column(Text, nullable=False)
    conflict_warnings: Mapped[str] = mapped_column(Text, nullable=False)
    diff_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    change_request: Mapped[ChangeRequest] = relationship(back_populates="preview")
