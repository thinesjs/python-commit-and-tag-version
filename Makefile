.PHONY: install install-dev test test-unit test-integration lint format check clean build

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

test-unit:
	pytest -v -m "not integration"

test-integration:
	pytest -v -m integration

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

check: lint test

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build
