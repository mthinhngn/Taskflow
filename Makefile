.PHONY: help up down logs test clean build

help:
	@echo "TaskFlow Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make up          - Start all services with Docker Compose"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make test        - Run backend tests"
	@echo "  make build       - Build Docker images"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make db-migrate  - Run database migrations"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-db:
	docker compose logs -f db

test:
	docker compose exec api pytest -v

test-cov:
	docker compose exec api pytest --cov=app --cov-report=html

db-migrate:
	docker compose exec api alembic upgrade head

db-downgrade:
	docker compose exec api alembic downgrade -1

db-shell:
	docker compose exec db psql -U taskflow -d taskflow

redis-cli:
	docker compose exec cache redis-cli

build:
	docker compose build

clean:
	docker compose down -v

api-shell:
	docker compose exec api bash

frontend-shell:
	docker compose exec frontend sh

format:
	docker compose exec api black app/
	docker compose exec api isort app/
