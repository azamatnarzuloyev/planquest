.PHONY: up down restart logs logs-backend logs-frontend build test lint format db-shell migrate migrate-create clean

# === Docker ===
up:
	docker-compose up -d

up-build:
	docker-compose up -d --build

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

build:
	docker-compose build

# === Database ===
db-shell:
	docker-compose exec postgres psql -U planquest

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(name)"

# === Testing ===
test:
	docker-compose exec backend pytest

test-v:
	docker-compose exec backend pytest -v

# === Linting ===
lint:
	docker-compose exec backend ruff check .

format:
	docker-compose exec backend ruff format .

# === Cleanup ===
clean:
	docker-compose down -v --remove-orphans

# === Celery ===
logs-worker:
	docker-compose logs -f celery-worker

logs-beat:
	docker-compose logs -f celery-beat

# === Bot ===
webhook-test:
	curl -s -X POST http://localhost:8000/api/telegram/webhook -H "Content-Type: application/json" -d '{"update_id":1,"message":{"message_id":1,"from":{"id":12345,"is_bot":false,"first_name":"Test"},"chat":{"id":12345,"type":"private"},"date":1710500000,"text":"/start"}}'

# === Health check ===
health:
	curl -s http://localhost:8000/health | python3 -m json.tool
