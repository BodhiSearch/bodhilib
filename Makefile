.PHONY: help clean clean_docs docs run_docs clean_guides guides run_guides autodocs

all: help

help:
	@echo "clean        - remove all build artifacts"
	@echo "clean_docs   - remove all doc build artifacts"
	@echo "docs         - compile the documentation using Sphinx"
	@echo "run_docs     - run the docs on port 8000"
	@echo "clean_guides - remove all guides build artifacts"
	@echo "guides       - compile the documentation using Sphinx"
	@echo "run_guides   - run the docs on port 9000"
	@echo "autodocs     - run sphinx-autobuild to watch for changes and rebuild docs"

clean: clean_docs clean_guides

check:
	poetry check
	poetry lock --check

install:
	poetry install

lint: install
	poetry run pre-commit run --all-files

test: install
	poetry run pytest --cov=bodhilib --cov-report=html

build: clean install
	poetry build

clean_docs:
	rm -rf docs/api/_build/

docs: clean_docs
	docs/docs.py

run_docs:
	poetry run python -m http.server -d docs/api/_build 8000

autodocs: clean_docs
	poetry run sphinx-autobuild -n --watch docs --watch libs/bodhilib/src -b html docs/api docs/api/_build/
