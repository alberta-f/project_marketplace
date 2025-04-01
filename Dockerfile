FROM python:3.12-slim

RUN pip install --upgrade pip && pip install poetry && pip install alembic

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-root
  # && poetry run celery -A app.celery_worker.celery_app worker --loglevel=info -Q email

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
