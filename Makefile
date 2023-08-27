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

clean_docs:
	rm -rf docs/api/_build/

docs: clean_docs
	docs/docs.sh

run_docs:
	poetry run python -m http.server -d docs/api/_build 8000

clean_guides:
	rm -rf docs/guides/_build/

guides: clean_guides
	docs/guides.sh

run_guides:
	poetry run python -m http.server -d docs/guides/_build 9000

autodocs: clean_docs
	poetry run sphinx-autobuild -n --watch docs --watch libs/bodhilib/src -b html docs/api docs/api/_build/
