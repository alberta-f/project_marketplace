# ==== CONFIG ====
ENV_FILE=.env
ENV_TEST_FILE=.env.test

# ==== DOCKER ====
up:
	docker-compose --env-file $(ENV_FILE) up -d

build:
	docker-compose build

rebuild:
	docker-compose down -v
	docker-compose build
	docker-compose up -d

logs:
	docker-compose logs -f

down:
	docker-compose down -v

restart:
	docker-compose restart

# ==== BACKEND ====
shell:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend alembic upgrade head

makemigrations:
	docker-compose exec backend alembic revision --autogenerate -m "New migration"

# ==== TESTING ====
test-down:
	docker-compose -f docker-compose.test.yaml down -v

test-up:
	docker-compose -f docker-compose.test.yaml up --build --abort-on-container-exit

test-restart:	test-down test-up


test-shell:
	docker-compose -f docker-compose.yaml -f docker-compose.test.yaml run --rm test_runner bash

# ==== CLEAN ====
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .mypy_cache .pytest_cache logs.txt
