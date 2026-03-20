.PHONY: install lock run test docker-up docker-down clean

VENV_BIN := .venv/bin

install:
	POETRY_VIRTUALENVS_IN_PROJECT=true poetry install --with dev

lock:
	POETRY_VIRTUALENVS_IN_PROJECT=true poetry lock

run:
	PYTHONPATH=. $(VENV_BIN)/uvicorn salary_api.main:app --reload --host $${APP_HOST:-0.0.0.0} --port $${APP_PORT:-8001}

test:
	PYTHONPATH=. $(VENV_BIN)/pytest -c pytest.ini tests

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
