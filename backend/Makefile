env:
	source ./.venv/bin/activate

install:
	poetry install

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

test:
	pytest tests/ -v

seed:
	python -m tools.seeder

seed-fresh:
	python -m tools.seeder --clear

.PHONY: env run dev install migrate migrate-create migrate-up migrate-down test seed seed-fresh
