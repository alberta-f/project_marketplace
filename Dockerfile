FROM python:3.12-slim

RUN pip install --upgrade pip && pip install poetry && pip install alembic gunicorn

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-root --with dev

COPY . /app

EXPOSE 8000

RUN adduser --disabled-password --gecos '' celeryuser
USER celeryuser

ENV WEB_CONCURRENCY=5

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "$WEB_CONCURRENCY", "-b", "0.0.0.0:8000", "app.main:app"]
