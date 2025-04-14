.PHONY: test-db migrate test clean

# запускаем тестовую бд (только postgres_test)
test-db:
 docker compose -f docker-compose.yaml -f docker-compose.test.yaml up -d postgres_test

# создаём таблицы без alembic
init-tables:
 DATABASE_URL=postgresql+asyncpg://test_user:test_pass@localhost:5433/test_db \
 PYTHONPATH=. python tests/init_test_db.py

# запускаем pytest
test:
 PYTHONPATH=. pytest

# всё с нуля: контейнер + таблицы + тесты
all: test-db migrate test

# чистим
clean:
 docker compose -f docker-compose.yaml -f docker-compose.test.yaml down -v
