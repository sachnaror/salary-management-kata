from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from salary_api.settings import ensure_runtime_directories, settings

ensure_runtime_directories()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def run_schema_updates() -> None:
    with engine.begin() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
        }
        if "change_requests" not in tables:
            return

        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(change_requests)")).fetchall()
        }
        if "request_date" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE change_requests "
                    "ADD COLUMN request_date VARCHAR NOT NULL DEFAULT '1970-01-01'"
                )
            )


run_schema_updates()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
