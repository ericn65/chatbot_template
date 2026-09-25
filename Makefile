.DEFAULT_GOAL := help

UV ?= uv
TEST_ARGS ?=
PORT ?= 8000

.PHONY: help install hooks test coverage lint format typecheck check pre-commit telegram dashboard dashboard-training dashboard-correlations

help: ## Mostrar los comandos disponibles
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instalar dependencias, incluidas las de desarrollo
	$(UV) sync --group dev

hooks: ## Instalar los hooks de pre-commit
	$(UV) run pre-commit install

test: lint typecheck ## Comprobar Ruff y mypy y ejecutar tests sin cobertura (TEST_ARGS='ruta -k filtro')
	$(UV) run pytest --no-cov $(TEST_ARGS)

coverage: ## Ejecutar tests con cobertura en terminal, XML y HTML
	$(UV) run pytest --cov-report=html $(TEST_ARGS)

lint: ## Comprobar el codigo y su formato sin modificar archivos
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format: ## Corregir lint automaticamente y formatear el codigo
	$(UV) run ruff check --fix .
	$(UV) run ruff format .

typecheck: ## Comprobar tipos con mypy
	$(UV) run mypy

check: test ## Alias de test: Ruff, mypy y tests

pre-commit: ## Ejecutar todos los hooks (pueden modificar archivos)
	$(UV) run pre-commit run --all-files

telegram: ## Iniciar el webhook local de Telegram (requiere .env)
	$(UV) run uvicorn scripts.telegram_hook:app --reload --port $(PORT)

dashboard: ## Abrir el dashboard principal
	$(UV) run streamlit run scripts/run_dashboard.py

dashboard-training: ## Abrir el dashboard de entrenamiento
	$(UV) run streamlit run scripts/run_training_dashboard.py

dashboard-correlations: ## Abrir el dashboard de correlaciones
	$(UV) run streamlit run scripts/run_correlations_dashboard.py
