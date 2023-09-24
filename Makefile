.PHONY: help clean clean_docs docs run_docs clean_guides guides run_guides autodocs

all: help

help:
	@echo "clean        - remove all build artifacts"
	@echo "check        - check poetry file for descrepencies, used by CI"
	@echo "install      - install all python dependencies"
	@echo "lint         - run all code quality and linting checks"
	@echo "test         - run all unit tests with coverage"
	@echo "build        - build the python package"
	@echo "clean_docs   - remove all doc build artifacts"
	@echo "docs         - compile the documentation using Sphinx"
	@echo "run_docs     - run the docs on port 8000"

clean: clean_docs clean_guides

check:
	poetry check
	poetry lock --check

install:
	poetry install --compile

lint: install
	poetry run pre-commit run --all-files

test: install
	poetry run pytest --cov=bodhilib --cov-report=html

build: clean install
	poetry build

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	docs/docs.py

run_docs:
	poetry run python -m http.server -d docs/_build 8000
