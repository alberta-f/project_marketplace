FROM python:3.12-slim

RUN pip install --upgrade pip && pip install poetry && pip install alembic

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-root

COPY . /app

EXPOSE 8000

RUN adduser --disabled-password --gecos '' celeryuser
USER celeryuser


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
