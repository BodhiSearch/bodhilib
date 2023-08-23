.PHONY: help clean clean_docs build_docs linkcheck

all: help

help:
	@echo "clean       - remove all build artifacts"
	@echo "clean_docs  - remove all doc build artifacts"
	@echo "build_docs  - compile the documentation using Sphinx"

clean: clean_docs

clean_docs:
	rm -rf docs/_build/
	rm -rf docs/reference/

build_docs: clean_docs
	docs/build_docs.sh

run_docs:
	poetry run python -m http.server -d docs/_build 8000

run_autodocs:
	poetry run sphinx-autobuild -n --watch docs --watch bodhilib.cohere -b html docs/ docs/_build/

build: clean build_docs
