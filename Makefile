
COMPOSE          ?= docker-compose          # ← v2 (у alias docker‑compose тоже сработает)
COMPOSE_TEST_YML  = -f docker-compose.test.yaml

.PHONY: help up down restart build rebuild logs shell \
        migrate makemigrations \
        dev prod clean \
        test test-up test-build test-run test-down test-shell


up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down -v

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) down -v
	$(COMPOSE) build
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec backend bash

migrate:
	$(COMPOSE) exec backend alembic upgrade head

makemigrations:
	$(COMPOSE) exec backend alembic revision --autogenerate -m "New migration"


test-up:
	$(COMPOSE) $(COMPOSE_TEST_YML) up -d --build postgres_test

test-build:
	$(COMPOSE) $(COMPOSE_TEST_YML) build test_runner

test-run:
	$(COMPOSE) $(COMPOSE_TEST_YML) run --rm test_runner

test: test-up test-build
	@echo "⏳  Waiting for postgres_test to warm up …"
	sleep 3
	$(MAKE) test-run
	$(MAKE) test-down

test-down:
	$(COMPOSE) $(COMPOSE_TEST_YML) down -v

test-shell:
	$(COMPOSE) $(COMPOSE_TEST_YML) run --rm test_runner bash

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .mypy_cache .pytest_cache logs.txt
