.PHONY: help lint format format-check test test-ci check run migrate reqs

help:
	@echo "OmniTech - Comandos disponibles"
	@echo "================================"
	@echo "make lint        - Ejecutar ruff linter"
	@echo "make format      - Formatear codigo con ruff"
	@echo "make format-check - Verificar formato (sin modificar)"
	@echo "make test        - Ejecutar tests con pytest"
	@echo "make test-ci     - Ejecutar tests en modo CI (con cobertura)"
	@echo "make check       - Ejecutar lint + format-check + test"
	@echo "make run         - Iniciar servidor de desarrollo"
	@echo "make migrate     - Ejecutar migraciones"
	@echo "make reqs        - Instalar dependencias"

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

test:
	pytest

test-ci:
	pytest --cov=omnitech --cov-report=term-missing --cov-report=xml

check: lint format-check test

run:
	python manage.py runserver

migrate:
	python manage.py migrate

reqs:
	pip install -r requirements.txt
