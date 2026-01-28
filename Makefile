.PHONY: help install dev test lint format type-check clean docker-up docker-down docker-test pre-commit-install

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Run development server"
	@echo "  make test             - Run all tests with coverage"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code with ruff"
	@echo "  make type-check       - Run mypy type checking"
	@echo "  make clean            - Clean cache and temp files"
	@echo "  make docker-up        - Start services with Docker Compose"
	@echo "  make docker-down      - Stop Docker Compose services"
	@echo "  make docker-test      - Run tests in Docker"
	@echo "  make pre-commit-install - Set up pre-commit hooks"

install:
	pip install -r requirements.txt
	pip install -e .

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest --cov=src tests/

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist/ build/ *.egg-info/
	rm -rf htmlcov/ .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

pre-commit-install:
	pre-commit install
	pre-commit run --all-files
