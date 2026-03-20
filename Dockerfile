FROM python:3.12-slim

ENV POETRY_VERSION=2.3.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY salary_api ./salary_api
COPY README.md .env.example ./
COPY data ./data
COPY logs ./logs
COPY rulechain ./rulechain

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "salary_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
